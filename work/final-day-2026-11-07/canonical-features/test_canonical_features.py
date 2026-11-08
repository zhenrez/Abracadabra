"""Canonical-source acceptance; no historical glyph/phoneme equivalence inferred."""
from pathlib import Path
import copy
import hashlib
import json
import tempfile
import unittest

import numpy as np
from canonical_features import build_features, verify_bindings, write_features

PROJECT = Path(__file__).resolve().parents[3]
SOURCE = PROJECT / 'work/unit001/frozen/source/matrix-message.txt'


def cell(bundle, label, ordinal):
    return next(item for item in bundle['sidecar']['cells']
                if item['script_label'] == label and item['local_ordinal'] == ordinal)


class CanonicalFeatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = build_features()

    def test_canonical_grid_keeps_all_three_fields_and_addresses(self):
        bundle = self.bundle
        self.assertEqual(bundle['vector'].shape, (15, 36, 20))
        self.assertEqual(bundle['mask'].shape, (15, 36, 20))
        self.assertEqual(bundle['mask'].dtype, np.dtype(bool))
        self.assertEqual(len(bundle['sidecar']['cells']), 540)
        self.assertEqual(len({item['cell_id'] for item in bundle['sidecar']['cells']}), 540)
        rows = [line.split('\t') for line in SOURCE.read_bytes().decode('utf-8').splitlines()]
        for index, item in enumerate(bundle['sidecar']['cells']):
            script, column = divmod(index, 36)
            self.assertEqual(item['script_label'], rows[1 + script * 3][0])
            self.assertEqual(item['local_ordinal'], column + 1)
            self.assertEqual((item['raw_glyph'], item['raw_ipa'], item['raw_english']),
                             tuple(rows[1 + script * 3 + delta][column + 1] for delta in range(3)))
        self.assertEqual(bundle['source_bytes'], SOURCE.read_bytes())
        self.assertEqual(bundle['sidecar']['source']['sha256'], hashlib.sha256(SOURCE.read_bytes()).hexdigest())

    def test_blank_unknown_unresolved_and_native_types_stay_distinct(self):
        bundle = self.bundle
        states = [item['value_state'] for item in bundle['sidecar']['cells']]
        self.assertEqual(states.count('BLANK'), 159)
        self.assertEqual(states.count('UNKNOWN_VALUE'), 4)
        self.assertEqual(states.count('UNRESOLVED_LABEL'), 1)
        self.assertEqual(cell(bundle, 'Sabaic / South Arabian', 29)['raw_ipa'], 's³')
        english = bundle['sidecar']['scripts'].index('English')
        self.assertFalse(bundle['mask'][english, :, :15].any())
        self.assertFalse(bundle['vector'][english, :, :15].any())
        self.assertEqual(cell(bundle, 'English', 5)['phonetic_type'], 'LETTER_NAME')
        self.assertIsNone(cell(bundle, 'English', 5)['parsed_ipa'])
        persian = [item for item in bundle['sidecar']['cells'] if item['script_label'] == 'Old Persian']
        self.assertEqual(sum(item['phonetic_type'] == 'VOWEL_SIGN' for item in persian), 3)
        self.assertEqual(sum(item['phonetic_type'] == 'SYLLABOGRAM' for item in persian), 33)
        self.assertEqual(persian[3]['parsed_ipa']['kind'], 'sequence')

    def test_atomic_emphasis_and_ordered_alternatives_are_not_averaged(self):
        bundle = self.bundle
        emphatic = cell(bundle, 'Proto-Sinaitic (proxy)', 9)
        self.assertEqual(emphatic['parsed_ipa']['kind'], 'segment')
        self.assertEqual(emphatic['raw_ipa'], 'tˤ')
        self.assertEqual(bundle['vector'][0, 8, 14], 1)
        self.assertEqual(bundle['vector'][0, 8, :15].sum(), 4)
        alternative = cell(bundle, 'Square Hebrew', 2)
        self.assertEqual(alternative['raw_ipa'], 'b/v')
        self.assertEqual([branch['segments'][0]['ipa'] for branch in alternative['parsed_ipa']['alternatives']], ['b', 'v'])
        self.assertTrue(all(len(branch['segments'][0]['vector']) == 15 for branch in alternative['parsed_ipa']['alternatives']))
        row = bundle['sidecar']['scripts'].index('Square Hebrew')
        self.assertFalse(bundle['mask'][row, 1, :15].any())
        self.assertFalse(bundle['vector'][row, 1, :15].any())

    def test_strict_geometry_and_normalized_outputs_are_deterministic(self):
        bundle = self.bundle
        self.assertFalse(bundle['mask'][:, :, 15:].any())
        self.assertFalse(bundle['vector'][:, :, 15:].any())
        norms = np.linalg.norm(bundle['normalized'], axis=-1)
        self.assertTrue(np.all(np.isclose(norms, 0) | np.isclose(norms, 1)))
        self.assertTrue(np.isfinite(bundle['normalized']).all())
        with tempfile.TemporaryDirectory() as tmp:
            first, second = Path(tmp) / 'a', Path(tmp) / 'b'
            write_features(bundle, first)
            write_features(build_features(), second)
            self.assertEqual(sorted(p.name for p in first.iterdir()), sorted(p.name for p in second.iterdir()))
            for path in first.iterdir():
                self.assertEqual(path.read_bytes(), (second / path.name).read_bytes(), path.name)
            with np.load(first / 'matrix.npz', allow_pickle=False) as arrays:
                self.assertEqual(arrays['vector'].shape, (15, 36, 20))
                self.assertEqual(arrays['cell_ids'].shape, (15, 36))
                self.assertTrue(np.array_equal(arrays['mask'], bundle['mask']))
            self.assertEqual((first / 'source.tsv').read_bytes(), SOURCE.read_bytes())
            self.assertEqual(len(json.loads((first / 'vectors.json').read_text(encoding='utf-8'))['cells']), 540)

    def test_source_or_dependency_binding_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_source = Path(tmp) / 'source.tsv'
            fake_source.write_bytes(SOURCE.read_bytes().replace(b'Alphabet', b'ALPHABET', 1))
            with self.assertRaises(ValueError):
                build_features(source_path=fake_source)
        altered = dict(self.bundle)
        altered['sidecar'] = copy.deepcopy(self.bundle['sidecar'])
        altered['sidecar']['imports'][0]['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            verify_bindings(altered)

    def test_raw_sidecar_binding_tamper_is_rejected(self):
        changes = [('raw_glyph', 'X'), ('raw_ipa', 'p'),
                   ('raw_english', 'altered approximation'),
                   ('record_id', 'unbound witness'), ('cell_id', 'unbound cell'),
                   ('phonetic_type', 'LETTER_NAME'),
                   ('glyph_type', 'UNICODE_STANDARD_CHAR'), ('claim_refs', [])]
        changed_coordinates = copy.deepcopy(self.bundle['sidecar']['cells'][0]['coordinates'])
        changed_coordinates['glyph']['start'] += 1
        changes.append(('coordinates', changed_coordinates))
        for field, value in changes:
            with self.subTest(field=field):
                altered = dict(self.bundle)
                altered['sidecar'] = copy.deepcopy(self.bundle['sidecar'])
                altered['sidecar']['cells'][0][field] = value
                with self.assertRaises(ValueError):
                    verify_bindings(altered)

    def test_derived_projection_tamper_is_rejected(self):
        for field in ('vector', 'mask', 'normalized'):
            with self.subTest(field=field):
                altered = dict(self.bundle)
                altered[field] = self.bundle[field].copy()
                if field == 'mask':
                    altered[field][0, 0, 0] = not altered[field][0, 0, 0]
                else:
                    altered[field][0, 0, 0] += 0.5
                with self.assertRaises(ValueError):
                    verify_bindings(altered)
        with self.subTest(field='parsed_ipa'):
            altered = dict(self.bundle)
            altered['sidecar'] = copy.deepcopy(self.bundle['sidecar'])
            altered['sidecar']['cells'][0]['parsed_ipa']['alternatives'][0]['segments'][0]['ipa'] = 'b'
            with self.assertRaises(ValueError):
                verify_bindings(altered)


if __name__ == '__main__':
    unittest.main()
