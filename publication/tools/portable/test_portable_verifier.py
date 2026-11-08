from contextlib import redirect_stdout
from pathlib import Path
import hashlib
import importlib.util
import io
import json
import shutil
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
DELIVERY = Path('work/final-day-2026-11-07')


class PortableVerifierTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'relocated-checkout'
        self.root.mkdir()
        required = [Path('package.json'), Path('work/unit001/evidence.py'),
                    Path('work/unit001/frozen/source/matrix-message.txt'),
                    Path('work/ariadne-inverse/features.py'),
                    Path('work/ariadne-inverse/numpy_pipeline.py'),
                    DELIVERY / 'canonical-features/canonical_features.py',
                    DELIVERY / 'canonical-features/source-bindings.json',
                    DELIVERY / 'audit/deliverables.json',
                    DELIVERY / 'results/delivery-receipt.json',
                    DELIVERY / 'current-deliverables.json']
        for relative in required:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PROJECT / relative, target)
        self.bundle = self.root / DELIVERY / 'results/canonical-features-v2'
        shutil.copytree(PROJECT / DELIVERY / 'results/canonical-features-v2', self.bundle)
        # Engineering-only fixture refs keep the complete106 original rows exact
        # without copying unrelated research and private execution artifacts.
        evidence = self.root / DELIVERY / 'fixture-evidence.json'
        evidence.write_text('{}\n', encoding='utf-8')
        current = self.read(DELIVERY / 'current-deliverables.json')
        for row in current['requirements']:
            row['engineering_assessment']['evidence_refs'] = [
                (DELIVERY / 'fixture-evidence.json').as_posix()]
        self.write(DELIVERY / 'current-deliverables.json', current)

    def read(self, relative):
        return json.loads((self.root / relative).read_bytes())

    def write(self, relative, value):
        (self.root / relative).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    def module(self, path=None):
        path = path or HERE / 'verify_abracadabra.py'
        self.assertTrue(path.is_file(), 'Portable verifier implementation is absent')
        spec = importlib.util.spec_from_file_location('portable_verifier_test_target', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def resign_payload(self, name):
        manifest = self.read(DELIVERY / 'results/canonical-features-v2/manifest.json')
        raw = (self.bundle / name).read_bytes()
        manifest['files'][name] = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
        self.write(DELIVERY / 'results/canonical-features-v2/manifest.json', manifest)

    def test_relocated_checkout_derives_without_modifying_archived_source_locator(self):
        module = self.module()
        before = (self.bundle / 'vectors.json').read_bytes()
        result = module.verify_repository(self.root)
        self.assertEqual(result['status'], 'PASSED')
        self.assertEqual(result['canonical']['shape'], [15, 36, 20])
        self.assertEqual(result['requirements']['count'], 106)
        self.assertEqual(result['historical_receipts']['scope'], 'HISTORICAL_WINDOWS_SCOPE')
        self.assertEqual(before, (self.bundle / 'vectors.json').read_bytes())

    def test_changed_payload_is_rejected(self):
        module = self.module()
        with (self.bundle / 'matrix.npz').open('ab') as stream:
            stream.write(b'changed')
        with self.assertRaises(ValueError):
            module.verify_repository(self.root)

    def test_changed_numeric_value_is_rejected_even_with_rehashed_payload(self):
        module = self.module()
        import numpy as np
        with np.load(self.bundle / 'matrix.npz', allow_pickle=False) as archive:
            arrays = {name: archive[name].copy() for name in archive.files}
        arrays['vector'][0, 0, 0] = 123
        np.savez(self.bundle / 'matrix.npz', **arrays)
        self.resign_payload('matrix.npz')
        with self.assertRaises(ValueError):
            module.verify_repository(self.root)

    def test_changed_raw_sidecar_is_rejected_even_with_rehashed_payload(self):
        module = self.module()
        sidecar = self.read(DELIVERY / 'results/canonical-features-v2/vectors.json')
        sidecar['cells'][0]['raw_glyph'] = 'ALTERED'
        self.write(DELIVERY / 'results/canonical-features-v2/vectors.json', sidecar)
        self.resign_payload('vectors.json')
        with self.assertRaises(ValueError):
            module.verify_repository(self.root)

    def test_undeclared_source_path_change_is_rejected(self):
        module = self.module()
        sidecar = self.read(DELIVERY / 'results/canonical-features-v2/vectors.json')
        sidecar['source']['path'] = 'a-different-archived-source-path'
        self.write(DELIVERY / 'results/canonical-features-v2/vectors.json', sidecar)
        self.resign_payload('vectors.json')
        with self.assertRaises(ValueError):
            module.verify_repository(self.root)

    def test_escaping_engineering_reference_and_changed_original_are_rejected(self):
        module = self.module()
        current = self.read(DELIVERY / 'current-deliverables.json')
        current['requirements'][0]['engineering_assessment']['evidence_refs'] = ['../outside.json']
        self.write(DELIVERY / 'current-deliverables.json', current)
        with self.assertRaises(ValueError):
            module.verify_repository(self.root)
        current['requirements'][0]['engineering_assessment']['evidence_refs'] = [
            (DELIVERY / 'fixture-evidence.json').as_posix()]
        current['requirements'][0]['original']['status'] = 'FABRICATED_COMPLETION'
        self.write(DELIVERY / 'current-deliverables.json', current)
        with self.assertRaises(ValueError):
            module.verify_repository(self.root)

    def test_receipt_does_not_overwrite_inputs_or_an_existing_file(self):
        module = self.module()
        result = module.verify_repository(self.root)
        with self.assertRaises(ValueError):
            module.write_receipt(result, self.bundle / 'new-receipt.json', self.root)
        output = self.root / 'fresh-receipts/portable.json'
        module.write_receipt(result, output, self.root)
        with self.assertRaises(FileExistsError):
            module.write_receipt(result, output, self.root)
        self.assertEqual(json.loads(output.read_bytes())['status'], 'PASSED')

    def test_script_works_from_its_intended_publication_location(self):
        original = HERE / 'verify_abracadabra.py'
        self.module(original)
        copied = self.root / 'scripts/verify_abracadabra.py'
        copied.parent.mkdir()
        shutil.copyfile(original, copied)
        module = self.module(copied)
        self.assertEqual(module.locate_repo(copied), self.root)
        output = self.root / 'fresh-receipts/copied-script.json'
        with redirect_stdout(io.StringIO()):
            self.assertEqual(module.main(['--output', str(output)]), 0)
        self.assertEqual(json.loads(output.read_bytes())['requirements']['count'], 106)

    def test_actual_legacy_relative_locators_are_adapted_only_at_bound_hashes(self):
        module = self.module()
        names = ('carrier-statistics.json', 'residual-results.json')
        for name in names:
            shutil.copyfile(PROJECT / 'work/ariadne-inverse' / name,
                            self.root / 'work/ariadne-inverse' / name)
        current = self.read(DELIVERY / 'current-deliverables.json')
        current['requirements'][0]['engineering_assessment']['evidence_refs'] = [
            'work/final-day-2026-11-07/../ariadne-inverse/' + name for name in names]
        self.write(DELIVERY / 'current-deliverables.json', current)
        result = module.verify_repository(self.root)
        self.assertEqual(result['status'], 'PASSED')
        self.assertEqual(len(result['requirements']['locator_adaptations']), 2)
        (self.root / 'work/ariadne-inverse/carrier-statistics.json').write_bytes(b'altered')
        with self.assertRaises(ValueError):
            module.verify_repository(self.root)

    def test_unavailable_external_evidence_does_not_erase_catalog_conservation(self):
        module = self.module()
        current = self.read(DELIVERY / 'current-deliverables.json')
        current['requirements'][0]['engineering_assessment']['evidence_refs'] = [
            'https://example.invalid/unretrieved-evidence']
        self.write(DELIVERY / 'current-deliverables.json', current)
        result = module.verify_repository(self.root)
        self.assertEqual(result['status'], 'PARTIAL')
        self.assertTrue(result['requirements']['original_rows_and_statuses_equal'])
        self.assertEqual(result['requirements']['unverified_references'][0]['status'], 'NOT_VERIFIED')


if __name__ == '__main__':
    unittest.main()
