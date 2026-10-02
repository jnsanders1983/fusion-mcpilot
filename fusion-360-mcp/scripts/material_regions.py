"""Split a selected root solid at a parametric axis plane into two material regions."""
import json
from entity_selection import SOURCE

def split_script(document,selector,axis,offset_expression,regions):
    from measure_geometry import build_script
    build_script(document,[selector,{'name':'validation-only'}],'interference')
    if selector.get('occurrence_path'):raise ValueError('Partition supports root bodies only; component geometry requires a scoped implementation.')
    if axis!='z' or not isinstance(offset_expression,str) or not offset_expression.strip():raise ValueError('Verified partition supports an XY plane at a millimeter-compatible Z expression.')
    if len(regions)!=2 or len({r['name'] for r in regions})!=2:raise ValueError('Two distinct region names required, lower then upper.')
    for r in regions:
        if not isinstance(r['name'],str) or not r['name']:raise ValueError('Region names required.')
        rgb=r.get('rgb')
        if rgb is not None and (len(rgb)!=3 or any(type(v) is not int or not 0<=v<=255 for v in rgb)):raise ValueError('RGB channels must be integers 0–255.')
    c={'document':document,'selector':selector,'axis':axis,'offset':offset_expression,'regions':regions}
    return 'import adsk.core,adsk.fusion,json,time,math\n'+SOURCE+'\n'+TEMPLATE.replace('CONFIG_JSON',repr(json.dumps(c)))

TEMPLATE='''C=json.loads(CONFIG_JSON)
def run(_context: str):
 start=time.perf_counter();app=adsk.core.Application.get();doc=app.activeDocument
 if doc is None or doc.name!=C['document']:raise RuntimeError('Partition document changed.')
 d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=d.rootComponent
 body=resolve_body(d,C['selector'])
 if not body.isSolid:raise RuntimeError('Partition requires a solid.')
 if any(b!=body and b.name in [r['name'] for r in C['regions']] for b in root.bRepBodies):raise RuntimeError('Region name already used.')
 offset=d.unitsManager.evaluateExpression(C['offset'],'mm');axis=C['axis'];box=body.boundingBox
 if not math.isfinite(offset) or not getattr(box.minPoint,axis)+1e-6<offset<getattr(box.maxPoint,axis)-1e-6:raise RuntimeError('Partition plane must pass through the solid interior.')
 volume=body.volume;count=root.bRepBodies.count
 source=None
 if any(r.get('rgb') is not None for r in C['regions']):
  lib=app.materialLibraries.itemByName('Fusion Appearance Library')
  source=lib.appearances.itemByName('Plastic - Matte (White)') if lib else None
  if source is None:raise RuntimeError('Required matte appearance is unavailable; no split performed.')
 plane_input=root.constructionPlanes.createInput()
 reference={'z':root.xYConstructionPlane,'x':root.yZConstructionPlane,'y':root.xZConstructionPlane}[axis]
 if not plane_input.setByOffset(reference,adsk.core.ValueInput.createByString(C['offset'])):raise RuntimeError('Partition plane input rejected.')
 plane=root.constructionPlanes.add(plane_input);plane.name='Material interface';plane.isLightBulbOn=False
 feature=root.features.splitBodyFeatures.add(root.features.splitBodyFeatures.createInput(body,plane,True));feature.name='Material region partition'
 if not d.computeAll():raise RuntimeError('Partition recompute failed; inspect before replay.')
 bodies=list(feature.bodies)
 if len(bodies)!=2 or root.bRepBodies.count!=count+1 or any(not b.isSolid for b in bodies):raise RuntimeError('Expected exactly two solid regions.')
 bodies.sort(key=lambda b:getattr(b.boundingBox.minPoint,axis))
 if abs(sum(b.volume for b in bodies)-volume)>max(1e-7,volume*1e-8):raise RuntimeError('Partition changed total volume.')
 if abs(getattr(bodies[0].boundingBox.maxPoint,axis)-offset)>1e-6 or abs(getattr(bodies[1].boundingBox.minPoint,axis)-offset)>1e-6:raise RuntimeError('Partition interface differs from plane.')
 records=[]
 for b,r in zip(bodies,C['regions']):
  b.name=r['name']
  if r.get('rgb') is not None:
   appearance=d.appearances.addByCopy(source,'Region '+r['name'])
   color=adsk.core.ColorProperty.cast(appearance.appearanceProperties.itemById('opaque_albedo'))
   if color is None:raise RuntimeError('Appearance color schema changed.')
   color.value=adsk.core.Color.create(*r['rgb'],255);b.appearance=appearance
  bounds=b.boundingBox
  records.append({'name':b.name,'entity_token':b.entityToken,'volume_mm3':b.volume*1000,'bounds_mm':[getattr(p,k)*10 for p in (bounds.minPoint,bounds.maxPoint) for k in ('x','y','z')]})
 issues=[f.name for f in root.features if f.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
 if issues:raise RuntimeError('Unhealthy partition features: '+str(issues))
 print(json.dumps({'document':doc.name,'regions':records,'total_volume_mm3':sum(b.volume*1000 for b in bodies),'original_volume_mm3':volume*1000,'plane_expression':C['offset'],'interface_mm':offset*10,'geometry_preserved':True,'feature_health_verified':True,'fusion_execution_verification_seconds':time.perf_counter()-start}))
'''
