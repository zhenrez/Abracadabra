import unittest
from vowel_drift import *

class DriftTests(unittest.TestCase):
    def test_known_outputs(self):
        op=VowelDriftOperator()
        self.assertEqual(op.transform([1,5,8,16],'greek'),['a','e','ɛː','o'])
        self.assertEqual(op.transform([1,5,8,16],'latin'),['a','e','h','o'])
    def test_identity_and_glide(self):
        op=VowelDriftOperator()
        for i,s in CARRIER.items():
            if s not in LARYNGEALS:self.assertEqual(op.apply_vowel_drift(i,'greek'),s)
        self.assertEqual(op.transform([10],'greek',include_glide=True),['i'])
    def test_validation_and_missing(self):
        op=VowelDriftOperator((Target('empty',{}),))
        self.assertEqual(op.transform([1,2],'empty'),['ʔ','b'])
        with self.assertRaises(ValueError):op.transform([1],'empty',missing='error')
        for i in (0,23,True,1.0):
            with self.assertRaises(ValueError):op.transform([i],'empty')
        with self.assertRaises(ValueError):op.transform([1],'unknown')
    def test_rotation_and_indices(self):
        v=(1,0)
        for _ in range(4):v=VowelDriftOperator.rotate_phase(v)
        self.assertEqual(v,(1,0))
        self.assertEqual(GREEK.mappings[8].target_index,7)
        self.assertEqual(LATIN.mappings[16].target_index,14)

if __name__=='__main__':unittest.main()
