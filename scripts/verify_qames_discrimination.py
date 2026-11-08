"""Independent pair-merge enumeration and internal-state verification."""
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'docs/reconstruction/symbol-sound-census'
names = ('Babylonian', 'Jerome', 'Palestinian', 'Secunda', 'Tiberian')
derived = {'Babylonian', 'Tiberian'}

def canonical(t):
    return t if isinstance(t, str) else '(' + ','.join(sorted(map(canonical, t))) + ')'

forests = {tuple(names)}
for _ in range(4):
    next_forests = set()
    for forest in forests:
        for i, j in itertools.combinations(range(len(forest)), 2):
            merged = tuple(sorted((forest[i], forest[j]), key=canonical))
            remainder = [x for k, x in enumerate(forest) if k not in (i, j)]
            next_forests.add(tuple(sorted(remainder + [merged], key=canonical)))
    forests = next_forests

def explicit_minimum(tree):
    edges, internal, tip_states = [], [], {}
    def visit(node):
        key = canonical(node)
        if isinstance(node, str):
            tip_states[key] = int(node in derived)
        else:
            internal.append(key)
            for child in node:
                edges.append((key, canonical(child)))
                visit(child)
    visit(tree)
    root = canonical(tree)
    candidates = []
    for states in itertools.product((0, 1), repeat=len(internal)-1):
        assignment = {**tip_states, root: 0, **dict(zip(internal[1:], states))}
        if all(assignment[a] <= assignment[b] for a, b in edges):
            candidates.append(sum(assignment[b] - assignment[a] for a, b in edges))
    return min(candidates)

independent = {canonical(f[0]): explicit_minimum(f[0]) for f in forests}
output = BASE / 'qames-topology-discrimination.json'
data = json.loads(output.read_text(encoding='utf-8-sig'))

def parse(s):
    # Safe parser for this limited named-leaf Newick, no eval.
    cursor = 0
    def node():
        nonlocal cursor
        if s[cursor] == '(':
            cursor += 1
            left = node()
            assert s[cursor] == ','
            cursor += 1
            right = node()
            assert s[cursor] == ')'
            cursor += 1
            return (left, right)
        start = cursor
        while s[cursor] not in ',);':
            cursor += 1
        return s[start:cursor]
    result = node()
    assert s[cursor:] == ';'
    return result

actual = {canonical(parse(row['tree'])): row for row in data['candidates']}
assert len(actual) == len(data['candidates']) == len(independent) == 105
assert set(actual) == set(independent)
assert sum(n == 1 for n in independent.values()) == 15
assert sum(n == 2 for n in independent.values()) == 90
for key, minimum in independent.items():
    assert actual[key]['minimumIndependentGainsWithoutLoss'] == minimum
    assert actual[key]['singleInnovationNoLossCompatible'] == (minimum == 1)
source = ROOT / data['source']
assert hashlib.sha256(source.read_bytes()).hexdigest() == data['sourceSha256']
receipt = json.loads((BASE / 'qames-discrimination-jev.json').read_text(encoding='utf-8-sig'))
assert receipt['result']['status'] == 'judged'
report = {
    'status': 'passed',
    'method': 'Independent successive-pair forest merges; exhaustive binary internal-state assignments, root fixed to 0, losses forbidden. Does not import tested generator.',
    'counts': {'all': 105, 'oneGain': 15, 'twoGains': 90},
    'checked': ['Exact canonical tree-set equality', 'Every candidate minimum gain count', 'Every candidate one-gain acceptance flag', 'Source SHA256 binding', 'Existing judged Jev receipt'],
    'rootStemAssessment': 'Current mixed tip states force a 0 root under no-loss assumptions, so the implementation is correct for this dataset. Its gains helper would count an implicit stem gain for an all-derived input despite its root-state-0 docstring; it must not be reused for that case without explicit stem semantics.',
    'scope': 'Combinatorial correctness only. Historical character coding, chronology, common inheritance versus parallel innovation/contact, and original sound remain unverified. Counts are not probabilities.',
    'jev': {'newInferenceInvokedByReviewer': False, 'reusedReceipt': 'qames-discrimination-jev.json', 'model': receipt['result']['resolved_model']},
    'inputs': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [output, ROOT / 'scripts/execute_qames_discrimination.py', source]}
}
target = BASE / 'qames-independent-review.json'
target.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
assert json.loads(target.read_text(encoding='utf-8'))['status'] == 'passed'
print(json.dumps({'status': 'passed', 'candidateChecks': 105, 'oneGain': 15, 'twoGains': 90, 'report': str(target)}))
