"""Common-frame mesh capture and core 3MF assembly packaging; no printer output."""
import argparse,json,math,re,zipfile,struct,xml.etree.ElementTree as ET
from pathlib import Path
from entity_selection import SOURCE
from safe_data import model_xml,strict_json,MAX_NODES
from validate_mesh import inspect,validate,indexed_topology

NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',NS)
tag=lambda name:'{'+NS+'}'+name


def capture_script(document,selectors):
    from measure_geometry import build_script
    build_script(document,selectors,'interference')  # shared selector contract
    config={'document':document,'selectors':selectors}
    return 'import adsk.core,adsk.fusion,json,time\n'+SOURCE+'\n'+CAPTURE.replace('CONFIG_JSON',repr(json.dumps(config)))


CAPTURE='''C=json.loads(CONFIG_JSON)
def run(_context: str):
 start=time.perf_counter();app=adsk.core.Application.get();doc=app.activeDocument
 if doc is None or doc.name!=C['document']:raise RuntimeError('Mesh target changed.')
 d=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'));root=d.rootComponent
 def matrices_for(path):
  found=[]
  def walk(comp,current,matrices,depth):
   if depth>64:raise RuntimeError('Assembly depth exceeds limit.')
   if current==path:found.append(matrices);return
   for o in comp.occurrences:
    name=current+'+'+o.name if current else o.name
    if path==name or path.startswith(name+'+'):walk(o.component,name,matrices+[o.transform2],depth+1)
  walk(root,'',[],0)
  if len(found)!=1:raise RuntimeError('Mesh occurrence path is missing or ambiguous.')
  return found[0]
 parts=[];seen=[]
 for selector in C['selectors']:
  proxy=resolve_body(d,selector)
  if any(proxy==earlier for earlier in seen):raise RuntimeError('Duplicate mesh body instance.')
  seen.append(proxy);body=proxy.nativeObject or proxy
  if not body.isSolid:raise RuntimeError('Print region must be a solid.')
  calculator=body.meshManager.createMeshCalculator();calculator.setQuality(adsk.fusion.TriangleMeshQualityOptions.HighQualityTriangleMesh)
  mesh=calculator.calculate()
  if mesh is None:raise RuntimeError('Native tessellation failed.')
  matrices=matrices_for(selector.get('occurrence_path',''));vertices=[]
  for point in mesh.nodeCoordinates:
   p=point.copy()
   for matrix in reversed(matrices):
    if not p.transformBy(matrix):raise RuntimeError('World mesh transformation failed.')
   vertices.append([p.x*10,p.y*10,p.z*10])
  indexes=list(mesh.nodeIndices)
  if len(indexes)%3:raise RuntimeError('Native triangle index count differs.')
  path=selector.get('occurrence_path','')
  parts.append({'name':path+' / '+body.name if path else body.name,'occurrence_path':path,'vertices_mm':vertices,'triangles':[indexes[i:i+3] for i in range(0,len(indexes),3)],'cad_volume_mm3':body.volume*1000})
 print(json.dumps({'unit':'millimeter','parts':parts,'cloud_saved':False,'fusion_execution_verification_seconds':time.perf_counter()-start}))
'''


def part_check(part,indexed=True):
    vertices=part['vertices_mm'];indexes=part['triangles']
    if not vertices or not indexes or len(vertices)+len(indexes)>MAX_NODES:raise ValueError('Empty or excessive part mesh.')
    if any(len(v)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in v) for v in vertices):raise ValueError('Finite XYZ coordinates required.')
    if any(len(tri)!=3 or any(type(i) is not int or not 0<=i<len(vertices) for i in tri) for tri in indexes):raise ValueError('Invalid triangle indexes.')
    low=[min(v[k] for v in vertices) for k in range(3)];high=[max(v[k] for v in vertices) for k in range(3)]
    result=inspect([[vertices[i] for i in tri] for tri in indexes],[b-a for a,b in zip(low,high)],part.get('cad_volume_mm3'))
    if indexed:result.update(indexed_topology(vertices,indexes))
    return result


def weld_part(part):
    """Share exactly identical coordinates within one region; never move vertices."""
    part_check(part,indexed=False)
    lookup={};vertices=[];remap=[]
    for vertex in part['vertices_mm']:
        key=tuple(vertex)
        if key not in lookup:lookup[key]=len(vertices);vertices.append(list(vertex))
        remap.append(lookup[key])
    result={**part,'vertices_mm':vertices,'triangles':[[remap[i] for i in tri] for tri in part['triangles']]}
    part_check(result)
    return result


def export_bundle(data,directory):
    """Write a new compact folder, preserving one common world frame."""
    directory=Path(directory)
    # Validate inputs before creating outputs; package() validates materials.
    data={**data,'parts':[weld_part(p) for p in data['parts']]}
    checks=[part_check(p) for p in data['parts']]
    if data.get('unit')!='millimeter' or not 2<=len(checks)<=32:raise ValueError('Expected 2–32 millimeter regions.')
    directory.mkdir(parents=True,exist_ok=False)
    result=package(data,directory/'assembly.3mf');files=[]
    for index,(part,expected) in enumerate(zip(data['parts'],checks),1):
        label=re.sub(r'[^A-Za-z0-9_-]+','-',part['name']).strip('-')[:60] or 'region'
        path=directory/(str(index).zfill(2)+'-'+label+'.stl')
        with path.open('xb') as stream:
            stream.write(b'Common assembly frame; millimeter coordinates'.ljust(80,b' '))
            stream.write(struct.pack('<I',len(part['triangles'])))
            for triangle in part['triangles']:
                stream.write(struct.pack('<12fH',0,0,0,*[v for i in triangle for v in part['vertices_mm'][i]],0))
        checked=validate(path,expected['size_mm'],part.get('cad_volume_mm3',expected['volume_mm3']))
        if any(abs(a-b)>.01 for actual,wanted in zip(checked['bounds_mm'],expected['bounds_mm']) for a,b in zip(actual,wanted)):raise RuntimeError('STL changed world placement.')
        files.append({'file':path.name,'name':part['name'],'material':part['material'],'mesh':checked})
    result.update(stls=files,unit='millimeter',coordinate_frame='root assembly world',slicer_import_verified=False,physical_print_verified=False)
    (directory/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result


def package(data,destination):
    parts=[weld_part(p) for p in data['parts']];destination=Path(destination)
    if data.get('unit')!='millimeter' or not 2<=len(parts)<=32:raise ValueError('Multi-part print requires 2–32 regions in a common millimeter frame.')
    if len({p['name'] for p in parts})!=len(parts):raise ValueError('Print part names must be distinct.')
    before=[]
    for part in parts:
        before.append(part_check(part))
        material=part.get('material',{})
        if not material.get('name') or not re.fullmatch(r'#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?',material.get('color','')):raise ValueError('Each region needs a material label and #RRGGBB or #RRGGBBAA color.')
    model=ET.Element(tag('model'),{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'})
    ET.SubElement(model,tag('metadata'),{'name':'Application'}).text='Fusion portable skill'
    resources=ET.SubElement(model,tag('resources'));materials=ET.SubElement(resources,tag('basematerials'),{'id':'1'})
    for part in parts:ET.SubElement(materials,tag('base'),{'name':part['material']['name'],'displaycolor':part['material']['color']})
    for index,part in enumerate(parts):
        obj=ET.SubElement(resources,tag('object'),{'id':str(index+2),'type':'model','name':part['name'],'pid':'1','pindex':str(index)})
        mesh=ET.SubElement(obj,tag('mesh'));vertices=ET.SubElement(mesh,tag('vertices'));triangles=ET.SubElement(mesh,tag('triangles'))
        for vertex in part['vertices_mm']:ET.SubElement(vertices,tag('vertex'),dict(zip(('x','y','z'),(format(v,'.17g') for v in vertex))))
        for triangle in part['triangles']:ET.SubElement(triangles,tag('triangle'),dict(zip(('v1','v2','v3'),map(str,triangle))))
    group_id=str(len(parts)+2)
    components=ET.SubElement(ET.SubElement(resources,tag('object'),{'id':group_id,'type':'model','name':'Multi-part assembly'}),tag('components'))
    for index in range(len(parts)):ET.SubElement(components,tag('component'),{'objectid':str(index+2)})
    ET.SubElement(ET.SubElement(model,tag('build')),tag('item'),{'objectid':group_id})
    xml=ET.tostring(model,encoding='utf-8',xml_declaration=True)
    with destination.open('xb') as stream:
        with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
            archive.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
            archive.writestr('3D/3dmodel.model',xml)
    reread=read_parts(destination)
    if len(reread)!=len(parts):raise RuntimeError('Packaged part count differs.')
    for source,check,expected in zip(parts,reread,before):
        if source['name']!=check['name'] or part_check(check)!=expected or source['material']!=check['material']:raise RuntimeError('Packaged regions lost geometry, labels, placement or material metadata.')
    return {'file':str(destination.resolve()),'part_count':len(parts),'parts':[{'name':part['name'],'material':part['material'],'mesh':check} for part,check in zip(parts,before)],'relative_placement_verified':True,'slicer_extruder_assignment_verified':False,'overlap_or_material_compatibility_checked':False}


def read_parts(path):
    model=model_xml(path)
    if model.get('unit')!='millimeter':raise ValueError('3MF must declare millimeters.')
    resources=model.find(tag('resources'));objects={obj.get('id'):obj for obj in resources.findall(tag('object'))}
    bases={obj.get('id'):obj for obj in resources.findall(tag('basematerials'))};parts=[];count=0
    def walk(identifier,stack,transforms):
        nonlocal count
        count+=1
        if count>256 or len(stack)>32 or identifier in stack:raise ValueError('Cyclic or excessive 3MF component hierarchy.')
        obj=objects[identifier];mesh=obj.find(tag('mesh'))
        if mesh is not None:
            vertices=[]
            for node in mesh.find(tag('vertices')):
                p=[float(node.get(k)) for k in ('x','y','z')]
                for matrix in reversed(transforms):p=[sum(p[j]*matrix[j*3+i] for j in range(3))+matrix[9+i] for i in range(3)]
                vertices.append(p)
            triangles=[[int(node.get(k)) for k in ('v1','v2','v3')] for node in mesh.find(tag('triangles'))]
            material={}
            if obj.get('pid') in bases:
                base=list(bases[obj.get('pid')])[int(obj.get('pindex','0'))];material={'name':base.get('name'),'color':base.get('displaycolor')}
            part={'name':obj.get('name','part-'+identifier),'vertices_mm':vertices,'triangles':triangles,'material':material};part_check(part);parts.append(part)
        else:
            for component in obj.find(tag('components')):
                matrix=[float(v) for v in component.get('transform','1 0 0 0 1 0 0 0 1 0 0 0').split()]
                if len(matrix)!=12 or not all(math.isfinite(v) for v in matrix):raise ValueError('Invalid component transform.')
                walk(component.get('objectid'),stack+[identifier],transforms+[matrix])
    for item in model.find(tag('build')):
        matrix=[float(v) for v in item.get('transform','1 0 0 0 1 0 0 0 1 0 0 0').split()]
        if len(matrix)!=12 or not all(math.isfinite(v) for v in matrix):raise ValueError('Invalid build transform.')
        walk(item.get('objectid'),[],[matrix])
    return parts


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest');p.add_argument('destination')
    args=p.parse_args();data=strict_json(Path(args.manifest).read_text(encoding='utf-8'));print(json.dumps(package(data,args.destination),indent=2))

if __name__=='__main__':main()
