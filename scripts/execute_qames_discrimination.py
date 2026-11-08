"""Conditional topology discrimination; not a historical genealogy estimator."""
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/reconstruction/symbol-sound-census'
LABELS = ('Babylonian', 'Jerome', 'Palestinian', 'Secunda', 'Tiberian')
DERIVED = frozenset(('Babylonian', 'Tiberian'))

def trees(labels):
    if len(labels) == 1:
        return [labels[0]]
    result = []
    # Anchor smallest label on the left, eliminating unordered-child duplicates.
    for n in range(len(labels)):
        for rest in itertools.combinations(labels[1:], n):
            left = (labels[0],) + rest
            right = tuple(x for x in labels if x not in left)
            if right:
                result.extend((a, b) for a in trees(left) for b in trees(right))
    return result

def leaves(tree):
    return frozenset([tree]) if isinstance(tree, str) else leaves(tree[0]) | leaves(tree[1])

def clades(tree):
    return [leaves(tree)] if isinstance(tree, str) else [leaves(tree)] + clades(tree[0]) + clades(tree[1])

def gains(tree, at_root=True):
    """Minimum gains on edges, root fixed at 0; no stem change or losses."""
    if at_root:
        if isinstance(tree, str):
            if tree in DERIVED:
                raise ValueError('A derived singleton cannot have root state 0 without a stem edge')
            return 0
        return gains(tree[0], False) + gains(tree[1], False)
    tips = leaves(tree)
    if tips <= DERIVED:
        return 1
    if not tips & DERIVED:
        return 0
    return gains(tree[0], False) + gains(tree[1], False)

def newick(tree):
    return tree if isinstance(tree, str) else '(' + newick(tree[0]) + ',' + newick(tree[1]) + ')'

def main():
    source = OUT / 'phyla-waves-assessment.json'
    assessment = json.loads(source.read_text(encoding='utf-8-sig'))
    feature = next(x for x in assessment['concreteCharacters'] if x['id'] == 'PW-C1')
    assert set(feature['authorReportedDerivedTraditions']) == DERIVED
    assert set(feature['authorReportedUnroundedComparanda']) == set(LABELS) - DERIVED
    candidates = trees(LABELS)
    rows = [{'tree': newick(t) + ';', 'minimumIndependentGainsWithoutLoss': gains(t),
             'singleInnovationNoLossCompatible': DERIVED in clades(t)} for t in candidates]
    assert len(rows) == len({x['tree'] for x in rows}) == 105
    accepted = [r for r in rows if r['singleInnovationNoLossCompatible']]
    assert len(accepted) == 15
    assert all((r['minimumIndependentGainsWithoutLoss'] == 1) == r['singleInnovationNoLossCompatible'] for r in rows)
    assert all(r['minimumIndependentGainsWithoutLoss'] <= 2 for r in rows)
    result = {
        'source': str(source.relative_to(ROOT)),
        'sourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'feature': feature['id'],
        'assumptions': ['Five labelled terminal traditions; rooted fully bifurcating unordered trees',
                        'Author-reported binary states accepted conditionally; ancestral state unrounded',
                        'One irreversible gain, no losses, no contact, no transcription error'],
        'counts': {'allRootedBinaryTrees': 105, 'singleGainNoLoss': 15, 'atMostTwoGainsNoLoss': 105},
        'derivation': 'Five-leaf rooted binary trees: 7!!=105. Contract the two derived leaves to one clade: four-leaf trees, 5!!=15. Two terminal gains fit every tree.',
        'consequence': 'The single-innovation assumption forces only the Babylonian/Tiberian clade. It leaves 15 full topologies; allowing independent terminal innovations restores all 105.',
        'discriminatingEvidenceNeeded': ['Independent relative chronology supporting one shared change',
                                      'Additional independently justified shared innovations',
                                      'Evidence distinguishing contact and scribal normalization from inheritance'],
        'limits': 'Conditional combinatorics, not a probability distribution, proof of historical ancestry, original pronunciation, or exhaustive network search. Polytomies and reticulation are outside this tree universe.',
        'candidates': rows
    }
    target = OUT / 'qames-topology-discrimination.json'
    target.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'passed', 'candidateCount': len(rows), 'compatibleCount': len(accepted), 'output': str(target)}))

if __name__ == '__main__':
    main()
