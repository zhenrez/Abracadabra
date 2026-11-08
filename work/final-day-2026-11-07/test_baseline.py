import unittest
from baseline import encode_literal,encode_dictionary,decode,fit_dictionary,grouped_folds,infer_basis

class CodingBaselineTests(unittest.TestCase):
    values=(('PHONEME_VALUE','ʔ'),('PHONEME_VALUE','b/v'),('UNKNOWN_VALUE','?'),('LETTER_NAME','eɪ'),('BLANK',''))
    def test_literal_exact_unicode_roundtrip(self):
        result=encode_literal(self.values)
        self.assertEqual(decode(result['bits']),self.values)
        self.assertEqual(result['total_bits'],len(result['bits']))
    def test_dictionary_and_escaped_unseen_values_roundtrip(self):
        vocabulary=fit_dictionary(self.values[:2])
        result=encode_dictionary(self.values,vocabulary)
        self.assertEqual(decode(result['bits']),self.values)
        self.assertEqual(result['escaped_values'],3)
    def test_description_costs_are_measured_not_constants(self):
        values=self.values*20
        result=encode_dictionary(values,fit_dictionary(values))
        self.assertEqual(result['model_bits']+result['data_bits'],result['total_bits'])
        self.assertGreater(result['model_bits'],0)
        self.assertLess(result['total_bits'],encode_literal(values)['total_bits'])
        self.assertEqual(result,encode_dictionary(values,fit_dictionary(values)))
    def test_related_groups_never_split_between_train_and_test(self):
        records=[{'record_id':str(i),'cluster':c} for i,c in enumerate(('A','A','B','C'))]
        folds=grouped_folds(records)
        self.assertEqual(len(folds),3)
        for fold in folds:
            self.assertFalse(set(fold['train_ids'])&set(fold['test_ids']))
            self.assertFalse(set(fold['train_clusters'])&set(fold['test_clusters']))
            self.assertFalse(fold['prospective_blind'])
    def test_corrupt_or_trailing_bitstreams_rejected(self):
        encoded=encode_literal(self.values)['bits']
        with self.assertRaises(ValueError):decode(encoded+'1')
        with self.assertRaises(ValueError):decode(encoded[:-1])
        with self.assertRaises(ValueError):decode('not bits')
    def test_bounded_basis_search_charges_dictionary_and_residuals(self):
        values=(('P','b'),('P','d'))*40
        result=infer_basis(values)
        self.assertEqual(result['selected_model'],'dictionary')
        self.assertEqual(set(result['basis']),{('P','b'),('P','d')})
        self.assertEqual(result['selected_bits'],min(c['total_bits'] for c in result['candidates']))
        self.assertFalse(result['global_optimality_claim'])
    def test_order_null_control_does_not_imply_historical_permutation(self):
        values=self.values*3
        a=infer_basis(values);b=infer_basis(tuple(reversed(values)))
        self.assertEqual(a['selected_bits'],b['selected_bits'])
        self.assertEqual(a['historical_support'],'NOT_VERIFIED')

if __name__=='__main__':unittest.main()
