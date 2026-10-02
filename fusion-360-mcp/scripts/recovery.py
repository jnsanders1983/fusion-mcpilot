"""Local F3D recovery archives and viewport snapshots; no cloud side effects."""
import json
from pathlib import Path
from contracts import geometry_expectations


def checkpoint_script(directory, document=None):
    config = {'directory':str(Path(directory).resolve()), 'document':document}
    return '''import adsk.core,adsk.fusion,json,os,time
C=json.loads(CONFIG_JSON)
def run(_context: str):
 start=time.perf_counter();app=adsk.core.Application.get();original=app.activeDocument
 os.makedirs(C['directory'],exist_ok=True)
 docs=[doc for doc in app.documents if C['document'] is None or doc.name==C['document']]
 if C['document'] and len(docs)!=1:raise RuntimeError('Checkpoint document missing or ambiguous.')
 records=[]
 try:
  for i,doc in enumerate(docs):
   design=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
   if design is None:
    records.append({'document':doc.name,'skipped':'Not a CAD Design product.'});continue
   doc.activate()
   archive=os.path.join(C['directory'],'document-'+str(i)+'.f3d')
   preview=os.path.join(C['directory'],'document-'+str(i)+'.png')
   if os.path.exists(archive) or os.path.exists(preview):raise RuntimeError('Checkpoint already exists.')
   if not design.exportManager.execute(design.exportManager.createFusionArchiveExportOptions(archive)):raise RuntimeError('Recovery archive export failed.')
   if not os.path.exists(archive) or os.path.getsize(archive)==0:raise RuntimeError('Recovery archive is empty.')
   image_ok=app.activeViewport.saveAsImageFile(preview,960,660)
   records.append({'document':doc.name,'archive':archive,'archive_bytes':os.path.getsize(archive),'preview':preview if image_ok else None,'modified':doc.isModified})
 finally:
  if original is not None and original.isValid:original.activate()
 print(json.dumps({'checkpoints':records,'original_document':original.name if original else None,'cloud_saved':False,'fusion_execution_verification_seconds':time.perf_counter()-start}))
'''.replace('CONFIG_JSON',repr(json.dumps(config)))


def restore_script(archive, document, expected=None, disposable_owner=None):
    """Import local F3D or STEP into a new document; retain failures for inspection.

    Optional expectations apply to root solids only. A restored user document
    loses the benchmark disposal marker; only explicit test restores get one.
    """
    path=Path(archive).expanduser().resolve()
    if path.suffix.lower() not in ('.f3d','.step','.stp') or not path.is_file():
        raise ValueError('Import requires an existing local F3D or STEP file.')
    if not document:raise ValueError('Choose a unique restored document name.')
    expected=expected or {}
    if set(expected)-{'body_count','volume_mm3','size_mm','parameter_expressions'}:
        raise ValueError('Unsupported recovery expectation.')
    geometry_expectations({k:v for k,v in expected.items() if k!='parameter_expressions'})
    expressions=expected.get('parameter_expressions',{})
    if not isinstance(expressions,dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in expressions.items()):raise ValueError('Parameter expectations map names to expression strings.')
    config={'archive':str(path),'format':path.suffix.lower(),'document':document,'expected':expected,'owner':disposable_owner}
    return '''import adsk.core,adsk.fusion,json,time
C=json.loads(CONFIG_JSON)
def run(_context: str):
 start=time.perf_counter();app=adsk.core.Application.get()
 if any(doc.name==C['document'] for doc in app.documents):raise RuntimeError('Restore document name already exists.')
 options=app.importManager.createFusionArchiveImportOptions(C['archive']) if C['format']=='.f3d' else app.importManager.createSTEPImportOptions(C['archive'])
 if options is None:raise RuntimeError('Archive import options unavailable.')
 options.isViewFit=False
 doc=app.importManager.importToNewDocument(options)
 if doc is None:raise RuntimeError('Archive import did not produce a document; inspect live state.')
 doc.name=C['document'];doc.activate()
 design=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
 if design is None:raise RuntimeError('Restored document has no CAD design.')
 root=design.rootComponent
 marker=root.attributes.itemByName('fusion-360-mcp','acceptance_owner')
 if marker is not None:marker.deleteMe()
 if C['owner']:root.attributes.add('fusion-360-mcp','acceptance_owner',C['owner'])
 if not design.computeAll():raise RuntimeError('Restored design failed recompute.')
 bodies=list(root.bRepBodies)
 if any(not body.isSolid for body in bodies):raise RuntimeError('Restored root contains a non-solid body.')
 issues=[{'component':comp.name,'feature':f.name,'message':f.errorOrWarningMessage} for comp in design.allComponents for f in comp.features if f.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
 if issues:raise RuntimeError('Restored design contains unhealthy features: '+json.dumps(issues))
 volume=sum(body.volume*1000 for body in bodies);size=None
 if bodies:
  lower=[min(getattr(b.boundingBox.minPoint,k) for b in bodies)*10 for k in ('x','y','z')]
  upper=[max(getattr(b.boundingBox.maxPoint,k) for b in bodies)*10 for k in ('x','y','z')]
  size=[hi-lo for lo,hi in zip(lower,upper)]
 parameters={p.name:p.expression for p in design.userParameters}
 e=C['expected']
 if 'body_count' in e and len(bodies)!=e['body_count']:raise RuntimeError('Restored body count differs.')
 if 'volume_mm3' in e and abs(volume-e['volume_mm3'])>max(0.03,abs(e['volume_mm3'])*1e-6):raise RuntimeError('Restored volume differs.')
 if 'size_mm' in e and (size is None or len(e['size_mm'])!=3 or any(abs(a-b)>1e-4 for a,b in zip(size,e['size_mm']))):raise RuntimeError('Restored dimensions differ.')
 if any(parameters.get(k)!=v for k,v in e.get('parameter_expressions',{}).items()):raise RuntimeError('Restored parameter expressions differ.')
 print(json.dumps({'ok':True,'document':doc.name,'archive':C['archive'],'root_body_count':len(bodies),'root_volume_mm3':volume,'root_size_mm':size,'parameter_expressions':parameters,'feature_issues':issues,'cloud_saved':False,'fusion_execution_verification_seconds':time.perf_counter()-start}))
'''.replace('CONFIG_JSON',repr(json.dumps(config)))


def main():
    import argparse,time
    from mcp_client import FusionClient
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log-dir',required=True)
    commands=parser.add_subparsers(dest='command',required=True)
    snapshot=commands.add_parser('snapshot')
    snapshot.add_argument('--directory',required=True)
    snapshot.add_argument('--document')
    restore=commands.add_parser('restore')
    restore.add_argument('--archive',required=True,help='Local F3D or STEP file; STEP does not preserve native feature history.')
    restore.add_argument('--document',required=True)
    restore.add_argument('--expectations',help='JSON file with root-solid recovery expectations.')
    args=parser.parse_args()
    if args.command=='snapshot':script=checkpoint_script(args.directory,args.document)
    else:
        expected=json.loads(Path(args.expectations).read_text(encoding='utf-8')) if args.expectations else None
        script=restore_script(args.archive,args.document,expected)
    begin=time.perf_counter();client=FusionClient(args.log_dir);result=client.execute(script)
    print(json.dumps({'result':result,'mcp_round_trip_seconds':client.last_rpc_seconds,'runner_seconds':time.perf_counter()-begin,'scope':'Excludes assistant thinking and response writing.'},indent=2))

if __name__=='__main__':main()
