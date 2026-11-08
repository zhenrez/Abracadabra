"""Exact-label permutation audit, with explicit partial incidence matrices.

For a bijection p of n positions, M[j,p[j]]=1 and M M^T=I.
For numeric source features X, target features are M@X. For phoneme strings
use source[p] (matrix multiplication is not defined on strings).
If inventories differ, A is a rectangular partial incidence matrix, NOT a
permutation. Unmatched rows stay zero and carry nulls in the index vector.
Non-cyclic permutations are still linear maps; 'Non-Linear Divergence' is
retained only as a requested diagnostic label, not a mathematical assertion.
"""
import argparse,csv,json
from collections import Counter
from pathlib import Path
import numpy as np
from vowel_drift import CARRIER
from features import parse_ipa

def resonance(token):
    parsed=parse_ipa(token)
    if parsed['kind']!='segment':return 'ambiguous_or_sequence'
    s=parsed['alternatives'][0]['segments'][0]
    if not any(s['mask'][:7]):return 'vowel'
    names=['labial','labial','dental_alveolar','postalveolar_palatal','velar','uvular_pharyngeal','glottal']
    return names[int(np.argmax(s['vector'][:7]))]

def cyclic_distance(source,target):
    if len(source)!=len(target) or not source:return None
    distances=[sum(a!=b for a,b in zip(source[k:]+source[:k],target)) for k in range(len(source))]
    best=min(distances)
    return dict(left_shifts=[i for i,d in enumerate(distances) if d==best],minimum_hamming=best,
                exact_rotation=best==0)

def grouping(labels):
    return sum(a==b for a,b in zip(labels,labels[1:]))

def analyze(source,target,seed=22):
    source=list(source);target=list(target)
    if not source or len(set(source))!=len(source) or any(not isinstance(x,str) or not x for x in source):
        raise ValueError('Source must contain unique nonempty phoneme labels')
    if any(x is not None and (not isinstance(x,str) or not x) for x in target):raise ValueError('Invalid target label')
    lookup={s:i for i,s in enumerate(source)}
    indices=[lookup.get(t) for t in target]
    matrix=np.zeros((len(target),len(source)),dtype=int)
    for j,i in enumerate(indices):
        if i is not None:matrix[j,i]=1
    bijection=matrix.shape[0]==matrix.shape[1] and bool(np.all(matrix.sum(0)==1) and np.all(matrix.sum(1)==1))
    if bijection:
        assert np.array_equal(matrix@matrix.T,np.eye(len(source),dtype=int))
        assert list(np.asarray(source)[indices])==target
    classes=[resonance(t) if t is not None else 'missing' for t in target]
    eligible=[c for c in classes if c not in ('missing','ambiguous_or_sequence')]
    observed=grouping(eligible);rng=np.random.default_rng(seed)
    null=[grouping(list(rng.permutation(eligible))) for _ in range(999)]
    rotation=cyclic_distance(source,target)
    return dict(source_count=len(source),target_count=len(target),bijection=bijection,
                permutation_1_based=[i+1 if i is not None else None for i in indices],
                matrix=matrix.tolist(),matrix_type='permutation' if bijection else 'partial_incidence',
                missing_source=[s for s in source if s not in target],
                unmatched_target=[dict(index=i+1,phoneme=t) for i,t in enumerate(target) if t not in lookup],
                duplicate_target={k:v for k,v in Counter(target).items() if v>1 and k is not None},
                rotation=rotation,classification='cyclic' if bijection and rotation['exact_rotation'] else
                  'Non-Linear Divergence: non-cyclic permutation' if bijection else 'inventory divergence: no permutation exists',
                articulatory_classes=classes,grouping=dict(observed_adjacent_same_class=observed,
                  eligible=len(eligible),permutations=999,seed=seed,
                  upper_tail=(1+sum(v>=observed for v in null))/1000,
                  scope='Exploratory adjacency diagnostic after excluding missing/ambiguous values; no liturgical or intentional attribution'))

def load_mapping(path):
    if path.suffix.lower()=='.json':
        value=json.loads(path.read_text(encoding='utf-8'));return value['source'],value['target']
    with path.open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    return [r['source'] for r in rows if r['source']], [r['target'] or None for r in rows]

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args();root=Path(__file__).parent
    if args.input:result=analyze(*load_mapping(args.input))
    else:
        cells=json.loads((root/'table.json').read_text(encoding='utf-8'))['cells']
        names=['Sabaic / South Arabian','Old English (Futhorc)']
        targets={name:[c['ipa'] for c in cells if c['script']==name and c['ipa'] is not None] for name in names}
        result={name:analyze(list(CARRIER.values()),values) for name,values in targets.items()}
        result['between_targets_rotation']=cyclic_distance(*targets.values())
    if args.output:args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True,indent=2))
