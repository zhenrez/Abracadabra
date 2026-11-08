import unittest
import numpy as np
from permutation import analyze,cyclic_distance

class PermutationTests(unittest.TestCase):
    def test_rotation(self):
        r=analyze(['b','d','g'],['d','g','b'])
        self.assertTrue(r['bijection']);self.assertEqual(r['permutation_1_based'],[2,3,1])
        self.assertEqual(r['rotation']['minimum_hamming'],0)
        np.testing.assert_array_equal(np.array(r['matrix'])@np.array([10,20,30]),[20,30,10])
    def test_noncyclic(self):
        r=analyze(['b','d','g'],['b','g','d'])
        self.assertTrue(r['bijection']);self.assertFalse(r['rotation']['exact_rotation'])
    def test_missing_extra_duplicate(self):
        r=analyze(['b','d','g'],['b','b',None,'f'])
        self.assertFalse(r['bijection']);self.assertEqual(r['missing_source'],['d','g'])
        self.assertEqual(r['permutation_1_based'],[1,1,None,None])
        self.assertIsNone(r['rotation'])
    def test_invalid_and_deterministic(self):
        with self.assertRaises(ValueError):analyze(['b','b'],['b'])
        self.assertEqual(analyze(['b','d'],['d','b']),analyze(['b','d'],['d','b']))

if __name__=='__main__':unittest.main()
