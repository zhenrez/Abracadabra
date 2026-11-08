/** Small formal adverse controls; these examples make no historical assertions. */
import assert from 'node:assert/strict';
import {readFileSync, writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {createNativeExecutor} from '../../dist/native-operators.js';

const hash = value => createHash('sha256').update(value).digest('hex');
const sourcePath = 'data/raw/archive/SUN_Universal_Archive/Library/SUN_DEEP_RECOVERY/SUN_GG_v1_final.json';
const sourceId = '9e03168cabf04e3887245d93c75f1f9d0034a53bead61e5d8b5a5e0315b259e8';
const native = createNativeExecutor(readFileSync(sourcePath), sourceId);
let assertions = 0;
const check = (condition, message) => {assert.ok(condition, message); assertions++;};
function reverse(values) {
  const result = native.execute('MEC-03', {values});
  check(result.status === 'executed', 'Source-bound finite reversal executes');
  return result.output.values;
}

// A declared additive toy encoding is many-to-one. It is not an ancient alphabet.
const weights = {A: 1, B: 2, C: 3, D: 4};
const encode = word => [...word].reduce((sum, symbol) => sum + weights[symbol], 0);
check('AC' !== 'BB' && encode('AC') === encode('BB'), 'Distinct equal-length words can share one numerical sum');
check('AB' !== 'BA' && encode('AB') === encode('BA'), 'The numerical sum loses order');

// Reverse the ordered alphabet to construct a substitution. Do not reverse words.
function substitution(alphabet) {
  check(new Set(alphabet).size === alphabet.length, 'Substitution alphabet has distinct symbols');
  const reversed = reverse(alphabet);
  return Object.fromEntries(alphabet.map((symbol, i) => [symbol, reversed[i]]));
}
const alphabet = ['A', 'B', 'C', 'D'];
const map = substitution(alphabet);
const differentOrder = substitution(['A', 'C', 'D', 'B']);
for (const symbol of alphabet) check(map[map[symbol]] === symbol, 'Ordered-alphabet reversal substitution is involutive');
check(map.A !== differentOrder.A, 'Changing the alphabet order can change the substitution');
const apply = word => [...word].map(symbol => map[symbol]).join('');
check(apply('AB') === 'DC' && reverse(['A', 'B']).join('') === 'BA', 'Letter substitution differs from reversing word position');

// Partition refinement can distinguish candidates without invented probabilities.
const candidates = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
const coarse = [['a', 'b', 'c', 'd'], ['e', 'f', 'g', 'h']];
const fine = [['a', 'b'], ['c', 'd'], ['e', 'f'], ['g', 'h']];
function validPartition(partition) {
  const flat = partition.flat();
  return flat.length === candidates.length && new Set(flat).size === candidates.length && candidates.every(x => flat.includes(x));
}
check(validPartition(coarse) && validPartition(fine), 'Both observations cover exactly the supplied candidate family');
check(fine.every(block => coarse.some(parent => block.every(x => parent.includes(x)))), 'The fine observation refines the coarse partition');
check(Math.max(...fine.map(x => x.length)) === 2 && Math.max(...coarse.map(x => x.length)) === 4, 'Refinement improves the largest surviving class in this equally feasible finite example');

// Synthetic calendar: a label change alone does not move a physical instant.
const instants = [0, 1, 2, 3, 4, 5];
const profileA = instant => instant;
const profileB = instant => instant < 3 ? instant : instant + 10;
const rows = instants.map(instant => ({instant, oldLabel: profileA(instant), changedLabel: profileB(instant)}));
check(rows.every((row, i) => row.instant === instants[i]), 'Calendar relabeling preserves all supplied physical instants');
check(rows[3].changedLabel - rows[2].changedLabel === 11 && rows[3].instant - rows[2].instant === 1, 'Skipped labels do not imply skipped elapsed days');
check(rows.find(x => x.oldLabel === 4).instant === rows.find(x => x.changedLabel === 14).instant, 'Different calendar labels can identify the same instant');

const evidence = {
  schema: 'sunny.strategy-finite-controls.v1',
  createdUtc: new Date().toISOString(),
  status: 'passed', exitCode: 0, assertions,
  scope: 'Declared finite formal examples only; no historical alphabet, pronunciation, calendar restoration, identity claim or blind prediction.',
  sourceBinding: {path: sourcePath, sourceId, sha256: hash(readFileSync(sourcePath)), mechanism: 'MEC-03', sourceRole: 'Existing musical finite-reversal operator reused as an abstract operation; no Hebrew letter identity inferred.'},
  artifactBindings: Object.fromEntries(['docs/evidence/strategy-finite-controls.mjs', 'src/native-operators.ts', 'dist/native-operators.js', 'src/prediction.ts'].map(path => [path, hash(readFileSync(path))])),
  noninjectiveEncoding: {weights, distinctWords: ['AC', 'BB'], sameValue: encode('AC'), orderCollision: ['AB', 'BA']},
  orderedAlphabetSubstitution: {alphabet, substitution: map, changedAlphabetOrder: ['A', 'C', 'D', 'B'], changedSubstitution: differentOrder, finiteDomainVerified: alphabet, phoneticData: null},
  observationPartitions: {candidates, coarse, fine, largestClassSizes: {coarse: 4, fine: 2}, probabilityDistribution: null, comparisonCondition: 'Supplied complete finite candidate family and equally feasible observations; no universal cost-optimality claim.'},
  syntheticCalendar: {rows, condition: 'Label-coordinate change only; no behavioral or astronomical dynamics supplied.'},
  proofBoundary: 'Additive encoding collision refutes injectivity in this declared example. Reversal substitution is involutive for any finite distinct ordered alphabet by index map i -> n-1-i; the finite checks illustrate that proof, not ancient source authenticity.',
  persistentProcessesStarted: 0,
};
writeFileSync('docs/evidence/strategy-finite-controls.json', JSON.stringify(evidence, null, 2) + '\n');
console.log(JSON.stringify({status: evidence.status, exitCode: 0, assertions, historicalClaimsTested: 0, output: 'docs/evidence/strategy-finite-controls.json'}));
