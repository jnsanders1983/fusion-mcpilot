"""Small repeatable assembly fixture: nested and repeated component occurrences."""
import json

def build_fixture(document,owner,overlap=False):
    return TEMPLATE.replace('CONFIG_JSON',repr(json.dumps({'document':document,'owner':owner,'overlap':overlap})))

TEMPLATE='''import adsk.core,adsk.fusion,json,math,time
C=json.loads(CONFIG_JSON)
def run(_context: str):
 begin=time.perf_counter();app=adsk.core.Application.get()
 if any(doc.name==C['document'] for doc in app.documents):raise RuntimeError('Assembly target already exists.')
 doc=app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType);doc.name=C['document']
 design=adsk.fusion.Design.cast(app.activeProduct);root=design.rootComponent
 root.attributes.add('fusion-360-mcp','acceptance_owner',C['owner'])
 def placement(x,y,z,angle=0):
  matrix=adsk.core.Matrix3D.create()
  if angle and not matrix.setToRotation(angle,adsk.core.Vector3D.create(0,0,1),adsk.core.Point3D.create(0,0,0)):raise RuntimeError('Rotation rejected.')
  matrix.translation=adsk.core.Vector3D.create(x/10,y/10,z/10)
  return matrix
 carrier=root.occurrences.addNewComponent(placement(100,30,0,math.pi/2));carrier.component.name='Carrier'
 child=carrier.component.occurrences.addNewComponent(placement(25,0,8));child.component.name='Insert'
 comp=child.component;point=adsk.core.Point3D.create;s=comp.sketches.add(comp.xYConstructionPlane)
 pts=[s.sketchPoints.add(point(x,y,0)) for x,y in ((0,0),(2,0),(2,1),(0,1))]
 lines=[s.sketchCurves.sketchLines.addByTwoPoints(a,b) for a,b in zip(pts,pts[1:]+pts[:1])]
 for i,line in enumerate(lines):(s.geometricConstraints.addHorizontal if i%2==0 else s.geometricConstraints.addVertical)(line)
 s.geometricConstraints.addCoincident(pts[0],s.originPoint)
 for a,b,orientation,distance in [(pts[0],pts[1],adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation,'20 mm'),(pts[1],pts[2],adsk.fusion.DimensionOrientations.VerticalDimensionOrientation,'10 mm')]:
  s.sketchDimensions.addDistanceDimension(a,b,orientation,point(3,2,0)).parameter.expression=distance
 if not s.isFullyConstrained:raise RuntimeError('Assembly fixture sketch is not constrained.')
 ip=comp.features.extrudeFeatures.createInput(s.profiles.item(0),adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
 ip.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByString('6 mm')),adsk.fusion.ExtentDirections.PositiveExtentDirection)
 body=comp.features.extrudeFeatures.add(ip).bodies.item(0);body.name='Insert solid';s.isVisible=False
 copy=root.occurrences.addExistingComponent(comp,placement(-30,10,0))
 if C['overlap']:root.occurrences.addExistingComponent(comp,placement(-25,12,1))
 if not design.computeAll():raise RuntimeError('Assembly recompute failed.')
 if abs(body.volume*1000-1200)>0.01 or root.allOccurrences.count!=(4 if C['overlap'] else 3):raise RuntimeError('Assembly fixture dimensions/count differ.')
 centers=[[95,65,11],[-20,15,3]];bounds=[[90,55,8,100,75,14],[-30,10,0,-10,20,6]]
 if C['overlap']:centers.append([-15,17,4]);bounds.append([-25,12,1,-5,22,7])
 print(json.dumps({'document':doc.name,'body_token':body.entityToken,'occurrence_paths':[o.fullPathName for o in root.allOccurrences],'expected_instance_volume_mm3':3600 if C['overlap'] else 2400,'expected_centers_world_mm':centers,'expected_bounds_world_mm':bounds,'fusion_execution_verification_seconds':time.perf_counter()-begin}))
'''
