import unittest
from drift_engine import *

class SplitTests(unittest.TestCase):
    def test_parity_and_inverse(self):
        e=DriftEngine()
        self.assertEqual(len(e.transform()['rows']),22)
        for i in CARRIER:
            s=State(i);self.assertEqual(e.parity.toggle(e.parity.toggle(s)),s)
        self.assertEqual(e.parity.emit(State(2,1)),'v')
    def test_no_overwrite(self):
        with self.assertRaises(ValueError):ParityScript(CARRIER).emit(State(1,1))
        with self.assertRaises(ValueError):ParityScript(CARRIER).emit(State(23))
    def test_expansion_bijection(self):
        rows=DriftEngine().transform('expansion')['rows']
        self.assertEqual(len(rows),28)
        self.assertEqual(len({(r['source_index'],r['parity']) for r in rows}),28)
    def test_ugaritic_exact_and_unmatched(self):
        e=DriftEngine(); rows=e.transform('expansion','ugaritic')['rows']
        self.assertEqual([r['phoneme'] for r in rows],UG_VALUES)
        self.assertEqual(e.inverse_candidates(28,'ugaritic'),[])
        self.assertEqual(e.inverse_candidates(4,'ugaritic'),[dict(source_index=11,parity=1,index_delta=-7)])
        with self.assertRaises(ValueError):e.inverse_candidates(31,'ugaritic')
    def test_arabic_and_determinism(self):
        e=DriftEngine();self.assertEqual(e.transform('expansion','arabic'),e.transform('expansion','arabic'))
        self.assertEqual([r['phoneme'] for r in e.transform('expansion','arabic')['rows']],AR_VALUES)

if __name__=='__main__':unittest.main()
