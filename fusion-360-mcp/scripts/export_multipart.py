"""Export explicit live Fusion body instances as common-frame STL and core 3MF."""
import argparse,json,time
from pathlib import Path
from safe_data import strict_json
from mcp_client import FusionClient
from multipart_print import capture_script,export_bundle
from measure_geometry import build_script

def export(client,document,regions,directory,backend=None):
    if backend!='custom':raise ValueError('This legacy writer requires explicit backend="custom". Prefer Fusion native export; consult the multi-material reference.')
    if not isinstance(regions,list) or not 2<=len(regions)<=32:raise ValueError('Choose 2–32 regions.')
    selectors=[r['selector'] for r in regions]
    script=capture_script(document,selectors)
    target=Path(directory)
    if target.exists():raise ValueError('Choose a new output directory; existing outputs are preserved.')
    start=time.perf_counter()
    interference=client.execute(build_script(document,selectors,'interference'),True)
    interference_mcp=client.last_rpc_seconds
    if interference['interference_count']:raise RuntimeError('Selected regions overlap; resolve ownership of shared volume before material export.')
    data=client.execute(script,True);capture_mcp=client.last_rpc_seconds
    for part,region in zip(data['parts'],regions):part['material']=region['material']
    result=export_bundle(data,target)
    result.update(document=document,interference=interference,export_execution_verification_seconds=time.perf_counter()-start,
                  fusion_execution_verification_seconds=interference['fusion_execution_verification_seconds']+data['fusion_execution_verification_seconds'],
                  aggregate_mcp_round_trip_seconds=interference_mcp+capture_mcp)
    (target/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    client.log('multipart_export',result=result)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--document',required=True);parser.add_argument('--regions',required=True)
    parser.add_argument('--directory',required=True);parser.add_argument('--log-dir',required=True)
    parser.add_argument('--backend',required=True,choices=['custom'],help='Explicit opt-in to the legacy custom writer; use native Fusion exporters when suitable.')
    args=parser.parse_args();regions=strict_json(Path(args.regions).read_text(encoding='utf-8'))
    print(json.dumps(export(FusionClient(args.log_dir),args.document,regions,args.directory,args.backend),indent=2))

if __name__=='__main__':main()
