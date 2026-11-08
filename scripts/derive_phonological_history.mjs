/** Execute source-conditioned temporal discriminators; no historical mechanism is selected. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {contactTiming} from '../dist/phonological-history.js';
import {rational} from '../dist/law.js';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out='state/delivery-2026-11-07/history-discriminator';
const read=p=>fs.readFileSync(path.join(root,p));
const load=p=>JSON.parse(read(p));
const sha=raw=>createHash('sha256').update(raw).digest('hex');
const q=n=>rational(String(n),'1');
const w=(lo=null,hi=null,lc=true,uc=true)=>({lower:lo===null?null:q(lo),upper:hi===null?null:q(hi),lowerClosed:lc,upperClosed:uc});
const any=()=>w();
const assessment=load('docs/reconstruction/symbol-sound-census/phyla-waves-assessment.json');
const context=load('state/reconstruction/phonological-context-constraints.json');
const independent=load(out+'/review/result.json');
const adapterReview=load(out+'/review/adapter-review.json');
assert.equal(independent.status,'passed');assert.equal(adapterReview.status,'passed');
assert.equal(sha(read('src/phonological-history.ts')),adapterReview.testedHashes.source);
assert.equal(sha(read('dist/phonological-history.js')),adapterReview.testedHashes.dist);

const controls=[
  {id:'positive_attestations_B_then_T',inputs:[w(null,6),any(),w(null,9)],expected:true},
  {id:'same_attestations_reverse_direction',inputs:[w(null,9),any(),w(null,6)],expected:true},
  {id:'donor_lower_after_recipient_upper',inputs:[w(4),any(),w(null,3)],expected:false,
    proper:[[any(),any(),w(null,3)],[w(4),any(),any()]]},
  {id:'contact_lower_after_recipient_upper',inputs:[any(),w(4),w(null,3)],expected:false,
    proper:[[any(),any(),w(null,3)],[any(),w(4),any()]]},
  {id:'donor_lower_after_contact_upper',inputs:[w(4),w(null,3),any()],expected:false,
    proper:[[any(),w(null,3),any()],[w(4),any(),any()]]}
].map(c=>{
  const result=contactTiming(...c.inputs);assert.equal(result.feasible,c.expected);
  const proper=(c.proper??[]).map(inputs=>({inputs,result:contactTiming(...inputs)}));
  assert.ok(proper.every(x=>x.result.feasible));
  return {...c,proper,result,scope:'Synthetic arbitrary order coordinates, not attested dates or extracted historical bounds'};
});

// Complete cell partition of the real line for the declared two-onset trajectories.
const cells=[{id:'before2',representative:1},{id:'at2',representative:2},{id:'between2and4',representative:3},
  {id:'at4',representative:4},{id:'after4',representative:5}];
const trajectory={donorOnset:2,recipientOnset:4};
const phoneAt=t=>[Number(t>=trajectory.donorOnset),Number(t>=trajectory.recipientOnset)];
const comparison=cells.map(c=>({...c,contactModel:phoneAt(c.representative),parallelModel:phoneAt(c.representative)}));
assert.ok(comparison.every(c=>JSON.stringify(c.contactModel)===JSON.stringify(c.parallelModel)));
const queryRegister=[
 {id:'HD-Q1',need:'Context-matched independently licensed donor negative state plus recipient positive state, with their relative date bounds.',
  consequence:'Can exclude the specified donor-to-recipient edge if the donor onset lower bound is later than the recipient acquisition upper bound.',
  missing:'Both phonetic licenses, exact witness contexts and independently justified bounds; an absent transcription is not a negative phone observation.'},
 {id:'HD-Q2',need:'Independently bounded period when this transmission could occur, plus recipient acquisition upper bound.',
  consequence:'Can exclude this proposed contact if its earliest possible date follows recipient acquisition.',
  missing:'Contact opportunity bounds cannot be inferred merely from failing to find a contact record; third-party and other episodes remain separate.'},
 {id:'HD-Q3',need:'Independently justified transcription-to-phone mapping in the exact source context.',
  consequence:'Can separate a pure written-normalization explanation from a changed-pronunciation explanation.',
  missing:'Received vowel letters and current scholarly reconstructed phones are not independent ancient acoustic observations; hybrid explanations survive.'},
 {id:'HD-Q4',need:'Evidence constraining transmission, copying or lineage independently of the sound-state trajectories.',
  consequence:'Required to distinguish contact from an observationally identical independent-change realization when their full trajectories coincide.',
  missing:'More sound-state samples, even perfect all-time phone trajectories in the counterexample, do not identify the causal edge.'}
];
const result={
 schema:'sunny.phonological-history-constraints.v1',
 jevReceipt:'state/jev-receipts/000061-54b57b45fbcd.json',
 problem:'Derive which source-qualified constraints can discriminate inheritance, contact, parallel change and observation-channel explanations.',
 nativeConditions:[
  'Same lexical item or justified correspondence, historical vowel, morphology, syllable environment, performance register and feature identity are required before joining observations.',
  'Distinct community-specific events remain distinct: the reported T v and B w do not license a common consonantal-change event.',
  'Innovation onset, earliest surviving positive attestation, copy date and first community acquisition are distinct addresses.',
  'A dated positive attestation gives an onset upper bound under persistence; it does not date the innovation exactly or supply its lower bound.',
  'Monotonicity/no loss and direct feature-causing contact are explicit model conditions, not universal historical rules.'
 ],
 sourceCases:{coarseFeature:assessment.concreteCharacters.find(c=>c.id==='PW-C1'),
  copyingAlternative:assessment.concreteCharacters.find(c=>c.id==='PW-C3'),
  contextualReadingBranches:context.conditionalExecutions,sourceGradeIsNotPhone:true,
  refinement:'The older105/15treecount experiment remains intact within its declared binary character and no-contact assumptions. It does not adjudicate the richer contexts or networks.'},
 operator:{implementation:'src/phonological-history.ts',domain:'Three real-valued event windows with exact rational or unbounded endpoints; endpoint inclusion retained.',
  relation:'donorOnset < contact <= recipientOnset; weak-donor equality is an explicit alternative parameter.',
  projection:'admissibleContact = K intersect (inf(D), sup(R)), with the recipient upper endpoint included exactly when R includes it; all input windows must be nonempty.',
  proof:'A feasible contact must exceed the donor infimum and not exceed an available recipient supremum. Conversely choose any point in that intersection, choose an earlier donor in D, and a recipient at or after it in R. Strict/open endpoints determine equality cases. The weak-donor case admits the donor lower endpoint only if D contains it.',
  exactWitnessReturned:true,inputEndpointIntegerDigitBudget:128,derivedRationalDigitsUnbounded:true,
  resourceBoundary:'The endpoint input budget is computational only; it does not choose a historical time scale.'},
 conditionalControls:controls,
 allTimeCounterexample:{coordinates:'Arbitrary real order coordinates, no historical dating.',
  contactHistory:{...trajectory,contactTime:3,causalEdge:'donor-to-recipient'},
  parallelHistory:{...trajectory,contactTime:null,causalEdge:null},
  cells:comparison,
  proof:'Both realizations use exactly the same two step functions. They are constant on each open cell and equal at both discontinuities, which partitions the entire real line. No query of these phonetic states can identify which causal realization generated them.',
  consequence:'Sound-state agreement alone does not establish a transmission edge, even when the complete trajectories are known. Additional musical or relational constraints could discriminate only through a justified adapter.',
  scope:'Existence of an observationally equivalent pair within these declared models; not a proof that all possible histories or every inheritance model are equivalent.'},
 queryRegister,
 priorArt:{
  standingProtocol:'G16: recurring original-source prior art, P0-A baseline, controlled First &3/4 Order exposure and exact transfer/reuse conditions.',
  inheritedBaseline:'state/research/reactivation/symbols/p0a-14-baseline.json',
  currentCensusStatus:'Bounded mainstream method extension; complete updated14question census and ten-question/M1-M12 heterodox phase remain open. No exhaustive novelty claim.',
  sources:load(out+'/primary/retrieval.json'),
  inspected:[
   {id:'erdem-2005',pages:[1,2,3],reuse:'Model transmission separately from tree ancestry; contact requires contemporary communities.',limit:'The paper models linguistic networks, not sacred original phonetics or a musical geometry.'},
   {id:'angluin-1988',pages:[1,2,3],reuse:'Specify allowed observation queries and retain equivalence when their answers cannot separate models.',limit:'Historical sources are not a reliable answer oracle; exact-learning guarantees do not transfer.'},
   {id:'dechter-1991',pages:[8,9,10,11,12],reuse:'Represent event intervals explicitly and derive conditional temporal consistency.',limit:'This adapter solves only the stated three-window relation; no complete temporal-network/ASP implementation or theorem re-proof claimed.'}
  ],
  searchTerms:['Temporal Phylogenetic Networks and Logic Programming','Queries and Concept Learning','Dechter Meiri Pearl temporal constraint networks shortest paths'],
  contributionBeyondPriorArt:'Source-bound observation-query register, explicit qames/context transfer limits, exact interval adapter, all-time contact/parallel countermodel and three inclusion-minimal contradictory bound pairs.',
  novelty:'A conditional SUNNY application of established methods; no new general theorem, historical innovation or exhaustive literature coverage claimed.'},
 independentChecks:{review:out+'/review/adapter-review.json',cases:adapterReview.cases,witnesses:adapterReview.independentExactWitnessChecks,
  projections:adapterReview.independentProjectionMembershipChecks,sourceStable:adapterReview.sourceStable},
 currentHistoricalBoundsAdmitted:0,
 remaining:['Original witness collation','Independent phonetic licensing','Context-matched dated attestations and admissible negative evidence','Independent causal/transmission constraints','Hybrid, loss and third-party histories'],
 originalSoundRecovered:false,historicalMechanismSelected:false,blindPrediction:false,fullMissionComplete:false
};
const inputs=['docs/reconstruction/symbol-sound-census/phyla-waves-assessment.json',
 'docs/reconstruction/symbol-sound-census/qames-topology-discrimination.json','state/reconstruction/phonological-context-constraints.json',
 'state/jev-receipts/000061-54b57b45fbcd.json',out+'/review/result.json',out+'/review/adapter-review.json',
 ...result.priorArt.sources.map(s=>s.path)];
result.inputSnapshots=inputs.map(p=>{
 const raw=read(p),hash=sha(raw),dest='data/raw/reconstruction-integrations/'+hash+'/'+path.basename(p);
 fs.mkdirSync(path.dirname(path.join(root,dest)),{recursive:true});
 if(fs.existsSync(path.join(root,dest)))assert.ok(read(dest).equals(raw));else fs.writeFileSync(path.join(root,dest),raw);
 return {sourcePath:p,snapshotPath:dest,sha256:hash,bytes:raw.length};
});
result.codeBindings=['src/phonological-history.ts','dist/phonological-history.js','src/law.ts','dist/law.js',
 'scripts/derive_phonological_history.mjs','tests/phonological-history.test.mjs',out+'/review/check_adapter.py',out+'/review/run_adapter_cases.mjs']
 .map(p=>({path:p,sha256:sha(read(p))}));
const bytes=JSON.stringify(result,null,2)+'\n';
for(const p of [out+'/result.json','state/reconstruction/phonological-history-constraints.json'])fs.writeFileSync(path.join(root,p),bytes);
console.log(JSON.stringify({status:'passed',exit_code:0,controls:controls.length,minimalAdditionalBoundPairs:3,
 allTimeContactParallelCountermodel:true,independentAdapterCases:adapterReview.cases,currentHistoricalBoundsAdmitted:0,historicalMechanismSelected:false}));
