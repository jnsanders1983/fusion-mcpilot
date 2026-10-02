"""Scoped native minimum-distance and interference queries for live bodies."""
import json
from entity_selection import SOURCE

def build_script(document,selectors,operation='distance'):
    if operation not in ('distance','interference'):raise ValueError('Unsupported measurement operation.')
    if not document or not 2<=len(selectors)<=50 or (operation=='distance' and len(selectors)!=2):raise ValueError('Distance requires two bodies; interference supports 2–50.')
    for selector in selectors:
        if not isinstance(selector,dict) or not set(selector)<= {'name','entity_token','occurrence_path'} or not (selector.get('name') or selector.get('entity_token')) or any(not isinstance(v,str) for v in selector.values()):raise ValueError('Explicit live body selectors require string values.')
    config={'document':document,'selectors':selectors,'operation':operation}
    return 'import adsk.core,adsk.fusion,json,time\n'+SOURCE+'\n'+TEMPLATE.replace('CONFIG_JSON',repr(json.dumps(config)))

TEMPLATE='''C=json.loads(CONFIG_JSON)
def run(_context: str):
 start=time.perf_counter();app=adsk.core.Application.get();doc=app.activeDocument
 if doc is None or doc.name!=C['document']:raise RuntimeError('Measurement target changed.')
 design=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
 if design is None:raise RuntimeError('No CAD Design product.')
 bodies=[resolve_body(design,s) for s in C['selectors']]
 for i,body in enumerate(bodies):
  if any(body==earlier for earlier in bodies[:i]):raise RuntimeError('Select distinct body instances.')
 if C['operation']=='distance':
  measurement=app.measureManager.measureMinimumDistance(*bodies)
  if measurement is None:raise RuntimeError('Minimum-distance query returned no result.')
  result={'distance_mm':measurement.value*10,'positions_world_mm':[[getattr(p,k)*10 for k in ('x','y','z')] for p in (measurement.positionOne,measurement.positionTwo)],'scope':'Minimum separation; zero alone does not prove volumetric interference.'}
 else:
  entities=adsk.core.ObjectCollection.create()
  for body in bodies:entities.add(body)
  ip=design.createInterferenceInput(entities);ip.areCoincidentFacesIncluded=False
  interference=design.analyzeInterference(ip)
  if interference is None:raise RuntimeError('Interference query returned no result.')
  result={'interference_count':interference.count,'pairs':[{'entity_one':interference.item(i).entityOne.name,'entity_two':interference.item(i).entityTwo.name} for i in range(interference.count)],'scope':'Native interference pairs; no persistent interference geometry or solver stress results generated.'}
 result.update(ok=True,document=doc.name,fusion_execution_verification_seconds=time.perf_counter()-start)
 print(json.dumps(result))
'''


def main():
    import argparse,time
    from pathlib import Path
    from mcp_client import FusionClient
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--document',required=True)
    p.add_argument('--selectors',required=True,help='JSON file containing two or more body selectors.')
    p.add_argument('--operation',choices=('distance','interference'),default='distance')
    p.add_argument('--log-dir',required=True)
    args=p.parse_args();selectors=json.loads(Path(args.selectors).read_text(encoding='utf-8'))
    script=build_script(args.document,selectors,args.operation)
    begin=time.perf_counter();client=FusionClient(args.log_dir);result=client.execute(script,True)
    print(json.dumps({'result':result,'mcp_round_trip_seconds':client.last_rpc_seconds,'runner_seconds':time.perf_counter()-begin,'scope':'Excludes assistant thinking and response writing.'},indent=2))

if __name__=='__main__':main()
