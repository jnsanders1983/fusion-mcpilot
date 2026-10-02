"""Create a verified metric native feature recipe in a new document."""
import argparse,json,time,uuid
from pathlib import Path
from feature_recipes import RECIPES,build_script
from mcp_client import FusionClient

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--recipe',choices=list(RECIPES),required=True)
    p.add_argument('--document',required=True)
    p.add_argument('--set',action='append',default=[],metavar='NAME=VALUE')
    p.add_argument('--log-dir',default=str(Path('work/fusion-runs')/('run-'+uuid.uuid4().hex[:12])))
    a=p.parse_args();parameters={}
    for assignment in a.set:
        name,raw=assignment.split('=',1)
        parameters[name]=int(raw) if name in ('columns','rows','count') else float(raw)
    script=build_script(a.recipe,parameters,a.document,uuid.uuid4().hex)
    begin=time.perf_counter();c=FusionClient(a.log_dir);result=c.execute(script)
    print(json.dumps({'result':result,'mcp_round_trip_seconds':c.last_rpc_seconds,'connection_setup_seconds':c.setup_seconds,'runner_seconds':time.perf_counter()-begin,'scope':'Excludes assistant thinking and response writing.'},indent=2))

if __name__=='__main__':main()
