"""Check native document access and script readiness without model edits."""
import argparse,json,time,uuid
from mcp_client import FusionClient


def probe(client):
    result={'native_documents_readable':False,'script_ready':False}
    try:
        response=client.rpc('tools/call',{'name':'fusion_mcp_read','arguments':{'queryType':'document','operation':'open'}})['result']
        if response.get('isError'):raise RuntimeError('Native document read failed.')
        native=json.loads(next(item['text'] for item in response['content'] if item.get('type')=='text'))
        if native.get('success') is not True:raise RuntimeError('Native document read returned no success.')
        result.update(native_documents_readable=True,documents=native.get('results',[]))
    except Exception as error:
        result['native_error']=str(error);return result
    nonce=uuid.uuid4().hex
    script='import adsk.core,json\ndef run(_context: str):\n app=adsk.core.Application.get()\n print(json.dumps({"probe":'+repr(nonce)+',"fusion_version":app.version,"document":app.activeDocument.name if app.activeDocument else None}))\n'
    try:
        response=client.execute(script,True)
        if response.get('probe')!=nonce:raise RuntimeError('Script readiness nonce mismatch.')
        result.update(script_ready=True,script_result=response,script_mcp_seconds=client.last_rpc_seconds)
    except Exception as error:
        result.update(script_error=str(error),script_mcp_seconds=client.last_rpc_seconds)
    result['scope']='Native reads and a fresh read-only script; HTTP availability alone does not prove script readiness. No cancellation or automatic retry.'
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--log-dir',required=True)
    args=parser.parse_args();begin=time.perf_counter();client=FusionClient(args.log_dir)
    result=probe(client);result['runner_seconds']=time.perf_counter()-begin
    client.log('readiness_probe',result=result)
    print(json.dumps(result,indent=2))
    if not result['script_ready']:raise SystemExit(1)

if __name__=='__main__':main()
