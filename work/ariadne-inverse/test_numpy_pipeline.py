import unittest
from pathlib import Path
import numpy as np
from build_dataset import dataset
from numpy_pipeline import table_to_numpy, normalize_vectors, validate_normalized, bitmap_geometry, FontGeometry, raw_table_to_data, phoneme_vector, record_distance

class NumPyTests(unittest.TestCase):
    def test_alignment_nulls_and_atomic_emphasis(self):
        scripts,a=table_to_numpy(dataset())
        self.assertEqual(a.shape,(15,36))
        self.assertEqual(a['vector'].shape,(15,36,20))
        self.assertEqual(a['vector'][0,8,14],1)
        self.assertEqual(a['ipa'][0,8],'tˤ')
        self.assertTrue(np.all(a['vector'][0,22:]==0))
        self.assertFalse(a['mask'][:,:,15:].any())
        self.assertTrue(validate_normalized(a['normalized']))
        self.assertEqual(a['kind'][9,3],'sequence')
        self.assertEqual(a['details'][9,3]['segment_vectors'][0].shape,(2,20))
    def test_normalization_contract(self):
        a=normalize_vectors([[0,0],[3,4]])
        np.testing.assert_allclose(a,[[0,0],[.6,.8]])
        self.assertTrue(validate_normalized(a))
        self.assertFalse(validate_normalized([[2,0]]))
        with self.assertRaises(ValueError): normalize_vectors([[float('nan')]])
    def test_graph_shapes(self):
        line=np.zeros((9,9),bool); line[4,1:8]=True
        g,_=bitmap_geometry(line)
        self.assertEqual(g[0],2); self.assertEqual(g[1],0); self.assertEqual(g[2],1); self.assertEqual(g[3],0)
        square=np.zeros((13,13),bool); square[2,2:11]=1; square[10,2:11]=1; square[2:11,2]=1; square[2:11,10]=1
        g,_=bitmap_geometry(square)
        self.assertEqual(g[3],1); self.assertEqual(g[4],4)
    def test_font_missing_fails_closed(self):
        path=Path('C:/Windows/Fonts/seguihis.ttf')
        if not path.exists(): self.skipTest('Host font absent')
        f=FontGeometry(path)
        self.assertIsNone(f('\U0010ffff'))
        a=f('𐤀'); b=f('𐤀')
        self.assertIsNotNone(a)
        np.testing.assert_array_equal(a[0],b[0])
        self.assertEqual(a[1]['font_sha256'],b[1]['font_sha256'])
    def test_duplicate_addresses_rejected(self):
        data=dataset(); data['cells'].append(data['cells'][0])
        with self.assertRaises(ValueError): table_to_numpy(data)
    def test_tsv_roundtrip(self):
        from build_dataset import ROWS
        lines=['\t'.join(['Alphabet']+[str(i) for i in range(1,37)])]
        for name,glyphs,ipa,_,_ in ROWS:
            lines.extend(['\t'.join([name]+list(glyphs)), '\t'.join(['IPA']+ipa.split())])
        parsed=raw_table_to_data('\n'.join(lines))
        self.assertEqual(parsed['cells'],dataset()['cells'])
        with self.assertRaises(ValueError): raw_table_to_data('Alphabet\t1\n')
    def test_null_vector_and_distance(self):
        np.testing.assert_array_equal(phoneme_vector(None),np.zeros(15))
        self.assertEqual(phoneme_vector('tˤ')[14],1)
        with self.assertRaises(ValueError): phoneme_vector('ka')
        _,a=table_to_numpy(dataset())
        self.assertTrue(np.isnan(record_distance(a[0,0],a[0,35])))
        self.assertEqual(record_distance(a[0,0],a[0,0]),0)

if __name__=='__main__': unittest.main()
