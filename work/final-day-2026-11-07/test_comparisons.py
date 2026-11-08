from fractions import Fraction as Q
import unittest
from comparisons import ScalarOperator,QuantityAdapter,commutation,adapter_candidates,historical_reconstruct

class TypedComparisonTests(unittest.TestCase):
    def test_reciprocal_length_frequency_diagram(self):
        source=ScalarOperator('Chinese D','length_ratio',Q(2,3))
        target=ScalarOperator('frequency fifth','frequency_ratio',Q(3,2))
        adapter=QuantityAdapter('length_ratio','frequency_ratio','reciprocal',Q(1))
        result=commutation(source,target,adapter,(Q(7,11),Q(13,17)))
        self.assertEqual(result['status'],'PRESERVED_UNDER_DECLARED_ADAPTER')
        self.assertTrue(all(row['residual']=='0' for row in result['cases']))
        self.assertEqual(result['historical_support'],'NOT_VERIFIED')
    def test_incompatible_composites_produce_counterexample(self):
        source=ScalarOperator('SUN RL','length_ratio',Q(1,2))
        target=ScalarOperator('Chinese DU','length_ratio',Q(8,9))
        result=commutation(source,target,QuantityAdapter('length_ratio','length_ratio','identity',Q(1)),(Q(7,11),))
        self.assertEqual(result['status'],'COUNTEREXAMPLE')
        self.assertEqual(result['cases'][0]['source_then_adapter'],'7/22')
        self.assertEqual(result['cases'][0]['adapter_then_target'],'56/99')
    def test_type_mismatch_rejected(self):
        with self.assertRaises(ValueError):commutation(ScalarOperator('a','length_ratio',Q(2,3)),
            ScalarOperator('b','length_ratio',Q(3,2)),QuantityAdapter('length_ratio','frequency_ratio','reciprocal',Q(1)),(Q(1),))
    def test_equivalent_operator_fits_do_not_determine_register(self):
        source=ScalarOperator('a','length_ratio',Q(2,3));target=ScalarOperator('b','length_ratio',Q(2,3))
        candidates=[QuantityAdapter('length_ratio','length_ratio','identity',Q(scale)) for scale in (1,2)]
        result=adapter_candidates(source,target,candidates,(Q(3,5),Q(7,11)))
        self.assertEqual(result['identifiability'],'MULTIPLE_DISTINGUISHABLE')
        self.assertEqual(len(result['survivors']),2)
    def test_historical_correspondence_fails_closed(self):
        with self.assertRaises(PermissionError):historical_reconstruct({'glyph':'א','pitch':'A'})

if __name__=='__main__':unittest.main()
