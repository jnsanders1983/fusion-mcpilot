"""Verified simple-polygon extrusion, including concave profiles, in root coordinates."""
import json,math


def validate_polygon(points):
    if not isinstance(points,(list,tuple)) or not 3<=len(points)<=256 or any(not isinstance(p,(list,tuple)) or len(p)!=2 or any(type(v) not in (int,float) or not math.isfinite(v) for v in p) for p in points):raise ValueError('Polygon requires 3–256 finite XY vertices in millimeters.')
    pts=[list(p) for p in points]
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def on(a,b,p):return abs(cross(a,b,p))<1e-9 and min(a[0],b[0])-1e-9<=p[0]<=max(a[0],b[0])+1e-9 and min(a[1],b[1])-1e-9<=p[1]<=max(a[1],b[1])+1e-9
    def intersect(a,b,c,d):
        products=(cross(a,b,c)*cross(a,b,d),cross(c,d,a)*cross(c,d,b))
        return (products[0]<0 and products[1]<0) or on(a,b,c) or on(a,b,d) or on(c,d,a) or on(c,d,b)
    for i,a in enumerate(pts):
        if math.dist(a,pts[(i+1)%len(pts)])<1e-6:raise ValueError('Polygon has a zero-length edge.')
        for j in range(i+1,len(pts)):
            if j==i+1 or (i==0 and j==len(pts)-1):continue
            if intersect(a,pts[(i+1)%len(pts)],pts[j],pts[(j+1)%len(pts)]):raise ValueError('Polygon self-intersects or touches a nonadjacent edge.')
    area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(pts,pts[1:]+pts[:1]))/2
    if abs(area)<1e-6:raise ValueError('Polygon has negligible area.')
    if area<0:pts.reverse();area=-area
    return pts,area


def build_script(points,height_mm,document,body_name='Profile solid',z_mm=0,new_document=True,owner=None):
    points,area=validate_polygon(points)
    if type(height_mm) not in (int,float) or not math.isfinite(height_mm) or height_mm<=0:raise ValueError('Height must be positive finite millimeters.')
    if type(z_mm) not in (int,float) or not math.isfinite(z_mm):raise ValueError('Finite Z offset required.')
    if not document or not body_name:raise ValueError('Explicit document and body names required.')
    return TEMPLATE.replace('CONFIG_JSON',repr(json.dumps({'points':points,'area':area,'height':height_mm,'z':z_mm,'document':document,'body_name':body_name,'new_document':new_document,'owner':owner})))

TEMPLATE='''import adsk.core,adsk.fusion,json,time
C=json.loads(CONFIG_JSON)
def run(_context: str):
 start=time.perf_counter();app=adsk.core.Application.get()
 if C['new_document']:
  if any(doc.name==C['document'] for doc in app.documents):raise RuntimeError('New profile document already exists.')
  doc=app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType);doc.name=C['document']
 else:
  doc=app.activeDocument
  if doc is None or doc.name!=C['document']:raise RuntimeError('Profile append target changed.')
 d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=d.rootComponent
 if any(b.name==C['body_name'] for b in root.bRepBodies):raise RuntimeError('Profile body name already exists.')
 if C['owner'] and C['new_document']:root.attributes.add('fusion-360-mcp','acceptance_owner',C['owner'])
 before=root.bRepBodies.count
 plane=root.xYConstructionPlane
 if C['z']:
  ip=root.constructionPlanes.createInput();ip.setByOffset(plane,adsk.core.ValueInput.createByString(str(C['z'])+' mm'));plane=root.constructionPlanes.add(ip)
 s=root.sketches.add(plane);s.name='Fixed-coordinate polygon profile';s.isComputeDeferred=True
 try:
  points=[s.sketchPoints.add(adsk.core.Point3D.create(x/10,y/10,0)) for x,y in C['points']]
  for a,b in zip(points,points[1:]+points[:1]):s.sketchCurves.sketchLines.addByTwoPoints(a,b)
  for p in points:p.isFixed=True
 finally:s.isComputeDeferred=False
 if s.profiles.count!=1 or not s.isFullyConstrained:raise RuntimeError('Polygon profile failed closed/constrained checks.')
 ip=root.features.extrudeFeatures.createInput(s.profiles.item(0),adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
 extent=adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByString(str(C['height'])+' mm'))
 if not ip.setOneSideExtent(extent,adsk.fusion.ExtentDirections.PositiveExtentDirection):raise RuntimeError('Polygon extent rejected.')
 feature=root.features.extrudeFeatures.add(ip);body=feature.bodies.item(0);body.name=C['body_name'];s.isVisible=False
 if not d.computeAll() or not body.isSolid or root.bRepBodies.count!=before+1:raise RuntimeError('Polygon body/recompute check failed.')
 if any(f.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState for f in root.features):raise RuntimeError('Polygon design has unhealthy features.')
 volume=C['area']*C['height'];bounds=[min(p[0] for p in C['points']),min(p[1] for p in C['points']),C['z'],max(p[0] for p in C['points']),max(p[1] for p in C['points']),C['z']+C['height']]
 actual=[getattr(p,k)*10 for p in (body.boundingBox.minPoint,body.boundingBox.maxPoint) for k in ('x','y','z')]
 if abs(body.volume*1000-volume)>max(0.03,volume*1e-6) or any(abs(a-b)>1e-4 for a,b in zip(bounds,actual)):raise RuntimeError('Polygon intent verification failed.')
 print(json.dumps({'ok':True,'document':doc.name,'body':body.name,'body_token':body.entityToken,'volume_mm3':body.volume*1000,'bounds_mm':actual,'sketch_fully_constrained':s.isFullyConstrained,'sketch_scope':'Fixed coordinates; edit native extrusion height or rebuild polygon coordinates.','cloud_saved':False,'fusion_execution_verification_seconds':time.perf_counter()-start}))
'''
