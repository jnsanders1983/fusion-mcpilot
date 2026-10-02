"""Offline feature-contract tests; never connects to a CAD server."""
import ast
import unittest
from feature_recipes import RECIPES,validate,build_script

class FeatureTests(unittest.TestCase):
    def test_defaults_compile(self):
        for name in RECIPES:
            with self.subTest(name=name):ast.parse(build_script(name,{},'Test','test-owner'))
    def test_invalid_controls(self):
        cases=[('box',{'width':True}),('box',{'width':float('nan')}),('box',{'radius':1}),('filleted_box',{'radius':25}),('chamfered_box',{'chamfer':30}),('open_box',{'wall':25}),('boolean_union',{'offset':45}),('hole_plate',{'columns':2.5}),('hole_plate',{'pitch':35}),('hole_plate',{'diameter':12}),('loft_block',{'top_scale':3}),('revolved_tube',{'inner_radius':18})]
        for name,p in cases:
            with self.subTest(name=name,p=p),self.assertRaises(ValueError):validate(name,p)
    def test_arguments_are_literal(self):
        script=build_script('box',{},"bad'\nraise Exception('injected')",'owner')
        ast.parse(script)
        self.assertIn("json.loads(",script)
    def test_circular_pattern_limits(self):
        for p in ({'count':2.5},{'count':1},{'count':51},{'pattern_radius':25},{'diameter':15,'count':20}):
            with self.subTest(p=p),self.assertRaises(ValueError):validate('circular_hole_flange',p)

if __name__=='__main__':unittest.main(verbosity=2)
