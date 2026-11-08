import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import {createHash} from 'node:crypto';
const root=new URL('../',import.meta.url),read=p=>fs.readFileSync(new URL(p,root)),load=p=>JSON.parse(read(p));
const data=load('state/delivery-2026-11-07/global-closure/phase-probe-designs.json');
test('every one- and two-word design is accounted for, with explicit failed-design witnesses',()=>{
 assert.deepEqual(data.counts,{candidates:12,wordOccurrences:144,singleProbes:144,unorderedDistinctProbePairs:10296,minimalSufficientPairs:4608,insufficientPairs:5688,minimumProbes:2});
 assert.equal(new Set([...data.sufficientPairs,...data.insufficientPairs].map(p=>[p.first,p.second].join('|'))).size,10296);
 for(const s of data.singleSummaries)assert.ok(s.distinctOutputs<=6);
 for(const p of data.insufficientPairs){const [a,b]=p.counterexample.candidateIds.map(id=>data.candidates.find(c=>c.id===id));
  assert.notEqual(a.id,b.id);assert.deepEqual([a.phases[p.first],a.phases[p.second]],[b.phases[p.first],b.phases[p.second]]);}
});
test('candidate values match repeated native translations and retain shared source frames',()=>{
 const native=load('state/native-comparison.json');
 for(const c of native.candidates)for(const w of data.words){let q=0;for(let n=0;n<w.r;n++)q=(q+c.assignment.b)%6;for(let n=0;n<w.l;n++)q=(q+c.assignment.d)%6;
  assert.equal(data.candidates.find(x=>x.id===c.id).phases[w.id],q);assert.ok(c.sourceRefs.every(ref=>w.sourceRefs.includes(ref)));}
});
test('extension preserves all earlier orientation fields and its immutable source/code bindings',()=>{
 const current=load('state/reconstruction/orientation-predictions.json'),prior=load(current.probe_designs.priorOrientationSnapshot.snapshotPath);
 const omit=x=>Object.fromEntries(Object.entries(x).filter(([k])=>k!=='probe_designs'));
 assert.deepEqual(omit(current),omit(prior));
 for(const b of [...data.inputSnapshots.map(x=>({path:x.snapshotPath,sha256:x.sha256})),...data.codeBindings])assert.equal(createHash('sha256').update(read(b.path)).digest('hex'),b.sha256,b.path);
});
test('identification within a fixed family does not become historical or global selection',()=>{
 assert.equal(data.globalClosure.newIndependentHistoricalConstraints,0);
 assert.equal(data.globalClosure.absoluteOrientationSelected,false);assert.equal(data.globalClosure.blindPrediction,false);
 assert.ok(data.requiredSourceContract.some(s=>s.includes('phase-preserving')));
 assert.equal(data.priorArt.internalResult.includes('already'),true);
});
