import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {solveContextualAlignment} from './build/contextual-alignment.js';

const owned=path.dirname(fileURLToPath(import.meta.url));
const workspace=path.resolve(owned,'../../../..');
const readBytes=p=>fs.readFileSync(path.resolve(workspace,p));
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const json=p=>JSON.parse(readBytes(p).toString('utf8').replace(/^\uFEFF/,''));
const artifactPath='state/reconstruction/contextual-alignment.json';
const artifactBytes=readBytes(artifactPath),artifact=json(artifactPath);
const mod=(a,m)=>((a%m)+m)%m;
const sourceSnapshots=[];
const sources=artifact.inputSnapshots.map(s=>{
  const bytes=readBytes(s.snapshotPath),current=readBytes(s.sourceOccurrencePath);
  assert.equal(hash(bytes),s.sha256,'Snapshot hash '+s.snapshotPath);
  assert.equal(bytes.length,s.bytes,'Snapshot size '+s.snapshotPath);
  sourceSnapshots.push({...s,currentOccurrenceSha256:hash(current),currentOccurrenceMatchesSnapshot:hash(current)===s.sha256});
  return JSON.parse(bytes.toString('utf8').replace(/^\uFEFF/,''));
});
assert.equal(sources.length,3);
const [obstruction,positive,native]=sources;
assert.equal(hash(readBytes(artifact.code.path)),artifact.code.sha256,'Solver hash');
const compiledBindings=['contextual-alignment.js','law.js','prediction.js'].map(name=>{
  const isolatedSha256=hash(fs.readFileSync(path.join(owned,'build',name)));
  const rootDistSha256=hash(readBytes('dist/'+name));
  assert.equal(isolatedSha256,rootDistSha256,'Root dist differs from reviewed build '+name);
  return {name,isolatedSha256,rootDistSha256};
});
const pairs=[['rejectedCase','rejected'],['ancestralCase','ancestral'],['allCase','allRituals']];
for(const [caseKey,resultKey] of pairs){
  assert.deepEqual(JSON.parse(JSON.stringify(solveContextualAlignment(artifact.cases[caseKey]))),artifact.results[resultKey],'Recompute serialized '+caseKey);
}
for(const e of obstruction.equations){
  const match=/^([a-z]+)-([a-z]+)-(\d+)=0mod(\d+)$/.exec(e.expression.replace(/\s/g,''));
  assert.ok(match,'Declared equation syntax');
  const bound=artifact.cases.rejectedCase.links.find(link=>link.id===e.id);
  assert.ok(bound,'Equation represented '+e.id);
  assert.equal(bound.from,match[2]);assert.equal(bound.to,match[1]);
  assert.equal(bound.offset,Number(match[3]));assert.equal(artifact.cases.rejectedCase.modulus,Number(match[4]));
}
assert.equal(artifact.cases.rejectedCase.links.length,obstruction.equations.length);
assert.deepEqual(artifact.cases.rejectedCase.assumptions,obstruction.hypotheses);
assert.deepEqual(artifact.nativeMathematicalRegister.nativeRoles,native.cases);
assert.deepEqual(artifact.nativeMathematicalRegister.roleOffsets,positive.operator.offsets);
assert.equal(artifact.results.rejected.status,'inconsistent');
assert.equal(artifact.results.rejected.assignmentCount,'0');
assert.equal(artifact.proofLedger.cycle.residue,4);
assert.deepEqual(artifact.proofLedger.cycle,artifact.results.rejected.cycle);
assert.deepEqual(artifact.proofLedger.inclusionMinimalCore,artifact.results.rejected.inclusionMinimalCore);
for(const row of artifact.proofLedger.deletionChecks){
  const result=solveContextualAlignment({...artifact.cases.rejectedCase,links:artifact.cases.rejectedCase.links.filter(link=>link.id!==row.removed)});
  assert.equal(row.assignmentCount,result.assignmentCount);assert.equal(row.status,result.status);
}
assert.equal(artifact.proofLedger.deletionChecks.length,3);
assert.equal(artifact.results.ancestral.assignmentCount,'12');
assert.equal(artifact.results.allRituals.assignmentCount,'12');
let ancestralRows=0;
for(const row of positive.ancestral_family.representatives){
  const assigned=artifact.results.ancestral.assignments.find(a=>a.alpha===row.alpha);
  assert.ok(assigned,'Every source origin represented');
  for(let i=0;i<4;i++){
    const role=positive.ancestral_family.mode_roles[i];
    assert.equal(assigned['g'+i],row.implicit_gong_pcs[i]);
    assert.equal(mod(row.final_pcs[i]-positive.operator.offsets[role],12),assigned['g'+i]);
    ancestralRows++;
  }
}
assert.equal(positive.ancestral_family.representatives.length,12);
let rowOriginChecks=0;
const extension=positive.all_three_rows_modular_extension;
for(const assignment of artifact.results.allRituals.assignments){
  for(const [i,row] of extension.rows.entries()){
    const link=artifact.cases.allCase.links[i];
    assert.equal(link.id,row.model_context_id);
    assert.equal(link.from,'alpha');assert.equal(link.to,'g'+i);
    assert.equal(row.role_offset,positive.operator.offsets[row.role]);
    assert.equal(link.offset,row.relative_implicit_gong_pc);
    assert.equal(assignment['g'+i],mod(assignment.alpha+row.relative_final_pc-row.role_offset,12));
    rowOriginChecks++;
  }
}
assert.equal(rowOriginChecks,144);
assert.equal(artifact.proofLedger.allRitualRowOriginChecks,rowOriginChecks);
const fraction=s=>{const [n,d='1']=s.split('/');return [BigInt(n),BigInt(d)];};
let exactChecks=0;
for(const [i,row] of positive.optional_exact_rational_profile.rows.entries()){
  const [fn,fd]=fraction(row.relative_final_frequency),[gn,gd]=fraction(row.relative_gong_frequency),[rn,rd]=fraction(row.role_ratio),k=row.octave_exponent;
  assert.ok(Number.isSafeInteger(k));
  const left=fn*gd*rd*(k<0?2n**BigInt(-k):1n);
  const right=fd*gn*rn*(k>=0?2n**BigInt(k):1n);
  assert.equal(left,right,'Independent integer cross-product');
  assert.deepEqual(artifact.proofLedger.exactRationalRegisterChecks[i],{...row,equality_verified:true});exactChecks++;
}
assert.equal(exactChecks,4);
assert.deepEqual(artifact.transformationRegister.exactLiftBoundary,positive.optional_all_ritual_lift_limit);
assert.deepEqual(artifact.conditionalPredictions.ancestral,artifact.results.ancestral.prediction);
assert.deepEqual(artifact.conditionalPredictions.allRituals,artifact.results.allRituals.prediction);
for(const key of ['canonicalPromotion','globalOrientationSelected','historicalInterpretationSelected'])assert.equal(artifact[key],false);
assert.equal(artifact.conditionalPredictions.blind,false);
assert.equal(artifact.conditionalPredictions.originUnderdetermined,true);
for(const context of artifact.scoreFragment.contexts){
  assert.equal(context.onset,null);assert.equal(context.duration,null);assert.equal(context.instrumentInstance,null);
}
assert.equal(hash(readBytes(artifactPath)),hash(artifactBytes),'Root artifact stable during audit');
const result={schema:'sunny.contextual-alignment-artifact-audit.v1',checked_utc:new Date().toISOString(),status:'passed',artifactPath,artifactSha256:hash(artifactBytes),sourceSnapshots,compiledBindings,caseRecomputations:pairs.length,sourceEquationBindings:obstruction.equations.length,ancestralRoleOriginChecks:ancestralRows,allRitualRowOriginChecks:rowOriginChecks,exactRationalRegisterChecks:exactChecks,scope:'Source snapshot fidelity and finite declared adapter arithmetic; independent historical adjudication is not established.',rootArtifactStableDuringRun:true};
fs.writeFileSync(path.join(owned,'artifact-audit-result.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
