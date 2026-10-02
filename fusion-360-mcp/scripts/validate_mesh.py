"""Check a single-solid binary STL or millimeter 3MF export; Python stdlib.

Rejects unhandled 3MF assembly instances/transforms rather than silently flattening.
Edge incidence and winding checks do not prove absence of self-intersections.
STL has no declared unit: expected millimeter dimensions are mandatory.
"""
from pathlib import Path
from collections import Counter,defaultdict
import struct,json,zipfile,xml.etree.ElementTree as ET,math,argparse
from safe_data import model_xml,MAX_ARCHIVE_BYTES
def indexed_topology(vertices,indexes):
    """3MF adjacency is defined by shared vertex indices, not nearby positions."""
    edges=Counter();directions=Counter()
    for tri in indexes:
        if len(tri)!=3 or any(type(i) is not int or not 0<=i<len(vertices) for i in tri) or len(set(tri))!=3:raise RuntimeError('Invalid indexed triangle.')
        for a,b in zip(tri,tri[1:]+tri[:1]):
            edges[tuple(sorted((a,b)))]+=1;directions[(a,b)]+=1
    opened=sum(n==1 for n in edges.values());nonmanifold=sum(n>2 for n in edges.values())
    if opened or nonmanifold:raise RuntimeError('Indexed mesh is not manifold: '+str(opened)+' open edges, '+str(nonmanifold)+' nonmanifold edges.')
    if any(directions[(a,b)]!=directions[(b,a)] for a,b in directions):raise RuntimeError('Indexed mesh has inconsistent winding.')
    return {'indexed_open_edges':opened,'indexed_nonmanifold_edges':nonmanifold,'indexed_winding_verified':True}

def inspect(triangles,expected_size,expected_volume=None):
    if len(expected_size)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in expected_size):raise ValueError('Three positive finite millimeter dimensions required.')
    if expected_volume is not None and (type(expected_volume) not in (int,float) or not math.isfinite(expected_volume) or expected_volume<=0):raise ValueError('Expected volume must be positive and finite.')
    edges=Counter()
    directions=Counter()
    verts=set()
    signed_volume=0
    adjacency=defaultdict(set)
    for tri in triangles:
        if len(tri)!=3 or any(len(p)!=3 or any(not math.isfinite(v) for v in p) for p in tri):raise RuntimeError('Triangle coordinates must be finite XYZ values.')
        keys=[tuple(p) for p in tri]
        if len(set(keys))!=3:raise RuntimeError('Degenerate triangle.')
        verts.update(keys)
        a,b,c=tri
        u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
        area_cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        if sum(v*v for v in area_cross)<=1e-20:raise RuntimeError('Zero-area triangle.')
        cross=(b[1]*c[2]-b[2]*c[1],b[2]*c[0]-b[0]*c[2],b[0]*c[1]-b[1]*c[0])
        signed_volume+=sum(x*y for x,y in zip(a,cross))/6
        for u,v in zip(keys,keys[1:]+keys[:1]):
            edges[tuple(sorted((u,v)))]+=1
            directions[(u,v)]+=1
            adjacency[u].add(v);adjacency[v].add(u)
    if not verts:raise RuntimeError('Empty mesh.')
    if any(n!=2 for n in edges.values()):raise RuntimeError('Non-watertight or non-manifold mesh.')
    if any(directions[(u,v)]!=directions[(v,u)] for u,v in directions):raise RuntimeError('Inconsistent winding.')
    remaining=set(verts)
    components=0
    while remaining:
        components+=1
        stack=[remaining.pop()]
        while stack:
            for v in adjacency[stack.pop()]:
                if v in remaining:remaining.remove(v);stack.append(v)
    if components!=1:raise RuntimeError('Unexpected disconnected mesh.')
    low=[min(p[i] for p in verts) for i in range(3)]
    high=[max(p[i] for p in verts) for i in range(3)]
    sizes=[b-a for a,b in zip(low,high)]
    if any(abs(a-b)>0.01 for a,b in zip(sizes,expected_size)):raise RuntimeError('Wrong millimeter scale.')
    if signed_volume<=0:raise RuntimeError('Negative/zero oriented mesh volume.')
    if expected_volume and abs(signed_volume-expected_volume)/expected_volume>0.001:raise RuntimeError('Mesh volume differs excessively from CAD.')
    return {'triangles':len(triangles),'vertices':len(verts),'size_mm':sizes,'bounds_mm':[low,high],
        'watertight_edge_incidence':True,'consistent_winding':True,'connected_components':components,
        'volume_mm3':signed_volume,'euler_characteristic':len(verts)-len(edges)+len(triangles)}

def stl_triangles(p):
    if p.stat().st_size>MAX_ARCHIVE_BYTES:raise ValueError('STL exceeds mesh size limit.')
    raw=p.read_bytes()
    if len(raw)<84:raise RuntimeError('Truncated binary STL header.')
    count=struct.unpack_from('<I',raw,80)[0]
    if len(raw)!=84+50*count:raise RuntimeError('Invalid binary STL size.')
    values=[struct.unpack_from('<12fH',raw,84+50*i) for i in range(count)]
    return [[tuple(row[3+j*3:6+j*3]) for j in range(3)] for row in values]

def mf_triangles(p):
    model=model_xml(p)
    ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
    if model.get('unit')!='millimeter':raise RuntimeError('3MF must explicitly use millimeters.')
    items=model.findall('m:build/m:item',ns)
    if len(items)!=1:raise RuntimeError('Expected one 3MF build item.')
    item=items[0]
    if item.get('transform') not in (None,'1 0 0 0 1 0 0 0 1 0 0 0'):
        raise RuntimeError('Unexpected 3MF instance transform requires explicit handling.')
    objects=model.findall('m:resources/m:object',ns)
    matches=[o for o in objects if o.get('id')==item.get('objectid')]
    if len(matches)!=1:raise RuntimeError('3MF build references a missing or ambiguous mesh object.')
    obj=matches[0]
    v=[tuple(float(p.get(k)) for k in ('x','y','z')) for p in obj.findall('m:mesh/m:vertices/m:vertex',ns)]
    indexes=[tuple(int(p.get(k)) for k in ('v1','v2','v3')) for p in obj.findall('m:mesh/m:triangles/m:triangle',ns)]
    if not v or not indexes or any(i<0 or i>=len(v) for inds in indexes for i in inds):raise RuntimeError('3MF requires a nonempty direct mesh with valid vertex indexes.')
    indexed_topology(v,indexes)
    return [[v[i] for i in inds] for inds in indexes],v,indexes

def validate(path,size_mm,volume_mm3=None):
    path=Path(path)
    if path.suffix.lower()=='.3mf':triangles,_,_=mf_triangles(path)
    elif path.suffix.lower()=='.stl':triangles=stl_triangles(path)
    else:raise ValueError('Only millimeter 3MF and binary STL are supported.')
    result=inspect(triangles,size_mm,volume_mm3)
    result['declared_unit']='millimeter' if path.suffix.lower()=='.3mf' else 'none; scale checked against expected millimeters'
    result['self_intersections_checked']=False
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mesh')
    p.add_argument('--size-mm',type=float,nargs=3,required=True)
    p.add_argument('--volume-mm3',type=float)
    p.add_argument('--report',help='Optional report path in the working/log directory.')
    args=p.parse_args()
    result=validate(args.mesh,args.size_mm,args.volume_mm3)
    if args.report:Path(args.report).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
