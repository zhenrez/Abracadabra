"""Deterministic table audit and descriptive / blocked control experiment."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import platform
import random
import zlib
from features import FEATURES, parse_ipa, graph_features
from inverse import reconstruct

ROOT=Path(__file__).resolve().parent

def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')

def hashes(root):
    return {str(p.relative_to(root)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((root/'src').glob('*.ts'))}

def eligible(c):
    return (c['role']!='letter_names' and c['parsed']['kind']=='segment' and
            not c['parsed']['alternatives'][0]['segments'][0]['modifiers'])

def majority(values):
    counts=Counter(values)
    return min(counts,key=lambda x:(-counts[x],x))

def blocked_error(cells):
    """Raw segment token error, not coarse-vector error. Family blocks are declared."""
    errors=Counter(); totals=Counter(); folds=[]
    for block in sorted({c['block'] for c in cells}):
        train=[c for c in cells if c['block']!=block]; test=[c for c in cells if c['block']==block]
        global_value=majority([c['ipa'] for c in train])
        by_column=defaultdict(list)
        for c in train: by_column[c['column']].append(c['ipa'])
        predicted={col:majority(v) for col,v in by_column.items()}
        err=Counter()
        for c in test:
            err['column']+=int(predicted.get(c['column'],global_value)!=c['ipa'])
            err['global']+=int(global_value!=c['ipa'])
        errors.update(err); totals[block]=len(test)
        folds.append(dict(block=block,train=len(train),test=len(test),errors=dict(err)))
    n=sum(totals.values())
    return dict(n=n,folds=folds,errors=dict(errors),
                rates={k:v/n for k,v in errors.items()},
                advantage=(errors['global']-errors['column'])/n)

def analyze(data, permutations=199):
    cells=[]
    for c in data['cells']:
        c=dict(c); c['parsed']=parse_ipa(c['ipa']); c['geometry']=graph_features(c['graph']); cells.append(c)
    selected=[c for c in cells if eligible(c)]
    actual=blocked_error(selected)
    rng=random.Random(724036); controls=[]
    # Shuffle complete nonempty column addresses within each script, preserving
    # inventory, missingness support and held-out block membership.
    for _ in range(permutations):
        shuffled=[dict(c) for c in selected]
        for script in sorted({c['script'] for c in shuffled}):
            rows=[c for c in shuffled if c['script']==script]
            columns=[c['column'] for c in rows]; rng.shuffle(columns)
            for c,column in zip(rows,columns): c['column']=column
        controls.append(blocked_error(shuffled)['advantage'])
    vectors=[s for c in cells for a in c['parsed']['alternatives'] for s in a['segments']]
    keys={tuple(s['vector']) for s in vectors}
    raw_tokens={s['ipa'] for s in vectors}
    machine=reconstruct(vectors)
    collisions=defaultdict(set)
    for s in vectors: collisions[tuple(s['vector'])].add(s['ipa'])
    payload=canonical(data)
    return cells,dict(schema='ariadne.measured.v1',source_sha256=hashlib.sha256(payload).hexdigest(),
        source_hash_encoding='canonical JSON UTF-8; file hashes separately in manifest',
        scripts=len({c['script'] for c in cells}),slots=len(cells),populated=sum(c['ipa'] is not None for c in cells),
        kinds=dict(Counter(c['parsed']['kind'] for c in cells)),
        topology_available=sum(c['geometry'] is not None for c in cells),
        segment_occurrences_including_all_alternatives=len(vectors),unique_segment_tokens=len(raw_tokens),
        unique_coarse_vectors=len(keys),coarse_collisions=[sorted(v) for v in collisions.values() if len(v)>1],
        declared_operator_factoring=dict(roots=len(machine['basis']),operators=machine['operators'],
            observations=len(machine['assignments']),coarse_feature_residual_edits=sum(len(a['coarse_feature_edits']) for a in machine['assignments']),
            interpretation=machine['interpretation']),
        serialized_table_bytes=len(payload),zlib_level9_bytes=len(zlib.compress(payload,9)),
        compression_interpretation='JSON compression is descriptive; repeated schema/proxies are included. Not MDL model selection.',
        blocked_column_baseline=actual,
        control=dict(seed=724036,permutations=permutations,statistic='global_error_rate minus column_error_rate',
                     mean_advantage=sum(controls)/len(controls) if controls else None,
                     empirical_upper_tail=(1+sum(x>=actual['advantage'] for x in controls))/(1+len(controls)),
                     scope='exploratory table-alignment diagnostic; blocks are coarse dependencies, not independent historical replicates'),
        exclusions='Missing/unknown/unresolved, English letter names, alternatives, multi-segment values and modified segments excluded from predictive baseline. Full vectors retained.')

def main():
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,default=ROOT/'results'); args=p.parse_args()
    if args.output.exists(): raise SystemExit('Use a new output directory to preserve existing evidence')
    before=hashes(ROOT.parents[1])
    data=json.loads((ROOT/'table.json').read_text(encoding='utf-8'))
    cells,result=analyze(data)
    after=hashes(ROOT.parents[1])
    if before!=after: raise RuntimeError('Source hash changed during execution')
    args.output.mkdir(parents=True)
    for name,value in [('vectors.json',dict(features=FEATURES,cells=cells)),('measured.json',result)]:
        (args.output/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    segments=[s for c in cells for a in c['parsed']['alternatives'] for s in a['segments']]
    (args.output/'basis-operators-residuals.json').write_text(json.dumps(reconstruct(segments),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    bound=sorted(ROOT.glob('*.py'))+[ROOT/'table.json',ROOT/'table.tsv']
    manifest=dict(python=platform.python_version(),src_before=before,src_after=after,src_unchanged=before==after,
                  files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in bound},
                  outputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in args.output.glob('*.json')})
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True,indent=2))

if __name__=='__main__': main()
