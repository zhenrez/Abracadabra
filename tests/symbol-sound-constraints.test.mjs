import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {buildAlefConstraintCase} from '../scripts/reconstruct_symbol_sound_constraints.mjs';
const load=p=>JSON.parse(fs.readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const testimony=load('docs/reconstruction/symbol-sound-census/tiberian-alef-testimony.json');
const operations=load('state/research/reactivation/symbols/tiberian-alef-operations.json');
const input=()=>buildAlefConstraintCase(testimony,operations,['source:testimony','source:operations']);

test('source-qualified final cases refute universal dotted-consonant interpretation',()=>{
  const c=input();
  assert.deepEqual(c.result.evaluation.rejected,['universal-dot-consonantal']);
  assert.equal(c.rows.length,7);
  const rejected=c.result.evaluation.results.find(x=>x.candidateId==='universal-dot-consonantal');
  assert.equal(rejected.witnesses.filter(x=>x.verdict==='fail').length,3);
});
test('both retained grammatical interpretations agree on all seven presence targets',()=>{
  const c=input();
  assert.equal(c.result.retainedCandidateIds.length,2);
  assert.ok(c.result.predictions.filter(x=>x.targetId.startsWith('presence:')).every(x=>x.status==='determined-within-supplied-family'));
  assert.equal(c.presenceProjection.length,1);
  assert.equal(c.presenceProjection[0].candidateIds.length,2);
  assert.equal(c.result.predictions.find(x=>x.targetId==='mark-function').status,'alternatives');
});
test('neither original duration, fixedHz nor strengthening factor is manufactured',()=>{
  const c=input();
  for(const id of ['duration-factor','absolute-Hz','waveform']){
    const p=c.result.predictions.find(x=>x.targetId===id);
    assert.equal(p.status,'unknown');assert.equal(p.missingCandidateIds.length,2);
  }
  assert.equal(c.blindPrediction,false);assert.equal(c.historicalInterpretationSelected,false);
});
test('wrong canonical loci or missing source bindings fail explicitly',()=>{
  const bad=structuredClone(operations);bad.source_reports[2].canonical_targets[0]='Genesis1:1';
  assert.throws(()=>buildAlefConstraintCase(testimony,bad,['source:a']),/canonical/);
  assert.throws(()=>buildAlefConstraintCase(testimony,operations,[]),/source/);
});
test('published execution binds actual compiled files and every exported score source',()=>{
  const artifact=load('state/reconstruction/symbol-sound-constraints.json');
  for(const file of ['dist/law.js','dist/prediction.js'])assert.ok(artifact.codeBindings.some(x=>x.path===file),file);
  const frozen=new Set(artifact.inputSnapshots.map(s=>s.snapshotPath));
  const walk=v=>{
    if(Array.isArray(v)){for(const item of v)walk(item);return;}
    if(v&&typeof v==='object')for(const [key,value] of Object.entries(v)){
      if(key==='sourceRefs')assert.ok(value.every(ref=>frozen.has(ref)),'mutable source reference');
      else walk(value);
    }
  };
  walk(artifact.scoreViews);
  assert.ok(artifact.inputSnapshots.some(x=>x.sourceOccurrencePath.endsWith('/khan2020.pdf')),'primary PDF binding');
});
