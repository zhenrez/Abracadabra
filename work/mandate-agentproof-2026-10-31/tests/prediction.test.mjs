import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {predictOverCandidates} from '../dist/prediction.js';

const native = JSON.parse(fs.readFileSync(new URL('../state/native-comparison.json', import.meta.url), 'utf8'));
const target = (id, keys) => ({id, keys, sourceRefs: native.kernel.sourceRefs});
const enriched = native.candidates.map(c => ({...c, assignment: {
  ...c.assignment, Rphase: c.assignment.b, Ophase: c.assignment.O[1], O3: [0, (3*c.assignment.O[1])%6],
}}));

test('actual twelve completions give a shared binary flip despite unresolved selector', () => {
  const result = predictOverCandidates(enriched,native.constraints,native.kernel,[target('third-octave',['O3'])]);
  assert.equal(result.evaluation.unresolved.length,12);
  assert.equal(result.retainedCandidateIds.length,12);
  assert.equal(result.predictions[0].status,'determined-within-supplied-family');
  assert.deepEqual(result.predictions[0].alternatives[0].value,[[0,3]]);
  assert.equal(result.globalOrientationSelected,false);
});

test('source-native ordered phase observations distinguish all twelve without electing one', () => {
  const result = predictOverCandidates(enriched,native.constraints,native.kernel,[
    target('R',['Rphase']),target('O',['Ophase']),target('R-and-O',['Rphase','Ophase']),
  ]);
  assert.deepEqual(result.predictions.map(p=>p.alternatives.length),[6,2,12]);
  assert.equal(result.predictions[2].alternatives.every(a=>a.candidateIds.length===1),true);
  assert.equal(result.predictions[2].status,'alternatives');
});

test('a missing value or unbound target prevents a false unanimous prediction', () => {
  const incomplete = enriched.map((c,i)=>i===0 ? {...c,assignment:{...c.assignment,other:1}} : c);
  delete incomplete[0].assignment.O3;
  const result = predictOverCandidates(incomplete,native.constraints,native.kernel,[target('incomplete',['O3'])]);
  assert.equal(result.predictions[0].status,'unknown');
  assert.equal(result.predictions[0].missingCandidateIds.length,1);
  assert.equal(predictOverCandidates(enriched,[],native.kernel,[{id:'unbound',keys:['O3'],sourceRefs:[]}]).predictions[0].status,'unknown');
});

test('contradiction yields no survivors, not vacuous agreement', () => {
  const impossible = {id:'impossible',kernelSha256:native.kernel.sha256,sourceRefs:native.kernel.sourceRefs,
    authority:'assumption',predicate:{op:'eq',key:'b',value:99}};
  const result = predictOverCandidates(enriched,[impossible],native.kernel,[target('empty',['O3'])]);
  assert.equal(result.predictions[0].status,'no-surviving-candidates');
  assert.equal(result.predictions[0].alternatives.length,0);
});

test('duplicate targets and repeated keys fail explicitly', () => {
  assert.throws(()=>predictOverCandidates(enriched,[],native.kernel,[target('x',['b']),target('x',['d'])]),/unique/);
  assert.throws(()=>predictOverCandidates(enriched,[],native.kernel,[target('x',['b','b'])]),/unique/);
});
