"""Cut blind hex fit pockets into an explicitly selected rectangular coupon blank."""
import json,math
def cut_script(document,af_values,width=50,length=20,height=9,depth=6,lead=.5):
    dims=[width,length,height,depth,lead,*af_values]
    if not 1<=len(af_values)<=12 or any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in dims):raise ValueError('Finite positive coupon dimensions required.')
    pitch=width/len(af_values)
    if depth>=height or lead>=depth or max(af_values)+2*lead>=min(pitch,length)*math.sqrt(3)/2:raise ValueError('Coupon pockets need clearance and a remaining floor.')
    c={'document':document,'af':af_values,'width':width,'length':length,'height':height,'depth':depth,'lead':lead}
    return TEMPLATE.replace('CONFIG_JSON',repr(json.dumps(c)))
TEMPLATE='''import adsk.core,adsk.fusion,json,time,math
C=json.loads(CONFIG_JSON)
def run(_context: str):
 start=time.perf_counter();app=adsk.core.Application.get()
 if app.activeDocument.name!=C['document']:raise RuntimeError('Coupon document changed.')
 d=adsk.fusion.Design.cast(app.activeProduct);root=d.rootComponent
 if root.bRepBodies.count!=1:raise RuntimeError('Expected one rectangular coupon blank.')
 blank=root.bRepBodies.item(0);before=blank.volume*1000
 if abs(before-C['width']*C['length']*C['height'])>.01:raise RuntimeError('Blank volume differs.')
 box=blank.boundingBox
 if any(abs(getattr(box.minPoint,k))>1e-6 for k in ('x','y','z')):raise RuntimeError('Blank must start at root origin.')
 if any(abs(getattr(box.maxPoint,k)*10-v)>1e-4 for k,v in zip(('x','y','z'),(C['width'],C['length'],C['height']))):raise RuntimeError('Blank bounds differ.')
 value=adsk.core.ValueInput.createByString
 plane_input=root.constructionPlanes.createInput();plane_input.setByOffset(root.xYConstructionPlane,value(str(C['height'])+' mm'))
 plane=root.constructionPlanes.add(plane_input);plane.isLightBulbOn=False
 sketch=root.sketches.add(plane);sketch.name='Fit sockets, increasing AF from left'
 for i,af in enumerate(C['af']):
  cx=C['width']*(i+.5)/len(C['af']);cy=C['length']/2;radius=af/math.sqrt(3)
  points=[sketch.sketchPoints.add(adsk.core.Point3D.create((cx+radius*math.cos(j*math.pi/3))/10,(cy+radius*math.sin(j*math.pi/3))/10,0)) for j in range(6)]
  for a,b in zip(points,points[1:]+points[:1]):sketch.sketchCurves.sketchLines.addByTwoPoints(a,b)
  for point in points:point.isFixed=True
 if not sketch.isFullyConstrained or sketch.profiles.count!=len(C['af']):raise RuntimeError('Coupon profiles differ.')
 profiles=adsk.core.ObjectCollection.create()
 for profile in sketch.profiles:profiles.add(profile)
 ip=root.features.extrudeFeatures.createInput(profiles,adsk.fusion.FeatureOperations.CutFeatureOperation)
 ip.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(value(str(C['depth'])+' mm')),adsk.fusion.ExtentDirections.NegativeExtentDirection)
 root.features.extrudeFeatures.add(ip).name='Blind fit pockets'
 edges=adsk.core.ObjectCollection.create()
 for edge in blank.edges:
  b=edge.boundingBox
  if abs(b.minPoint.z-C['height']/10)<1e-6 and abs(b.maxPoint.z-b.minPoint.z)<1e-7 and any(abs(edge.length*10-af/math.sqrt(3))<1e-4 for af in C['af']):edges.add(edge)
 if edges.count!=6*len(C['af']):raise RuntimeError('Coupon entrance edge selection differs.')
 ip=root.features.chamferFeatures.createInput2();ip.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges,value(str(C['lead'])+' mm'),False)
 root.features.chamferFeatures.add(ip).name='Fit socket lead-ins';sketch.isVisible=False
 if not d.computeAll():raise RuntimeError('Coupon recompute failed.')
 expected=before-sum(math.sqrt(3)/2*af*af*C['depth']+math.sqrt(3)/2*(2*af*C['lead']**2+4/3*C['lead']**3) for af in C['af'])
 if abs(blank.volume*1000-expected)>.04 or not blank.isSolid:raise RuntimeError('Coupon volume differs.')
 if any(f.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState for f in root.features):raise RuntimeError('Coupon feature health failed.')
 print(json.dumps({'document':C['document'],'socket_af_mm_left_to_right':C['af'],'socket_depth_mm':C['depth'],'volume_mm3':blank.volume*1000,'analytic_volume_mm3':expected,'fusion_execution_verification_seconds':time.perf_counter()-start}))
'''
