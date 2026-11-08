from pathlib import Path
import hashlib
import tempfile
import unittest

from mathematical_sources import resolve_source


class MathematicalSourceTests(unittest.TestCase):
    def fixture(self,root):
        prior=b'{"generation":1}\n';later=b'{"generation":2}\n'
        (root/'prior.json').write_bytes(prior);(root/'later.json').write_bytes(later)
        sha=lambda raw:hashlib.sha256(raw).hexdigest()
        record=lambda name,raw:{'path':name,'sha256':sha(raw),'bytes':len(raw),'availability':'VERIFIED'}
        reference={'path':'mutable/original.json','sha256':sha(prior),'exists':True}
        source={'original_path':reference['path'],'original_sha256':reference['sha256'],'per_M_ids':['M01'],
                'initial_version':record('prior.json',prior),'current_version':record('later.json',later),
                'version_relation':'NEWLY_OBSERVED_VERSION','data_role':'DERIVED_SCIENTIFIC_STATE'}
        return reference,{'sources':[source]}

    def test_baseline_and_later_version_survive_live_path_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);reference,registry=self.fixture(root)
            resolved=resolve_source(reference,registry,root,'M01')
            self.assertEqual(resolved['initial_version']['sha256'],reference['sha256'])
            self.assertNotEqual(resolved['initial_version']['sha256'],resolved['current_version']['sha256'])
            self.assertFalse((root/reference['path']).exists())
            self.assertEqual(reference['path'],'mutable/original.json')

    def test_source_or_snapshot_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);reference,registry=self.fixture(root)
            (root/'prior.json').write_bytes(b'changed')
            with self.assertRaises(ValueError):resolve_source(reference,registry,root,'M01')

    def test_missing_mapping_and_wrong_requirement_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);reference,registry=self.fixture(root)
            with self.assertRaises(ValueError):resolve_source(reference,{'sources':[]},root,'M01')
            with self.assertRaises(ValueError):resolve_source(reference,registry,root,'M02')

    def test_snapshot_escape_and_false_initial_digest_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);reference,registry=self.fixture(root)
            registry['sources'][0]['initial_version']['path']='../escape.json'
            with self.assertRaises(ValueError):resolve_source(reference,registry,root,'M01')
            reference,registry=self.fixture(root)
            registry['sources'][0]['original_sha256']='0'*64
            with self.assertRaises(ValueError):resolve_source(reference,registry,root,'M01')


if __name__=='__main__':unittest.main()
