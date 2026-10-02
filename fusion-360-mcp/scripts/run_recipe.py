"""Execute a reviewed Fusion Python recipe once through the configured MCP."""
import argparse,json,time
from pathlib import Path
from mcp_client import FusionClient

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('recipe')
    p.add_argument('--log-dir',required=True)
    p.add_argument('--read-only',action='store_true')
    p.add_argument('--result',help='Optional JSON result path in the working directory.')
    a=p.parse_args()
    start=time.perf_counter()
    script=Path(a.recipe).read_text(encoding='utf-8')
    c=FusionClient(Path(a.log_dir))
    result=c.execute(script,a.read_only)
    output={'result':result,'mcp_round_trip_seconds':c.last_rpc_seconds,
            'connection_setup_seconds':c.setup_seconds,'runner_seconds':time.perf_counter()-start}
    if a.result:Path(a.result).write_text(json.dumps(output,indent=2),encoding='utf-8')
    print(json.dumps(output,indent=2))

if __name__=='__main__':main()
