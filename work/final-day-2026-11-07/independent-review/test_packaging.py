from pathlib import Path
import importlib.util
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


class PackagingTests(unittest.TestCase):
    def module(self,name):
        self.assertIsNotNone(importlib.util.find_spec(name),'Packaging/verification implementation is absent')
        return __import__(name)

    def test_all_original_rows_preserved_verbatim(self):
        p=self.module('package_delivery')
        census=json.loads((ROOT/'audit/deliverables.json').read_text(encoding='utf-8'))
        delivery=json.loads((ROOT/'results/delivery-receipt.json').read_text(encoding='utf-8'))
        current=p.current_rows(census,delivery)
        self.assertEqual([r['original'] for r in current],census['requirements'])
        self.assertEqual(len(current),106)
        self.assertTrue(all(r['engineering_assessment']['remaining_dependencies'] is not None for r in current))

    def test_verifier_rejects_changed_output_and_path_escape(self):
        v=self.module('verify_delivery')
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'output.json').write_text('{}',encoding='utf-8')
            with self.assertRaises(ValueError):v.verify_receipt_outputs(root,{'outputs':{'output.json':'wrong'}})
            with self.assertRaises(ValueError):v.verify_receipt_outputs(root,{'outputs':{'../outside.json':'wrong'}})

    def test_verifier_rejects_reclassified_original_requirement(self):
        p=self.module('package_delivery');v=self.module('verify_delivery')
        census=json.loads((ROOT/'audit/deliverables.json').read_text(encoding='utf-8'))
        delivery=json.loads((ROOT/'results/delivery-receipt.json').read_text(encoding='utf-8'))
        current=p.current_rows(census,delivery)
        current[0]['original']['status']='COMPLETE'
        with self.assertRaises(ValueError):v.verify_rows(census,{'requirements':current})

    def test_all_project_execution_variants_remain_visible(self):
        p=self.module('package_delivery')
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'runtime').mkdir()
            for name in ('project-checks.json','project-serial-checks.json','project-after-repair-checks.json'):
                (root/'runtime'/name).write_text(json.dumps({'command':['node'],'exit_code':1,'observed_counts':{'tests':99}}),encoding='utf-8')
            with patch.object(p,'ROOT',root):
                self.assertEqual(len(p.project_test_records()),3)

    def test_current_catalog_is_stable_and_has_no_browser_hash_cycle(self):
        p=self.module('package_delivery')
        census=json.loads((ROOT/'audit/deliverables.json').read_text(encoding='utf-8'))
        delivery=json.loads((ROOT/'results/delivery-receipt.json').read_text(encoding='utf-8'))
        left=p.current_package(census,delivery);right=p.current_package(census,delivery)
        self.assertEqual(left,right)
        self.assertEqual(left['generated_utc'],delivery['timestamp_utc'])
        self.assertNotIn('Browser',[row['capability'] for row in left['capabilities']])


if __name__=='__main__':unittest.main()
