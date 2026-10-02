"""Reusable local delivery and Fusion script generators. Python stdlib only."""
from pathlib import Path
import json

def prepare_paths(output_dir, work_dir):
    output=Path(output_dir).expanduser().resolve()
    work=Path(work_dir).expanduser().resolve()
    if work==output or work.is_relative_to(output) or output.is_relative_to(work):
        raise ValueError('Deliverables and working records must be separate directory trees.')
    paths={name:output/name for name in ('cad','print','images','docs')}
    for path in [*paths.values(),work]:path.mkdir(parents=True,exist_ok=True)
    return paths,work

def export_script(document,output_dir,stem,formats=('3mf','f3d')):
    """Export exactly one root solid; no cloud save, dialog, or print utility."""
    if not stem or Path(stem).name!=stem or any(c in stem for c in '\\/:'):
        raise ValueError('stem must be a filename without a path.')
    if not formats or len(set(formats))!=len(formats) or not set(formats)<= {'3mf','stl','f3d','step'}:raise ValueError('Choose unique supported formats.')
    config={'document':document,'output':str(Path(output_dir).resolve()),'stem':stem,'formats':list(formats)}
    return '''import adsk.core,adsk.fusion,json,time,os
C=json.loads(CONFIG_JSON)
def run(_context: str):
 start=time.perf_counter()
 app=adsk.core.Application.get()
 if app.activeDocument.name!=C['document']:raise RuntimeError('Wrong export document.')
 design=adsk.fusion.Design.cast(app.activeProduct)
 if design is None:raise RuntimeError('Active product is not a Design.')
 root=design.rootComponent
 if root.bRepBodies.count!=1:raise RuntimeError('Expected one root print solid; select an assembly explicitly.')
 body=root.bRepBodies.item(0)
 if not body.isSolid:raise RuntimeError('Print body must be solid.')
 if any(f.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState for f in root.features):raise RuntimeError('Unhealthy features.')
 manager=design.exportManager
 files=[]
 for fmt in C['formats']:
  folder='cad' if fmt in ('f3d','step') else 'print'
  filename=os.path.join(C['output'],folder,C['stem']+'.'+fmt)
  if os.path.exists(filename):raise RuntimeError('Export exists; choose a revision or explicitly authorize replacement.')
  if fmt=='f3d':options=manager.createFusionArchiveExportOptions(filename)
  elif fmt=='step':options=manager.createSTEPExportOptions(filename,root)
  elif fmt=='3mf':
   options=manager.createC3MFExportOptions(body,filename)
   options.meshRefinement=adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
   options.sendToPrintUtility=False
  else:
   options=manager.createSTLExportOptions(body,filename)
   options.unitType=adsk.fusion.DistanceUnits.MillimeterDistanceUnits
   options.isBinaryFormat=True
   options.meshRefinement=adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
   options.sendToPrintUtility=False
  if not manager.execute(options):raise RuntimeError('Export failed: '+fmt)
  if not os.path.isfile(filename) or os.path.getsize(filename)==0:raise RuntimeError('Export is missing or empty: '+fmt)
  files.append(filename)
 print(json.dumps({'files':files,'cloud_saved':False,'volume_mm3':body.volume*1000,'fusion_execution_verification_seconds':time.perf_counter()-start}))
'''.replace('CONFIG_JSON',repr(json.dumps(config)))

def appearance_script(document,color=(24,133,140),accent=(43,49,57)):
    """Apply copied matte plastic shaders to a one-body organizer.

    Accent selector targets horizontal recessed faces. No scene/workspace changes
    or render submission: scene settings crashed Fusion in this integration.
    """
    for rgb in (color,accent):
        if len(rgb)!=3 or any(type(v) is not int or not 0<=v<=255 for v in rgb):
            raise ValueError('Colors must be three integer channels in 0–255.')
    c={'document':document,'color':list(color),'accent':list(accent)}
    return '''import adsk.core,adsk.fusion,json,time,math,os
C=json.loads(CONFIG_JSON)
def run(_context: str):
 start=time.perf_counter()
 app=adsk.core.Application.get()
 if app.activeDocument.name!=C['document']:raise RuntimeError('Wrong render document.')
 d=adsk.fusion.Design.cast(app.activeProduct)
 if d is None or d.rootComponent.bRepBodies.count!=1:raise RuntimeError('Expected one root solid.')
 lib=app.materialLibraries.itemByName('Fusion Appearance Library')
 source=lib.appearances.itemByName('Plastic - Matte (White)') if lib else None
 if source is None:raise RuntimeError('Matte plastic appearance missing; inspect local libraries.')
 def appearance(name,rgb,rough):
  a=d.appearances.itemByName(name)
  if a is None:a=d.appearances.addByCopy(source,name)
  color=adsk.core.ColorProperty.cast(a.appearanceProperties.itemById('opaque_albedo'))
  roughness=adsk.core.FloatProperty.cast(a.appearanceProperties.itemById('surface_roughness'))
  if color is None or roughness is None:raise RuntimeError('Appearance property schema changed.')
  color.value=adsk.core.Color.create(*rgb,255)
  roughness.value=rough
  return a
 teal=appearance('Studio body matte',C['color'],0.42)
 graphite=appearance('Studio recessed graphite',C['accent'],0.60)
 body=d.rootComponent.bRepBodies.item(0)
 body.appearance=teal
 top=body.boundingBox.maxPoint.z
 count=0
 for face in body.faces:
  b=face.boundingBox
  if abs(b.minPoint.z-b.maxPoint.z)<1e-7 and b.minPoint.z>1e-6 and b.minPoint.z<top-1e-6:
   face.appearance=graphite
   count+=1
 print(json.dumps({'appearance_applied':True,'accent_faces':count,'finish':'matte plastic; roughness shading, no bitmap texture','fusion_execution_verification_seconds':time.perf_counter()-start}))
'''.replace('CONFIG_JSON',repr(json.dumps(c)))

def preview_script(document,path,width=1200,height=825):
    """Capture a framed viewport; does not touch Render scene settings."""
    c={'document':document,'path':str(Path(path).resolve()),'width':width,'height':height}
    return '''import adsk.core,adsk.fusion,json,time,os
C=json.loads(CONFIG_JSON)
def run(_context: str):
 start=time.perf_counter()
 app=adsk.core.Application.get()
 if app.activeDocument.name!=C['document']:raise RuntimeError('Wrong preview document.')
 d=adsk.fusion.Design.cast(app.activeProduct)
 if d is None:raise RuntimeError('No Design product.')
 if os.path.exists(C['path']):raise RuntimeError('Preview exists; choose a revision.')
 b=d.rootComponent.boundingBox
 center=adsk.core.Point3D.create(*[(getattr(b.minPoint,k)+getattr(b.maxPoint,k))/2 for k in ('x','y','z')])
 span=max(b.maxPoint.x-b.minPoint.x,b.maxPoint.y-b.minPoint.y,b.maxPoint.z-b.minPoint.z)
 cam=app.activeViewport.camera
 cam.isSmoothTransition=False
 cam.target=center
 cam.eye=adsk.core.Point3D.create(center.x+span*1.2,center.y-span*1.6,center.z+span*1.5)
 cam.upVector=adsk.core.Vector3D.create(0,0,1)
 cam.isFitView=True
 app.activeViewport.camera=cam
 if not app.activeViewport.saveAsImageFile(C['path'],C['width'],C['height']):raise RuntimeError('Preview failed.')
 print(json.dumps({'image':C['path'],'type':'Fusion viewport; not ray-traced','fusion_execution_verification_seconds':time.perf_counter()-start}))
'''.replace('CONFIG_JSON',repr(json.dumps(c)))
