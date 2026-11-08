"""Verify a relocated ARIADNE checkout without rewriting historical evidence.

Only the archived source locator is explicitly adapted for fresh derivation.
This is a new portable check, not a replay of the original Windows proof.
"""
from pathlib import Path, PurePosixPath, PureWindowsPath
from copy import deepcopy
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import platform
import sys

import numpy as np


DELIVERY = Path('work/final-day-2026-11-07')
CANONICAL = DELIVERY / 'results/canonical-features-v2'
BRIDGE = DELIVERY / 'canonical-features/canonical_features.py'
BINDINGS = DELIVERY / 'canonical-features/source-bindings.json'
SOURCE = Path('work/unit001/frozen/source/matrix-message.txt')
PAYLOADS = {'README.md', 'matrix.npz', 'source.tsv', 'summary.json', 'vectors.json'}
IMPORTS = {'work/unit001/evidence.py', 'work/ariadne-inverse/features.py',
           'work/ariadne-inverse/numpy_pipeline.py'}
REFERENCE_ALIASES = {
    'work/final-day-2026-11-07/../ariadne-inverse/carrier-statistics.json':
        'work/ariadne-inverse/carrier-statistics.json',
    'work/final-day-2026-11-07/../ariadne-inverse/residual-results.json':
        'work/ariadne-inverse/residual-results.json'}
PROTECTED = ('work/final-day-2026-11-07', 'work/unit001',
             'work/ariadne-inverse', 'work/unit002', 'work/four-orientations',
             'src', 'scripts', 'tests', 'data', 'archives')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def relative_path(root, value):
    require(isinstance(value, str) and bool(value), 'A relative repository reference is required')
    require('\\' not in value and not PureWindowsPath(value).drive,
            'Drive-qualified or noncanonical repository reference')
    relative = PurePosixPath(value)
    require(not relative.is_absolute() and all(part not in ('.', '..') for part in relative.parts),
            'Repository reference escapes its root')
    root = Path(root).resolve()
    result = root.joinpath(*relative.parts).resolve()
    require(result.is_relative_to(root), 'Repository reference escapes its root')
    return result


def locate_repo(script_path=None):
    start = Path(script_path or __file__).resolve().parent
    for candidate in (start, *start.parents):
        if (candidate / 'package.json').is_file() and (candidate / BRIDGE).is_file():
            return candidate
    raise ValueError('Cannot locate the repository; supply --repo-root explicitly')


class InputSnapshot:
    def __init__(self, root):
        self.root = root
        self.hashes = {}

    def read(self, relative):
        name = Path(relative).as_posix()
        path = relative_path(self.root, name)
        require(path.is_file(), 'Required repository file is absent: ' + name)
        raw = path.read_bytes()
        actual = digest(raw)
        require(name not in self.hashes or self.hashes[name] == actual,
                'Input changed during portable verification: ' + name)
        self.hashes[name] = actual
        return raw

    def json(self, relative):
        return json.loads(self.read(relative))

    def unchanged(self):
        for name, expected in self.hashes.items():
            require(digest(relative_path(self.root, name).read_bytes()) == expected,
                    'Input changed during portable verification: ' + name)


def verify_repository(repo_root):
    root = Path(repo_root).resolve()
    snapshot = InputSnapshot(root)
    snapshot.read('package.json')
    manifest = snapshot.json(CANONICAL / 'manifest.json')
    require(manifest.get('schema') == 'ariadne.canonical-feature-artifacts.v1',
            'Unsupported canonical artifact schema')
    require(set(manifest.get('files', {})) == PAYLOADS, 'Canonical payload inventory changed')
    for name, record in manifest['files'].items():
        raw = snapshot.read(CANONICAL / name)
        require(type(record.get('bytes')) is int and len(raw) == record['bytes']
                and digest(raw) == record['sha256'], 'Canonical payload changed: ' + name)
    sidecar = snapshot.json(CANONICAL / 'vectors.json')
    require(manifest['source'] == sidecar['source'], 'Archived source locator or identity changed')
    require(manifest['method'] == sidecar['method'] and manifest['imports'] == sidecar['imports'],
            'Archived method or import declarations disagree')
    require(manifest['font_proxy'] is None and sidecar['font_proxy'] is None,
            'This portable profile supports the strict no-font artifact only')
    bridge_raw = snapshot.read(BRIDGE)
    bindings_raw = snapshot.read(BINDINGS)
    require(digest(bridge_raw) == sidecar['method']['bridge_sha256']
            and digest(bindings_raw) == sidecar['method']['bindings_sha256'],
            'Bound derivation implementation changed')
    bindings = json.loads(bindings_raw)
    require({item['path'] for item in bindings['imports']} == IMPORTS
            and len(bindings['imports']) == len(IMPORTS), 'Canonical import inventory changed')
    require(bindings['imports'] == sidecar['imports'], 'Bound canonical imports disagree')
    for item in bindings['imports']:
        require(digest(snapshot.read(item['path'])) == item['sha256'],
                'Bound canonical implementation changed: ' + item['path'])
    require(bindings['canonical_source']['path'] == SOURCE.as_posix(),
            'Canonical source reference changed')
    source_raw = snapshot.read(SOURCE)
    require(source_raw == snapshot.read(CANONICAL / 'source.tsv')
            and digest(source_raw) == bindings['canonical_source']['sha256']
            == sidecar['source']['sha256'], 'Canonical original source changed')

    spec = importlib.util.spec_from_file_location('_abracadabra_fresh_canonical', root / BRIDGE)
    require(spec is not None and spec.loader is not None, 'Cannot load the bound canonical builder')
    canonical = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = canonical
    spec.loader.exec_module(canonical)
    fresh = canonical.build_features(source_path=root / SOURCE, font_proxy=None)
    expected_arrays = {name: fresh[name] for name in ('vector', 'mask', 'normalized')}
    expected_arrays.update(
        scripts=np.asarray(fresh['sidecar']['scripts']), columns=np.arange(1, 37),
        cell_ids=np.asarray([cell['cell_id'] for cell in fresh['sidecar']['cells']]).reshape(15, 36),
        value_state=np.asarray([cell['value_state'] for cell in fresh['sidecar']['cells']]).reshape(15, 36))
    with np.load(root / CANONICAL / 'matrix.npz', allow_pickle=False) as archive:
        require(set(archive.files) == set(expected_arrays), 'Canonical array inventory changed')
        for name, expected_array in expected_arrays.items():
            observed = archive[name]
            require(observed.dtype == expected_array.dtype
                    and np.array_equal(observed, expected_array),
                    'Canonical array differs from fresh source derivation: ' + name)
    adapted = deepcopy(sidecar)
    old_locator = adapted['source']['path']
    require(isinstance(old_locator, str) and bool(old_locator), 'Archived source locator is absent')
    adapted['source']['path'] = fresh['sidecar']['source']['path']
    require(adapted == fresh['sidecar'], 'Canonical logical sidecar differs from fresh source derivation')

    census = snapshot.json(DELIVERY / 'audit/deliverables.json')
    current = snapshot.json(DELIVERY / 'current-deliverables.json')
    original = census['requirements']
    rows = current['requirements']
    require(len(original) == len(rows) == 106, 'Original106-row coverage changed')
    require([row['original'] for row in rows] == original, 'An original requirement or status changed')
    require(len({row['id'] for row in original}) == 106, 'Duplicate original requirement identity')
    require(current['original_census_sha256'] == snapshot.hashes[(DELIVERY / 'audit/deliverables.json').as_posix()],
            'Original census hash changed')
    delivery_raw = snapshot.read(DELIVERY / 'results/delivery-receipt.json')
    require(current['delivery_receipt_sha256'] == digest(delivery_raw), 'Current assessment receipt binding changed')
    require(current.get('full_mission_complete') is False, 'Current catalog falsely certifies full mission completion')
    references = set()
    adaptations = {}
    unverified = []
    for row in rows:
        assessment = row['engineering_assessment']
        require(isinstance(assessment.get('status'), str) and bool(assessment['status'])
                and isinstance(assessment.get('remaining_dependencies'), list),
                'Current engineering assessment is incomplete')
        refs = assessment.get('evidence_refs')
        require(isinstance(refs, list) and bool(refs), 'Current evidence references are absent')
        for reference in refs:
            require(isinstance(reference, str) and bool(reference), 'Evidence locator must be a string')
            canonical_reference = REFERENCE_ALIASES.get(reference, reference)
            if reference in REFERENCE_ALIASES:
                expected = {item['sha256'] for original_row in original
                            for item in original_row.get('evidence', ())
                            if item.get('path') == canonical_reference and item.get('exists') is True}
                require(len(expected) == 1, 'Legacy locator lacks a unique original source binding')
                require(digest(snapshot.read(canonical_reference)) == next(iter(expected)),
                        'Legacy locator target differs from its original byte binding')
                entry = adaptations.setdefault(reference, {
                    'supplied_reference': reference, 'canonical_relative_reference': canonical_reference,
                    'source_sha256': next(iter(expected)), 'requirement_ids': [],
                    'method': 'EXPLICIT_HASH_BOUND_LEGACY_RELATIVE_ALIAS'})
                entry['requirement_ids'].append(row['original']['id'])
            elif reference.lower().startswith(('https://', 'http://', 'file://')) or \
                    PureWindowsPath(reference).drive or PurePosixPath(reference).is_absolute():
                unverified.append({'requirement_id': row['original']['id'], 'reference': reference,
                                   'status': 'NOT_VERIFIED', 'reason': 'EXTERNAL_LOCATOR_NOT_READ'})
                continue
            else:
                path = relative_path(root, reference)
                if not path.is_file():
                    unverified.append({'requirement_id': row['original']['id'], 'reference': reference,
                                       'status': 'NOT_VERIFIED', 'reason': 'REPOSITORY_ARTIFACT_UNAVAILABLE'})
                    continue
                snapshot.read(reference)
            references.add(canonical_reference)
    snapshot.unchanged()
    return {
        'schema': 'sun.abracadabra-portable-verification.v1',
        'status': 'PARTIAL' if unverified else 'PASSED', 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'repo_root': str(root),
        'canonical': {'payloads_verified': len(PAYLOADS), 'shape': list(fresh['vector'].shape),
                      'arrays_fresh_equal': list(expected_arrays),
                      'whole_logical_sidecar_equal': True, 'source_sha256': digest(source_raw),
                      'geometry': 'STRICT_UNAVAILABLE',
                      'explicit_adapter': {'field': 'source.path',
                          'archived_locator_sha256': digest(old_locator.encode('utf-8')),
                          'new_repository_relative_locator': SOURCE.as_posix(),
                          'reason': 'Relocated checkout; all other logical fields and exact source bytes unchanged'}},
        'requirements': {'count': 106, 'status': 'PRESERVED', 'original_rows_and_statuses_equal': True,
                         'relative_evidence_references': len(references),
                         'locator_adaptations': [adaptations[name] for name in sorted(adaptations)],
                         'unverified_references': unverified},
        'runtime': {'python': sys.version, 'platform': platform.platform(),
                    'dependencies': {name: importlib.metadata.version(name) for name in ('numpy', 'scipy')}},
        'input_sha256': dict(sorted(snapshot.hashes.items())), 'inputs_unchanged': True,
        'historical_receipts': {'scope': 'HISTORICAL_WINDOWS_SCOPE',
                               'original_proof_reexecuted': False, 'original_receipts_rewritten': False},
        'full_mission_complete': False,
        'scope': 'New source derivation and catalog conservation only; no historical truth, plugin/model execution or original-host proof replay'}


def write_receipt(receipt, output, repo_root):
    root = Path(repo_root).resolve()
    output = Path(output).resolve()
    require(output.suffix.lower() == '.json', 'A new JSON receipt path is required')
    for prefix in PROTECTED:
        require(not output.is_relative_to((root / prefix).resolve()),
                'Receipt output is inside a preserved input area')
    inputs = receipt.get('input_sha256', {})
    require(all(output != relative_path(root, name) for name in inputs),
            'Receipt output would replace an input')
    output.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf-8')
    with output.open('xb') as stream:
        stream.write(raw)
    require(output.read_bytes() == raw, 'Portable receipt readback failed')
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, help='Default: locate repository above this script')
    parser.add_argument('--output', required=True, type=Path, help='New JSON receipt outside preserved input areas')
    args = parser.parse_args(argv)
    try:
        root = args.repo_root.resolve() if args.repo_root is not None else locate_repo()
        result = verify_repository(root)
        output = write_receipt(result, args.output, root)
    except (ValueError, OSError, KeyError, TypeError, ImportError) as error:
        print(json.dumps({'status': 'FAILED', 'error_type': type(error).__name__, 'error': str(error),
                          'original_receipts_rewritten': False}))
        return 1
    print(json.dumps({'status': result['status'], 'receipt': str(output),
                      'canonical_shape': result['canonical']['shape'],
                      'original_requirements': result['requirements']['count'],
                      'original_proof_reexecuted': False}))
    return 0 if result['status'] == 'PASSED' else 2


if __name__ == '__main__':
    raise SystemExit(main())
