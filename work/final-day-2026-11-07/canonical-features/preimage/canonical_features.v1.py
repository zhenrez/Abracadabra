"""Canonical G0 → existing15D IPA/5D geometry adapter, with literal sidecars."""
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
import hashlib
import importlib.util
import io
import json
import sys
import zipfile

import numpy as np

PROJECT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BINDINGS = HERE / 'source-bindings.json'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + '\n').encode('utf-8')


def plain(value):
    if isinstance(value, Mapping):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    return value


def locked_inputs():
    lock = json.loads(BINDINGS.read_bytes())
    for record in lock['imports']:
        if digest((PROJECT / record['path']).read_bytes()) != record['sha256']:
            raise ValueError('Reused implementation changed: ' + record['path'])
    return lock


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError('Cannot load bound implementation')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclass annotations require a registered module
    spec.loader.exec_module(module)
    return module


def reused_modules(lock):
    paths = [PROJECT / item['path'] for item in lock['imports']]
    g0 = load_module('_ariadne_canonical_g0', paths[0])
    articulation = load_module('_ariadne_canonical_ipa', paths[1])
    # The legacy adapter imports "features". Bind that dependency only while
    # loading, then restore the caller's namespace; its function retains the
    # correct parser object without changing unrelated imports in the process.
    previous = sys.modules.get('features')
    sys.modules['features'] = articulation
    try:
        pipeline = load_module('_ariadne_canonical_numpy', paths[2])
    finally:
        if previous is None:
            sys.modules.pop('features', None)
        else:
            sys.modules['features'] = previous
    return g0, articulation, pipeline


def build_features(source_path=None, font_proxy=None):
    lock = locked_inputs()
    source_path = Path(source_path) if source_path is not None else PROJECT / lock['canonical_source']['path']
    raw = source_path.read_bytes()
    if digest(raw) != lock['canonical_source']['sha256']:
        raise ValueError('Source differs from the frozen canonical G0 matrix')
    g0, articulation, pipeline = reused_modules(lock)
    graph = g0.import_matrix(raw, str(source_path.resolve()))
    if len(graph.cells) != 540 or len(graph.grid.script_labels) != 15:
        raise ValueError('Canonical15×36 grid required')
    witness = {item.raw_cell_id: item for item in graph.witnesses}
    vector = np.zeros((15, 36, 20), dtype=np.float64)
    mask = np.zeros((15, 36, 20), dtype=bool)
    font = pipeline.FontGeometry(font_proxy) if font_proxy is not None else None
    font_meta = None if font is None else {
        'path': str(font.path.resolve()), 'sha256': font.sha256,
        'size': font.size, 'threshold': 128,
        'scope': 'MODERN_FONT_PROXY_ONLY; no historical glyph topology claim'}
    cells = []
    for index, cell in enumerate(graph.cells):
        row, column = divmod(index, 36)
        typed = witness.get(cell.cell_id)
        phonetic_type = typed.phonetic_type.value if typed is not None else None
        parsed = None
        if not cell.glyph:
            state = 'BLANK'
        elif phonetic_type == 'LETTER_NAME':
            state = 'LETTER_NAME_EXCLUDED'
        else:
            parsed = articulation.parse_ipa(cell.ipa)
            state = {'unknown': 'UNKNOWN_VALUE', 'unresolved_label': 'UNRESOLVED_LABEL',
                     'segment': 'ATOMIC_VALUE', 'sequence': 'SEQUENCE_VALUE',
                     'alternatives': 'ALTERNATIVE_VALUES'}[parsed['kind']]
            if parsed['kind'] == 'segment':
                atom = parsed['alternatives'][0]['segments'][0]
                vector[row, column, :15] = atom['vector']
                mask[row, column, :15] = atom['mask']
        geometry = None
        if font is not None and cell.glyph:
            result = font(cell.glyph)
            if result is not None:
                values, metadata = result
                values = np.asarray(values, dtype=float)
                if values.shape != (5,) or not np.isfinite(values).all() or np.any(values < 0):
                    raise ValueError('Invalid font-proxy geometry')
                vector[row, column, 15:] = values
                mask[row, column, 15:] = True
                geometry = {**metadata, 'raw_glyph': cell.glyph,
                            'unicode_scalars': list(map(ord, cell.glyph)), 'font': font_meta}
        cells.append({
            'cell_id': cell.cell_id, 'record_id': typed.record_id if typed is not None else None,
            'script_id': cell.script_id, 'script_label': cell.script_label,
            'local_ordinal': cell.ordinal, 'raw_glyph': cell.glyph,
            'raw_ipa': cell.ipa, 'raw_english': cell.english,
            'blank_fields': list(cell.blank_fields), 'coordinates': plain(cell.coordinates),
            'phonetic_type': phonetic_type,
            'glyph_type': typed.glyph_type.value if typed is not None else None,
            'claim_refs': list(typed.claim_refs) if typed is not None else [],
            'value_state': state, 'parsed_ipa': parsed, 'geometry': geometry})
    normalized = pipeline.normalize_vectors(vector)
    if not pipeline.validate_normalized(normalized):
        raise ValueError('Legacy normalization validation failed')
    sidecar = {
        'schema': 'ariadne.canonical-feature-bridge.v1',
        'source': {'path': str(source_path.resolve()), 'sha256': digest(raw),
                   'artifact_id': graph.source.artifact_id,
                   'role': 'USER_SUPPLIED_COMPARATIVE_DATASET'},
        'imports': lock['imports'], 'scripts': list(graph.grid.script_labels),
        'feature_names': list(articulation.FEATURES) + list(pipeline.G_NAMES),
        'method': {'version': 'canonical-v1', 'bridge_sha256': digest(Path(__file__).read_bytes()),
                   'bindings_sha256': digest(BINDINGS.read_bytes()),
                   'numpy_version': np.__version__,
                   'normalization': 'Existing normalize_vectors; zero norms remain zero',
                   'segmentation': 'Existing literal IPA parser; no new affricate/diphthong boundaries',
                   'unicode': 'Raw strings unchanged; legacy NFC applies only to derived IPA parsing',
                   'english': 'Letter names excluded from phonemic vectors and segment parsing'},
        'font_proxy': font_meta, 'cells': cells}
    bundle = {'vector': vector, 'mask': mask, 'normalized': normalized,
              'sidecar': sidecar, 'source_bytes': raw}
    verify_bindings(bundle)
    return bundle


def verify_bindings(bundle):
    lock = locked_inputs()
    sidecar = bundle['sidecar']
    if sidecar['imports'] != lock['imports']:
        raise ValueError('Declared import bindings changed')
    if digest(bundle['source_bytes']) != lock['canonical_source']['sha256'] or sidecar['source']['sha256'] != lock['canonical_source']['sha256']:
        raise ValueError('Canonical source binding changed')
    if sidecar['method']['bridge_sha256'] != digest(Path(__file__).read_bytes()) or sidecar['method']['bindings_sha256'] != digest(BINDINGS.read_bytes()):
        raise ValueError('Bridge implementation/binding manifest changed')
    font = sidecar['font_proxy']
    if font is not None and digest(Path(font['path']).read_bytes()) != font['sha256']:
        raise ValueError('Font proxy changed')
    for name in ('vector', 'mask', 'normalized'):
        if bundle[name].shape != (15, 36, 20):
            raise ValueError('Canonical feature-array shape changed')
    return True


def deterministic_npz(arrays):
    result = io.BytesIO()
    with zipfile.ZipFile(result, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, array in sorted(arrays.items()):
            if array.dtype.hasobject:
                raise ValueError('Object arrays cannot enter the numeric archive')
            payload = io.BytesIO()
            np.lib.format.write_array(payload, np.asarray(array), allow_pickle=False)
            entry = zipfile.ZipInfo(name + '.npy', date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o600 << 16
            archive.writestr(entry, payload.getvalue(), compresslevel=9)
    return result.getvalue()


def write_features(bundle, output):
    verify_bindings(bundle)
    output = Path(output)
    if output.exists():
        raise ValueError('Use a new output directory; existing artifacts are preserved')
    data = bundle['sidecar']
    states = Counter(item['value_state'] for item in data['cells'])
    arrays = {key: bundle[key] for key in ('vector', 'mask', 'normalized')}
    arrays.update(scripts=np.asarray(data['scripts']), columns=np.arange(1, 37),
                  cell_ids=np.asarray([item['cell_id'] for item in data['cells']]).reshape(15, 36),
                  value_state=np.asarray([item['value_state'] for item in data['cells']]).reshape(15, 36))
    summary = {'shape': [15, 36, 20], 'positions': len(data['cells']),
               'populated': sum(bool(item['raw_glyph']) for item in data['cells']),
               'value_states': dict(sorted(states.items())),
               'atomic_sound_cells': int(bundle['mask'][:, :, :15].any(axis=-1).sum()),
               'geometry_cells': int(bundle['mask'][:, :, 15:].any(axis=-1).sum()),
               'geometry_scope': 'STRICT_UNAVAILABLE' if data['font_proxy'] is None else 'EXPLICIT_MODERN_FONT_PROXY',
               'source_sha256': data['source']['sha256'],
               'missing_policy': 'Zero plus false mask; all-zero cosine is undefined, not evidence of similarity',
               'distance_policy': 'Compare only jointly available features of compatible phonetic types; no name-to-phoneme projection'}
    readme = ('# Canonical feature artifacts\n\n'
              'The exact G0 table supplies540positions. matrix.npz contains15×36×20vectors, masks, unit/zero normalized vectors and stable addresses. '
              'vectors.json retains every glyph, supplied IPA, English approximation and original source coordinates, including159blanks. '
              'Ordered alternatives and sequences preserve native15Datomic segment data without averaging them. English letter names remain excluded from phonemic vectors.\n\n'
              'Default geometric values are zero with false masks because no actual historical glyph images were supplied. '
              'An explicitly selected font proxy is identified by its byte hash and exact glyph; it never establishes historical topology. '
              'source.tsv preserves the original bytes. manifest.json binds all derived files and imported implementations.\n\n'
              'The existing coarse articulatory dictionary and literal segmentation conventions are reused unchanged. '
              'Feature similarity is not a historical relationship, inferred original sound, frequency or root-state-machine proof.\n')
    payloads = {'matrix.npz': deterministic_npz(arrays), 'vectors.json': json_bytes(data),
                'summary.json': json_bytes(summary), 'source.tsv': bundle['source_bytes'],
                'README.md': readme.encode('utf-8')}
    manifest = {'schema': 'ariadne.canonical-feature-artifacts.v1', 'source': data['source'],
                'imports': data['imports'], 'method': data['method'], 'font_proxy': data['font_proxy'],
                'files': {name: {'sha256': digest(raw), 'bytes': len(raw)} for name, raw in sorted(payloads.items())}}
    output.mkdir(parents=True)
    for name, raw in payloads.items():
        (output / name).write_bytes(raw)
    (output / 'manifest.json').write_bytes(json_bytes(manifest))
    return manifest
