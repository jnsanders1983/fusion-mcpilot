"""Inspect or edit existing numeric user parameters with verified rollback."""
import argparse,json,time
from pathlib import Path
from mcp_client import FusionClient
from contracts import geometry_expectations


def build_script(document,changes=None,expected=None):
    if not isinstance(document,str) or not document:raise ValueError('Explicit document required.')
    changes={} if changes is None else changes
    if not isinstance(changes,dict) or any(not isinstance(k,str) or not k or not isinstance(v,str) or not v.strip() or len(v)>2048 or '\x00' in v for k,v in changes.items()):
        raise ValueError('Changes must map parameter names to Fusion expression strings.')
    expected=geometry_expectations({} if expected is None else expected,'root_')
    return TEMPLATE.replace('CONFIG_JSON',repr(json.dumps({'document':document,'changes':changes,'expected':expected})))


TEMPLATE='''import adsk.core,adsk.fusion,json,time,math
C=json.loads(CONFIG_JSON)
def run(_context: str):
 start=time.perf_counter();app=adsk.core.Application.get()
 docs=[doc for doc in app.documents if doc.name==C['document']]
 if len(docs)!=1:raise RuntimeError('Parameter target missing or ambiguous.')
 doc=docs[0];d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
 if d is None:raise RuntimeError('Parameter target has no CAD Design.')
 def inventory():
  return [{'name':p.name,'expression':p.expression,'unit':p.unit,'value_database_units':p.value,'comment':p.comment} for p in d.userParameters]
 def geometry():
  return sorted([{'component':comp.name,'body':body.name,'solid':body.isSolid,'volume_mm3':body.volume*1000,'bounds_mm':[getattr(p,k)*10 for p in (body.boundingBox.minPoint,body.boundingBox.maxPoint) for k in ('x','y','z')]} for comp in d.allComponents for body in comp.bRepBodies],key=lambda row:(row['component'],row['body'],row['volume_mm3']))
 def healthy():
  issues=[{'component':comp.name,'feature':f.name,'message':f.errorOrWarningMessage} for comp in d.allComponents for f in comp.features if f.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
  if issues:raise RuntimeError('Unhealthy features: '+json.dumps(issues))
 def root_metrics():
  bodies=list(d.rootComponent.bRepBodies);size=None
  if bodies:size=[(max(getattr(b.boundingBox.maxPoint,k) for b in bodies)-min(getattr(b.boundingBox.minPoint,k) for b in bodies))*10 for k in ('x','y','z')]
  return {'root_body_count':len(bodies),'root_size_mm':size,'root_volume_mm3':sum(b.volume*1000 for b in bodies)}
 before=inventory()
 if not C['changes']:
  print(json.dumps({'ok':True,'document':doc.name,'parameters':before,'scope':'Numeric user parameters; values use Fusion database units, expressions retain explicit units.','fusion_execution_verification_seconds':time.perf_counter()-start}));return
 healthy();baseline=geometry();prior={row['name']:row['expression'] for row in before}
 for name,expression in C['changes'].items():
  parameter=d.userParameters.itemByName(name)
  if parameter is None:raise RuntimeError('Unknown user parameter: '+name)
  if not d.unitsManager.isValidExpression(expression,parameter.unit):raise RuntimeError('Expression/unit mismatch: '+name)
  if not math.isfinite(d.unitsManager.evaluateExpression(expression,parameter.unit)):raise RuntimeError('Nonfinite parameter expression: '+name)
 changed=[]
 try:
  for name,expression in C['changes'].items():
   changed.append(name);d.userParameters.itemByName(name).expression=expression
  if not d.computeAll():raise RuntimeError('Edited design failed recompute.')
  healthy();metrics=root_metrics();e=C['expected']
  if 'root_body_count' in e and metrics['root_body_count']!=e['root_body_count']:raise RuntimeError('Unexpected root body count.')
  if 'root_size_mm' in e and (metrics['root_size_mm'] is None or len(e['root_size_mm'])!=3 or any(abs(a-b)>1e-4 for a,b in zip(metrics['root_size_mm'],e['root_size_mm']))):raise RuntimeError('Unexpected root dimensions.')
  if 'root_volume_mm3' in e and abs(metrics['root_volume_mm3']-e['root_volume_mm3'])>max(0.03,abs(e['root_volume_mm3'])*1e-6):raise RuntimeError('Unexpected root volume.')
  result={'ok':True,'document':doc.name,'changed_parameters':changed,'parameters':inventory(),'metrics':metrics,'feature_health_verified':True}
 except Exception as error:
  rollback_errors=[]
  for name in reversed(changed):
   try:d.userParameters.itemByName(name).expression=prior[name]
   except Exception as restore_error:rollback_errors.append(str(restore_error))
  try:
   if not d.computeAll():raise RuntimeError('Rollback recompute failed.')
   healthy();restored=geometry()
   if any(d.userParameters.itemByName(name).expression!=prior[name] for name in changed):raise RuntimeError('Rollback expressions differ.')
   if len(restored)!=len(baseline):raise RuntimeError('Rollback body count differs.')
   for a,b in zip(baseline,restored):
    if any(a[k]!=b[k] for k in ('component','body','solid')) or abs(a['volume_mm3']-b['volume_mm3'])>max(0.03,abs(a['volume_mm3'])*1e-6) or any(abs(x-y)>1e-4 for x,y in zip(a['bounds_mm'],b['bounds_mm'])):raise RuntimeError('Rollback geometry differs.')
  except Exception as verification_error:rollback_errors.append(str(verification_error))
  result={'ok':False,'document':doc.name,'error':str(error),'rollback_verified':not rollback_errors,'rollback_errors':rollback_errors,'scope':'Restoration checks expressions, feature health, body count, solidity, bounds and volumes; not full topology equivalence.'}
 result['cloud_saved']=False;result['fusion_execution_verification_seconds']=time.perf_counter()-start
 print(json.dumps(result))
'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--document',required=True)
    parser.add_argument('--set',action='append',default=[],metavar='NAME=EXPRESSION')
    parser.add_argument('--expectations',help='Optional JSON file with root geometry acceptance checks.')
    parser.add_argument('--log-dir',required=True)
    args=parser.parse_args();changes=dict(item.split('=',1) for item in args.set)
    expected=json.loads(Path(args.expectations).read_text(encoding='utf-8')) if args.expectations else None
    script=build_script(args.document,changes,expected)
    begin=time.perf_counter();client=FusionClient(args.log_dir);result=client.execute(script,read_only=not changes)
    print(json.dumps({'result':result,'mcp_round_trip_seconds':client.last_rpc_seconds,'runner_seconds':time.perf_counter()-begin,'scope':'Excludes assistant thinking and response writing.'},indent=2))
    if result.get('ok') is False:raise SystemExit(1)

if __name__=='__main__':main()
