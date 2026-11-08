/** Exact experimental-design refinement of the recovered optional phase family. */
import fs from 'node:fs';import path from 'node:path';import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';import {fileURLToPath} from 'node:url';
import {predictOverCandidates} from '../dist/prediction.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>fs.readFileSync(path.join(root,p));const load=p=>JSON.parse(read(p));
const sha=x=>createHash('sha256').update(x).digest('hex');const mod=(n,m)=>((n%m)+m)%m;
const gcd=(a,b)=>b?gcd(b,a%b):Math.abs(a);
function snapshot(p){const raw=read(p),digest=sha(raw),target=`data/raw/reconstruction-integrations/${digest}/${path.basename(p)}`;
 const abs=path.join(root,target);fs.mkdirSync(path.dirname(abs),{recursive:true});
 if(fs.existsSync(abs))assert.deepEqual(fs.readFileSync(abs),raw);else fs.writeFileSync(abs,raw);
 return {sourcePath:p,snapshotPath:target,sha256:digest,bytes:raw.length};}
const native=load('state/native-comparison.json');
assert.equal(native.candidates.length,12);
const familyRefs=[...new Set([...native.kernel.sourceRefs,...native.candidates.flatMap(c=>c.sourceRefs)])];
const orientationPath='state/reconstruction/orientation-predictions.json';
const orientation=load(orientationPath);const prior=snapshot(orientationPath);
const words=[];
for(let r=0;r<12;r++)for(let l=0;l<12;l++)words.push({id:`R${r}L${l}`,r,l,
 angular:mod(5*r+7*l,12),phaseCoefficientB:mod(r-l,6),phaseCoefficientS:mod(l,6),
 expression:`R^${r} L^${l}`,sourceRefs:familyRefs});
const candidates=native.candidates.map(c=>({...c,assignment:{...c.assignment,
 ...Object.fromEntries(words.map(w=>[w.id,mod((w.r-w.l)*c.assignment.b+w.l*c.assignment.O[1],6)]))}}));
const targets=words.map(w=>({id:w.id,keys:[w.id],sourceRefs:w.sourceRefs}));
const single=predictOverCandidates(candidates,native.constraints,native.kernel,targets);
assert.equal(single.retainedCandidateIds.length,12);
const singleSummaries=single.predictions.map(p=>({wordId:p.targetId,distinctOutputs:p.alternatives.length,
 indistinguishableGroups:p.alternatives.map(x=>({phase:x.value[0],candidateIds:x.candidateIds}))}));
assert.ok(singleSummaries.every(x=>x.distinctOutputs<=6));
const pairs=[],pairFailures=[];
for(let i=0;i<words.length;i++)for(let j=i+1;j<words.length;j++){
 const first=words[i],second=words[j];
 const result=predictOverCandidates(candidates,native.constraints,native.kernel,[{
  id:'two-source-qualified-phases',keys:[first.id,second.id],sourceRefs:familyRefs}]);
 const groups=result.predictions[0].alternatives;
 const coefficientGcd=gcd(gcd(first.r-first.l,second.r-second.l),6);
 const determinant=first.r*second.l-second.r*first.l;
 const criterion=coefficientGcd===1&&mod(determinant,3)!==0;
 assert.equal(groups.length===12,criterion,JSON.stringify([first,second]));
 const row={first:first.id,second:second.id,coefficientGcd,determinantMod3:mod(determinant,3),distinctJointOutputs:groups.length};
 if(criterion)pairs.push(row);else {const collision=groups.find(g=>g.candidateIds.length>1);
  assert.ok(collision);pairFailures.push({...row,counterexample:{observations:collision.value,candidateIds:collision.candidateIds.slice(0,2)}});}
}
const samples=[['R1L0','R1L1'],['R2L0','R0L2'],['R1L0','R0L1'],['R3L0','R0L3']].map(([a,b])=>{
 const result=predictOverCandidates(candidates,native.constraints,native.kernel,[{id:`${a}+${b}`,keys:[a,b],sourceRefs:familyRefs}]);
 return {first:a,second:b,groups:result.predictions[0].alternatives};});
// The old source explicitly classifies these maps. This is a replay, not new discovery.
const maps=[];for(const u of [1,5])for(let v=0;v<6;v++)maps.push({u,v});
const mapToCandidate=[];
for(const c of native.candidates){const mappings=maps.map(t=>{
 const b=mod(t.u*c.assignment.b+5*t.v,6),d=mod(t.u*c.assignment.d+7*t.v,6);
 const found=native.candidates.find(x=>x.assignment.b===b&&x.assignment.d===d);assert.ok(found);
 return {...t,targetCandidateId:found.id};});assert.equal(new Set(mappings.map(x=>x.targetCandidateId)).size,12);
 mapToCandidate.push({candidateId:c.id,mappings});}
const inputPaths=['state/native-comparison.json',
 'data/raw/recovered/f07f6e78ad08c09559939d044f382c5fb15a88ca56d10f2a6f5d060475e908fb/SUN_SOL_Orientation_Atlas.md',
 'state/jev-receipts/000063-298ff24c136a.json',
 'state/delivery-2026-11-07/global-closure/prior-art-search.json',
 'state/delivery-2026-11-07/global-closure/prior-art-primary.json'];
const report={schema:'sunny.phase-probe-designs.v1',jevReceipt:inputPaths[2],
 scope:'The recovered optional twelve-completion family with fixed coordinate labels and origin only; no historical phase observations are admitted.',
 priorArt:{internal:inputPaths[1],internalResult:'Section4.2 already gives all12 as one p-preserving orbit. Section3 distinguishes gauge changes from moving maps against fixed source labels.',
 external:'https://bdasgup.github.io/resume/publ/papers/ber3-swat04.pdf',
 reuse:'Reuse pair-separation/test-collection formulation. Exhaustively enumerate this small family; no approximation, arbitrary weighting, or claim of inventing test cover.'},
 counts:{candidates:candidates.length,wordOccurrences:words.length,singleProbes:singleSummaries.length,
 unorderedDistinctProbePairs:pairs.length+pairFailures.length,minimalSufficientPairs:pairs.length,insufficientPairs:pairFailures.length,minimumProbes:2},
 formula:'q(R^r L^l)=(r-l)b+l s mod6, b inZ6, s in{1,5}',
 criterion:'gcd(r1-l1,r2-l2,6)=1 AND (r1*l2-r2*l1) mod3 !=0',
 derivation:[
 'For equal observations between candidates, write (r_i-l_i)Δb+l_iΔs=0 mod6 for i=1,2.',
 'When Δs=0, only Δb=0 is allowed exactly when gcd(r1-l1,r2-l2,6)=1. Otherwise at least two different b values collide at fixed s.',
 'When Δs=±2, work modulo2 and modulo3. Under the gcd condition at least one b coefficient is odd and one is nonzero modulo3.',
 'Modulo2 forces Δb even. Modulo3 a nonzero Δs has a solution exactly when (r1-l1)l2-(r2-l2)l1=r1*l2-r2*l1 vanishes modulo3.',
 'A nonzero determinant modulo3 forbids opposite-s collisions. If it vanishes, a modulo3 solution combines with the even modulo2 condition by CRT to produce a distinct colliding candidate.',
 'Thus the two stated conditions are necessary and sufficient. No single phase observation has more than six values, so any sufficient pair is cardinality-minimal for twelve candidates.'
 ],words,candidates:candidates.map(c=>({id:c.id,b:c.assignment.b,d:c.assignment.d,s:c.assignment.O[1],
 phases:Object.fromEntries(words.map(w=>[w.id,c.assignment[w.id]]))})),singleSummaries,
 sufficientPairs:pairs,insufficientPairs:pairFailures,examples:samples,
 recoveredOrbitReplay:mapToCandidate,
 requiredSourceContract:[
 'A source-authenticated map from each observed entity/event into a declared R/L word and phase label.',
 'The two observations must use the same admitted frame, phase order, origin and native semantic units; constructing labels from the desired candidate is circular.',
 'If a relabeling moves every source label with its coordinates, it remains a coordinate change; these tests cannot make that gauge choice historically unique.',
 'A lexical, glyph, number, color or sound observation is not a phase constraint until its source-defined bridge is established.',
 'The separate lawful phase-preserving profile and unspecified larger families remain retained; sufficiency here does not eliminate them.'
 ],
 globalClosure:{newIndependentHistoricalConstraints:0,absoluteOrientationSelected:false,
  exactScalarResidualSelectsPhase:false,reason:'The scalar value of a fixed R/L/O word is independent of b,s; replaying that value alone cannot select its phase completion.',
  historicalTargetWithheld:false,blindPrediction:false,fullMissionComplete:false},
 novelty:{orientationOrbit:'previously established and explicitly reused',
  arbitraryTwoWordCriterion:'derived here against the recovered execution artifacts; novelty against the entire research corpus is not established'},
 inputSnapshots:inputPaths.map(snapshot),codeBindings:['scripts/derive_phase_probe_designs.mjs','src/prediction.ts','dist/prediction.js'].map(p=>({path:p,sha256:sha(read(p))}))};
const base='state/delivery-2026-11-07/global-closure';fs.mkdirSync(path.join(root,base),{recursive:true});
fs.writeFileSync(path.join(root,base,'phase-probe-designs.json'),JSON.stringify(report,null,2)+'\n');
orientation.probe_designs={...report,priorOrientationSnapshot:orientation.probe_designs?.priorOrientationSnapshot??prior};
fs.writeFileSync(path.join(root,orientationPath),JSON.stringify(orientation,null,2)+'\n');
console.log(JSON.stringify({status:'passed',exit_code:0,...report.counts,oldOrbitReused:true,newHistoricalConstraints:0,fullMissionComplete:false}));
