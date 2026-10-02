"""Read-only live recovery inventory. No cached geometry and no mutation replay."""
import argparse
import ast
import json
from pathlib import Path
import time
from mcp_client import FusionClient

RECIPE = '''import adsk.core, adsk.fusion, json, time
EXPECT_DOCUMENT = None
def run(_context: str):
    start = time.perf_counter()
    app = adsk.core.Application.get()
    doc = app.activeDocument
    if doc is None:
        raise RuntimeError('No active document.')
    if EXPECT_DOCUMENT and doc.name != EXPECT_DOCUMENT:
        raise RuntimeError('Active document changed; inspection stopped.')
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design is None:
        raise RuntimeError('Active product is not a Fusion CAD design.')
    components = [design.rootComponent] + list(design.allComponents)
    seen = set()
    bodies, issues = [], []
    for component in components:
        token = component.entityToken
        if token in seen:
            continue
        seen.add(token)
        for body in component.bRepBodies:
            box = body.boundingBox
            marker = body.attributes.itemByName('fusion-360-mcp', 'primitive')
            bodies.append({'component':component.name, 'body':body.name,
                'entity_token':body.entityToken, 'solid':body.isSolid,
                'volume_mm3':body.volume * 1000,
                'bounds_mm':[v*10 for v in [box.minPoint.x,box.minPoint.y,box.minPoint.z,
                    box.maxPoint.x,box.maxPoint.y,box.maxPoint.z]],
                'skill_primitive':marker.value if marker else None})
        for feature in component.features:
            if feature.healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
                issues.append({'component':component.name,'feature':feature.name,
                    'message':feature.errorOrWarningMessage})
    print(json.dumps({'document':doc.name,'modified':doc.isModified,'fusion_version':app.version,
        'bodies':bodies,'feature_issues':issues,'saved':False,
        'scope':'component definitions; bounds in component coordinates; instances not expanded',
        'fusion_execution_verification_seconds':round(time.perf_counter()-start,4)}))
'''

def build_inspection(target_document=None):
    tree = ast.parse(RECIPE)
    for node in tree.body:
        if isinstance(node, ast.Assign) and node.targets[0].id == 'EXPECT_DOCUMENT':
            node.value = ast.Constant(target_document)
    return ast.unparse(ast.fix_missing_locations(tree))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target-document')
    import uuid
    parser.add_argument('--log-dir', default=str(Path('work/fusion-runs') / ('run-' + uuid.uuid4().hex[:12])))
    args = parser.parse_args()
    start = time.perf_counter()
    client = FusionClient(Path(args.log_dir))
    value = client.execute(build_inspection(args.target_document), read_only=True)
    value['timing'] = {'mcp_round_trip_seconds':client.last_rpc_seconds,
        'connection_setup_seconds':client.setup_seconds,
        'runner_total_seconds':time.perf_counter()-start}
    print(json.dumps(value, indent=2))

if __name__ == '__main__':
    main()
