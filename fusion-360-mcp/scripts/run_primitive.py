"""Run a packaged primitive with numeric arguments; report and log all timings."""
import argparse
import ast
import csv
import datetime
import json
import math
from pathlib import Path
import sys
import time
import uuid
from mcp_client import FusionClient


def build_script(shape, dimensions, replace_body=None, target_document=None, fit_view=True):
    keys = {'sphere': {'radius'}, 'torus': {'major_radius','tube_radius'},
            'frustum': {'base_radius','top_radius','height'}}
    if shape not in keys or set(dimensions) != keys[shape]:
        raise ValueError('Shape dimensions do not match the recipe.')
    if not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in dimensions.values()):
        raise ValueError('Dimensions must be finite numbers.')
    if shape == 'sphere' and dimensions['radius'] <= 0:
        raise ValueError('Radius must be positive.')
    if shape == 'torus' and not dimensions['major_radius'] > dimensions['tube_radius'] > 0:
        raise ValueError('Major radius must exceed the positive tube radius.')
    if shape == 'frustum' and not (dimensions['base_radius'] > 0 and dimensions['top_radius'] >= 0 and dimensions['height'] > 0):
        raise ValueError('Base radius and height must be positive; top radius cannot be negative.')
    tree = ast.parse(Path(__file__).with_name('primitives.py').read_text(encoding='utf-8'))
    values = {'SHAPE': shape, 'DIMENSIONS_MM': dimensions, 'REPLACE_BODY': replace_body,
              'EXPECT_DOCUMENT_NAME': target_document, 'FIT_VIEW': fit_view}
    replaced = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            key = node.targets[0].id
            if key in values:
                node.value = ast.parse(repr(values[key]), mode='eval').body
                replaced.add(key)
    if replaced != set(values):
        raise RuntimeError('Primitive template/configuration mismatch.')
    return ast.unparse(tree)


def main():
    started = time.perf_counter()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shape', choices=['sphere', 'torus', 'frustum'], required=True)
    for name in ('radius', 'major-radius', 'tube-radius', 'base-radius', 'top-radius', 'height'):
        parser.add_argument('--'+name+'-mm', type=float)
    parser.add_argument('--replace-body')
    parser.add_argument('--target-document')
    parser.add_argument('--no-fit', action='store_true', help='For benchmarks or an explicit request to preserve the view')
    parser.add_argument('--log-dir', default=str(Path('work/fusion-runs') / ('run-' + uuid.uuid4().hex[:12])))
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    required = {'sphere': ('radius',), 'torus': ('major_radius', 'tube_radius'),
                'frustum': ('base_radius', 'top_radius', 'height')}[args.shape]
    dimensions = {}
    for key in required:
        value = getattr(args, key+'_mm')
        if value is None:
            parser.error('--'+key.replace('_','-')+'-mm is required for '+args.shape)
        dimensions[key] = value
    for key in ('radius', 'major_radius', 'tube_radius', 'base_radius', 'top_radius', 'height'):
        if key not in required and getattr(args,key+'_mm') is not None:
            parser.error('Unexpected dimension for '+args.shape+': '+key)
    script = build_script(args.shape, dimensions, args.replace_body, args.target_document, not args.no_fit)
    if args.dry_run:
        print(script)
        return
    client = FusionClient(args.log_dir)
    result = client.execute(script)
    rpc_seconds = client.last_rpc_seconds
    total = time.perf_counter() - started
    timing = {'mcp_execution_verification_seconds': round(rpc_seconds,4),
              'fusion_execution_verification_seconds': result['fusion_execution_verification_seconds'],
              'connection_setup_seconds': round(client.setup_seconds,4),
              'runner_total_seconds': round(total,4)}
    output = {'result': result, 'timing': timing,
              'scope': 'Runner total includes local preparation and connection setup; excludes assistant thinking and response writing.'}
    client.log('primitive_completed', **output)
    path = Path(args.log_dir)/'performance.csv'
    fields = ['timestamp_utc','shape','dimensions_mm','verified'] + list(timing)
    with path.open('a',newline='',encoding='utf-8') as stream:
        writer = csv.DictWriter(stream,fieldnames=fields)
        if stream.tell() == 0:
            writer.writeheader()
        writer.writerow({'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        'shape':args.shape,'dimensions_mm':json.dumps(dimensions),'verified':True,**timing})
    print(json.dumps(output))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps({'success':False,'error':str(error),'retry':'Inspect live state before retrying; no automatic replay.'}),file=sys.stderr)
        raise SystemExit(1)
