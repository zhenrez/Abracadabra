"""Lossless source bundles and typed relations; no historical promotion by counting."""
import base64,hashlib,json,zlib
from pathlib import Path
from jsonschema import Draft202012Validator
from dataclasses import dataclass
from typing import Literal

RELATIONS={'identity','order','function','generation','realization','association','contradiction'}
ROLES={'source','user_specification','proxy','hypothesis','derived','unknown'}

def digest(raw):return hashlib.sha256(raw).hexdigest()

def preserve(source_id,raw,locator,role):
    if not source_id or not locator or role not in ROLES:raise ValueError('Source identity, locator and valid role required')
    return dict(id=source_id,locator=locator,role=role,sha256=digest(raw),
                encoding='base64',bytes=base64.b64encode(raw).decode('ascii'))

def restore(source):
    if source['role'] not in ROLES or source['encoding']!='base64':raise ValueError('Invalid source metadata')
    raw=base64.b64decode(source['bytes'],validate=True)
    if digest(raw)!=source['sha256']:raise ValueError('Source hash mismatch')
    return raw

def validate(bundle):
    schema=json.loads(Path(__file__).with_name('evidence.schema.json').read_text(encoding='utf-8'))
    Draft202012Validator(schema).validate(bundle)
    if bundle['schema']!='sun.orientation-evidence.v1':raise ValueError('Unsupported schema')
    ids=[s['id'] for s in bundle['sources']]
    if len(set(ids))!=len(ids):raise ValueError('Duplicate source identity')
    for s in bundle['sources']:restore(s)
    oids=set()
    for o in bundle['observations']:
        if o['id'] in oids:raise ValueError('Duplicate observation')
        oids.add(o['id'])
        if o['source_id'] not in ids or o['role'] not in ROLES:raise ValueError('Unbound observation')
        for key in ('native_system','native_address','literal','uncertainty','witness','historical_time'):
            if key not in o:raise ValueError('Missing observation field: '+key)
    for relation in bundle['relations']:
        if relation['kind'] not in RELATIONS:raise ValueError('Untyped relationship')
        if not relation['source_refs'] or any(s not in ids for s in relation['source_refs']):raise ValueError('Unbound relationship')
        if any(o not in oids for o in (relation['from'],relation['to'])):raise ValueError('Unknown observation endpoint')
    return True

def compress(bundle):
    validate(bundle)
    return zlib.compress(json.dumps(bundle,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8'),9)

def decompress(raw):
    bundle=json.loads(zlib.decompress(raw));validate(bundle);return bundle
