import ast, importlib.util, io, json, os, pathlib, tempfile, unittest
from unittest.mock import patch
import sys
scripts=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(scripts))
from run_primitive import build_script
from mcp_client import FusionClient, connection_settings

class ConfigurationTests(unittest.TestCase):
    def test_url_needs_no_host_installation(self):
        with patch.dict(os.environ, {'FUSION_MCP_URL': 'http://localhost:1234/mcp'}, clear=True):
            server, source = connection_settings()
            self.assertEqual(server['url'], 'http://localhost:1234/mcp')
            self.assertEqual(source, 'FUSION_MCP_URL')
    def test_external_json_and_precedence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp)/'fusion.json'
            path.write_text(json.dumps({'url':'http://localhost:5678/mcp','env_http_headers':{'X-Key':'MY_KEY'}}))
            with patch.dict(os.environ, {'FUSION_MCP_CONFIG':str(path)}, clear=True):
                server, source = connection_settings()
                self.assertEqual(server['env_http_headers'], {'X-Key':'MY_KEY'})
            with patch.dict(os.environ, {'FUSION_MCP_CONFIG':str(path),'FUSION_MCP_URL':'http://localhost:9012/mcp'}, clear=True):
                self.assertEqual(connection_settings()[0]['url'],'http://localhost:9012/mcp')
    def test_explicit_bad_config_never_falls_back(self):
        with patch.dict(os.environ, {'FUSION_MCP_CONFIG':'missing-fusion-config.json'}, clear=True):
            with self.assertRaises(FileNotFoundError): connection_settings()
    def test_invalid_endpoint_and_timeout(self):
        for url in ('file:///tmp/test','http://secret:password@localhost/mcp','http://localhost/mcp#fragment'):
            with self.subTest(url=url), patch.dict(os.environ, {'FUSION_MCP_URL':url}, clear=True):
                with self.assertRaises(ValueError): connection_settings()
        for value in ('0', '-1', 'nan', 'inf'):
            with self.subTest(timeout=value), patch.dict(os.environ, {'FUSION_MCP_URL':'http://localhost/mcp','FUSION_MCP_TIMEOUT_SEC':value}, clear=True):
                with self.assertRaises(ValueError): connection_settings()
from inspect_design import build_inspection

class RecipeTests(unittest.TestCase):
    def test_parameters_are_data(self):
        text=build_script('sphere',{'radius':22},"name'\nraise RuntimeError('injection')",'Test')
        tree=ast.parse(text)
        values={n.targets[0].id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)}
        self.assertEqual(values['REPLACE_BODY'],"name'\nraise RuntimeError('injection')")
        self.assertEqual(values['DIMENSIONS_MM'],{'radius':22})
    def test_invalid_geometry_rejected_locally(self):
        cases=[('sphere',{'radius':-1}),('sphere',{'radius':float('nan')}),('sphere',{'radius':True}),
               ('torus',{'major_radius':4,'tube_radius':5}),('frustum',{'base_radius':4,'top_radius':-1,'height':10}),
               ('frustum',{'base_radius':4,'top_radius':2,'height':0}),('sphere',{'radius':2,'height':3})]
        for shape,dims in cases:
            with self.subTest(shape=shape,dims=dims),self.assertRaises(ValueError): build_script(shape,dims)
    def test_cone_and_cylinder_supported(self):
        for top in (0,15): ast.parse(build_script('frustum',{'base_radius':15,'top_radius':top,'height':40}))
    def test_checks_survive_optimized_python(self):
        tree=ast.parse(build_script('sphere',{'radius':12}))
        self.assertFalse(any(isinstance(node,ast.Assert) for node in ast.walk(tree)))
        compile(tree,'recipe','exec',optimize=2)
    def test_inspection_target_is_literal(self):
        target="doc'\nraise Exception('injection')"
        tree=ast.parse(build_inspection(target))
        node=next(n for n in tree.body if isinstance(n,ast.Assign))
        self.assertEqual(ast.literal_eval(node.value),target)

class Response:
    def __init__(self,body,content_type='application/json',session=None):
        self.body=body.encode();self.stream=io.BytesIO(self.body);self.headers={'Content-Type':content_type}
        if session:self.headers['Mcp-Session-Id']=session
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,size=-1):return self.stream.read(size)
    def readline(self,size=-1):return self.stream.readline(size)
    def __iter__(self):return iter(self.body.splitlines(keepends=True))

class ClientTests(unittest.TestCase):
    def setup_client(self,temp,responses):
        config=pathlib.Path(temp)/'config.toml'
        config.write_text('[mcp_servers.fusion360]\nurl="http://127.0.0.1:27182/mcp"\n')
        self.calls=[]
        def opener(request,timeout):
            self.calls.append(json.loads(request.data))
            reply=responses.pop(0)
            if isinstance(reply,BaseException):raise reply
            return reply
        base_env={key:os.environ[key] for key in ('SYSTEMROOT','WINDIR','SystemRoot') if key in os.environ}
        self.env=patch.dict(os.environ,{**base_env,'CODEX_HOME':temp},clear=True)
        self.net=patch('urllib.request.OpenerDirector.open',side_effect=opener)
        self.env.start();self.net.start()
        self.addCleanup(self.env.stop);self.addCleanup(self.net.stop)
        return FusionClient(pathlib.Path(temp)/'logs')
    def init_responses(self):
        return [Response(json.dumps({'jsonrpc':'2.0','id':1,'result':{'protocolVersion':'2024-11-05','serverInfo':{'name':'test'}}}),session='test-session'),Response('')]
    def test_sse_matches_id_ignores_notifications(self):
        with tempfile.TemporaryDirectory() as tmp:
            replies=self.init_responses()+[Response('event: message\ndata: {"jsonrpc":"2.0","method":"notice"}\n\nevent: message\ndata: {"jsonrpc":"2.0","id":3,"result":{"ok":true}}\n\n','text/event-stream')]
            client=self.setup_client(tmp,replies)
            result=client.rpc('tools/list')
            self.assertTrue(result['result']['ok'])
            self.assertEqual(client.headers['Mcp-Session-Id'],'test-session')
    def test_mutation_error_is_not_replayed(self):
        with tempfile.TemporaryDirectory() as tmp:
            outer={'success':False,'error':'intentional test'}
            replies=self.init_responses()+[Response(json.dumps({'jsonrpc':'2.0','id':3,'result':{'content':[{'type':'text','text':json.dumps(outer)}]}}))]
            client=self.setup_client(tmp,replies)
            with self.assertRaises(RuntimeError):client.execute('def run(c): pass')
            self.assertEqual(len(self.calls),3)
            logs=[json.loads(line) for line in (pathlib.Path(tmp)/'logs/actions.jsonl').read_text().splitlines()]
            self.assertEqual(logs[-1]['outcome'],'unconfirmed')
            self.assertTrue(any(row['event']=='fusion_dispatch' for row in logs))
    def test_mismatched_response_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            client=self.setup_client(tmp,self.init_responses()+[Response('{"id":100,"result":{}}')])
            with self.assertRaises(RuntimeError):client.rpc('tools/list')
            self.assertEqual(len(self.calls),3)
    def test_lost_mutation_reply_is_not_replayed(self):
        with tempfile.TemporaryDirectory() as tmp:
            client=self.setup_client(tmp,self.init_responses()+[TimeoutError('Lost response after dispatch')])
            with self.assertRaises(TimeoutError):client.execute('def run(c): pass')
            self.assertEqual(len(self.calls),3)
            rows=[json.loads(x) for x in (pathlib.Path(tmp)/'logs/actions.jsonl').read_text().splitlines()]
            self.assertEqual(rows[-1]['outcome'],'unconfirmed')
    def test_malformed_reply_is_not_replayed(self):
        with tempfile.TemporaryDirectory() as tmp:
            client=self.setup_client(tmp,self.init_responses()+[Response('{"id":3,"result":')])
            with self.assertRaises(json.JSONDecodeError):client.execute('def run(c): pass')
            self.assertEqual(len(self.calls),3)
    def test_completed_native_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            outer={'success':True,'message':json.dumps({'ok':True,'volume_mm3':1234})}
            response={'id':3,'result':{'content':[{'type':'text','text':json.dumps(outer)}]}}
            client=self.setup_client(tmp,self.init_responses()+[Response(json.dumps(response))])
            self.assertEqual(client.execute('def run(c): pass')['volume_mm3'],1234)
    def test_empty_success_is_unconfirmed_and_logged(self):
        with tempfile.TemporaryDirectory() as tmp:
            outer={'success':True,'message':''}
            response={'id':3,'result':{'content':[{'type':'text','text':json.dumps(outer)}]}}
            client=self.setup_client(tmp,self.init_responses()+[Response(json.dumps(response))])
            with self.assertRaisesRegex(RuntimeError,'no structured script result'):client.execute('def run(c): pass')
            self.assertEqual(len(self.calls),3)
            rows=[json.loads(line) for line in (pathlib.Path(tmp)/'logs/actions.jsonl').read_text().splitlines()]
            protocol=next(row for row in rows if row['event']=='fusion_protocol_error')
            self.assertEqual(protocol['response'],outer)
            self.assertEqual(rows[-1]['outcome'],'unconfirmed')
    def test_native_cad_failure_inside_successful_transport(self):
        with tempfile.TemporaryDirectory() as tmp:
            outer={'success':False,'error':'Feature failed after partial construction'}
            response={'id':3,'result':{'content':[{'type':'text','text':json.dumps(outer)}]}}
            client=self.setup_client(tmp,self.init_responses()+[Response(json.dumps(response))])
            with self.assertRaises(RuntimeError):client.execute('def run(c): pass')
            self.assertEqual(len(self.calls),3)

class MultipartExportTests(unittest.TestCase):
    def fixture(self):
        parts=[]
        for name,offset in [('Nested instance',[-100,20,3]),('Repeated instance',[50,-30,8])]:
            parts.append({'name':name,'vertices_mm':[[x+offset[0],y+offset[1],z+offset[2]] for x,y,z in [[0,0,0],[1,0,0],[0,1,0],[0,0,1]]],
                          'triangles':[[0,2,1],[0,1,3],[0,3,2],[1,2,3]],'cad_volume_mm3':1/6,'material':{'name':'PLA '+name,'color':'#00A0A0'}})
        return {'unit':'millimeter','parts':parts}
    def test_stl_and_3mf_preserve_distinct_world_positions(self):
        from multipart_print import export_bundle,read_parts
        with tempfile.TemporaryDirectory() as tmp:
            result=export_bundle(self.fixture(),pathlib.Path(tmp)/'output')
            reread=read_parts(pathlib.Path(tmp)/'output/assembly.3mf')
            self.assertEqual([r['mesh']['bounds_mm'][0] for r in result['stls']],[[-100,20,3],[50,-30,8]])
            self.assertEqual([p['vertices_mm'] for p in reread],[p['vertices_mm'] for p in self.fixture()['parts']])
            self.assertFalse(result['slicer_import_verified'])
    def test_existing_output_is_not_overwritten(self):
        from multipart_print import export_bundle
        with tempfile.TemporaryDirectory() as tmp:
            directory=pathlib.Path(tmp)/'output';directory.mkdir();sentinel=directory/'keep.txt';sentinel.write_text('preserve')
            with self.assertRaises(FileExistsError):export_bundle(self.fixture(),directory)
            self.assertEqual(sentinel.read_text(),'preserve')
    def test_invalid_triangle_rejected_before_output(self):
        from multipart_print import export_bundle
        with tempfile.TemporaryDirectory() as tmp:
            data=self.fixture();data['parts'][0]['triangles'][0][0]=-1
            directory=pathlib.Path(tmp)/'output'
            with self.assertRaises(ValueError):export_bundle(data,directory)
            self.assertFalse(directory.exists())
    def test_nonmillimeter_manifest_rejected(self):
        from multipart_print import export_bundle
        with tempfile.TemporaryDirectory() as tmp:
            data=self.fixture();data['unit']='inch'
            with self.assertRaises(ValueError):export_bundle(data,pathlib.Path(tmp)/'output')

class MaterialRegionTests(unittest.TestCase):
    def regions(self):return [{'name':'Lower','rgb':[40,40,40]},{'name':'Upper','rgb':[0,160,160]}]
    def test_partition_script_is_valid_and_uses_parametric_expression(self):
        from material_regions import split_script
        script=split_script('Dock',{'name':'Body'},'z','base_height',self.regions())
        ast.parse(script)
        self.assertIn('base_height',script)
    def test_assembly_context_partition_rejected(self):
        from material_regions import split_script
        with self.assertRaises(ValueError):split_script('Dock',{'name':'Body','occurrence_path':'Carrier:1'},'z','8 mm',self.regions())
    def test_unverified_axes_and_invalid_colors_rejected(self):
        from material_regions import split_script
        with self.assertRaises(ValueError):split_script('Dock',{'name':'Body'},'y','8 mm',self.regions())
        regions=self.regions();regions[0]['rgb'][0]=256
        with self.assertRaises(ValueError):split_script('Dock',{'name':'Body'},'z','8 mm',regions)

class IndexedTopologyTests(unittest.TestCase):
    def unwelded(self):
        source=MultipartExportTests().fixture()['parts'][0]
        vertices=[source['vertices_mm'][i] for tri in source['triangles'] for i in tri]
        return {**source,'vertices_mm':vertices,'triangles':[[i,i+1,i+2] for i in range(0,len(vertices),3)]}
    def test_coordinate_closed_but_index_open_is_rejected(self):
        from multipart_print import part_check
        part=self.unwelded()
        part_check(part,indexed=False)
        with self.assertRaisesRegex(RuntimeError,'12 open edges'):part_check(part)
    def test_exact_weld_preserves_every_triangle_coordinate(self):
        from multipart_print import weld_part,part_check
        source=self.unwelded();welded=weld_part(source)
        self.assertEqual([[source['vertices_mm'][i] for i in t] for t in source['triangles']],[[welded['vertices_mm'][i] for i in t] for t in welded['triangles']])
        self.assertEqual(len(welded['vertices_mm']),4)
        self.assertEqual(part_check(welded)['indexed_open_edges'],0)
    def test_small_actual_gap_is_not_hidden_by_rounding(self):
        from multipart_print import weld_part
        part=self.unwelded();part['vertices_mm'][0]=list(part['vertices_mm'][0]);part['vertices_mm'][0][0]+=0.0000001
        with self.assertRaises(RuntimeError):weld_part(part)

class CouponAndMultiBodyContracts(unittest.TestCase):
    def test_coupon_rejects_breakthrough_and_overlapping_pockets(self):
        from hex_fit_coupon import cut_script
        with self.assertRaises(ValueError):cut_script('Coupon',[6.65],depth=9)
        with self.assertRaises(ValueError):cut_script('Coupon',[6.65]*12)
    def test_organizer_rejects_unverified_region_counts(self):
        from parametric_organizer import variants_script
        with self.assertRaises(ValueError):variants_script('Dock',[],expected_body_count=3)

if __name__=='__main__':unittest.main(verbosity=2)
