/** Source-bound finite consequences; this family is not the whole SUNNY model. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {predictOverCandidates} from '../dist/prediction.js';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const load = p => JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const mod = (n,m) => ((n%m)+m)%m;
const input = load('state/native-comparison.json');
const native = load('docs/evidence/native-completions.json');
const atlasPath = 'data/raw/recovered/' + native.preserved_source_sha256 + '/SUN_SOL_Orientation_Atlas.md';
assert.equal(sha(fs.readFileSync(path.join(root,atlasPath))),native.preserved_source_sha256);
assert.equal(input.candidates.length,12);
const receipt = load('docs/evidence/mandate-mathematics-superjev.json');
assert.equal(receipt.status,'judged');
assert.equal(receipt.answers.investigation.winner,'derive_residual_and_prediction_sets');
assert.equal(receipt.answers.prediction_semantics.winner,'all_nonrejected');
const refs = [input.provenance.atlas_source_id];
const words = [];
for(let r=0;r<12;r++)for(let l=0;l<12;l++) words.push({r,l,key:'word:'+r+':'+l});
const candidates = input.candidates.map(c => {
  const assignment = {...c.assignment,Rphase:c.assignment.b,Ophase:c.assignment.O[1]};
  for(const w of words)assignment[w.key]=[mod(5*w.r+7*w.l,12),mod(c.assignment.b*w.r+c.assignment.d*w.l,6)];
  return {...c,assignment};
});
const targets = words.map(w=>({id:w.key,keys:[w.key],sourceRefs:refs}));
targets.push({id:'R-phase',keys:['Rphase'],sourceRefs:refs},
  {id:'O-phase',keys:['Ophase'],sourceRefs:refs},
  {id:'R-and-O-phase',keys:['Rphase','Ophase'],sourceRefs:refs});
const result = predictOverCandidates(candidates,input.constraints,input.kernel,targets);
const common = words.filter(w=>result.predictions.find(p=>p.targetId===w.key).status==='determined-within-supplied-family');
for(const w of words) {
  const actual = common.includes(w);
  const expected = mod(w.r-w.l,6)===0 && mod(w.l,3)===0;
  assert.equal(actual,expected,'unanimity criterion at '+w.key);
}
assert.equal(common.length,8);
for(const c of candidates) {
  const reached = new Set();
  for(let r=0;r<12;r++)for(let l=0;l<12;l++) reached.add(c.assignment['word:'+r+':'+l].join(','));
  assert.equal(reached.size,72,'transitivity '+c.id);
  assert.deepEqual(c.assignment['word:3:3'],[0,3]);
}
const values = id=>result.predictions.find(p=>p.targetId===id).alternatives.length;
assert.equal(values('R-phase'),6);assert.equal(values('O-phase'),2);assert.equal(values('R-and-O-phase'),12);
const addresses = [...new Map(common.map(w=>{
  const value=result.predictions.find(p=>p.targetId===w.key).alternatives[0].value[0];
  return [JSON.stringify(value),value];
})).values()];
const proofs = [
  {
    id:'OP-UNANIMITY',
    stage:'extended-conditional',
    premises:['Source optional transitive family R=(5,b), L=(7,d), b+d=s in{1,5} mod6.','Observed coordinate labels and origin are fixed.'],
    derivation:[
      'For word R^r L^l, phase q=(r-l)b+ls modulo6, angular p=5r+7l modulo12.',
      'Compare b and b+1 with s fixed: independence of b iff r-l=0 modulo6.',
      'Compare s=1 and s=5: independence iff4l=0 modulo6, equivalently l=0 modulo3.',
      'Both are necessary and sufficient. Thus r=l modulo6 and l=0 modulo3.',
      'For representatives0<=r,l<12, eight words satisfy this criterion, with four shared addresses.'
    ],
    consequence:'Some localities are determined across all twelve completions without selecting an absolute orientation.',
    limits:['The source phase-preserving profile is another retained family and is not eliminated.','Shared values are conditional family consequences, not blind historical predictions.'],
    sourceRefs:refs,
  },
  {
    id:'OP-MINIMUM-PHASE-PROBES',
    stage:'extended-conditional',
    derivation:[
      'Every one-word phase observation has at most6values because q is modulo6; angular displacement is the same in every candidate.',
      'Therefore no single one-word address observation can distinguish12candidates.',
      'The ordered observations q(R)=b and q(O)=s identify(b,s), hence d=s-b modulo6, uniquely.',
      'They attain the lower bound of two such observations. Independent source-to-phase evidence is still needed to instantiate either observation.'
    ],
    minimal_observations_in_this_class:2,sourceRefs:refs,
  },
  {
    id:'OP-FINITE-ADDRESS-EXACT-PITCH',
    stage:'reproduced-and-derived-conditional',
    premises:['Exact rational scalar laws R=2/3,L=3/4,O=1/2; octave equivalence is multiplication by integer powers of2.'],
    derivation:[
      'R^r L^l O^o=2^(r-2l-o)3^(l-r).',
      'Unique prime factorization implies two such products agree modulo octaves iff their3-exponents l-r agree.',
      'The exact scalar R has infinite order modulo octaves: no nonzero integern has3^n equal to a power of2.',
      'The finite address R has order12, yet R^12=4096/531441 and2^7 R^12=524288/531441 !=1.',
      'Thus exact rational pitch cannot descend faithfully through this finite address projection. An additional residual or path quantity must remain; this does not prescribe its geometric realization.'
    ],
    example:{scalar:'4096/531441',octave_compensated:'524288/531441',finite_address:[0,0]},
    sourceRefs:refs,
  }
];
const output = {
  schema:'sunny.orientation-prediction-reconstruction.v1',
  generated_utc:new Date().toISOString(),
  mandate:'Current direct user SUNNY Reconstruction and Predictive Derivation Mandate, SectionsII-D/F andIII-4/5/7.',
  provenance:{atlas_path:atlasPath,atlas_sha256:native.preserved_source_sha256,atlas_source_id:refs[0],
    native_input_sha256:sha(fs.readFileSync(path.join(root,'state/native-comparison.json'))),
    jev_request:'state/mandate-mathematics-request.json',jev_result:'docs/evidence/mandate-mathematics-superjev.json',
    jev_model:receipt.resolved_model,independent_check:'docs/evidence/orientation-wolfram-check.json'},
  family:{scope:input.scope,count:12,whole_SUNNY_family_complete:false,
    retained_other_profile:'R=(5,0), L=(7,0), O=(0,0); not rejected by this optional-transitive investigation.'},
  checks:{candidate_count:12,generated_addresses_per_candidate:72,word_targets:144,
    common_word_targets:common.length,shared_addresses:addresses,minimum_phase_observations:2},
  proofs,common_words:common,conditional_predictions:result,
  novelty:{blind:false,novelty_against_full_corpus:'not-established',status:'Computed and proved consequences; no empirical-success claim.'},
  outstanding:['Independent source-qualified phase observations','Whole musical/generational constraint integration beyond this source family','Class-growth/radius/rebound/fourth-axis laws','Prospective withheld-target testing after sufficient reconstruction'],
};
fs.writeFileSync(path.join(root,'state/reconstruction/orientation-predictions.json'),JSON.stringify(output,null,2)+'\n');
const document = [
  '# Executed conditional orientation consequences','',
  'Actual Jev '+receipt.resolved_model+' directed the hypothesis tests and conditional prediction semantics. Exact computation and proofs determine the results; model probabilities do not certify them.','',
  'This reconstructs one recovered family within SUNNY. All other native musical systems, the global generational mission and the phase-preserving SUN profile remain in scope.','',
  '## What is now computed','',
  '- All twelve recovered transitive completions generate72addresses.',
  '- Across144words R^rL^l (0<=r,l<12), eight have the same address in all twelve completions.',
  '- Their four shared addresses are '+addresses.map(x=>'('+x.join(',')+')').join(',')+'.',
  '- Ordered R-phase and O-phase observations separate all twelve. One word-address observation cannot do so.',
  '- Finite address closure does not imply exact rational-pitch closure; the residual must survive the projection.','',
  ...proofs.flatMap(p=>['## '+p.id,'',...(p.premises??[]).map(x=>'- Premise: '+x),'',
    ...p.derivation.map((x,i)=>(i+1)+'. '+x),'',p.consequence??'','']),
  '## Evidence and limits','',
  '[Source Atlas](../../'+atlasPath+') supplies the laws and optional family. [Full execution](../../state/reconstruction/orientation-predictions.json) retains every candidate prediction and unresolved selector. [Independent Wolfram check](../evidence/orientation-wolfram-check.json) confirms the enumerated counts and exact residual.',
  '',
  'The common-word formula is proved for all integer exponents under these native laws; the144word run checks a complete residue grid. This does not prove global family completeness or independently map historical entities into phase coordinates. No claim of blind novelty is made. The phase observations are discriminating mathematical targets, not already recovered historical evidence.','',
];
fs.writeFileSync(path.join(root,'docs/reconstruction/ORIENTATION_PREDICTIONS.md'),document.join('\n'));
console.log(JSON.stringify({status:'passed',exit_code:0,...output.checks,global_orientation_selected:false,blind_prediction:false}));
