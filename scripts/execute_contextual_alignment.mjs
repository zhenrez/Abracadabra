/** Execute recovered source-conditioned adapters using SUNNY's existing predictor. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {solveContextualAlignment} from '../dist/contextual-alignment.js';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const digest=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const checkOnly=process.argv.includes('--check');
const destination=path.join(root,'state/reconstruction/contextual-alignment.json');
const published=checkOnly?JSON.parse(fs.readFileSync(destination,'utf8')):null;
const snapshots=[];
function snapshot(relative){
  if(checkOnly){
    const binding=published.inputSnapshots.find(s=>s.sourceOccurrencePath===relative);
    assert.ok(binding,'Published input binding missing: '+relative);
    const raw=fs.readFileSync(path.join(root,binding.snapshotPath));
    assert.equal(digest(raw),binding.sha256,'Published input snapshot changed');
    assert.equal(raw.length,binding.bytes);
    snapshots.push(binding);
    return JSON.parse(raw.toString('utf8').replace(/^\uFEFF/,''));
  }
  const original=path.resolve(root,relative);
  if(!original.startsWith(root+path.sep))throw new Error('Input outside project');
  const raw=fs.readFileSync(original),sha256=digest(raw);
  const snapshotPath=path.posix.join('data/raw/reconstruction-integrations',sha256,path.basename(relative));
  const target=path.join(root,snapshotPath);fs.mkdirSync(path.dirname(target),{recursive:true});
  if(!fs.existsSync(target))fs.writeFileSync(target,raw,{flag:'wx'});
  assert.equal(digest(fs.readFileSync(target)),sha256,'Immutable source snapshot changed');
  snapshots.push({sourceOccurrencePath:relative,snapshotPath,sha256,bytes:raw.length});
  return JSON.parse(raw.toString('utf8').replace(/^\uFEFF/,''));
}
const obstruction=snapshot('state/research/reactivation/chinese/conditional-adapter-obstruction.json');
const positive=snapshot('state/research/reactivation/chinese/positive-modal-adapter.json');
const native=snapshot('state/research/reactivation/chinese/native-role-relation.json');
const sourceRefs=snapshots.map(s=>s.snapshotPath);
const link=(id,from,to,offset)=>({id,from,to,offset,sourceRefs:[...sourceRefs]});
const links=obstruction.equations.map(e=>{
  const match=/^(\w+)-(\w+)-(\d+)=0mod(\d+)$/.exec(e.expression.replace(/\s/g,''));
  if(!match||Number(match[4])!==12)throw new Error('Unreviewed source equation: '+e.expression);
  return link(e.id,match[2],match[1],Number(match[3]));
});
const rejectedCase={id:'received-ritual-common-gong-adapter',modulus:12,variables:['c','h','t'],
  sourceRefs,assumptions:obstruction.hypotheses,links};
const rejected=solveContextualAlignment(rejectedCase);
assert.equal(rejected.status,'inconsistent');assert.equal(rejected.cycle.residue,4);
const deletionChecks=links.map(removed=>({removed:removed.id,...solveContextualAlignment({...rejectedCase,
  id:rejectedCase.id+'-without-'+removed.id,links:links.filter(e=>e.id!==removed.id)})}));
assert.ok(deletionChecks.every(x=>x.assignmentCount==='12'));

const zero=positive.ancestral_family.representatives.find(r=>r.alpha===0);
assert.deepEqual(zero.implicit_gong_pcs,[0,9,7,2]);
const ancestralCase={id:'ancestral-separate-modal-adapter',modulus:12,
  variables:['alpha','g0','g1','g2','g3'],sourceRefs,assumptions:positive.exact_source_conditions,
  links:zero.implicit_gong_pcs.map((n,i)=>link('mode'+i,'alpha','g'+i,n)),
  targets:zero.implicit_gong_pcs.map((_,i)=>({id:'relative-gong-'+i,kind:'difference',from:'alpha',to:'g'+i}))};
const ancestral=solveContextualAlignment(ancestralCase);assert.equal(ancestral.assignmentCount,'12');
for(const row of positive.ancestral_family.representatives){
  const reproduced=ancestral.assignments.find(a=>a.alpha===row.alpha);
  assert.deepEqual([0,1,2,3].map(i=>reproduced['g'+i]),row.implicit_gong_pcs);
}

const extension=positive.all_three_rows_modular_extension;
assert.equal(extension.rows.length,12);
const allCase={id:'three-rituals-separate-modal-adapter',modulus:12,
  variables:['alpha',...extension.rows.map((_,i)=>'g'+i)],sourceRefs,
  assumptions:[extension.source_condition,extension.relative_standard_concordance,extension.exact_lift_boundary],
  links:extension.rows.map((row,i)=>link(row.model_context_id,'alpha','g'+i,row.relative_implicit_gong_pc)),
  targets:extension.rows.map((row,i)=>({id:row.model_context_id,kind:'difference',from:'alpha',to:'g'+i}))};
const allRituals=solveContextualAlignment(allCase);assert.equal(allRituals.assignmentCount,'12');
let modularChecks=0;
for(const a of allRituals.assignments)for(const [i,row] of extension.rows.entries()){
  assert.equal(a['g'+i],((a.alpha+row.relative_final_pc-row.role_offset)%12+12)%12);modularChecks++;
}

const fraction=value=>{const [a,b='1']=value.split('/');return [BigInt(a),BigInt(b)];};
const exactRows=positive.optional_exact_rational_profile.rows.map(row=>{
  const [fn,fd]=fraction(row.relative_final_frequency),[gn,gd]=fraction(row.relative_gong_frequency),[rn,rd]=fraction(row.role_ratio);
  const k=row.octave_exponent;
  assert.ok(Number.isInteger(k));
  const n=gn*rn*(k>=0?2n**BigInt(k):1n),d=gd*rd*(k<0?2n**BigInt(-k):1n);
  assert.equal(fn*d,n*fd,'Rational/register lift mismatch');
  return {...row,equality_verified:true};
});

const output={schema:'sunny.contextual-alignment.v1',generated_utc:new Date().toISOString(),
  scope:'Executable conditional reconstruction of the specified received/later/modern source adapters; all16goals remain active.',
  inputSnapshots:snapshots,code:{path:'src/contextual-alignment.ts',sha256:digest(fs.readFileSync(path.join(root,'src/contextual-alignment.ts')))},
  reuse:{engine:'src/law.ts + src/prediction.ts',method:'Cyclic difference constraints, graph potentials, closed-cycle obstruction and free component origins.',
    priorArt:'The separate-modal interpretation and four ancestral tonics are already discussed in the cited primary/later witnesses and Hegesh2025; no new historical solution or generic graph theorem claimed.'},
  nativeMathematicalRegister:{variables:obstruction.variables,units:obstruction.units_domain,
    assumptions:obstruction.hypotheses,roleOffsets:positive.operator.offsets,nativeRoles:native.cases,
    domainBoundary:'The12-position adapter is explicit; it is not a replacement for complete Western/Chinese musical structure or an ancientHz calibration.'},
  cases:{rejectedCase,ancestralCase,allCase},results:{rejected,ancestral,allRituals},
  proofLedger:{cycle:rejected.cycle,inclusionMinimalCore:rejected.inclusionMinimalCore,
    deletionChecks:deletionChecks.map(x=>({removed:x.removed,assignmentCount:x.assignmentCount,status:x.status})),
    ancestralOriginChecks:12,allRitualRowOriginChecks:modularChecks,exactRationalRegisterChecks:exactRows},
  transformationRegister:{modalInverse:positive.operator,removed:positive.cross_context_constraints.removed,
    retained:positive.cross_context_constraints.retained,allRitualConditions:extension,
    exactLiftBoundary:positive.optional_all_ritual_lift_limit},
  discrepancyRegister:{excludedAdapter:obstruction.new_constraint_for_sunny,survivingAlternatives:obstruction.localized_alternatives,
    sourceConditionsForPositive:positive.exact_source_conditions,sourceVariantAndComma:positive.optional_all_ritual_lift_limit},
  conditionalPredictions:{ancestral:ancestral.prediction,allRituals:allRituals.prediction,
    originUnderdetermined:true,frequencyScaleUnderdetermined:'K>0 remains arbitrary in the ideal inverse-length profile.',
    blind:false,discriminatingObservation:positive.discriminating_observation},
  scoreFragment:{contexts:extension.rows.map(row=>({...row,origin:'alpha',onset:null,duration:null,instrumentInstance:null})),
    ancestralExactProfile:exactRows,scope:'Named final, role and implicit-gong relationships only; missing performance assignments and timing are not invented.'},
  canonicalPromotion:false,globalOrientationSelected:false,historicalInterpretationSelected:false,
  remaining:['Original symbol/sound coupling and contextual grammar','Historical adjudication between received and later modal readings',
    'Full exact12-row acoustic/register lift','Full systemic/generational architecture','Independent withheld-target prediction']};
if(checkOnly){
  const {generated_utc:oldTime,...oldResult}=published;
  const {generated_utc:newTime,...newResult}=output;
  assert.equal(JSON.stringify(newResult),JSON.stringify(oldResult),'Frozen result does not reproduce');
  console.log(JSON.stringify({status:'verified-frozen-execution',exit_code:0,inconsistentAdapterSolutions:0,
    cycleResidue:4,positiveOriginCount:12,prescriptions:12,modularChecks,exactRationalChecks:exactRows.length,
    mutation:false}));
  process.exit(0);
}
if(fs.existsSync(destination)){
  const raw=fs.readFileSync(destination),saved=path.join(root,'state/checkpoint-history','before-contextual-alignment-'+digest(raw)+'.json');
  if(!fs.existsSync(saved))fs.writeFileSync(saved,raw,{flag:'wx'});
}
fs.writeFileSync(destination,JSON.stringify(output,null,2)+'\n');
const report=`# SUNNY — executable contextual alignment\n\nRun: \`npm run build\`, then \`node scripts/execute_contextual_alignment.mjs\`.\n\nThe exact solver reuses SUNNY's candidate/prediction engine. It tests the recovered constraints rather than electing a global orientation.\n\n## Computed result\n\nThe single-context adapter requires h−c=4, t−c=7 and t−h=7 modulo12. Its closed cycle has nonzero residue4, so it has **zero solutions**. Deleting any one equation leaves12 solutions. Origin changes, global reversal and octave/register shifts do not remove this conditional obstruction.\n\nA source-supported separate-modal interpretation gives the ancestral implicit gongs **alpha+[0,9,7,2]**, retaining **all12 origins**. The conditional extension covers **all12 selected ritual prescriptions** and passes **144 row/origin checks**. Four ancestral exact rational/register equalities also pass. The full12-row exact lift remains withheld because the comma and textual-variant conditions are unresolved.\n\n## Meaning for the reconstruction\n\nA role label cannot be silently forced into one shared context. The executable family preserves source, role, context, register and remaining origin freedom. This contributes connected entries to the mathematical, transformation, constraint, proof, discrepancy, prediction and partial-score registers; it does not complete those deliverables.\n\nThe four-mode reading and its ancestral tonic assignments are **reused prior art**, not a new historical discovery. Source witnesses and modern adapter conditions remain distinct. No sacred phonetic system, historical alignment or blind prediction has been established.\n\nMachine-readable reconstruction: [contextual-alignment.json](../../state/reconstruction/contextual-alignment.json). Full positive/literal source packet: [Chinese research](../research/reactivation-chinese.md). The source bytes consumed by this run are preserved in content-addressed snapshots.\n`;
fs.writeFileSync(path.join(root,'docs/reconstruction/CONTEXTUAL_ALIGNMENT.md'),report);
console.log(JSON.stringify({status:'executed',inconsistentAdapterSolutions:0,cycleResidue:4,
  positiveOriginCount:12,prescriptions:12,modularChecks,exactRationalChecks:exactRows.length,
  output:'state/reconstruction/contextual-alignment.json',report:'docs/reconstruction/CONTEXTUAL_ALIGNMENT.md'}));
