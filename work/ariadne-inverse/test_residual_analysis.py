import unittest,json
from residual_analysis import *

class ResidualTests(unittest.TestCase):
    def test_information(self):
        self.assertEqual(entropy(['a']*4),0)
        self.assertEqual(entropy(['a','b']),1)
        self.assertIsNone(entropy([]))
        self.assertEqual(mutual_information([(0,0),(1,1)]),1)
        self.assertEqual(mutual_information([(0,0),(0,1),(1,0),(1,1)]),0)
        self.assertIsNone(mutual_information([]))
    def test_index_and_parity(self):
        self.assertEqual(prediction('Ancient Greek (Ionic)',7)[0],8)
        self.assertIsNone(prediction('Ancient Greek (Ionic)',8))
        self.assertEqual(prediction('Syriac',2)[1],{'b','v'})
    def test_table_contract(self):
        result=analyze(json.loads((ROOT/'table.json').read_text(encoding='utf-8'))['cells'])
        self.assertEqual(len(result['records']),540)
        self.assertEqual([r['target_column'] for r in result['unknown_glyph_nodes']],[2,4,18,26])
        self.assertTrue(all(r['phonetic_status']=='unknown' for r in result['unknown_glyph_nodes']))
        self.assertIsNone(result['historical_TMI']['value'])
        self.assertTrue(all(r['residual'] is None for r in result['records'] if r['script']=='Old Persian'))

if __name__=='__main__':unittest.main()
