import unittest
import numpy as np
from harmonic_verifier import *

class HarmonicTests(unittest.TestCase):
    def setUp(self):self.base=[x for xs in GROUPS.values() for x in xs]
    def test_base(self):
        r=HarmonicPhoneticVerifier().validate(self.base)
        self.assertEqual(r['status'],'Valid')
        self.assertEqual([len(r['matrix_distribution'][g]) for g in GROUPS],[3,7,12])
    def test_unique_completion(self):
        r=HarmonicPhoneticVerifier().validate([x for x in self.base if x!='m'])
        self.assertEqual(r['reconstruction_suggestion'],'m');self.assertEqual(r['status'],'Invalid')
    def test_duplicate(self):
        r=HarmonicPhoneticVerifier().validate(self.base[:-1]+['b'])
        self.assertEqual(r['status'],'Invalid');self.assertIsNone(r['reconstruction_suggestion'])
    def test_ambiguity(self):
        r=HarmonicPhoneticVerifier().validate([x for x in self.base if x not in ('s','ʃ')]+['s'])
        self.assertEqual(set(r['symmetry_gap']['possible_missing_slots']),{'s','ʃ'})
        self.assertIsNone(r['reconstruction_suggestion'])
    def test_expanded(self):
        e=HarmonicPhoneticVerifier('expanded');self.assertEqual(len(e.slots),29)
        self.assertEqual(e.validate(list(e.slots))['status'],'Valid')
        self.assertEqual(e.validate(list(e.slots)+['b'])['status'],'Invalid')
        self.assertEqual(e.candidates('v'),{'b:1'})
    def test_frequency(self):
        e=HarmonicPhoneticVerifier()
        np.testing.assert_allclose(e.harmonic_series(100,3),[100,200,300])
        np.testing.assert_allclose(e.frequency_distance([220],[110]),[1200])
        with self.assertRaises(ValueError):e.frequency_distance([0],[110])

if __name__=='__main__':unittest.main()
