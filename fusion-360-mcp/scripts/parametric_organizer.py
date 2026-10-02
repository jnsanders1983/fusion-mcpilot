"""Native parametric dock: constrained sketches and quantity-driven feature patterns."""
import json,math,inspect

DEFAULTS={'overall_width':104,'overall_length':66,'overall_height':18,'base_height':8,
          'tray_floor':3,'corner_radius':3,'side_wall':6,'front_rim':5,'bank_gap':5,
          'socket_af':6.65,'socket_depth':10,'socket_pitch':15,'socket_margin':9,
          'lead_in':0.5,'rim_bevel':0.8}

def layout(parameters):
    p={**DEFAULTS,**parameters}
    if set(p)!=set(DEFAULTS):raise ValueError('Unknown parameter name.')
    if any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in p.values()):raise ValueError('Finite positive parameter values required.')
    w,l,h=p['overall_width'],p['overall_length'],p['overall_height']
    tray=l/3;start=p['front_rim']+tray+p['bank_gap'];bank=l-start
    cols=1+math.floor((w-2*p['socket_margin'])/p['socket_pitch'])
    rows=1+math.floor((bank-2*p['socket_margin'])/p['socket_pitch'])
    if cols<2 or rows<1 or cols*rows>200:raise ValueError('Supported layout needs 2+ columns, 1+ rows and at most 200 sockets.')
    if not p['tray_floor']<p['base_height']<h or p['socket_depth']>=h-p['tray_floor']:raise ValueError('Invalid vertical floor/depth parameters.')
    margin=p['corner_radius']+p['socket_af']/math.sqrt(3)+2*p['lead_in']/math.sqrt(3)+p['rim_bevel']
    if p['socket_margin']<margin or p['socket_pitch']<=2*(p['socket_af']+2*p['lead_in'])/math.sqrt(3):raise ValueError('Socket pitch/margin would overlap pockets or rack edge.')
    if p['side_wall']<=p['rim_bevel'] or p['corner_radius']>=min(tray,w-2*p['side_wall'])/2:raise ValueError('Tray too small for wall/radius.')
    if p['front_rim']<3.2 or p['rim_bevel']>=min(p['corner_radius'],h-p['base_height'])/2:raise ValueError('Invalid front rim or bevel.')
    sx=(w-(cols-1)*p['socket_pitch'])/2
    sy=start+(bank-(rows-1)*p['socket_pitch'])/2
    return {'base':[w,l,p['corner_radius'],p['base_height']],
            'rack':[0,start,w,bank,p['corner_radius'],h-p['base_height']],
            'tray':[p['side_wall'],p['front_rim'],w-2*p['side_wall'],tray,p['corner_radius'],p['base_height']-p['tray_floor']],
            'socket_af':p['socket_af'],'socket_depth':p['socket_depth'],'lead_in':p['lead_in'],
            'centers':[[sx+i*p['socket_pitch'],sy+j*p['socket_pitch']] for j in range(rows) for i in range(cols)],
            'grooves':[[sx+i*p['socket_pitch']-4,2,8,1.2,.5,.6] for i in range(cols)],'rim_bevel':p['rim_bevel']}

def build_script(parameters,document):
    layout(parameters)
    return COMMON+'\n'+BUILD.replace('CONFIG_JSON',repr(json.dumps({'parameters':{**DEFAULTS,**parameters},'document':document})))

def variants_script(document,variants,expected_body_count=1):
    if type(expected_body_count) is not int or expected_body_count not in (1,2):raise ValueError('Organizer verification supports one solid or two material regions.')
    if any(not set(v)<=set(DEFAULTS) for v in variants):raise ValueError('Only primary parameter edits are supported.')
    if any(type(value) not in (int,float) or not math.isfinite(value) or value<=0 for v in variants for value in v.values()):raise ValueError('Primary edits must be positive finite millimeter values.')
    validation='\nDEFAULTS='+repr(DEFAULTS)+'\n'+inspect.getsource(layout)+'\n'
    return COMMON+validation+VARIANTS.replace('CONFIG_JSON',repr(json.dumps({'document':document,'variants':variants,'expected_body_count':expected_body_count})))

COMMON='''import adsk.core,adsk.fusion,json,math,time
def verify_design(d,expected_body_count=1):
 p={x.name:x.value*10 for x in d.userParameters if x.unit=='mm'}
 n=lambda name:d.userParameters.itemByName(name).value
 cols=int(round(n('socket_columns')));rows=int(round(n('socket_rows')))
 w=p['overall_width'];l=p['overall_length'];h=p['overall_height'];bh=p['base_height'];r=p['corner_radius']
 tray=p['tray_length'];bank=p['bank_length'];start=p['bank_start'];af=p['socket_af'];lead=p['lead_in']
 root=d.rootComponent
 if root.bRepBodies.count!=expected_body_count:raise RuntimeError('Unexpected parametric body count.')
 bodies=list(root.bRepBodies)
 if any(not body.isSolid for body in bodies):raise RuntimeError('Not solid.')
 size=[(max(getattr(b.boundingBox.maxPoint,k) for b in bodies)-min(getattr(b.boundingBox.minPoint,k) for b in bodies))*10 for k in ('x','y','z')]
 if expected_body_count==2:
  ordered=sorted(bodies,key=lambda b:b.boundingBox.minPoint.z)
  if abs(ordered[0].boundingBox.maxPoint.z-bh/10)>1e-6 or abs(ordered[1].boundingBox.minPoint.z-bh/10)>1e-6:raise RuntimeError('Material interface did not follow base height.')
 if any(abs(a-b)>1e-4 for a,b in zip(size,[w,l,h])):raise RuntimeError('Parametric bounds differ.')
 issues=[f.name for f in root.features if f.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
 if issues:raise RuntimeError('Parametric feature issues: '+str(issues))
 if not all(s.isFullyConstrained for s in root.sketches):raise RuntimeError('Driving sketches are not fully constrained.')
 hexarea=math.sqrt(3)/2*af*af
 floors=[]
 for face in [face for body in bodies for face in body.faces]:
  b=face.boundingBox
  if abs(b.minPoint.z-(h-p['socket_depth'])/10)<1e-6 and abs(b.maxPoint.z-b.minPoint.z)<1e-7 and abs(face.area*100-hexarea)<1e-4:
   floors.append([(b.minPoint.x+b.maxPoint.x)*5,(b.minPoint.y+b.maxPoint.y)*5])
 # Splitting exactly at socket floors merges foundation top faces. Count
 # the matching hexagonal inner loops on the rack's interface instead.
 if expected_body_count==2 and abs(h-p['socket_depth']-bh)<1e-5:
  floors=[]
  upper=max(bodies,key=lambda b:b.boundingBox.maxPoint.z)
  for face in upper.faces:
   box=face.boundingBox
   if abs(box.minPoint.z-bh/10)>1e-6 or abs(box.maxPoint.z-box.minPoint.z)>1e-7:continue
   for loop in face.loops:
    if loop.isOuter or loop.edges.count!=6 or any(abs(e.length*10-af/math.sqrt(3))>1e-4 for e in loop.edges):continue
    edges=list(loop.edges)
    low=[min(getattr(e.boundingBox.minPoint,k) for e in edges) for k in ('x','y')]
    high=[max(getattr(e.boundingBox.maxPoint,k) for e in edges) for k in ('x','y')]
    floors.append([(a+b)*5 for a,b in zip(low,high)])
 if len(floors)!=cols*rows:raise RuntimeError('Live socket count differs from parameter count.')
 expected_centers=[[p['seed_x']+i*p['socket_pitch'],p['seed_y']+j*p['socket_pitch']] for j in range(rows) for i in range(cols)]
 for center in expected_centers:
  if not any(math.dist(center,a)<1e-4 for a in floors):raise RuntimeError('Socket pattern position differs.')
 area=lambda w,h,r:w*h-(4-math.pi)*r*r
 expected=area(w,l,r)*bh+area(w,bank,r)*(h-bh)-area(p['tray_width'],tray,r)*(bh-p['tray_floor'])-cols*rows*hexarea*p['socket_depth']
 entry=math.sqrt(3)/2*(2*af*lead*lead+4/3*lead**3)
 perimeter=2*(w+bank-4*r)+2*math.pi*r
 bevel=p['rim_bevel']
 expected-=cols*rows*entry+perimeter*bevel**2/2-math.pi*bevel**3/3+cols*area(8,1.2,.5)*.6
 volume=sum(body.volume*1000 for body in bodies)
 if abs(volume-expected)>0.04:raise RuntimeError('Full styled analytic volume differs: '+str([volume,expected]))
 return {'size_mm':size,'columns':cols,'rows':rows,'socket_count':len(floors),'socket_centers_mm':expected_centers,
  'volume_mm3':volume,'analytic_volume_mm3':expected,'fully_constrained_sketches':True,'feature_health_verified':True,'solid':True,'body_count':len(bodies),'parameters_mm':p}
'''

BUILD='''C=json.loads(CONFIG_JSON)
def run(_context: str):
 begin=time.perf_counter();app=adsk.core.Application.get()
 if any(doc.name==C['document'] for doc in app.documents):raise RuntimeError('Target exists; inspect before replay.')
 doc=app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType);doc.name=C['document']
 d=adsk.fusion.Design.cast(app.activeProduct);root=d.rootComponent
 d.unitsManager.distanceDisplayUnits=adsk.fusion.DistanceUnits.MillimeterDistanceUnits
 value=adsk.core.ValueInput.createByString
 for name,num in C['parameters'].items():d.userParameters.add(name,value(str(num)+' mm'),'mm','Editable dock control')
 derived=[('tray_length','overall_length / 3','mm'),('tray_width','overall_width - 2 * side_wall','mm'),('bank_start','front_rim + tray_length + bank_gap','mm'),('bank_length','overall_length - bank_start','mm'),('rack_rise','overall_height - base_height','mm'),
 ('socket_columns','1 + floor((overall_width - 2 * socket_margin) / socket_pitch)',''),('socket_rows','1 + floor((bank_length - 2 * socket_margin) / socket_pitch)',''),('socket_count','socket_columns * socket_rows',''),
 ('seed_x','(overall_width - (socket_columns - 1) * socket_pitch) / 2','mm'),('seed_y','bank_start + (bank_length - (socket_rows - 1) * socket_pitch) / 2','mm'),('socket_radius','socket_af / sqrt(3)','mm')]
 for name,expression,unit in derived:d.userParameters.add(name,value(expression),unit,'Derived; edit primary controls instead')
 def mm(expression):return d.unitsManager.evaluateExpression(expression,'mm')*10
 point=lambda x,y:adsk.core.Point3D.create(x/10,y/10,0)
 def plane(z):
  if z=='0 mm':return root.xYConstructionPlane
  ip=root.constructionPlanes.createInput();ip.setByOffset(root.xYConstructionPlane,value(z))
  return root.constructionPlanes.add(ip)
 def dimension(s,a,b,orientation,expression):
  text=point((a.geometry.x+b.geometry.x)*5+5,(a.geometry.y+b.geometry.y)*5+5)
  dim=s.sketchDimensions.addDistanceDimension(a,b,orientation,text)
  if dim is None:raise RuntimeError('Driving dimension rejected.')
  dim.parameter.expression=expression
 def anchor(s,p,xexpr,yexpr):
  x=mm(xexpr);y=mm(yexpr);g=s.geometricConstraints
  if abs(x)+abs(y)<1e-8:g.addCoincident(p,s.originPoint);return
  if abs(x)<1e-8 or abs(y)<1e-8:
   line=s.sketchCurves.sketchLines.addByTwoPoints(s.originPoint,p);line.isConstruction=True
  if abs(x)<1e-8:g.addVertical(line)
  else:dimension(s,s.originPoint,p,adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation,xexpr)
  if abs(y)<1e-8:g.addHorizontal(line)
  else:dimension(s,s.originPoint,p,adsk.fusion.DimensionOrientations.VerticalDimensionOrientation,yexpr)
 def rectangle(label,x,y,w,h,z):
  s=root.sketches.add(plane(z));s.name=label
  px,py,pw,ph=map(mm,[x,y,w,h])
  pts=[s.sketchPoints.add(point(*xy)) for xy in [(px,py),(px+pw,py),(px+pw,py+ph),(px,py+ph)]]
  lines=[s.sketchCurves.sketchLines.addByTwoPoints(a,b) for a,b in zip(pts,pts[1:]+pts[:1])]
  for i,line in enumerate(lines):
   (s.geometricConstraints.addHorizontal if i%2==0 else s.geometricConstraints.addVertical)(line)
  anchor(s,pts[0],x,y)
  dimension(s,pts[0],pts[1],adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation,w)
  dimension(s,pts[1],pts[2],adsk.fusion.DimensionOrientations.VerticalDimensionOrientation,h)
  if not s.isFullyConstrained or s.profiles.count!=1:raise RuntimeError('Rectangle is not fully driven: '+label)
  return s
 def extrude(sketch,name,expr,op,negative=False,body=None):
  ip=root.features.extrudeFeatures.createInput(sketch.profiles.item(0),op)
  if body is not None:ip.participantBodies=[body]
  extent=adsk.fusion.DistanceExtentDefinition.create(value(expr))
  ip.setOneSideExtent(extent,adsk.fusion.ExtentDirections.NegativeExtentDirection if negative else adsk.fusion.ExtentDirections.PositiveExtentDirection)
  f=root.features.extrudeFeatures.add(ip);f.name=name
  return f
 def vertical_fillet(body,name,radius,zmin=None,zmax=None):
  edges=adsk.core.ObjectCollection.create()
  for e in body.edges:
   b=e.boundingBox
   if abs(b.maxPoint.x-b.minPoint.x)<1e-7 and abs(b.maxPoint.y-b.minPoint.y)<1e-7 and b.maxPoint.z-b.minPoint.z>1e-7:
    if zmin is None or (abs(b.minPoint.z-mm(zmin)/10)<1e-6 and abs(b.maxPoint.z-mm(zmax)/10)<1e-6):edges.add(e)
  if edges.count!=4:raise RuntimeError('Corner fillet selection differs: '+name+' '+str(edges.count))
  ip=root.features.filletFeatures.createInput()
  ip.addConstantRadiusEdgeSet(edges,value(radius),False)
  f=root.features.filletFeatures.add(ip);f.name=name
  return f
 ops=adsk.fusion.FeatureOperations
 base=extrude(rectangle('Driven base','0 mm','0 mm','overall_width','overall_length','0 mm'),'Base','base_height',ops.NewBodyFeatureOperation).bodies.item(0)
 vertical_fillet(base,'Base corner radius','corner_radius')
 rack=extrude(rectangle('Driven rack','0 mm','bank_start','overall_width','bank_length','base_height'),'Rack','rack_rise',ops.NewBodyFeatureOperation).bodies.item(0)
 vertical_fillet(rack,'Rack corner radius','corner_radius')
 collection=adsk.core.ObjectCollection.create();collection.add(rack)
 ci=root.features.combineFeatures.createInput(base,collection);ci.operation=ops.JoinFeatureOperation;ci.isKeepToolBodies=False
 root.features.combineFeatures.add(ci).name='Joined rack and base'
 body=root.bRepBodies.item(0)
 extrude(rectangle('Driven tray','side_wall','front_rim','tray_width','tray_length','base_height'),'Tray','base_height - tray_floor',ops.CutFeatureOperation,True,body)
 vertical_fillet(body,'Tray corner radius','corner_radius','tray_floor','base_height')
 s=root.sketches.add(plane('overall_height'));s.name='Driven seed hex socket'
 circle=s.sketchCurves.sketchCircles.addByCenterRadius(point(mm('seed_x'),mm('seed_y')),mm('socket_radius')/10)
 circle.isConstruction=True
 anchor(s,circle.centerSketchPoint,'seed_x','seed_y')
 dim=s.sketchDimensions.addDiameterDimension(circle,point(mm('seed_x')+5,mm('seed_y')+5));dim.parameter.expression='2 * socket_radius'
 pts=[]
 for i in range(6):
  co=math.cos(i*math.pi/3);si=math.sin(i*math.pi/3)
  p=s.sketchPoints.add(point(mm('seed_x')+mm('socket_radius')*co,mm('seed_y')+mm('socket_radius')*si))
  s.geometricConstraints.addCoincident(p,circle);pts.append(p)
 lines=[s.sketchCurves.sketchLines.addByTwoPoints(a,b) for a,b in zip(pts,pts[1:]+pts[:1])]
 for line in lines[1:]:s.geometricConstraints.addEqual(lines[0],line)
 s.geometricConstraints.addHorizontal(lines[1])
 if not s.isFullyConstrained:raise RuntimeError('Hex sketch is not fully driven.')
 cut=extrude(s,'Seed blind socket','socket_depth',ops.CutFeatureOperation,True,body)
 edges=adsk.core.ObjectCollection.create()
 for e in body.edges:
  b=e.boundingBox
  if abs(b.minPoint.z-mm('overall_height')/10)<1e-6 and abs(b.maxPoint.z-b.minPoint.z)<1e-7 and abs(e.length-mm('socket_radius')/10)<1e-6:edges.add(e)
 if edges.count!=6:raise RuntimeError('Seed bevel selection differs.')
 ci=root.features.chamferFeatures.createInput2();ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges,value('lead_in'),False)
 entry=root.features.chamferFeatures.add(ci);entry.name='Seed entry bevel'
 def pattern(features,name,rows=False):
  entities=adsk.core.ObjectCollection.create()
  for f in features:entities.add(f)
  ip=root.features.rectangularPatternFeatures.createInput(entities,root.xConstructionAxis,value('socket_columns'),value('socket_pitch'),adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
  ip.patternComputeOption=adsk.fusion.PatternComputeOptions.OptimizedPatternCompute
  if rows:
   ip.directionTwoEntity=root.yConstructionAxis;ip.quantityTwo=value('socket_rows');ip.distanceTwo=value('socket_pitch')
  f=root.features.rectangularPatternFeatures.add(ip);f.name=name
 pattern([cut,entry],'Automatic socket grid',True)
 groove=extrude(rectangle('Driven grip detail','seed_x - 4 mm','2 mm','8 mm','1.2 mm','base_height'),'Seed grip groove','0.6 mm',ops.CutFeatureOperation,True,body)
 corner=vertical_fillet(body,'Grip corner radius','0.5 mm','base_height - 0.6 mm','base_height')
 pattern([groove,corner],'Automatic grip details')
 edges=adsk.core.ObjectCollection.create()
 for e in body.edges:
  b=e.boundingBox
  if abs(b.minPoint.z-mm('overall_height')/10)<1e-6 and abs(b.maxPoint.z-b.minPoint.z)<1e-7:
   if any(abs(a-v)<1e-6 for a,v in [(b.minPoint.x,0),(b.maxPoint.x,mm('overall_width')/10),(b.minPoint.y,mm('bank_start')/10),(b.maxPoint.y,mm('overall_length')/10)]):edges.add(e)
 if edges.count!=8:raise RuntimeError('Outer bevel selection differs.')
 ci=root.features.chamferFeatures.createInput2();ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges,value('rim_bevel'),False)
 root.features.chamferFeatures.add(ci).name='Parametric rack rim'
 for s in root.sketches:s.isVisible=False
 for p in root.constructionPlanes:p.isLightBulbOn=False
 if not d.computeAll():raise RuntimeError('Compute failed.')
 result=verify_design(d);result['document']=doc.name;result['cloud_saved']=False
 result['fusion_execution_verification_seconds']=time.perf_counter()-begin
 print(json.dumps(result))
'''

VARIANTS='''C=json.loads(CONFIG_JSON)
def run(_context: str):
 begin=time.perf_counter();app=adsk.core.Application.get()
 if app.activeDocument.name!=C['document']:raise RuntimeError('Wrong parametric document.')
 d=adsk.fusion.Design.cast(app.activeProduct);results=[]
 verify_design(d,C.get('expected_body_count',1))
 for v in C['variants']:
  current={name:d.userParameters.itemByName(name).value*10 for name in DEFAULTS}
  layout({**current,**v})
  before=verify_design(d,C.get('expected_body_count',1))
  snapshot={name:d.userParameters.itemByName(name).expression for name in v}
  try:
   for name,number in v.items():d.userParameters.itemByName(name).expression=str(number)+' mm'
   if not d.computeAll():raise RuntimeError('Parametric regeneration failed.')
   verified=verify_design(d,C.get('expected_body_count',1))
   results.append(verified)
  except Exception as error:
   failures=[]
   for name,expression in snapshot.items():
    try:d.userParameters.itemByName(name).expression=expression
    except Exception as restore_error:failures.append(name+': '+str(restore_error))
   try:
    if not d.computeAll():raise RuntimeError('Restoration recompute returned false.')
    restored=verify_design(d,C.get('expected_body_count',1))
    if restored['socket_count']!=before['socket_count'] or abs(restored['volume_mm3']-before['volume_mm3'])>0.04 or any(abs(a-b)>1e-4 for a,b in zip(restored['size_mm'],before['size_mm'])):raise RuntimeError('Restored geometry differs from baseline.')
    if any(d.userParameters.itemByName(name).expression!=expression for name,expression in snapshot.items()):raise RuntimeError('Parameter expressions were not restored.')
   except Exception as restore_error:failures.append(str(restore_error))
   print(json.dumps({'ok':False,'error':str(error),'rollback_verified':not failures,'rollback_errors':failures,'variants':results,'fusion_execution_verification_seconds':time.perf_counter()-begin}))
   return
 print(json.dumps({'ok':True,'variants':results,'native_parameter_edits':True,'fusion_execution_verification_seconds':time.perf_counter()-begin}))
'''
