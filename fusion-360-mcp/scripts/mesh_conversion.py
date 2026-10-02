"""Convert one validated millimeter 3MF mesh to a plain triangle OBJ."""
import argparse,json
from pathlib import Path
from validate_mesh import mf_triangles,inspect


def obj_triangles(path):
    vertices=[];triangles=[]
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        fields=line.split()
        if not fields or fields[0].startswith('#'):continue
        if fields[0]=='v':
            if len(fields)!=4:raise ValueError('Only XYZ vertices are supported.')
            vertices.append(tuple(float(v) for v in fields[1:]))
        elif fields[0]=='f':
            if len(fields)!=4:raise ValueError('Only triangle faces are supported.')
            indexes=[int(v.split('/')[0]) for v in fields[1:]]
            if any(index<=0 or index>len(vertices) for index in indexes):raise ValueError('Unsupported OBJ vertex index.')
            triangles.append([vertices[index-1] for index in indexes])
    return triangles


def convert(source,destination,size_mm,volume_mm3=None):
    source=Path(source);destination=Path(destination)
    if source.suffix.lower()!='.3mf' or destination.suffix.lower()!='.obj':raise ValueError('Convert millimeter 3MF to OBJ.')
    triangles,vertices,indexes=mf_triangles(source)
    before=inspect(triangles,size_mm,volume_mm3)
    # Exclusive creation also protects against an overwrite race.
    with destination.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write('# Coordinates are millimeters. OBJ itself has no declared length unit.\n')
        for vertex in vertices:stream.write('v '+' '.join(format(v,'.17g') for v in vertex)+'\n')
        for triangle in indexes:stream.write('f '+' '.join(str(i+1) for i in triangle)+'\n')
    after=inspect(obj_triangles(destination),size_mm,volume_mm3)
    if before!=after:raise RuntimeError('OBJ conversion changed mesh geometry; retain file for inspection.')
    return {'file':str(destination.resolve()),'coordinate_convention':'millimeters; unitless OBJ format','mesh':after,'self_intersections_checked':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source');parser.add_argument('destination')
    parser.add_argument('--size-mm',type=float,nargs=3,required=True)
    parser.add_argument('--volume-mm3',type=float)
    args=parser.parse_args();print(json.dumps(convert(args.source,args.destination,args.size_mm,args.volume_mm3),indent=2))

if __name__=='__main__':main()
