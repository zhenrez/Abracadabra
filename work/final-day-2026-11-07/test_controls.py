import unittest
import controls

class NativeControlTests(unittest.TestCase):
    def test_source_documented_numbers(self):
        for text,number in [('dhīra',29),('māyā',15),('nāgā',30),('naṭanara',2010)]:
            with self.subTest(text=text):self.assertEqual(controls.decode_katapayadi(text)['number'],number)
    def test_clusters_dead_consonants_and_vowel_profiles(self):
        self.assertEqual(controls.decode_katapayadi('śrī')['number'],2)
        self.assertEqual(controls.decode_katapayadi('kya')['number'],1)
        self.assertIsNone(controls.decode_katapayadi('k')['number'])
        self.assertEqual(controls.decode_katapayadi('a')['number'],0)
        self.assertIsNone(controls.decode_katapayadi('a',vowel_policy='ignore')['number'])
    def test_encoding_candidates_are_not_unique_historical_words(self):
        encoded=controls.encode_katapayadi(29)
        self.assertGreater(len(encoded['candidates']),1)
        self.assertTrue(all(controls.decode_katapayadi(s)['number']==29 for s in encoded['candidates']))
        self.assertEqual(encoded['historical_support'],'NOT_VERIFIED')
    def test_native_articulation_does_not_merge_aspiration_or_retroflexion(self):
        records=controls.sanskrit_stop_table()
        self.assertEqual(len(records),25)
        self.assertEqual(len({r['vector'] for r in records}),25)
        by={r['iast']:r for r in records}
        self.assertNotEqual(by['ṭ']['vector'],by['t']['vector'])
        self.assertNotEqual(by['k']['vector'],by['kh']['vector'])
        self.assertEqual(by['m']['manner'],'nasal')
    def test_raw_and_invalid_inputs(self):
        result=controls.decode_katapayadi('dhi\u0304ra')
        self.assertEqual(result['raw'],'dhi\u0304ra')
        self.assertEqual(result['number'],29)
        for value in ('Dha','?','🙂'):
            with self.subTest(value=value),self.assertRaises(ValueError):controls.decode_katapayadi(value)
        for value in (-1,True,2.5):
            with self.subTest(value=value),self.assertRaises(ValueError):controls.encode_katapayadi(value)

if __name__=='__main__':unittest.main()
