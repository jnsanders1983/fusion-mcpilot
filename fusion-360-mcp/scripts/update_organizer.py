"""Edit native dock parameters once; validate live inputs and regenerated geometry."""
import argparse,json,time
from pathlib import Path
from mcp_client import FusionClient
from parametric_organizer import variants_script,DEFAULTS

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target-document',required=True)
    p.add_argument('--set',action='append',required=True,metavar='NAME=MM')
    p.add_argument('--log-dir',required=True)
    a=p.parse_args();changes={}
    for assignment in a.set:
        name,value=assignment.split('=',1)
        if name not in DEFAULTS:raise ValueError('Edit a primary control, not a derived parameter: '+name)
        changes[name]=float(value)
    begin=time.perf_counter();c=FusionClient(Path(a.log_dir))
    result=c.execute(variants_script(a.target_document,[changes]))
    print(json.dumps({'result':result,'mcp_round_trip_seconds':c.last_rpc_seconds,
                     'runner_seconds':time.perf_counter()-begin,'scope':'Excludes assistant thinking and response writing.'},indent=2))
    if result.get('ok') is False:raise SystemExit(1)

if __name__=='__main__':main()
