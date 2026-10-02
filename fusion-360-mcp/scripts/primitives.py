import adsk.core
import adsk.fusion
import json
import math
import time
SHAPE = 'sphere'
DIMENSIONS_MM = {'radius': 25}
REPLACE_BODY = None
EXPECT_DOCUMENT_NAME = None
FIT_VIEW = True

def run(_context: str):
    execution_start = time.perf_counter()
    app = adsk.core.Application.get()
    if EXPECT_DOCUMENT_NAME and app.activeDocument.name != EXPECT_DOCUMENT_NAME:
        raise RuntimeError('Active document changed; no changes made.')
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design is None:
        raise RuntimeError('The active product is not a Fusion CAD design.')
    root = design.rootComponent
    matches = [body for body in root.bRepBodies if body.name == REPLACE_BODY] if REPLACE_BODY else []
    if len(matches) > 1:
        raise RuntimeError('Replacement name is ambiguous; no changes made.')
    old_body = matches[0] if matches else None
    replacing = old_body is not None
    if REPLACE_BODY and old_body is None:
        raise RuntimeError('Requested replacement body not found; no changes made.')
    if old_body and old_body.attributes.itemByName('fusion-360-mcp', 'primitive') is None and (REPLACE_BODY not in ('Sphere 50 mm', 'Random torus')):
        raise RuntimeError('Replacement target is not a known skill primitive; no changes made.')
    old_feature = None
    if old_body:
        for item in root.features.revolveFeatures:
            if item.bodies.count == 1 and item.bodies.item(0) == old_body:
                old_feature = item
                break
        if old_feature is None:
            raise RuntimeError('Cannot safely identify the prior primitive feature; no changes made.')
    values = {k: float(v) for k, v in DIMENSIONS_MM.items()}
    if not all((math.isfinite(v) for v in values.values())):
        raise ValueError('Dimensions must be finite.')
    if SHAPE == 'sphere':
        if not (set(values) == {'radius'} and values['radius'] > 0):
            raise RuntimeError("Primitive verification failed: set(values) == {'radius'} and values['radius'] > 0")
    elif SHAPE == 'torus':
        if not (set(values) == {'major_radius', 'tube_radius'} and values['major_radius'] > values['tube_radius'] > 0):
            raise RuntimeError("Primitive verification failed: set(values) == {'major_radius', 'tube_radius'} and values['major_radius'] > values['tube_radius'] > 0")
    elif SHAPE == 'frustum':
        if not set(values) == {'base_radius', 'top_radius', 'height'}:
            raise RuntimeError("Primitive verification failed: set(values) == {'base_radius', 'top_radius', 'height'}")
        if not (values['base_radius'] > 0 and values['top_radius'] >= 0 and (values['height'] > 0)):
            raise RuntimeError("Primitive verification failed: values['base_radius'] > 0 and values['top_radius'] >= 0 and (values['height'] > 0)")
    else:
        raise ValueError('Supported shapes: sphere, torus, frustum.')
    units = design.unitsManager
    dims = {k: units.evaluateExpression(str(v) + ' mm', 'cm') for k, v in values.items()}
    if not all((v >= 0 for v in dims.values())):
        raise RuntimeError('Primitive verification failed: all((v >= 0 for v in dims.values()))')
    before = root.bRepBodies.count
    preparation_end = time.perf_counter()
    sketch = root.sketches.add(root.xZConstructionPlane)
    label = 'Skill ' + SHAPE
    suffix = 2
    while any((body.name == label and body != old_body for body in root.bRepBodies)):
        label = 'Skill ' + SHAPE + ' ' + str(suffix)
        suffix += 1
    sketch.name = label + ' profile'
    point = adsk.core.Point3D.create
    if SHAPE == 'sphere':
        r = dims['radius']
        arc = sketch.sketchCurves.sketchArcs.addByThreePoints(point(0, -r, 0), point(r, 0, 0), point(0, r, 0))
        sketch.sketchCurves.sketchLines.addByTwoPoints(arc.startSketchPoint, arc.endSketchPoint)
        expected_volume = 4 * math.pi * r ** 3 / 3
        expected_size = [2 * r] * 3
    elif SHAPE == 'torus':
        major, tube = (dims['major_radius'], dims['tube_radius'])
        sketch.sketchCurves.sketchCircles.addByCenterRadius(point(major, 0, 0), tube)
        expected_volume = 2 * math.pi ** 2 * major * tube ** 2
        expected_size = [2 * (major + tube), 2 * (major + tube), 2 * tube]
    else:
        base, top, height = (dims['base_radius'], dims['top_radius'], dims['height'])
        coords = [(0, 0), (base, 0), (top, height)]
        if top > 0:
            coords.append((0, height))
        lines = sketch.sketchCurves.sketchLines
        first = point(*coords[0], 0)
        previous = first
        start = None
        for x, y in coords[1:]:
            line = lines.addByTwoPoints(previous, point(x, y, 0))
            if start is None:
                start = line.startSketchPoint
            previous = line.endSketchPoint
        lines.addByTwoPoints(previous, start)
        expected_volume = math.pi * height * (base ** 2 + base * top + top ** 2) / 3
        expected_size = [2 * max(base, top), 2 * max(base, top), height]
    if not sketch.profiles.count == 1:
        raise RuntimeError('Expected a single closed profile.')
    features = root.features.revolveFeatures
    inputs = features.createInput(sketch.profiles.item(0), root.zConstructionAxis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    if not inputs.setAngleExtent(False, adsk.core.ValueInput.createByString('360 deg')):
        raise RuntimeError("Primitive verification failed: inputs.setAngleExtent(False, adsk.core.ValueInput.createByString('360 deg'))")
    feature = features.add(inputs)
    feature.name = label
    body = feature.bodies.item(0)
    body.name = label
    modeling_end = time.perf_counter()
    if not body.isSolid:
        raise RuntimeError('Primitive verification failed: body.isSolid')
    if not feature.healthState == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
        raise RuntimeError('Primitive verification failed: feature.healthState == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState')
    if not abs(body.volume - expected_volume) <= max(1e-05, expected_volume * 1e-06):
        raise RuntimeError('Primitive verification failed: abs(body.volume - expected_volume) <= max(1e-05, expected_volume * 1e-06)')
    box = body.boundingBox
    actual_size = [box.maxPoint.x - box.minPoint.x, box.maxPoint.y - box.minPoint.y, box.maxPoint.z - box.minPoint.z]
    if not all((abs(a - e) < 1e-05 for a, e in zip(actual_size, expected_size))):
        raise RuntimeError('Unexpected primitive dimensions.')
    body.attributes.add('fusion-360-mcp', 'primitive', SHAPE)
    verification_end = time.perf_counter()
    if old_feature:
        old_sketch_name = {'Sphere 50 mm': 'Sphere 50 mm - semicircle', 'Random torus': 'Random torus profile'}.get(REPLACE_BODY, REPLACE_BODY + ' profile')
        old_profile_sketch = root.sketches.itemByName(old_sketch_name)
        if not old_feature.deleteMe():
            raise RuntimeError('Replacement created, but prior feature deletion failed.')
        if old_profile_sketch is not None and old_profile_sketch.isValid:
            old_profile_sketch.isVisible = False
    if not root.bRepBodies.count == before + (0 if replacing else 1):
        raise RuntimeError('Primitive verification failed: root.bRepBodies.count == before + (0 if replacing else 1)')
    if replacing:
        if not not old_body.isValid:
            raise RuntimeError('Previous body unexpectedly remains valid.')
    replacement_end = time.perf_counter()
    sketch.isVisible = False
    if FIT_VIEW:
        viewport = app.activeViewport
        camera = viewport.camera
        camera.isSmoothTransition = False
        camera.isFitView = True
        viewport.camera = camera
    finished = time.perf_counter()
    print(json.dumps({'document': app.activeDocument.name, 'shape': SHAPE, 'body': body.name, 'input_mm': values, 'dimensions_mm': [v * 10 for v in actual_size], 'solid': True, 'volume_verified': True, 'feature_healthy': True, 'replaced': REPLACE_BODY, 'saved': False, 'fusion_execution_verification_seconds': round(finished - execution_start, 4), 'phases_seconds': {'prepare': round(preparation_end - execution_start, 4), 'model': round(modeling_end - preparation_end, 4), 'verify': round(verification_end - modeling_end, 4), 'replace': round(replacement_end - verification_end, 4), 'view': round(finished - replacement_end, 4)}}))
