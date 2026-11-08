"""Read-only native-source binding and finite group audit selected by Jev receipts12/16/25.

Never executes source-archive code, changes a source file, selects an orientation,
or treats a filename/status label as historical or scientific authority.
"""
from __future__ import annotations
import argparse
import collections
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import re
import sqlite3
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
HELPER = Path(r'C:\Users\Brend\.codex\plugins\cache\created-by-me-remote\prumo-jev-research\0.1.0\skills\evidence-audit\scripts\evidence_ledger.py')
TARGETS = {
    'certification': '9616124f92d51e2342446cafb50f81f71c7985dee46a052967d3b49f9eb42192',
    'matched_nulls': '5ed603b0c5dd0dd7444edc0e4040093e328b8e4d08e80c1b65e944317845d6ee',
    'generative_graph': '6a92f9710fa6cd2937b9b07c42315b7d9c80644bd453c659f17318f95c55f95d',
    'scientific_alphabet': '07f849ec545a55675acc9b7c134f333a90950ed752a4edb732cc93f08df4e738',
    'structural_graph': '3b2ee9687e5ae5561d3f821db07cbe7b39d9cdfae53c606ba0e9b9f77b771d54',
    'mutation_chronology': 'def5acfb2239f58fe91efbdab0096feba38a6d3e0a18a9ca20bf1e0e950dff94',
    'orientation_atlas': 'f07f6e78ad08c09559939d044f382c5fb15a88ca56d10f2a6f5d060475e908fb',
}
USER_MESSAGE = '08dbd85010d050b40c2009adf74b1610fda6794d26cb34adf091765e9c2b5844'

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def load(path: Path):
    return json.loads(path.read_bytes().decode('utf-8-sig'))

def save(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def collect(output: Path):
    con = sqlite3.connect(f'file:{(ROOT / "data/sunny.sqlite").as_posix()}?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    groups = {}
    for name, digest in TARGETS.items():
        copies = [dict(r) for r in con.execute('SELECT * FROM sources WHERE sha256=? ORDER BY path', (digest,))]
        if not copies:
            raise ValueError(f'known source not indexed: {name}')
        groups[name] = {'sha256': digest, 'copies': copies, 'independence': 'byte-identical occurrences, not independent corroboration'}
    user = con.execute('SELECT m.*,c.title,c.native_id conversation_native_id,s.path,s.original_path,s.sha256 source_sha256 FROM messages m JOIN conversations c ON c.id=m.conversation_id JOIN sources s ON s.id=m.source_id WHERE m.id=?', (USER_MESSAGE,)).fetchone()
    if not user:
        raise ValueError('historical user passage not indexed')
    user = dict(user)
    names = ('SUN_GG_v1_final.lock.json', 'SUN_Scientific_Music_Alphabet_v1.lock.json', 'SUN_36_Fiber_Frozen_Mechanism_Execution_v0.1.json', 'SUN_Frozen_Core_Invariant_Mechanism_Audit_v0.1.json')
    supporting = []
    for name in names:
        supporting.extend(dict(r) for r in con.execute('SELECT * FROM sources WHERE path LIKE ? ORDER BY path', ('%' + name,)))
    gd = load(Path(groups['structural_graph']['copies'][0]['path']))
    binding_leaves = []
    for field, digest in gd['binding'].items():
        matches = [dict(r) for r in con.execute('SELECT * FROM sources WHERE sha256=? ORDER BY path', (digest,))]
        binding_leaves.append({'binding_field': field, 'sha256': digest, 'copies': matches, 'status': 'recovered' if matches else 'NOT_RETRIEVED_IN_INDEXED_SOURCE_HASHES'})
    con.close()
    catalog = {'schema': 'sunny.native-source-catalog.v1', 'groups': groups, 'supporting': supporting, 'structural_graph_binding_leaves': binding_leaves, 'original_user_message': user,
               'governing_decisions': ['state/jev-receipts/000012-6e58a4c2fb92.json', 'state/jev-receipts/000016-1d2c69d2eba3.json', 'state/jev-receipts/000025-807db4173776.json'],
               'scope': 'literal source inventory; no canonical ontology or scientific authority assigned'}
    save(output, catalog)
    print(json.dumps({'catalog': str(output), 'groups': {k: len(v['copies']) for k, v in groups.items()}, 'supporting_occurrences': len(supporting), 'role': user['role']}))

def add(x, y):
    return ((x[0] + y[0]) % 12, (x[1] + y[1]) % 6)

def closure(generators):
    found = {(0, 0)}
    frontier = [(0, 0)]
    while frontier:
        x = frontier.pop()
        for generator in generators:
            y = add(x, generator)
            if y not in found:
                found.add(y)
                frontier.append(y)
    return found

def order(x):
    return math.lcm(12 // math.gcd(x[0], 12), 6 // math.gcd(x[1], 6))

def helper(operation, value):
    run = subprocess.run([sys.executable, str(HELPER), operation], input=json.dumps(value, ensure_ascii=False), text=True, encoding='utf-8', capture_output=True, timeout=20)
    if run.returncode:
        raise RuntimeError(f'Prumo {operation} failed: {run.stdout} {run.stderr}')
    result = json.loads(run.stdout)
    if result.get('ok') is not True:
        raise ValueError(result)
    return result

def passage(source_id, path, quote, objective_id, occurrence=None):
    text = path.read_bytes().decode('utf-8')  # Preserve mixed LF/CRLF and Unicode exactly.
    snapshot = helper('init-source', {'source_id': source_id, 'locator': str(path), 'text': text})['source']
    assert snapshot['sha256_utf8'] == sha(path.read_bytes())
    args = {'source': snapshot, 'objective': {'objective_id': objective_id, 'question': 'Verify this exact original passage and its source coordinate; factual support remains separately assessed.'}, 'quote': quote}
    if occurrence is not None:
        start, end = occurrence
        assert text[start:end] == quote
        args['source_offsets_utf16'] = [len(text[:start].encode('utf-16-le')) // 2, len(text[:end].encode('utf-16-le')) // 2]
    located = helper('locate', args)
    validation = helper('validate', {'source': snapshot, 'evidence': located['evidence']})
    assert located['evidence']['status'] == 'located' and validation['valid']
    return {'source_snapshot': snapshot, 'locate': located, 'validation': validation}

def check(catalog_path: Path, output: Path):
    catalog = load(catalog_path)
    input_observations = []
    seen_paths = set()
    records = [r for g in catalog['groups'].values() for r in g['copies']] + catalog['supporting']
    records += [r for leaf in catalog['structural_graph_binding_leaves'] for r in leaf['copies']]
    for record in records:
        p = Path(record['path'])
        if str(p) in seen_paths:
            continue
        seen_paths.add(str(p))
        actual = sha(p.read_bytes())
        assert actual == record['sha256'], f'source hash mismatch {p}'
        input_observations.append({'source_id': record['id'], 'path': str(p), 'expected_sha256': record['sha256'], 'actual_sha256': actual, 'matches': True})
    obj = {name: load(Path(group['copies'][0]['path'])) for name, group in catalog['groups'].items() if name not in ('mutation_chronology', 'orientation_atlas')}
    gg, cert, alphabet = obj['generative_graph'], obj['certification'], obj['scientific_alphabet']
    bound = [
        {'edge': 'certification -> GG', 'expected': cert['frozen_bindings']['graph_sha256'], 'actual': TARGETS['generative_graph']},
        {'edge': 'certification -> alphabet', 'expected': cert['frozen_bindings']['alphabet_sha256'], 'actual': TARGETS['scientific_alphabet']},
        {'edge': 'GG -> structural graph', 'expected': gg['bindings']['source_graph_sha256'], 'actual': TARGETS['structural_graph']},
        {'edge': 'GG -> alphabet', 'expected': gg['bindings']['alphabet_sha256'], 'actual': TARGETS['scientific_alphabet']},
    ]
    for record in catalog['supporting']:
        p = Path(record['path']); data = load(p)
        if p.name == 'SUN_GG_v1_final.lock.json':
            bound.extend([{'edge': record['id'] + ' -> GG', 'expected': data['sha256'], 'actual': TARGETS['generative_graph']}, {'edge': record['id'] + ' -> alphabet', 'expected': data['alphabet_sha256'], 'actual': TARGETS['scientific_alphabet']}])
        elif p.name == 'SUN_Scientific_Music_Alphabet_v1.lock.json':
            bound.append({'edge': record['id'] + ' -> alphabet', 'expected': data['sha256'], 'actual': TARGETS['scientific_alphabet']})
    assert all(edge['expected'] == edge['actual'] for edge in bound)
    addresses = gg['address_projection']['addresses']
    states = {(a['pitch_class'], a['phase']) for a in addresses}
    assert len(states) == len(addresses) == gg['address_projection']['count'] == 72
    assert states == set(itertools.product(range(12), range(6)))
    assert len({a['address_id'] for a in addresses}) == 72
    assert all(a['index_12x6'] == [a['pitch_class'], a['phase']] for a in addresses)
    B = lambda x: add(x, (0, 3))
    T = lambda x: add(x, (0, 4))
    ordered = [(x, B(x)) for x in sorted(states)]
    fibers = sorted({tuple(sorted(pair)) for pair in ordered})
    graph_orbits = []
    unvisited = set(states)
    while unvisited:
        start = min(unvisited); reached = {start}; frontier = [start]
        while frontier:
            x = frontier.pop(); y = B(x)
            if y not in reached: reached.add(y); frontier.append(y)
        graph_orbits.append(tuple(sorted(reached))); unvisited.difference_update(reached)
    assert sorted(graph_orbits) == fibers
    multiplicity = collections.Counter(x for fiber in fibers for x in fiber)
    assert len(fibers) == 36 and set(multiplicity) == states and set(multiplicity.values()) == {1}
    assert all(len(f) == 2 for f in fibers)
    assert all(B(B(x)) == x and B(x) != x and T(T(T(x))) == x and T(x) != x and B(T(x)) == T(B(x)) for x in states)
    assert {len(states - set(f)) for f in fibers} == {70}
    crt = {(p, q): (p, q % 3, q % 2) for p, q in states}
    assert len(set(crt.values())) == 72
    assert all(crt[B(x)] == (crt[x][0], crt[x][1], (crt[x][2] + 1) % 2) and crt[T(x)] == (crt[x][0], (crt[x][1] + 1) % 3, crt[x][2]) for x in states)
    # Literal table parsing is separate from independently generating the qualifying family.
    atlas_record = catalog['groups']['orientation_atlas']['copies'][0]
    atlas_path = Path(atlas_record['path']); atlas = atlas_path.read_bytes().decode('utf-8')
    section = re.search(r'### 4\.2 Retain the declared angular steps.*?(?=### 4\.3)', atlas, re.S)
    if not section: raise ValueError('original atlas section4.2 missing')
    table_rows = []
    for m in re.finditer(r'^\| ([0-5]) \| ([0-5]) \| ([0-5]) \|\s*$', section[0], re.M):
        # Consume only the table row, not the following newline/blank line.
        literal = m[0].rstrip('\r\n')
        start = section.start() + m.start(); end = start + len(literal)
        b, d1, d5 = map(int, m.groups())
        table_rows.append({'b': b, 'd_for_O1': d1, 'd_for_O5': d5, 'literal_row': literal, 'line': atlas.count('\n', 0, start) + 1, 'codepoint_offsets': [start, end]})
    assert len(table_rows) == 6 and [r['b'] for r in table_rows] == list(range(6))
    completions = []
    for row in table_rows:
        for expected_o, key in [(1, 'd_for_O1'), (5, 'd_for_O5')]:
            b, d = row['b'], row[key]; R, L = (5, b), (7, d)
            reached = closure((R, L)); assert len(reached) == 72 and (b + d) % 6 == expected_o
            completions.append({'id': f'atlas-b{b}-d{d}', 'R': list(R), 'L': list(L), 'O': [0, expected_o], 'source_id': atlas_record['id'], 'source_sha256': TARGETS['orientation_atlas'], 'source_line': row['line'], 'literal_table_row': row['literal_row'], 'inherited_status': 'recovered optional transitive family; not absolute orientation', 'fresh_check': {'generated_states': len(reached), 'R_order': order(R), 'L_order': order(L), 'O_order': order(add(R, L)), 'O_cubed_equals_B': add(add(add(R, L), add(R, L)), add(R, L)) == (0, 3)}, 'canonical_selected': False})
    phase_choices = [{'b': b, 'd': d, 'generated_states': len(closure(((5, b), (7, d))))} for b, d in itertools.product(range(6), repeat=2)]
    passing = {(x['b'], x['d']) for x in phase_choices if x['generated_states'] == 72}
    assert passing == {(x['R'][1], x['L'][1]) for x in completions} and len(passing) == 12
    phase_preserving = closure(((5, 0), (7, 0)))
    assert len(phase_preserving) == 12
    pair_classes = collections.Counter(); tested_pairs = 0; generated_pairs = 0
    determinant_disagreements = []
    for R, L in itertools.product(sorted(states), repeat=2):
        tested_pairs += 1; transitive = len(closure((R, L))) == 72
        determinant = math.gcd(R[0] * L[1] - R[1] * L[0], 6) == 1
        if transitive != determinant: determinant_disagreements.append([R, L])
        if transitive: generated_pairs += 1; pair_classes[(order(R), order(L), order(add(R, L)))] += 1
    assert tested_pairs == 5184 and generated_pairs == 1152 and not determinant_disagreements
    assert dict(pair_classes) == {(6, 12, 12): 384, (12, 6, 12): 384, (12, 12, 6): 384}
    # Exhaustive bijection test for the declared fixed-label C6 -> C3 x C2 null.
    pairs = tuple(itertools.product(range(3), range(2)))
    isomorphisms = []
    for perm in itertools.permutations(pairs):
        if all(perm[(a + b) % 6] == ((perm[a][0] + perm[b][0]) % 3, (perm[a][1] + perm[b][1]) % 2) for a in range(6) for b in range(6)):
            isomorphisms.append(perm)
    assert len(isomorphisms) == 2
    scalar = {'R': Fraction(2, 3), 'L': Fraction(3, 4), 'O': Fraction(1, 2)}
    assert scalar['R'] * scalar['L'] == scalar['O']
    assert (1 / scalar['R']) * (1 / scalar['L']) == 2
    assert (scalar['R'] ** 3) / ((1 / scalar['L']) ** 3) == Fraction(1, 8)
    alphabet_classes = collections.Counter(entry['role_class'] for entry in alphabet['entries'])
    assert len(alphabet['entries']) == alphabet['count'] == 22
    assert alphabet_classes == {'CONSTITUTIVE_CONSTRUCTOR': 3, 'TRANSITION_ACTION': 7, 'STRUCTURAL_RELATION': 12}
    # Historical role record is an exported Markdown Prompt, not a native ChatGPT UUID.
    user = catalog['original_user_message']; user_path = Path(user['path'])
    assert sha(user_path.read_bytes()) == user['source_sha256'] and user['role'] == 'user'
    text = user_path.read_bytes().decode('utf-8')
    block = re.search(r'^## Prompt:\s*\r?\n9/30/2026, 2:21:53 PM.*?(?=^## Response:)', text, re.M | re.S)
    if not block: raise ValueError('exact original user Prompt boundary missing')
    quote = '**run W72 against this frozen hypergraph, run matched nulls, and then start throwing independent systems at SUN under the frozen prediction protocol.**'
    qstart = text.index(quote, block.start(), block.end())
    helper_before = sha(HELPER.read_bytes())
    user_passage = passage(user['source_id'], user_path, quote, 'NATIVE-USER-AUTHORITY', (qstart, qstart + len(quote)))
    tstart = section.start() + section[0].index('| R phase b |')
    tend = table_rows[-1]['codepoint_offsets'][1]
    atlas_passage = passage(atlas_record['id'], atlas_path, atlas[tstart:tend], 'NATIVE-12-COMPLETION-TABLE', (tstart, tend))
    cert_record = catalog['groups']['certification']['copies'][0]
    selector_passage = passage(cert_record['id'], Path(cert_record['path']), 'frozen SUN graph does not independently distinguish which of the 36 fibers is the exceptional pair', 'NATIVE-SELECTOR-LIMIT')
    assert helper_before == sha(HELPER.read_bytes())
    failures_path = ROOT / 'docs/evidence/wolfram-orbit-input-error.json'
    old = load(failures_path)
    assert old['status'] == 'wrong_expression_for_unordered_B_orbits'
    result = {
        'schema': 'sunny.native-kernel-audit.v1', 'outcome': 'implementation and finite assertions verified in stated explicit ranges',
        'source_binding_edges': bound, 'source_byte_checks': input_observations,
        'inherited_claims': {'certification': cert, 'matched_nulls': obj['matched_nulls'], 'GG_projection_status': gg['address_projection']['status'], 'GG_limits': gg['limits'], 'structural_graph_limits': obj['structural_graph']['limits'], 'role_status': 'historical source assertions; not a new Jev endorsement or global proof'},
        'new_finite_checks': {'states': len(states), 'ordered_B_pairs': len(ordered), 'unordered_B_orbits': len(fibers), 'all_orbits_size': 2, 'partition_disjoint_and_exhaustive': True, 'B_order_two_no_fixed_points': True, 'T_order_three_no_fixed_points': True, 'T_B_commute': True, 'crt_bijection_and_actions_verified': True, 'removing_any_orbit_leaves': 70, 'possible_orbits_to_remove': 36, 'unique_exceptional_orbit_selected': False, 'fibers': [[list(x) for x in f] for f in fibers], 'alphabet_count': 22, 'alphabet_partition': dict(alphabet_classes), 'scalar_exact': {k: str(v) for k, v in scalar.items()}, 'scalar_RL': str(scalar['R'] * scalar['L']), 'scalar_inverse_product': '2', 'scalar_quarter_turn_path_ratio': '1/8'},
        'recovered_completions': completions,
        'new_completion_checks': {'tested_phase_choices': 36, 'transitive_phase_choices': 12, 'source_table_equals_independent_transitive_subset': True, 'all_phase_choices': phase_choices, 'tested_full_ordered_translation_pairs': tested_pairs, 'transitive_full_pairs': generated_pairs, 'determinant_criterion_disagreements': determinant_disagreements, 'order_classes': [{'orders': list(k), 'count': v} for k, v in sorted(pair_classes.items())], 'separate_phase_preserving_profile': {'R': [5, 0], 'L': [7, 0], 'O': [0, 0], 'orbit_size': len(phase_preserving), 'coset_orbits': 6, 'not_rejected_by_optional_transitivity': True}, 'global_orientation_winner': None},
        'matched_null_reproduction': {'all_label_bijections': 720, 'isomorphisms': 2, 'identity_fixed_bijections': 120, 'unconditional_fixed_label_mass': str(Fraction(2, 720)), 'identity_fixed_mass': str(Fraction(2, 120)), 'perfect_matchings_six_labeled_states': math.prod([1, 3, 5]), 'interpretation': 'exact counts under declared uniform finite label choices; not discovery p-values or historical-likelihood estimates'},
        'authority_passage': {'message_id': user['id'], 'parsed_role': user['role'], 'importer_ordinal': user['native_id'], 'native_chatgpt_message_uuid': None, 'source_id': user['source_id'], 'source_sha256': user['source_sha256'], 'original_export_locator': user['locator'], 'original_chat_url': 'https://chatgpt.com/c/6abcc244-5a80-83ea-8472-297ea3b081fe', 'scope': 'user authorized downstream test of the frozen report in that historical turn; not blanket approval of all later claims'},
        'passage_audits': {'user_original': user_passage, 'atlas_table': atlas_passage, 'certification_selector_limit': selector_passage},
        'failed_prior_check': {'path': str(failures_path), 'sha256': sha(failures_path.read_bytes()), 'status': old['status'], 'returned_count': 72, 'interpretation': 'outer-table sorting retained pair direction; an implementation error, not a counterexample to unordered-orbit count'},
        'corrected_independent_wolfram': {'path': 'docs/evidence/native-wolfram-orbits-corrected.json', 'sha256': sha((ROOT / 'docs/evidence/native-wolfram-orbits-corrected.json').read_bytes()), 'unordered_orbits': 36},
        'external_helper': {'path': str(HELPER), 'sha256_before': helper_before, 'sha256_after': sha(HELPER.read_bytes()), 'version': 'Prumo + Jev Research0.1.0/evidence-audit', 'executed_operations': ['init-source', 'locate', 'validate']},
        'software': {'python': platform.python_version(), 'implementation': platform.python_implementation(), 'arithmetic': 'exact Python integers and fractions.Fraction', 'randomness': 'none'},
        'non_claims': ['No unique absolute or exceptional-fiber orientation established', 'No recovery or proof of the original music-native70/72 derivation is claimed', 'No model probability or combinatorial reference mass is a calibrated domain probability', 'No original exported user Prompt is relabeled as a native message UUID', 'No archive script executed', 'No global acoustic, geometric, theological or deterministic-spacetime conclusion', 'Byte-identical copies are occurrences, not independent corroboration'],
    }
    save(output, result)
    print(json.dumps({'outcome': result['outcome'], 'states': 72, 'unordered_orbits': 36, 'source_table_records': len(completions), 'checked_translation_pairs': tested_pairs, 'passing_translation_pairs': generated_pairs, 'passage_audits_valid': 3, 'output': str(output)}))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['collect', 'check'])
    parser.add_argument('--catalog', type=Path, default=ROOT / 'state/native-sources.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.mode == 'collect': collect(args.output)
    else: check(args.catalog, args.output)

if __name__ == '__main__':
    main()
