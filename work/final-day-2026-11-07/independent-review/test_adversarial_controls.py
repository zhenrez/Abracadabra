"""Independent bounded codec and candidate-identity regression controls."""
from pathlib import Path
from fractions import Fraction as Q
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import baseline
from comparisons import ScalarOperator,QuantityAdapter,adapter_candidates


class AdversarialControlTests(unittest.TestCase):
    def test_literal_encoder_respects_its_decoder_budget(self):
        values=(('PHONEME_VALUE','x'*65536),)*16
        try:encoded=baseline.encode_literal(values)
        except ValueError:return
        self.assertLessEqual(len(encoded['bits']),8000000,
                             'Accepted encoder input produces an undecodable over-budget stream')
        self.assertEqual(baseline.decode(encoded['bits']),values)

    def test_dictionary_encoder_respects_its_decoder_budget(self):
        vocabulary=tuple((str(i),'x'*65536) for i in range(16))
        try:encoded=baseline.encode_dictionary((),vocabulary)
        except ValueError:return
        self.assertLessEqual(len(encoded['bits']),8000000,
                             'Accepted dictionary produces an undecodable over-budget stream')
        self.assertEqual(baseline.decode(encoded['bits']),())

    def test_identical_adapters_do_not_create_distinguishable_solutions(self):
        source=ScalarOperator('source','length_ratio',Q(2,3))
        target=ScalarOperator('target','length_ratio',Q(2,3))
        a=QuantityAdapter('length_ratio','length_ratio','identity',Q(1))
        try:result=adapter_candidates(source,target,(a,a),(Q(1),))
        except ValueError:return
        self.assertEqual(result['identifiability'],'UNIQUE_UNDER_DECLARED_FINITE_MODEL')
        self.assertEqual(len(result['survivors']),1)

    def test_basis_search_keeps_feasible_model_when_literal_exceeds_budget(self):
        values=(('P','x'*65536),)*16
        dictionary=baseline.encode_dictionary(values,(values[0],))
        self.assertLess(dictionary['total_bits'],8000000)
        result=baseline.infer_basis(values)
        self.assertEqual(result['selected_model'],'dictionary')
        self.assertEqual(result['selected_bits'],dictionary['total_bits'])


if __name__=='__main__':unittest.main()
