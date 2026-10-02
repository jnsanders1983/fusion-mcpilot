"""Live isolated feature regression suite with per-case recovery checkpoints."""
import argparse
import json
from pathlib import Path
import random
import time
import uuid
from feature_recipes import RECIPES,build_script
from mcp_client import FusionClient
from recovery import checkpoint_script

def close_owned_script(document,owner,original):
    config={'document':document,'owner':owner,'original':original}
    return '''import adsk.core,adsk.fusion,json
C=json.loads(CONFIG_JSON)
def run(_context: str):
 app=adsk.core.Application.get();docs=[d for d in app.documents if d.name==C['document']]
 if len(docs)!=1:raise RuntimeError('Disposable document missing or ambiguous.')
 doc=docs[0];design=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
 marker=design.rootComponent.attributes.itemByName('fusion-360-mcp','acceptance_owner') if design else None
 if marker is None or marker.value!=C['owner']:raise RuntimeError('Refusing to close a document not owned by this test.')
 if not doc.close(False):raise RuntimeError('Disposable document did not close.')
 originals=[d for d in app.documents if d.name==C['original']]
 if len(originals)==1:originals[0].activate()
 print(json.dumps({'closed_disposable':C['document'],'original_restored':len(originals)==1}))
'''.replace('CONFIG_JSON',repr(json.dumps(config)))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log-dir',required=True)
    parser.add_argument('--iterations',type=int,default=3)
    parser.add_argument('--seed',type=int,default=20261001)
    parser.add_argument('--recipes',nargs='+',choices=list(RECIPES),default=list(RECIPES))
    parser.add_argument('--initial-checkpoint',action='store_true')
    args=parser.parse_args()
    if not 1<=args.iterations<=30:parser.error('Use 1–30 iterations.')
    folder=Path(args.log_dir);folder.mkdir(parents=True,exist_ok=True)
    client=FusionClient(folder);rng=random.Random(args.seed);owner=uuid.uuid4().hex
    probe=client.execute("import adsk.core,json\ndef run(_context: str):\n app=adsk.core.Application.get()\n print(json.dumps({'document':app.activeDocument.name if app.activeDocument else None,'fusion_version':app.version}))",True)
    original=probe['document']
    if args.initial_checkpoint:client.execute(checkpoint_script(folder/'checkpoints'/('start-'+owner)))
    for recipe in args.recipes:
        for iteration in range(args.iterations):
            stage=recipe+'-'+owner[:8]+'-'+str(iteration)
            document='Skill acceptance '+stage
            parameters={**RECIPES[recipe]}
            # Perturb dimensions independently; fixed fractional controls keep
            # the fixture valid without caching any CAD result.
            for name,limits in {'width':(48,85),'length':(40,70),'height':(8,25)}.items():
                if name in parameters:parameters[name]=rng.randint(*limits)
            if recipe=='revolved_tube':parameters.update(inner_radius=rng.randint(5,9),outer_radius=rng.randint(12,20))
            if recipe=='circular_hole_flange':parameters.update(count=rng.randint(4,10),outer_radius=rng.randint(24,36),pattern_radius=rng.randint(13,18))
            record={'stage':stage,'recipe':recipe,'iteration':iteration,'seed':args.seed,'parameters':parameters,'document':document,'fusion_version':probe['fusion_version']}
            begin=time.perf_counter()
            try:
                result=client.execute(build_script(recipe,parameters,document,owner,disposable=True))
                record.update(outcome='verified',result=result,mcp_execution_seconds=client.last_rpc_seconds)
                recovery=client.execute(checkpoint_script(folder/'checkpoints'/stage,document))
                record['checkpoint']=recovery
                record['cleanup']=client.execute(close_owned_script(document,owner,original))
            except Exception as error:
                record.update(outcome='failed_or_unconfirmed',error=str(error))
                record['case_total_seconds']=time.perf_counter()-begin
                with (folder/'acceptance.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(record)+'\n')
                print(json.dumps({'stage':stage,'outcome':record['outcome'],'error':str(error)}),flush=True)
                # Do not retry or discard a partially built model. An agent
                # must inspect it before choosing recovery and another case.
                raise
            record['case_total_seconds']=time.perf_counter()-begin
            with (folder/'acceptance.jsonl').open('a',encoding='utf-8') as stream:stream.write(json.dumps(record)+'\n')
            print(json.dumps({'stage':stage,'outcome':'verified','mcp_seconds':record['mcp_execution_seconds'],'case_total_seconds':record['case_total_seconds']}),flush=True)

if __name__=='__main__':main()
