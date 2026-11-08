import unittest,json,base64
from pathlib import Path
from closeout_fixtures import build
from kernel import KernelStore,EvidenceClaim,SourceArtifact,DomainRecord
from contracts import CrossOrientationRegistry

class HistoricalControls(unittest.TestCase):
    def test_four_real_controls_roundtrip(self):
        stores=build();self.assertEqual(set(stores),{'recensions','qere_ketiv','epigraphy','orientations'})
        for store in stores.values():
            store.validate();self.assertEqual(KernelStore.from_json(store.to_json()).to_json(),store.to_json())
            self.assertFalse(any(s.authority=='SYNTHETIC_SCHEMA_FIXTURE' for s in store.records if isinstance(s,SourceArtifact)))
    def test_qere_layers(self):
        s=build()['qere_ketiv'];record=next(r for r in s.records if isinstance(r,DomainRecord))
        self.assertEqual(len(record.properties['pairs']),2)
        self.assertNotEqual(record.properties['pairs'][0]['written'],record.properties['pairs'][0]['read'])
        self.assertIsNone(record.properties['phonetic_realization'])
    def test_epigraphy_unresolved(self):
        s=build()['epigraphy'];claims=[r for r in s.records if isinstance(r,EvidenceClaim)]
        self.assertEqual({c.value for c in claims},{13,14,16})
        self.assertTrue(all(len(c.competing_claims)==2 for c in claims))
    def test_orientation_footnote_not_medieval_assertion(self):
        s=build()['orientations'];d=next(r for r in s.records if isinstance(r,DomainRecord))
        self.assertEqual(d.properties['attribution'],'modern translation footnote 74; no direct attribution of both procedures to Ibn Ezra')
        self.assertIsNone(d.properties['selected']);self.assertIsNone(d.properties['w72_alignment'])
    def test_recension_source_dependency(self):
        d=next(r for r in build()['recensions'].records if isinstance(r,DomainRecord))
        self.assertEqual(len(d.properties['recensions']),2)
        self.assertEqual(d.properties['independent_manuscripts_verified'],False)
    def test_g7_denied(self):
        r=CrossOrientationRegistry();self.assertEqual(r.adapters,())
        with self.assertRaises(PermissionError):r.register(build()['orientations'])
        with self.assertRaises(PermissionError):r.evaluate(None)
        with self.assertRaises(PermissionError):r.from_json('{"g7":true,"adapters":[]}')
if __name__=='__main__':unittest.main()
