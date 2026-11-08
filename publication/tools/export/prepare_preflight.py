"""Bind the reviewed publication selection to current bytes; never publish here."""
from pathlib import Path
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[3]
CONTROL = ROOT / 'work/github-delivery-2026-11-07'


def load(path):
    return json.loads(path.read_bytes())


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def write_new(path, value):
    raw = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')
    with path.open('xb') as stream:
        stream.write(raw)
    assert path.read_bytes() == raw


def main():
    inventory = CONTROL / 'inventory-v2/include-candidates.public.jsonl'
    candidates = [json.loads(line) for line in inventory.read_text(encoding='utf-8-sig').splitlines()]
    report = load(CONTROL / 'security/product-scan-v2.LOCAL-ONLY.json')
    assert report['finding_count'] == report['error_count'] == 0
    assert report['status'] == 'NO_PATTERN_HITS_IN_STABLE_OBSERVED_SCOPE'
    scanned = {row['path']: row for row in (json.loads(line) for line in
               (CONTROL / 'security/scanned-files-v2.LOCAL-ONLY.jsonl').read_text(encoding='utf-8-sig').splitlines())}
    skipped = {row['path']: row for row in report['skipped']}
    exclusions = load(CONTROL / 'security/publication-exclusions.LOCAL-ONLY.json')
    excluded = {row['path'] for row in exclusions['files']}
    promoted = load(CONTROL / 'security/publication-promotions.LOCAL-ONLY.json')['files']
    spec = importlib.util.spec_from_file_location('publication_bounded_scanner', CONTROL / 'security/scan_product_candidates.py')
    scanner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scanner)
    approvals = []
    post_scan_rechecks = []
    for row in candidates:
        name = row['path']
        if name in excluded:
            continue
        path = (ROOT / name).resolve()
        assert path.is_relative_to(ROOT) and path.is_file() and not path.is_symlink()
        actual = digest(path)
        checked = scanned[name]
        if actual != checked['sha256']:
            # The shared task updated its current README after the v2 observation.
            # Permit only this explicitly reviewed mutable document, never a
            # silent roll-forward of frozen evidence or numerical inputs.
            assert name == 'README.md' and checked['kind'] == 'TEXT', 'Changed after content scan: ' + name
            raw = path.read_bytes()
            assert hashlib.sha256(raw).hexdigest() == actual
            assert not scanner.scan_text(raw.decode('utf-8-sig'), name, actual)
            post_scan_rechecks.append({'path': name, 'observed_v2_sha256': checked['sha256'],
                'approved_current_sha256': actual, 'method': 'EXPLICIT_CURRENT_README_TEXT_RECHECK',
                'reason': 'Concurrent shared-task README update; original v2 observation remains preserved'})
        if checked['kind'] == 'TEXT':
            assert checked['text_pattern_status'].startswith('NO_HITS')
            method = checked['method']
        else:
            assert name in skipped and checked['decision'].startswith('INCLUDE')
            if checked['kind'] == 'ALL_ZERO_DIAGNOSTIC':
                assert set(path.read_bytes()) <= {0}, 'Nonzero diagnostic: ' + name
                method = 'PRESERVED_ALL_ZERO_FAILURE_DIAGNOSTIC'
            else:
                assert checked['kind'] == 'BINARY_MEDIA_OR_ARRAY', 'Binary role not reviewed: ' + name
                method = 'SOURCE_ROLE_REVIEW_BINARY_NOT_TEXT_SCANNED'
        approvals.append({'path': name, 'sha256': actual, 'status': 'APPROVED', 'method': method})
    for row in promoted:
        path = (ROOT / row['path']).resolve()
        assert path.is_relative_to(ROOT) and path.is_file() and not path.is_symlink()
        actual = digest(path)
        assert actual == row['sha256'], 'Promotion hash changed'
        if path.suffix.lower() not in scanner.BINARY_EXTENSIONS:
            assert not scanner.scan_text(path.read_text(encoding='utf-8-sig'), row['path'], actual)
        approvals.append({'path': row['path'], 'sha256': actual, 'status': 'APPROVED',
                          'method': 'EXPLICIT_PROJECT_SOURCE_OR_LICENSE_REVIEW'})
    assert len({row['path'].casefold() for row in approvals}) == len(approvals)
    preflight = {'schema': 'sun.reviewed-publication-byte-approvals.v1',
                 'files': approvals,
                 'boundary': 'Public-project scope only. No historical certification, blanket licence grant, binary secret guarantee or remote-write authorization.'}
    write_new(CONTROL / 'content-preflight.LOCAL-ONLY.json', preflight)
    write_new(CONTROL / 'promotions.LOCAL-ONLY.json', {'files': promoted})
    write_new(CONTROL / 'exclusions.LOCAL-ONLY.json', exclusions)
    write_new(CONTROL / 'post-scan-rechecks.LOCAL-ONLY.json', {'files': post_scan_rechecks})
    summary = {'status': 'PREPARED_NOT_PUBLISHED', 'approved_files': len(approvals),
               'excluded_candidate_count': len(excluded), 'promoted_files': len(promoted),
               'pattern_scan': {key: report[key] for key in ('scanned_count', 'scanned_bytes', 'finding_count', 'error_count', 'skipped_count')},
               'control_sha256': {name: digest(CONTROL / name) for name in
                    ('content-preflight.LOCAL-ONLY.json', 'promotions.LOCAL-ONLY.json', 'exclusions.LOCAL-ONLY.json')},
               'private_sources_retained_locally': True, 'remote_write_performed': False}
    write_new(CONTROL / 'preflight-summary.public.json', summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()
