"""Generate single-body rounded organizers from a millimeter layout, not a saved model."""
from pathlib import Path
import json,math

def validate_config(c):
    required={'base','rack','tray','socket_af','socket_depth','lead_in','centers','grooves','rim_bevel'}
    if set(c)!=required:raise ValueError('Unexpected/missing organizer layout fields.')
    def finite(values):
        if any(type(v) not in (int,float) or not math.isfinite(v) for v in values):raise ValueError('Dimensions must be finite numbers.')
    finite([*c['base'],*c['rack'],*c['tray'],c['socket_af'],c['socket_depth'],c['lead_in'],c['rim_bevel']])
    w,h,r,base=c['base']
    x,y,rw,rh,rr,rise=c['rack']
    tx,ty,tw,th,tr,depth=c['tray']
    if min(w,h,base,rise,c['socket_af'],c['socket_depth'],c['lead_in'])<=0:raise ValueError('Positive dimensions required.')
    for width,height,radius in [(w,h,r),(rw,rh,rr),(tw,th,tr)]:
        if not 0<radius<min(width,height)/2:raise ValueError('Invalid rounded rectangle radius.')
    if min(x,y,tx,ty)<0 or x+rw>w or y+rh>h or tx+tw>w or ty+th>y:raise ValueError('Rack/tray must fit base and remain separate.')
    if not 0<depth<base or not 0<c['socket_depth']<base+rise:raise ValueError('Blind pockets need a floor.')
    if not 0<=c['rim_bevel']<min(rr,rise)/2:raise ValueError('Invalid exterior rim bevel.')
    radius=c['socket_af']/math.sqrt(3)
    margin=radius+c['lead_in']*2/math.sqrt(3)+c['rim_bevel']
    if not c['centers']:raise ValueError('At least one socket is required.')
    for cx,cy in c['centers']:
        finite([cx,cy])
        if not x+rr+margin<=cx<=x+rw-rr-margin or not y+rr+margin<=cy<=y+rh-rr-margin:
            raise ValueError('Sockets must clear the rounded rack perimeter and bevel.')
    for i,a in enumerate(c['centers']):
        for b in c['centers'][i+1:]:
            if math.dist(a,b)<=2*(radius+c['lead_in']*2/math.sqrt(3)):raise ValueError('Socket entrances overlap.')
    for gx,gy,gw,gh,gr,gd in c['grooves']:
        finite([gx,gy,gw,gh,gr,gd])
        if not 0<gr<min(gw,gh)/2 or not 0<gd<base or gx<r or gx+gw>w-r or gy<0 or gy+gh>ty:
            raise ValueError('Grip grooves must fit in the front rim.')
    return c

def build_script(config,document_name):
    validate_config(config)
    if not document_name:raise ValueError('Document name is required.')
    c={'layout':config,'document':document_name}
    return TEMPLATE.replace('CONFIG_JSON',repr(json.dumps(c)))

TEMPLATE='''import adsk.core,adsk.fusion,json,math,time
C=json.loads(CONFIG_JSON)
def run(_context: str):
 start=time.perf_counter()
 app=adsk.core.Application.get()
 if any(d.name==C['document'] for d in app.documents):raise RuntimeError('Named document exists; inspect before replay.')
 doc=app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
 doc.name=C['document']
 d=adsk.fusion.Design.cast(app.activeProduct)
 d.unitsManager.distanceDisplayUnits=adsk.fusion.DistanceUnits.MillimeterDistanceUnits
 root=d.rootComponent
 c=C['layout']
 w,h,r,bh=c['base']
 rx,ry,rw,rh,rr,rise=c['rack']
 tx,ty,tw,th,tr,td=c['tray']
 af=c['socket_af']; lead=c['lead_in']; height=bh+rise
 value=adsk.core.ValueInput.createByString
 for name,number in [('base_height',bh),('rack_rise',rise),('tray_floor',bh-td),('socket_depth',c['socket_depth']),('lead_in',lead)]:
  if d.userParameters.add(name,value(str(number)+' mm'),'mm','Organizer feature control') is None:raise RuntimeError('Parameter rejected.')
 point=lambda x,y:adsk.core.Point3D.create(x/10,y/10,0)
 sketches=[]
 def plane(z):
  if z==0:return root.xYConstructionPlane
  ip=root.constructionPlanes.createInput()
  if not ip.setByOffset(root.xYConstructionPlane,value(z)):raise RuntimeError('Offset plane rejected.')
  return root.constructionPlanes.add(ip)
 def rounded(label,x,y,w,h,r,z):
  s=root.sketches.add(plane(z));s.name=label
  q=math.sqrt(0.5);lines=s.sketchCurves.sketchLines;arcs=s.sketchCurves.sketchArcs
  lines.addByTwoPoints(point(x+r,y),point(x+w-r,y))
  arcs.addByThreePoints(point(x+w-r,y),point(x+w-r+r*q,y+r-r*q),point(x+w,y+r))
  lines.addByTwoPoints(point(x+w,y+r),point(x+w,y+h-r))
  arcs.addByThreePoints(point(x+w,y+h-r),point(x+w-r+r*q,y+h-r+r*q),point(x+w-r,y+h))
  lines.addByTwoPoints(point(x+w-r,y+h),point(x+r,y+h))
  arcs.addByThreePoints(point(x+r,y+h),point(x+r-r*q,y+h-r+r*q),point(x,y+h-r))
  lines.addByTwoPoints(point(x,y+h-r),point(x,y+r))
  arcs.addByThreePoints(point(x,y+r),point(x+r-r*q,y+r-r*q),point(x+r,y))
  if s.profiles.count!=1:raise RuntimeError('Rounded profile count differs.')
  sketches.append(s)
  return s.profiles.item(0)
 def extrude(profile,label,expression,operation,direction,body=None):
  ip=root.features.extrudeFeatures.createInput(profile,operation)
  if body is not None:ip.participantBodies=[body]
  if not ip.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(value(expression)),direction):raise RuntimeError('Extrusion rejected.')
  f=root.features.extrudeFeatures.add(ip);f.name=label
  if f.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:raise RuntimeError(f.errorOrWarningMessage)
  return f
 ops=adsk.fusion.FeatureOperations
 pos=adsk.fusion.ExtentDirections.PositiveExtentDirection;neg=adsk.fusion.ExtentDirections.NegativeExtentDirection
 body=extrude(rounded('Base footprint',0,0,w,h,r,0),'Flat print base','base_height',ops.NewBodyFeatureOperation,pos).bodies.item(0)
 extrude(rounded('Rack footprint',rx,ry,rw,rh,rr,'base_height'),'Raised socket bank','rack_rise',ops.JoinFeatureOperation,pos,body)
 extrude(rounded('Tray footprint',tx,ty,tw,th,tr,'base_height'),'Parts tray','base_height - tray_floor',ops.CutFeatureOperation,neg,body)
 s=root.sketches.add(plane('base_height + rack_rise'));s.name='Hex socket layout'
 radius=af/math.sqrt(3)
 for cx,cy in c['centers']:
  points=[(cx+radius*math.cos(i*math.pi/3),cy+radius*math.sin(i*math.pi/3)) for i in range(6)]
  for a,b in zip(points,points[1:]+points[:1]):s.sketchCurves.sketchLines.addByTwoPoints(point(*a),point(*b))
 if s.profiles.count!=len(c['centers']):raise RuntimeError('Socket profile count differs.')
 profiles=adsk.core.ObjectCollection.create()
 for p in s.profiles:profiles.add(p)
 extrude(profiles,'Blind hex sockets','socket_depth',ops.CutFeatureOperation,neg,body);sketches.append(s)
 area=lambda w,h,r:w*h-(4-math.pi)*r*r
 expected=area(w,h,r)*bh+area(rw,rh,rr)*rise-area(tw,th,tr)*td-len(c['centers'])*math.sqrt(3)/2*af*af*c['socket_depth']
 if abs(body.volume*1000-expected)>0.02:raise RuntimeError('Analytic pre-style volume differs.')
 edges=adsk.core.ObjectCollection.create()
 for e in body.edges:
  b=e.boundingBox
  if abs(b.minPoint.z-height/10)<1e-6 and abs(b.maxPoint.z-height/10)<1e-6 and abs(e.length-radius/10)<1e-6:edges.add(e)
 if edges.count!=6*len(c['centers']):raise RuntimeError('Ambiguous socket edges.')
 ci=root.features.chamferFeatures.createInput2()
 if not ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges,value('lead_in'),False):raise RuntimeError('Socket chamfer rejected.')
 root.features.chamferFeatures.add(ci).name='Socket entrance bevels'
 for i,(x,y,wg,hg,rg,depth) in enumerate(c['grooves']):
  extrude(rounded('Grip groove '+str(i+1),x,y,wg,hg,rg,'base_height'),'Grip detail '+str(i+1),str(depth)+' mm',ops.CutFeatureOperation,neg,body)
 if c['rim_bevel']:
  edges=adsk.core.ObjectCollection.create()
  for e in body.edges:
   b=e.boundingBox
   outer=any(abs(a-v)<1e-6 for a,v in [(b.minPoint.x,rx/10),(b.maxPoint.x,(rx+rw)/10),(b.minPoint.y,ry/10),(b.maxPoint.y,(ry+rh)/10)])
   if abs(b.minPoint.z-height/10)<1e-6 and abs(b.maxPoint.z-height/10)<1e-6 and outer:edges.add(e)
  if edges.count!=8:raise RuntimeError('Exterior rack edge selection differs.')
  ci=root.features.chamferFeatures.createInput2()
  if not ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges,value(str(c['rim_bevel'])+' mm'),False):raise RuntimeError('Rim bevel rejected.')
  root.features.chamferFeatures.add(ci).name='Soft rack rim'
 body=root.bRepBodies.item(0);body.name='Organizer print body'
 for s in sketches:s.isVisible=False
 for p in root.constructionPlanes:p.isLightBulbOn=False
 if root.bRepBodies.count!=1 or not body.isSolid:raise RuntimeError('Expected one solid.')
 b=body.boundingBox
 size=[(getattr(b.maxPoint,k)-getattr(b.minPoint,k))*10 for k in ('x','y','z')]
 if any(abs(a-b)>1e-4 for a,b in zip(size,[w,h,height])):raise RuntimeError('Overall dimensions differ.')
 if any(f.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState for f in root.features):raise RuntimeError('Unhealthy feature.')
 print(json.dumps({'document':doc.name,'size_mm':size,'body_count':1,'solid':True,'feature_health_verified':True,'socket_count':len(c['centers']),'volume_mm3':body.volume*1000,'pre_style_volume_verified':True,'cloud_saved':False,'fusion_execution_verification_seconds':time.perf_counter()-start}))
'''
