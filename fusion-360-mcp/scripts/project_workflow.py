"""Reusable rounded hex-organizer workflow: build, verify, style and deliver once.

Writes only run.json and actions.jsonl as working records on success. A recovery
archive persists on failure. No generated Python/API dump or scene-setting calls.
"""
import argparse,json,time,math,hashlib
from pathlib import Path
from organizer import build_script,validate_config
from project_tools import prepare_paths,export_script,appearance_script,preview_script
from fit_coupon import coupon_script
from validate_mesh import validate,mf_triangles
from mcp_client import FusionClient

def functional_check(path,layout):
    _,vertices,_=mf_triangles(Path(path))
    height=layout['base'][3]+layout['rack'][5]
    af=layout['socket_af'];lead=layout['lead_in']
    for cx,cy in layout['centers']:
        for z,expected in [(height-layout['socket_depth'],af),(height,af+2*lead)]:
            radius=expected/math.sqrt(3)
            points=set((x,y) for x,y,h in vertices if abs(h-z)<1e-4 and math.hypot(x-cx,y-cy)<radius+0.05)
            if len(points)!=6:raise RuntimeError('Unexpected exported socket section.')
            for angle in [math.pi/6,math.pi/2,5*math.pi/6]:
                ps=[x*math.cos(angle)+y*math.sin(angle) for x,y in points]
                if abs(max(ps)-min(ps)-expected)>1e-4:raise RuntimeError('Exported socket fit differs.')
    x,y,w,h,_,depth=layout['tray']
    floor=min(z for vx,vy,z in vertices if x<=vx<=x+w and y<=vy<=y+h and z>0)
    if abs(floor-(layout['base'][3]-depth))>1e-4:raise RuntimeError('Exported tray floor differs.')
    return {'socket_sections_verified':len(layout['centers']),'tray_floor_mm':floor}

def print_notes(layout,stem,sizes):
    w,h,_,bh=layout['base'];height=bh+layout['rack'][5]
    tray=layout['tray'];floor=bh-tray[5]
    coupon=('Fit coupon: notch at bottom-left when viewed from above; sizes left-to-right '
            +', '.join(str(x)+' mm' for x in sizes)+' across flats. Print and test with your bits first.\n') if sizes else ''
    return f'''# {stem} print notes

Size: {w} x {h} x {height} mm. One solid; flat base on build plate.
Hex sockets: {layout['socket_af']} mm across flats, {layout['socket_depth']} mm deep,
{layout['lead_in']} mm entry bevel. Tray: {tray[2]} x {tray[3]} mm, {tray[5]} mm deep;
floor {floor} mm. Dimensions/feature health and exported mesh/critical sections checked.

{coupon}
CAD: ../cad/{stem}.f3d. Print: ../print/{stem}.3mf, millimeter units.
Images are Fusion viewport previews, not ray-traced renders. Appearance colors are
presentation only; this is one print body, without material assignments for a slicer.
Vertical features have named parameters; horizontal sketch coordinates are not fully
constrained for interactive resizing. Rerun the layout recipe for changed dimensions.

Starting FFF trial: 0.4 mm nozzle, 0.2 mm layers, three perimeters, 20-30% infill,
PLA/PETG as appropriate. Adjust for your machine and inspect the slicer preview.
No physical fit/strength test performed; mesh checks do not prove every geometric
self-intersection is absent. No Fusion cloud save was made.
'''

def run(layout,document,output_dir,work_dir,stem,coupon_sizes=None,parametric=False):
    start=time.perf_counter()
    if parametric:
        from parametric_organizer import layout as resolve_layout,build_script as native_build
        parameters=layout
        layout=resolve_layout(parameters)
    validate_config(layout)
    # Validate generators before connecting or creating a document.
    build=native_build(parameters,document) if parametric else build_script(layout,document)
    exports=export_script(document,output_dir,stem)
    paths,work=prepare_paths(output_dir,work_dir)
    expected_files=[paths['cad']/(stem+'.f3d'),paths['print']/(stem+'.3mf'),paths['images']/(stem+'-preview.png'),paths['docs']/'PRINT-NOTES.md']
    if coupon_sizes:expected_files.append(paths['print']/'fit-tests/socket-fit-coupon.3mf')
    if any(p.exists() for p in expected_files) or (work/'run.json').exists():raise RuntimeError('Output/run exists; choose a revision or clean up explicitly.')
    coupon=coupon_script(document,expected_files[-1],coupon_sizes) if coupon_sizes else None
    recovery=work/'recovery'
    (recovery/'cad').mkdir(parents=True,exist_ok=True)
    recovery_file=recovery/'cad/recovery.f3d'
    if recovery_file.exists():raise RuntimeError('Prior recovery exists; inspect before replay.')
    c=FusionClient(work)
    stages=[]
    def execute(name,script):
        result=c.execute(script)
        stages.append({'stage':name,'mcp_seconds':c.last_rpc_seconds,'result':result})
        return result
    model=execute('build_and_verify',build)
    execute('recovery_export',export_script(document,recovery,'recovery',('f3d',)))
    execute('appearance',appearance_script(document))
    execute('final_exports',exports)
    execute('viewport_preview',preview_script(document,paths['images']/(stem+'-preview.png')))
    coupon_result=execute('fit_coupon',coupon) if coupon else None
    verification=validate(paths['print']/(stem+'.3mf'),model['size_mm'],model['volume_mm3'])
    verification['functional']=functional_check(paths['print']/(stem+'.3mf'),layout)
    if coupon:
        verification['coupon']=validate(expected_files[-1],coupon_result['size_mm'],coupon_result['volume_mm3'])
    notes=print_notes(layout,stem,coupon_sizes)
    if parametric:
        notes=notes.replace('Vertical features have named parameters; horizontal sketch coordinates are not fully\nconstrained for interactive resizing. Rerun the layout recipe for changed dimensions.',
            'Native parametric model: all five driving sketches are fully constrained. Edit\noverall_width, overall_length, overall_height, socket_pitch or socket_af in Fusion\nModify > Change Parameters. Socket rows/columns/count are derived automatically.\nKeep values within the documented supported range; invalid dimensions can fail features.')
    expected_files[3].write_text(notes,encoding='utf-8')
    result={'status':'verified','run_id':work.name,'document':document,'layout':layout,'build_source_sha256':hashlib.sha256(build.encode()).hexdigest(),
        'stages':stages,'mesh_verification':verification,'deliverables':[str(p) for p in expected_files],
        'connection_setup_seconds':c.setup_seconds,'mcp_execution_verification_seconds':sum(s['mcp_seconds'] for s in stages),
        'in_fusion_seconds':sum(s['result'].get('fusion_execution_verification_seconds',0) for s in stages),
        'runner_seconds':time.perf_counter()-start,'scope':'Runner excludes assistant thinking/research/response writing; includes setup, local mesh verification and exports.',
        'cloud_saved':False,'render_type':'viewport','native_parametric':parametric}
    (work/'run.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    # After verified delivery, the exported native file supersedes the temporary checkpoint.
    recovery_file.unlink();(recovery/'cad').rmdir();recovery.rmdir()
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--layout',required=True)
    p.add_argument('--document',required=True)
    p.add_argument('--output-dir',required=True)
    p.add_argument('--work-dir',required=True)
    p.add_argument('--stem',default='organizer')
    p.add_argument('--coupon-sizes-mm',type=float,nargs='+')
    p.add_argument('--parametric',action='store_true',help='Layout file contains primary parameters; use native constrained sketches/patterns.')
    a=p.parse_args()
    r=run(json.loads(Path(a.layout).read_text(encoding='utf-8')),a.document,a.output_dir,a.work_dir,a.stem,a.coupon_sizes_mm,a.parametric)
    print(json.dumps({k:r[k] for k in ['status','document','mcp_execution_verification_seconds','in_fusion_seconds','runner_seconds','deliverables']},indent=2))

if __name__=='__main__':main()
