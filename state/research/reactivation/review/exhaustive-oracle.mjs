import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {solveContextualAlignment} from './build/contextual-alignment.js';

const root=path.dirname(fileURLToPath(import.meta.url));
const workspace=path.resolve(root,'../../../..');
const sourceRefs=['independent-review:declared-test-equation'];
const md=(a,m)=>{const b=BigInt(m);return Number(((BigInt(a)%b)+b)%b);};
const edge=(id,from,to,offset)=>({id,from,to,offset,sourceRefs});
const input=(id,modulus,variables,links)=>({id,modulus,variables,links,sourceRefs,assumptions:['Finite cyclic difference equations only; synthetic review case.'],targets:[...variables.map(variable=>({id:'value:'+variable,kind:'value',variable})),...variables.flatMap(from=>variables.map(to=>({id:JSON.stringify([from,to]),kind:'difference',from,to})))]});
const satisfying=(spec,links=spec.links)=>{
 const found=[],total=spec.modulus**spec.variables.length;
 for(let i=0;i<total;i++){
  let digits=i;const values=Object.create(null);
  for(const variable of spec.variables){values[variable]=digits%spec.modulus;digits=Math.floor(digits/spec.modulus);}
  if(links.every(e=>md(BigInt(values[e.to])-BigInt(values[e.from])-BigInt(e.offset),spec.modulus)===0))found.push(values);
 }
 return found;
};
const assignmentKey=(spec,a)=>JSON.stringify(spec.variables.map(v=>a[v]));
const setKeys=(spec,values)=>[...new Set(values.map(a=>assignmentKey(spec,a)))].sort();
const snapshotNames=['src/contextual-alignment.ts','src/law.ts','src/prediction.ts','tests/contextual-alignment.test.mjs'];
const digestFile=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const before=Object.fromEntries(snapshotNames.map(f=>[f,digestFile(path.join(workspace,f))]));
const coverage={cases:0,assignmentsEnumerated:0,consistent:0,inconsistent:0,symbolic:0,closedWalkCertificates:0,inclusionMinimalCores:0,predictionTargets:0,materializedAssignments:0,originFamilies:0};
const results=[];

function checkCase(spec,maxAssignments=10000){
 const exact=satisfying(spec),r=solveContextualAlignment(spec,{maxAssignments});
 coverage.cases++;coverage.assignmentsEnumerated+=spec.modulus**spec.variables.length;
 assert.equal(r.assignmentCount,String(exact.length),spec.id+' count');
 for(const key of ['canonicalPromotion','globalOrientationSelected','blindPrediction'])assert.equal(r[key],false,spec.id+' boundary '+key);
 assert.equal(r.scope,'declared-finite-cyclic-adapter-only');
 if(!exact.length){
  coverage.inconsistent++;assert.equal(r.status,'inconsistent');
  const cycle=r.cycle;assert.ok(cycle.steps.length>0);assert.equal(cycle.modulus,spec.modulus);
  let cursor=cycle.steps[0].from,total=0n;const start=cursor;
  for(const step of cycle.steps){
   const original=spec.links.find(e=>e.id===step.edgeId);assert.ok(original);
   assert.equal(step.from,cursor);cursor=step.to;
   assert.ok(step.sign===1||step.sign===-1);
   const from=step.sign===1?original.from:original.to,to=step.sign===1?original.to:original.from;
   assert.equal(step.from,from);assert.equal(step.to,to);
   assert.equal(step.offset,md(BigInt(step.sign)*BigInt(original.offset),spec.modulus));
   assert.deepEqual(step.sourceRefs,original.sourceRefs);
   total+=BigInt(step.sign)*BigInt(original.offset);
  }
  assert.equal(cursor,start);assert.notEqual(md(total,spec.modulus),0);assert.equal(cycle.residue,md(total,spec.modulus));coverage.closedWalkCertificates++;
  assert.equal(new Set(r.inclusionMinimalCore).size,r.inclusionMinimalCore.length);
  const core=r.inclusionMinimalCore.map(id=>{const e=spec.links.find(e=>e.id===id);assert.ok(e);return e;});
  assert.equal(satisfying(spec,core).length,0,spec.id+' core inconsistent');
  for(const e of core)assert.ok(satisfying(spec,core.filter(x=>x.id!==e.id)).length>0,spec.id+' core deletion '+e.id);
  coverage.inclusionMinimalCores++;assert.equal(r.assignments,null);assert.equal(r.prediction,null);
 }else{
  coverage.consistent++;
  const origins=r.freeOrigins;assert.equal(BigInt(spec.modulus)**BigInt(origins.length),BigInt(exact.length));
  assert.equal(origins.flatMap(x=>x.members).length,spec.variables.length);
  assert.equal(new Set(origins.flatMap(x=>x.members.map(m=>m.variable))).size,spec.variables.length);
  const expanded=[];
  for(let i=0;i<exact.length;i++){
   let digits=i;const a=Object.create(null);
   for(const c of origins){const shift=digits%spec.modulus;digits=Math.floor(digits/spec.modulus);assert.equal(c.members.find(x=>x.variable===c.referenceVariable).relativeValue,0);for(const member of c.members)a[member.variable]=md(BigInt(member.relativeValue)+BigInt(shift),spec.modulus);}
   expanded.push(a);
  }
  assert.deepEqual(setKeys(spec,expanded),setKeys(spec,exact),spec.id+' complete origin family');coverage.originFamilies++;
  if(exact.length>maxAssignments){coverage.symbolic++;assert.equal(r.status,'symbolic-family');assert.equal(r.assignments,null);assert.equal(r.prediction,null);}
  else{
   assert.equal(r.status,'admissible-family');assert.equal(r.assignments.length,exact.length);assert.deepEqual(setKeys(spec,r.assignments),setKeys(spec,exact));coverage.materializedAssignments+=r.assignments.length;
   assert.equal(r.prediction.retainedCandidateIds.length,exact.length);assert.equal(new Set(r.prediction.retainedCandidateIds).size,exact.length);
   assert.equal(r.prediction.globalOrientationSelected,false);assert.equal(r.prediction.canonicalPromotion,false);assert.equal(r.prediction.blindPrediction,false);assert.equal(r.prediction.familyCompleteness,'not-established');
   for(const target of spec.targets){
    const expected=new Map();
    for(const a of exact){const value=target.kind==='value'?a[target.variable]:md(BigInt(a[target.to])-BigInt(a[target.from]),spec.modulus),key=JSON.stringify([value]),id=spec.id+':origin:'+origins.map(o=>a[o.referenceVariable]).join('.');const group=expected.get(key)??[];group.push(id);expected.set(key,group);}
    const actual=r.prediction.predictions.find(p=>p.targetId===target.id);assert.ok(actual);assert.equal(actual.status,expected.size===1?'determined-within-supplied-family':'alternatives');assert.deepEqual(actual.missingCandidateIds,[]);assert.equal(actual.alternatives.length,expected.size);
    for(const alternative of actual.alternatives)assert.deepEqual([...alternative.candidateIds].sort(),[...expected.get(JSON.stringify(alternative.value))].sort(),spec.id+' prediction membership '+target.id);
    coverage.predictionTargets++;
   }
  }
 }
 results.push({id:spec.id,modulus:spec.modulus,variables:spec.variables.length,links:spec.links.length,exactSolutions:exact.length,status:r.status});
 return r;
}

const fixed=[
 input('zero-self-loop',6,['x'],[edge('z','x','x',0)]),
 input('nonzero-self-loop',6,['x'],[edge('n','x','x',-2)]),
 input('multiple-self-loops',4,['x','y'],[edge('z','x','x',0),edge('n','y','y',4),edge('c','x','y',-1)]),
 input('disconnected-composite',6,['x','y','z','w'],[edge('a','x','y',-7)]),
 input('redundant-forward-reverse',8,['x','y','z'],[edge('a','x','y',3),edge('b','y','x',-3),edge('c','y','z',-10),edge('d','x','z',-7)]),
 input('conflicting-parallel',9,['x','y'],[edge('a','x','y',-2),edge('b','y','x',1),edge('c','y','y',0)]),
 input('safe-integer-offsets',6,['x','y'],[edge('a','x','y',Number.MAX_SAFE_INTEGER),edge('b','y','x',-Number.MAX_SAFE_INTEGER)]),
 input('prototype-names',4,['__proto__','constructor','toString'],[edge('constructor','__proto__','constructor',-1),edge('__proto__','constructor','toString',2)]),
 input('isolated-components',4,['x','y','z','w'],[]),
 input('zero-modulus-multiple',8,['x','y'],[edge('a','x','y',16),edge('b','y','x',-24)]),
];
for(const spec of fixed)checkCase(spec,spec.id==='isolated-components'?1:10000);
let state=0x5A17C0DE;const random=limit=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state%limit;};
for(let i=0;i<240;i++){
 const m=[2,3,4,5,6,8,9][random(7)],n=1+random(4),variables=Array.from({length:n},(_,j)=>'v'+j),count=random(9),links=[];
 for(let j=0;j<count;j++)links.push(edge('e'+j,variables[random(n)],variables[random(n)],random(6*m+1)-3*m));
 checkCase(input('seeded-'+i,m,variables,links),i%3===0?1:10000);
}
const chinese=input('source-three-equation-adapter',12,['c','h','t'],[edge('A','c','h',4),edge('B','c','t',7),edge('C','h','t',7)]);
checkCase(chinese);for(const e of chinese.links)assert.equal(checkCase({...chinese,id:'source-drop-'+e.id,links:chinese.links.filter(x=>x.id!==e.id)}).assignmentCount,'12');
const modal=input('source-modal-relative-family',12,['alpha','g0','g1','g2','g3'],[0,9,7,2].map((x,i)=>edge('mode'+i,'alpha','g'+i,x)));
checkCase(modal);
const after=Object.fromEntries(snapshotNames.map(f=>[f,digestFile(path.join(workspace,f))]));assert.deepEqual(after,before,'root source/test snapshot changed during review');
const output={schema:'sunny.independent-cyclic-difference-review.v1',checked_utc:new Date().toISOString(),status:'passed',oracle:'Independent direct exhaustive assignments using BigInt equation residuals; graph-potential algorithm not reused.',seed:'0x5A17C0DE',fixedCases:fixed.length,seededCases:240,coverage,sourceHashes:before,compiledHashes:Object.fromEntries(['contextual-alignment.js','law.js','prediction.js'].map(f=>[f,digestFile(path.join(root,'build',f))])),rootInputsStableDuringRun:true,results,scope:'Finite declared difference constraints, certificates, inclusion minimality, complete origin family and materialized predictions. Historical source authenticity/global uniqueness remain outside this check.'};
fs.writeFileSync(path.join(root,'exhaustive-review-result.json'),JSON.stringify(output,null,2));console.log(JSON.stringify({status:output.status,coverage,rootInputsStableDuringRun:true},null,2));
