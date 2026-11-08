"""Resolve recorded mathematical evidence through exact immutable versions.

Initial and subsequently observed derived states coexist. Neither version is
promoted to historical truth, and mutable live paths are never a fallback.
"""
from pathlib import Path
from copy import deepcopy
import hashlib
import json


def _bytes(record,root):
    root=Path(root).resolve();path=(root/record['path']).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('Required version snapshot is absent or outside the project')
    if record.get('availability') not in ('VERIFIED','VERIFIED_EXACT_BYTES'):
        raise ValueError('Source version is not verified')
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=record['sha256'] or len(raw)!=record['bytes']:
        raise ValueError('Source version snapshot changed')
    return raw


def resolve_source(reference,registry,project_root,requirement_id):
    matches=[row for row in registry['sources'] if row['original_path']==reference['path']]
    if len(matches)!=1 or reference.get('exists') is not True:
        raise ValueError('Exactly one verified source mapping is required')
    source=matches[0]
    if source['original_sha256']!=reference['sha256'] or requirement_id not in source['per_M_ids']:
        raise ValueError('Source mapping changed the original reference or requirement')
    if source['initial_version']['sha256']!=reference['sha256']:
        raise ValueError('Initial source version does not reproduce the recorded digest')
    if source.get('data_role')!='DERIVED_SCIENTIFIC_STATE':
        raise ValueError('Mathematical source role changed')
    initial=_bytes(source['initial_version'],project_root)
    current=_bytes(source['current_version'],project_root)
    expected='UNCHANGED_INITIAL_BYTES' if initial==current else 'NEWLY_OBSERVED_VERSION'
    if source['version_relation']!=expected:
        raise ValueError('Version relationship disagrees with exact bytes')
    return {'original_reference':deepcopy(reference),'initial_version':deepcopy(source['initial_version']),
            'current_version':deepcopy(source['current_version']),'version_relation':expected,
            'data_role':'DERIVED_SCIENTIFIC_STATE','historical_truth':'NOT_EVALUATED_BY_VERSION_CAPTURE',
            'version_preference':'NO_CANONICAL_OR_SCIENTIFIC_PREFERENCE_ASSERTED'}


def load_registry(path,census,project_root):
    registry=json.loads(Path(path).read_bytes())
    originals=[row for row in census['requirements'] if row['scope']=='original_mathematical_output']
    if registry['requirements_original']!=originals:
        raise ValueError('Version registry altered an original mathematical requirement')
    source=registry['source_census'];root=Path(project_root).resolve()
    census_path=(root/source['snapshot_path']).resolve()
    if not census_path.is_relative_to(root) or not census_path.is_file():
        raise ValueError('Original census snapshot is missing or outside the project')
    raw=census_path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=source['sha256'] or json.loads(raw)!=census:
        raise ValueError('Original census snapshot binding changed')
    expected={item['path'] for row in originals for item in row['evidence']}
    actual=[row['original_path'] for row in registry['sources']]
    if len(actual)!=len(set(actual)) or set(actual)!=expected:
        raise ValueError('Version registry does not cover every original source exactly once')
    for entry in registry['sources']:
        required=sorted(row['id'] for row in originals if any(item['path']==entry['original_path'] for item in row['evidence']))
        if sorted(entry['per_M_ids'])!=required:
            raise ValueError('Version registry changed a mathematical requirement linkage')
    for row in originals:
        for item in row['evidence']:resolve_source(item,registry,project_root,row['id'])
    return registry
