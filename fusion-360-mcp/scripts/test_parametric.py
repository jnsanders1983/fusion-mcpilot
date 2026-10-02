"""Contract tests for parametric layout limits and generated native scripts."""
import unittest,math
from parametric_organizer import layout,build_script,variants_script

class ParametricTests(unittest.TestCase):
    def test_default_count(self):self.assertEqual(len(layout({})['centers']),12)
    def test_one_row_two_columns(self):self.assertEqual(len(layout({'overall_width':36,'overall_length':54})['centers']),2)
    def test_column_threshold(self):
        a=layout({'overall_width':107.99});b=layout({'overall_width':108})
        self.assertEqual(len(a['centers']),12);self.assertEqual(len(b['centers']),14)
    def test_invalid_geometry(self):
        for changes in [{'overall_width':30},{'tray_floor':9},{'socket_pitch':5},{'socket_margin':1},{'overall_height':float('nan')}]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):layout(changes)
    def test_generation(self):
        compile(build_script({},'A document'),'build','exec')
        compile(variants_script('A document',[{'overall_width':130}]),'update','exec')
    def test_derived_controls_are_rejected(self):
        with self.assertRaises(ValueError):variants_script('A document',[{'socket_columns':8}])
    def test_invalid_edits_rejected_before_dispatch(self):
        for value in (True,-1,0,float('nan'),float('inf')):
            with self.subTest(value=value),self.assertRaises(ValueError):variants_script('A document',[{'overall_width':value}])

if __name__=='__main__':unittest.main(verbosity=2)
