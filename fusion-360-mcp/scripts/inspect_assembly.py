"""Read-only occurrence-expanded inventory, with explicit world-space semantics."""
import argparse,json,time
from pathlib import Path
from mcp_client import FusionClient

def build_inspection(document=None):
    return RECIPE.replace('CONFIG_JSON',repr(json.dumps({'document':document})))

RECIPE='''import adsk.core,adsk.fusion,json,time,itertools
C=json.loads(CONFIG_JSON)
def run(_context: str):
 start=time.perf_counter();app=adsk.core.Application.get();doc=app.activeDocument
 if doc is None or (C['document'] and doc.name!=C['document']):raise RuntimeError('Inspection document changed or missing.')
 d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
 if d is None:raise RuntimeError('Document has no CAD Design product.')
 root=d.rootComponent;instances=[];issues=[];occurrences=[]
 def xyz(p):return [getattr(p,k)*10 for k in ('x','y','z')]
 def transform(point,matrices):
  out=point.copy()
  for matrix in reversed(matrices):
   if not out.transformBy(matrix):raise RuntimeError('Point transform rejected.')
  return out
 def bodies(component,path,matrices,visible):
  for body in component.bRepBodies:
   box=body.boundingBox
   corners=[transform(adsk.core.Point3D.create(x,y,z),matrices) for x,y,z in itertools.product((box.minPoint.x,box.maxPoint.x),(box.minPoint.y,box.maxPoint.y),(box.minPoint.z,box.maxPoint.z))]
   bounds=[min(getattr(p,k) for p in corners)*10 for k in ('x','y','z')]+[max(getattr(p,k) for p in corners)*10 for k in ('x','y','z')]
   center=transform(body.physicalProperties.centerOfMass,matrices)
   instances.append({'occurrence_path':path,'component':component.name,'body':body.name,'body_token':body.entityToken,'solid':body.isSolid,'visible':visible and body.isVisible,'volume_mm3':body.volume*1000,'center_of_mass_world_mm':xyz(center),'conservative_world_bounds_mm':bounds})
  for feature in component.features:
   if feature.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:issues.append({'occurrence_path':path,'feature':feature.name,'message':feature.errorOrWarningMessage})
 def walk(component,path,matrices,visible,depth):
  if depth>64 or len(occurrences)>10000:raise RuntimeError('Assembly exceeds bounded inspection limits.')
  bodies(component,path,matrices,visible)
  for occurrence in component.occurrences:
   child_path=path+'+'+occurrence.name if path else occurrence.name
   occurrences.append({'path':child_path,'component':occurrence.component.name,'visible':visible and occurrence.isVisible,'grounded':occurrence.isGrounded if depth==0 else None,'grounded_scope':'Root occurrences only; nested grounding unavailable through this property.','local_transform_cm':occurrence.transform2.asArray()})
   walk(occurrence.component,child_path,matrices+[occurrence.transform2],visible and occurrence.isVisible,depth+1)
 walk(root,'',[],True,0)
 print(json.dumps({'document':doc.name,'fusion_version':app.version,'occurrences':occurrences,'body_instances':instances,'instance_count':len(instances),'occurrence_count':len(occurrences),'instance_volume_sum_mm3':sum(row['volume_mm3'] for row in instances),'feature_issues':issues,'scope':'Occurrence instances expanded; centers in root/world mm; transformed local-box envelopes are conservative, not exact curved-body bounds; overlapping volumes are summed, not unioned.','fusion_execution_verification_seconds':time.perf_counter()-start}))
'''

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target-document');p.add_argument('--log-dir',required=True)
    a=p.parse_args();start=time.perf_counter();c=FusionClient(Path(a.log_dir));result=c.execute(build_inspection(a.target_document),True)
    print(json.dumps({'result':result,'mcp_round_trip_seconds':c.last_rpc_seconds,'runner_seconds':time.perf_counter()-start},indent=2))

if __name__=='__main__':main()
