"""Offline input and export validation; no CAD connection."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'fusion-360-mcp'/'scripts'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'devtools'))
import ast,json,tempfile,unittest,zipfile
from pathlib import Path
from contracts import geometry_expectations
from parameters import build_script
from measure_geometry import build_script as measurement
from mesh_conversion import convert,obj_triangles
from validate_mesh import inspect,stl_triangles,mf_triangles

VERTICES=[(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)]
FACES=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
TRIANGLES=[[VERTICES[i] for i in face] for face in FACES]

class ContractTests(unittest.TestCase):
    def test_bad_geometry_expectations_rejected(self):
        for e in ({'body_count':True},{'body_count':-1},{'size_mm':[1,2]},{'size_mm':[1,2,float('nan')]},{'volume_mm3':float('inf')},{'anything':1}):
            with self.subTest(e=e),self.assertRaises(ValueError):geometry_expectations(e)
    def test_parameter_arguments_remain_data(self):
        name="doc'\nraise Exception('injected')"
        script=build_script(name,{'width':'2 * length'})
        tree=ast.parse(script)
        node=next(n for n in tree.body if isinstance(n,ast.Assign) and n.targets[0].id=='C')
        config=json.loads(ast.literal_eval(node.value.args[0]))
        self.assertEqual(config['document'],name)
        self.assertEqual(config['changes'],{'width':'2 * length'})
    def test_selector_contract(self):
        for selectors in ([{'name':'a'}],[{'name':1},{'name':'b'}],[{'name':'a','bad':1},{'name':'b'}]):
            with self.subTest(selectors=selectors),self.assertRaises(ValueError):measurement('Doc',selectors)
    def test_cube_geometry(self):
        result=inspect(TRIANGLES,[1,1,1],1)
        self.assertAlmostEqual(result['volume_mm3'],1)
        self.assertEqual(result['euler_characteristic'],2)
    def test_bad_mesh_rejected(self):
        variants=[TRIANGLES[:-1],TRIANGLES+[TRIANGLES[0]],[[VERTICES[i] for i in reversed(FACES[0])]]+TRIANGLES[1:], [[(float('nan'),0,0),(0,1,0),(0,0,1)]]]
        for triangles in variants:
            with self.subTest(triangles=triangles),self.assertRaises(RuntimeError):inspect(triangles,[1,1,1],1)
    def test_scale_and_nonfinite_expectations_rejected(self):
        with self.assertRaises(RuntimeError):inspect(TRIANGLES,[10,10,10],1)
        with self.assertRaises(ValueError):inspect(TRIANGLES,[1,1,1],float('nan'))
    def test_truncated_stl_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'broken.stl';path.write_bytes(b'broken')
            with self.assertRaisesRegex(RuntimeError,'Truncated'):stl_triangles(path)
    def test_obj_roundtrip_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'cube.3mf';destination=source.with_suffix('.obj')
            vertices=''.join('<vertex x="%s" y="%s" z="%s"/>'%v for v in VERTICES)
            triangles=''.join('<triangle v1="%s" v2="%s" v3="%s"/>'%f for f in FACES)
            model='<model xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" unit="millimeter"><resources><object id="1"><mesh><vertices>'+vertices+'</vertices><triangles>'+triangles+'</triangles></mesh></object></resources><build><item objectid="1"/></build></model>'
            with zipfile.ZipFile(source,'w') as archive:archive.writestr('3D/3dmodel.model',model)
            result=convert(source,destination,[1,1,1],1)
            self.assertEqual(result['mesh']['triangles'],12)
            self.assertEqual(obj_triangles(destination),TRIANGLES)
            with self.assertRaises(FileExistsError):convert(source,destination,[1,1,1],1)

if __name__=='__main__':unittest.main(verbosity=2)
