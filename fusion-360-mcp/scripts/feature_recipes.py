"""Verified native feature recipes in new documents, using metric parameters."""
import json
import math

RECIPES = {
 'box': {'width':40,'length':30,'height':12},
 'filleted_box': {'width':40,'length':30,'height':12,'radius':3},
 'chamfered_box': {'width':40,'length':30,'height':12,'chamfer':2},
 'open_box': {'width':50,'length':36,'height':20,'wall':2},
 'hole_plate': {'width':60,'length':45,'height':6,'diameter':4,'pitch':12,'columns':3,'rows':2},
 'boolean_union': {'width':40,'length':30,'height':12,'offset':15},
 'boolean_cut': {'width':40,'length':30,'height':12,'offset':15},
 'boolean_intersect': {'width':40,'length':30,'height':12,'offset':15},
 'loft_block': {'width':40,'length':30,'height':20,'top_scale':0.6},
 'straight_sweep': {'width':16,'length':10,'height':30},
 'revolved_tube': {'height':25,'inner_radius':10,'outer_radius':16},
 'circular_hole_flange': {'height':6,'outer_radius':26,'pattern_radius':16,'diameter':4,'count':8},
}

def validate(recipe, parameters):
    if recipe not in RECIPES:raise ValueError('Unsupported native feature recipe.')
    if not set(parameters)<=set(RECIPES[recipe]):raise ValueError('Unknown recipe parameter.')
    p={**RECIPES[recipe],**parameters}
    if any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in p.values()):raise ValueError('Positive finite parameters required.')
    if 'radius' in p and p['radius']>=min(p['width'],p['length'])/2:raise ValueError('Fillet radius exceeds the footprint.')
    if 'chamfer' in p and p['chamfer']>=min(p['width'],p['length'])/2:raise ValueError('Chamfer exceeds the footprint.')
    if 'wall' in p and p['wall']>=min(p['width']/2,p['length']/2,p['height']):raise ValueError('Shell wall leaves no cavity.')
    if 'offset' in p and p['offset']>=p['width']:raise ValueError('Boolean tools must overlap.')
    if 'top_scale' in p and p['top_scale']>2:raise ValueError('Loft scale must not exceed 2.')
    if 'inner_radius' in p and p['inner_radius']>=p['outer_radius']:raise ValueError('Tube inner radius must be smaller than the outer radius.')
    if recipe=='circular_hole_flange':
        if type(p['count']) is not int or not 2<=p['count']<=50:raise ValueError('Circular pattern requires 2–50 holes.')
        if p['pattern_radius']+p['diameter']/2>=p['outer_radius'] or p['diameter']>=2*p['pattern_radius']*math.sin(math.pi/p['count']):raise ValueError('Circular holes overlap or leave the flange.')
    if recipe=='hole_plate':
        if type(p['columns']) is not int or type(p['rows']) is not int or not 2<=p['columns']<=20 or not 1<=p['rows']<=20 or p['columns']*p['rows']>200:raise ValueError('Grid requires 2–20 columns, 1–20 rows, at most 200 holes.')
        if p['diameter']>=p['pitch'] or (p['columns']-1)*p['pitch']+p['diameter']>=p['width'] or (p['rows']-1)*p['pitch']+p['diameter']>=p['length']:raise ValueError('Holes overlap or leave the plate.')
    return p

def build_script(recipe,parameters,document,owner,disposable=False):
    p=validate(recipe,parameters)
    if not document or not owner:raise ValueError('Explicit document and operation owner required.')
    return TEMPLATE.replace('CONFIG_JSON',repr(json.dumps({'recipe':recipe,'parameters':p,'document':document,'owner':owner,'disposable':disposable})))

TEMPLATE='''import adsk.core,adsk.fusion,json,time,math
C=json.loads(CONFIG_JSON)
def run(_context: str):
 start=time.perf_counter();app=adsk.core.Application.get()
 if any(doc.name==C['document'] for doc in app.documents):raise RuntimeError('Target exists; inspect before replay.')
 doc=app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType);doc.name=C['document']
 d=adsk.fusion.Design.cast(app.activeProduct);root=d.rootComponent
 root.attributes.add('fusion-360-mcp','operation_owner',C['owner'])
 if C['disposable']:root.attributes.add('fusion-360-mcp','acceptance_owner',C['owner'])
 d.unitsManager.distanceDisplayUnits=adsk.fusion.DistanceUnits.MillimeterDistanceUnits
 value=adsk.core.ValueInput.createByString
 for name,number in C['parameters'].items():d.userParameters.add(name,value(str(number) if name in ('columns','rows','count','top_scale') else str(number)+' mm'),'' if name in ('columns','rows','count','top_scale') else 'mm','Recipe control')
 n=lambda name:d.userParameters.itemByName(name).value*10
 point=lambda x,y:adsk.core.Point3D.create(x/10,y/10,0)
 dimorient=adsk.fusion.DimensionOrientations
 def dimension(s,a,b,orientation,expression):
  dim=s.sketchDimensions.addDistanceDimension(a,b,orientation,point((a.geometry.x+b.geometry.x)*5+5,(a.geometry.y+b.geometry.y)*5+5))
  if dim is None:raise RuntimeError('Driving dimension rejected.')
  dim.parameter.expression=expression
 def anchor(s,p,x,y,xexpr,yexpr):
  if abs(x)+abs(y)<1e-8:s.geometricConstraints.addCoincident(p,s.originPoint);return
  if abs(x)<1e-8 or abs(y)<1e-8:
   line=s.sketchCurves.sketchLines.addByTwoPoints(s.originPoint,p);line.isConstruction=True
  if abs(x)<1e-8:s.geometricConstraints.addVertical(line)
  else:dimension(s,s.originPoint,p,dimorient.HorizontalDimensionOrientation,xexpr)
  if abs(y)<1e-8:s.geometricConstraints.addHorizontal(line)
  else:dimension(s,s.originPoint,p,dimorient.VerticalDimensionOrientation,yexpr)
 def rectangle(x=0,xexpr='0 mm',plane=None,widthexpr='width',lengthexpr='length'):
  s=root.sketches.add(plane or root.xYConstructionPlane);s.name='Constrained rectangular profile'
  s.isComputeDeferred=True
  try:
   rw=d.unitsManager.evaluateExpression(widthexpr,'mm')*10;rl=d.unitsManager.evaluateExpression(lengthexpr,'mm')*10
   pts=[s.sketchPoints.add(point(a,b)) for a,b in [(x,0),(x+rw,0),(x+rw,rl),(x,rl)]]
   lines=[s.sketchCurves.sketchLines.addByTwoPoints(a,b) for a,b in zip(pts,pts[1:]+pts[:1])]
   for i,line in enumerate(lines):(s.geometricConstraints.addHorizontal if i%2==0 else s.geometricConstraints.addVertical)(line)
   anchor(s,pts[0],x,0,xexpr,'0 mm')
   dimension(s,pts[0],pts[1],dimorient.HorizontalDimensionOrientation,widthexpr)
   dimension(s,pts[1],pts[2],dimorient.VerticalDimensionOrientation,lengthexpr)
  finally:s.isComputeDeferred=False
  if s.profiles.count!=1 or not s.isFullyConstrained:raise RuntimeError('Rectangle is not fully constrained.')
  return s
 ops=adsk.fusion.FeatureOperations
 def extrude(s,op,body=None):
  ip=root.features.extrudeFeatures.createInput(s.profiles.item(0),op)
  if body is not None:ip.participantBodies=[body]
  extent=adsk.fusion.DistanceExtentDefinition.create(value('height'))
  if not ip.setOneSideExtent(extent,adsk.fusion.ExtentDirections.PositiveExtentDirection):raise RuntimeError('Extent rejected.')
  return root.features.extrudeFeatures.add(ip)
 recipe=C['recipe'];h=n('height');w=n('outer_radius')*2 if recipe in ('revolved_tube','circular_hole_flange') else n('width');l=h if recipe=='revolved_tube' else (w if recipe=='circular_hole_flange' else n('length'))
 expected=w*l*h;minimum=[0,0,0];size=[w,l,h];selected=0;hole_count=0
 if recipe=='loft_block':
  lower=rectangle()
  pi=root.constructionPlanes.createInput();pi.setByOffset(root.xYConstructionPlane,value('height'));plane=root.constructionPlanes.add(pi)
  upper=rectangle(plane=plane,widthexpr='width * top_scale',lengthexpr='length * top_scale')
  ip=root.features.loftFeatures.createInput(ops.NewBodyFeatureOperation);ip.loftSections.add(lower.profiles.item(0));ip.loftSections.add(upper.profiles.item(0))
  body=root.features.loftFeatures.add(ip).bodies.item(0)
  scale=C['parameters']['top_scale'];expected=w*l*h*(1+scale+scale*scale)/3;size=[w*max(1,scale),l*max(1,scale),h]
  plane.isLightBulbOn=False
 elif recipe=='straight_sweep':
  profile=rectangle();pathsketch=root.sketches.add(root.xZConstructionPlane)
  end=pathsketch.modelToSketchSpace(adsk.core.Point3D.create(0,0,h/10))
  line=pathsketch.sketchCurves.sketchLines.addByTwoPoints(pathsketch.originPoint,end)
  pathsketch.geometricConstraints.addVertical(line)
  dimension(pathsketch,line.startSketchPoint,line.endSketchPoint,dimorient.VerticalDimensionOrientation,'height')
  path=root.features.createPath(line)
  ip=root.features.sweepFeatures.createInput(profile.profiles.item(0),path,ops.NewBodyFeatureOperation)
  body=root.features.sweepFeatures.add(ip).bodies.item(0)
 elif recipe=='revolved_tube':
  profile=rectangle(n('inner_radius'),'inner_radius',widthexpr='outer_radius - inner_radius',lengthexpr='height')
  ip=root.features.revolveFeatures.createInput(profile.profiles.item(0),root.yConstructionAxis,ops.NewBodyFeatureOperation)
  if not ip.setAngleExtent(False,value('360 deg')):raise RuntimeError('Revolve extent rejected.')
  body=root.features.revolveFeatures.add(ip).bodies.item(0)
  ro=n('outer_radius');ri=n('inner_radius');expected=math.pi*(ro*ro-ri*ri)*h;size=[2*ro,h,2*ro];minimum=[-ro,0,-ro]
 elif recipe=='circular_hole_flange':
  s=root.sketches.add(root.xYConstructionPlane)
  circle=s.sketchCurves.sketchCircles.addByCenterRadius(point(0,0),n('outer_radius')/10)
  s.geometricConstraints.addCoincident(circle.centerSketchPoint,s.originPoint)
  s.sketchDimensions.addDiameterDimension(circle,point(n('outer_radius'),n('outer_radius'))).parameter.expression='2 * outer_radius'
  body=extrude(s,ops.NewBodyFeatureOperation).bodies.item(0)
  seed=root.sketches.add(root.xYConstructionPlane);radius=n('pattern_radius');diam=n('diameter');count=C['parameters']['count']
  circle=seed.sketchCurves.sketchCircles.addByCenterRadius(point(radius,0),diam/20)
  anchor(seed,circle.centerSketchPoint,radius,0,'pattern_radius','0 mm')
  seed.sketchDimensions.addDiameterDimension(circle,point(radius+diam,diam)).parameter.expression='diameter'
  cut=extrude(seed,ops.CutFeatureOperation,body)
  entities=adsk.core.ObjectCollection.create();entities.add(cut)
  ip=root.features.circularPatternFeatures.createInput(entities,root.zConstructionAxis);ip.quantity=value('count');ip.totalAngle=value('360 deg');ip.isSymmetric=False
  root.features.circularPatternFeatures.add(ip)
  centers=[]
  for face in body.faces:
   cylinder=adsk.core.Cylinder.cast(face.geometry)
   if cylinder is not None and abs(cylinder.radius*20-diam)<1e-5:centers.append([cylinder.origin.x*10,cylinder.origin.y*10])
  wanted=[[radius*math.cos(2*math.pi*i/count),radius*math.sin(2*math.pi*i/count)] for i in range(count)]
  if len(centers)!=count or any(not any(math.dist(a,b)<1e-4 for b in centers) for a in wanted):raise RuntimeError('Circular hole count or positions differ.')
  hole_count=count;ro=n('outer_radius');expected=math.pi*(ro*ro-count*(diam/2)**2)*h;size=[2*ro,2*ro,h];minimum=[-ro,-ro,0]
 else:body=extrude(rectangle(),ops.NewBodyFeatureOperation).bodies.item(0)
 body.name='Verified '+recipe
 if recipe in ('filleted_box','chamfered_box'):
  edges=adsk.core.ObjectCollection.create()
  for edge in body.edges:
   b=edge.boundingBox
   if abs(b.maxPoint.x-b.minPoint.x)<1e-7 and abs(b.maxPoint.y-b.minPoint.y)<1e-7 and abs((b.maxPoint.z-b.minPoint.z)*10-h)<1e-5:edges.add(edge)
  if edges.count!=4:raise RuntimeError('Vertical edge selector is ambiguous.')
  selected=edges.count
  if recipe=='filleted_box':
   ip=root.features.filletFeatures.createInput();ip.addConstantRadiusEdgeSet(edges,value('radius'),False);root.features.filletFeatures.add(ip)
   expected-=(4-math.pi)*n('radius')**2*h
  else:
   ip=root.features.chamferFeatures.createInput2();ip.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges,value('chamfer'),False);root.features.chamferFeatures.add(ip)
   expected-=2*n('chamfer')**2*h
 elif recipe=='open_box':
  faces=adsk.core.ObjectCollection.create()
  for face in body.faces:
   b=face.boundingBox
   if abs(b.minPoint.z*10-h)<1e-5 and abs(b.maxPoint.z-b.minPoint.z)<1e-7:faces.add(face)
  if faces.count!=1:raise RuntimeError('Top face selector is ambiguous.')
  ip=root.features.shellFeatures.createInput(faces,False);ip.insideThickness=value('wall');root.features.shellFeatures.add(ip)
  t=n('wall');expected-=(w-2*t)*(l-2*t)*(h-t);selected=faces.count
 elif recipe=='hole_plate':
  cols=C['parameters']['columns'];rows=C['parameters']['rows'];pitch=n('pitch');diam=n('diameter')
  sx=(w-(cols-1)*pitch)/2;sy=(l-(rows-1)*pitch)/2
  d.userParameters.add('seed_x',value('(width - (columns - 1) * pitch) / 2'),'mm','Derived')
  d.userParameters.add('seed_y',value('(length - (rows - 1) * pitch) / 2'),'mm','Derived')
  s=root.sketches.add(root.xYConstructionPlane);circle=s.sketchCurves.sketchCircles.addByCenterRadius(point(sx,sy),diam/20)
  anchor(s,circle.centerSketchPoint,sx,sy,'seed_x','seed_y')
  s.sketchDimensions.addDiameterDimension(circle,point(sx+diam,sy+diam)).parameter.expression='diameter'
  if not s.isFullyConstrained or s.profiles.count!=1:raise RuntimeError('Hole seed is not fully constrained.')
  cut=extrude(s,ops.CutFeatureOperation,body)
  entities=adsk.core.ObjectCollection.create();entities.add(cut)
  ip=root.features.rectangularPatternFeatures.createInput(entities,root.xConstructionAxis,value('columns'),value('pitch'),adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
  ip.directionTwoEntity=root.yConstructionAxis;ip.quantityTwo=value('rows');ip.distanceTwo=value('pitch')
  ip.patternComputeOption=adsk.fusion.PatternComputeOptions.OptimizedPatternCompute
  root.features.rectangularPatternFeatures.add(ip)
  centers=[]
  for face in body.faces:
   cylinder=adsk.core.Cylinder.cast(face.geometry)
   if cylinder is not None and abs(cylinder.radius*20-diam)<1e-5:
    centers.append([cylinder.origin.x*10,cylinder.origin.y*10])
  wanted=[[sx+i*pitch,sy+j*pitch] for j in range(rows) for i in range(cols)]
  if len(centers)!=len(wanted) or any(not any(math.dist(a,b)<1e-4 for b in centers) for a in wanted):raise RuntimeError('Live patterned hole count/positions differ.')
  hole_count=len(centers);expected-=cols*rows*math.pi*(diam/2)**2*h
 elif recipe.startswith('boolean_'):
  offset=n('offset');tool=extrude(rectangle(offset,'offset'),ops.NewBodyFeatureOperation).bodies.item(0)
  tools=adsk.core.ObjectCollection.create();tools.add(tool)
  ip=root.features.combineFeatures.createInput(body,tools)
  ip.operation={'boolean_union':ops.JoinFeatureOperation,'boolean_cut':ops.CutFeatureOperation,'boolean_intersect':ops.IntersectFeatureOperation}[recipe]
  ip.isKeepToolBodies=False;root.features.combineFeatures.add(ip)
  if recipe=='boolean_union':size[0]=w+offset
  elif recipe=='boolean_cut':size[0]=offset
  else:size[0]=w-offset;minimum[0]=offset
  expected=size[0]*l*h
 if not d.computeAll():raise RuntimeError('Feature recompute failed.')
 if root.bRepBodies.count!=1:raise RuntimeError('Unexpected remaining tool or solid count.')
 body=root.bRepBodies.item(0)
 if not body.isValid or not body.isSolid:raise RuntimeError('Body is not a valid solid.')
 issues=[f.name for f in root.features if f.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
 if issues:raise RuntimeError('Unhealthy recipe features: '+str(issues))
 if not all(s.isFullyConstrained for s in root.sketches):raise RuntimeError('Underconstrained driving sketch.')
 b=body.boundingBox;actual_min=[getattr(b.minPoint,k)*10 for k in ('x','y','z')];actual_size=[(getattr(b.maxPoint,k)-getattr(b.minPoint,k))*10 for k in ('x','y','z')]
 if any(abs(a-b)>1e-4 for a,b in zip(actual_min,minimum)) or any(abs(a-b)>1e-4 for a,b in zip(actual_size,size)):raise RuntimeError('Recipe bounds/location differ.')
 if abs(body.volume*1000-expected)>max(0.03,expected*1e-6):raise RuntimeError('Recipe analytic volume differs.')
 for sketch in root.sketches:sketch.isVisible=False
 print(json.dumps({'ok':True,'document':doc.name,'recipe':recipe,'body_token':body.entityToken,'body_count':1,'solid':True,'size_mm':actual_size,'minimum_mm':actual_min,'volume_mm3':body.volume*1000,'analytic_volume_mm3':expected,'selected_entities':selected,'hole_count':hole_count,'fully_constrained_sketches':True,'feature_health_verified':True,'cloud_saved':False,'fusion_execution_verification_seconds':time.perf_counter()-start}))
'''
