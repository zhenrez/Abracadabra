import test from 'node:test';
import assert from 'node:assert/strict';
import { evaluateCandidates, evaluatePredicate, rational, checkComposition, checkCorrespondence, checkLawDependencies, scorePredictionBatch } from '../dist/law.js';
import { GEOMETRY_SCOPE, wheelAddress, wheelPoint, torusPoint, sierpinskiTetrahedron } from '../dist/geometry.js';

const SHA = 'a'.repeat(64);
const kernel = { id: 'fixture-only', version: '1', sha256: SHA, sourceRefs: ['synthetic:test-kernel'] };
const candidate = (id, assignment) => ({ id, assignment, sourceRefs: ['synthetic:test-fixture'] });
const constraint = (id, predicate, extra = {}) => ({ id, predicate, kernelSha256: SHA, sourceRefs: ['synthetic:constraint'], authority: 'assumption', ...extra });

test('finite explicit filter retains tied candidates without canonical promotion', () => {
  const result = evaluateCandidates([candidate('a',{n:2}), candidate('b',{n:2}), candidate('c',{n:3})], [constraint('n2',{op:'eq',key:'n',value:2})], kernel);
  assert.deepEqual(result.admissible,['a','b']);
  assert.deepEqual(result.rejected,['c']);
  assert.equal(result.results[2].witnesses[0].verdict,'fail');
  assert.equal(result.canonicalPromotion,false);
  assert.equal(result.probability,null);
  assert.equal(result.familyCompleteness,'not-established');
});

test('missing evidence, missing values, mismatched kernels and custom operators stay unknown', () => {
  const tests = [
    constraint('missing',{op:'eq',key:'n',value:2}),
    constraint('no-source',{op:'eq',key:'present',value:1},{sourceRefs:[]}),
    constraint('other-kernel',{op:'eq',key:'present',value:1},{kernelSha256:'b'.repeat(64)}),
    constraint('new-operator',{op:'custom',name:'not-predefined',payload:{field:'open'}}),
  ];
  const result = evaluateCandidates([candidate('a',{present:1})],tests,kernel);
  assert.deepEqual(result.unresolved,['a']);
  assert.deepEqual(result.results[0].witnesses.map(w=>w.verdict),['unknown','unknown','unknown','unknown']);
});

test('an explicit failure remains a failure alongside unresolved constraints', () => {
  const r = evaluateCandidates([candidate('a',{x:1})],[constraint('fail',{op:'eq',key:'x',value:2}),constraint('missing',{op:'eq',key:'y',value:1})],kernel);
  assert.deepEqual(r.rejected,['a']);
  assert.equal(r.results[0].witnesses.length,2);
});

test('empty constraints provide no lawful promotion; duplicate IDs cannot disappear', () => {
  assert.deepEqual(evaluateCandidates([candidate('a',{})],[],kernel).unresolved,['a']);
  assert.throws(()=>evaluateCandidates([candidate('a',{}),candidate('a',{})],[],kernel),/duplicate candidate/);
  assert.throws(()=>evaluateCandidates([],[constraint('x',{op:'unknown',reason:'x'}),constraint('x',{op:'unknown',reason:'x'})],kernel),/duplicate constraint/);
  assert.throws(()=>evaluateCandidates([],[],{...kernel,sha256:'unfrozen'}),/SHA256/);
});

test('exact rational arithmetic preserves units and large integers without float tolerance', () => {
  assert.deepEqual(rational(-6,-9),{numerator:'2',denominator:'3'});
  assert.deepEqual(rational(0,-7),{numerator:'0',denominator:'1'});
  assert.throws(()=>rational(1,0),/zero/);
  assert.throws(()=>rational(Number.MAX_SAFE_INTEGER+1,1),/safe/);
  const p = {op:'ratio',numeratorKey:'a',denominatorKey:'b',expected:rational(2,3)};
  assert.equal(evaluatePredicate(p,{a:'18014398509481986',b:'27021597764222979'}).verdict,'pass');
  assert.equal(evaluatePredicate(p,{a:2,b:0}).verdict,'unknown');
  assert.equal(evaluatePredicate(p,{a:0.2,b:0.3}).verdict,'unknown');
  assert.equal(evaluatePredicate(p,{a:{numerator:'4',denominator:'3'},b:2}).verdict,'pass');
});

test('JSON object key order does not create false distinctions; null differs from absent', () => {
  assert.equal(evaluatePredicate({op:'eq',key:'a',value:{x:1,y:2}},{a:{y:2,x:1}}).verdict,'pass');
  assert.equal(evaluatePredicate({op:'eq',key:'a',value:null},{a:null}).verdict,'pass');
  assert.equal(evaluatePredicate({op:'eq',key:'a',value:null},{}).verdict,'unknown');
  assert.equal(evaluatePredicate({op:'allDifferent',keys:['a','b']},{a:{x:1,y:2},b:{y:2,x:1}}).verdict,'fail');
});

test('three-valued operators do not discard unknown children or count repeats as votes', () => {
  const yes={op:'eq',key:'x',value:1}; const no={op:'eq',key:'x',value:2}; const missing={op:'unknown',reason:'not retrieved'};
  assert.equal(evaluatePredicate({op:'all',predicates:[yes,missing]},{x:1}).verdict,'unknown');
  assert.equal(evaluatePredicate({op:'all',predicates:[no,missing]},{x:1}).verdict,'fail');
  assert.equal(evaluatePredicate({op:'any',predicates:[no,missing]},{x:1}).verdict,'unknown');
  assert.equal(evaluatePredicate({op:'any',predicates:[yes,missing]},{x:1}).verdict,'pass');
  assert.equal(evaluatePredicate({op:'all',predicates:[]},{}).verdict,'unknown');
  const r=evaluateCandidates([candidate('a',{x:1})],[constraint('one',yes,{dependencyGroups:['same-source']}),constraint('two',yes,{dependencyGroups:['same-source']})],kernel);
  assert.deepEqual(r.dependencyGroups,['same-source']);
  assert.equal(r.probability,null);
});

test('invalid nonfinite, cyclic and inherited assignment values cannot enter definite evaluation', () => {
  const cycle={}; cycle.self=cycle;
  for (const assignment of [{x:NaN},{x:Infinity},cycle,{x:new Date()}]) assert.throws(()=>evaluateCandidates([candidate('bad',assignment)],[],kernel),/invalid candidate/);
  assert.equal(evaluatePredicate({op:'eq',key:'x',value:null},{x:NaN}).verdict,'unknown');
  assert.equal(evaluatePredicate({op:'eq',key:'toString',value:'something'},{}).verdict,'unknown');
});

const op=(id,domain,codomain,invariants=[])=>({id,domain,codomain,invariants,sourceRefs:['synthetic:operator']});
const systems=[
  {id:'native-A',revision:'a1',objectTypes:['a'],operators:[op('rotate',['a'],'a',['period'])],sourceRefs:['synthetic:native-A']},
  {id:'native-B',revision:'b1',objectTypes:['b'],operators:[op('shift',['b'],'b',['period'])],sourceRefs:['synthetic:native-B']},
];
const correspondence={id:'fixture-map',fromSystemId:'native-A',toSystemId:'native-B',fromRevision:'a1',toRevision:'b1',objectMap:{a:'b'},operatorMap:{rotate:'shift'},sourceRefs:['synthetic:map'],witnesses:[]};

test('composition checks declared source and target types; multiple inputs stay unresolved',()=>{
  assert.equal(checkComposition(op('f',['a'],'b'),op('g',['b'],'c')).verdict,'pass');
  assert.equal(checkComposition(op('f',['a'],'b'),op('g',['c'],'d')).verdict,'fail');
  assert.equal(checkComposition(op('f',['a'],'b'),op('g',['b','b'],'c')).verdict,'unknown');
});

test('shared signatures never establish dynamics or invariant preservation',()=>{
  const r=checkCorrespondence(correspondence,systems);
  assert.equal(r.verdict,'unknown');
  assert.ok(r.checks.some(c=>c.reason.includes('missing dynamics')));
  assert.ok(r.checks.some(c=>c.reason.includes('missing invariant:period')));
  assert.ok(r.checks.some(c=>c.reason.includes('missing composition:rotate')));
  assert.equal(r.canonicalPromotion,false);
});

test('typed correspondence checks explicit witnesses without claiming independent proof',()=>{
  const witnesses=['dynamics','invariant:period','composition:rotate'].map(obligation=>({fromOperator:'rotate',toOperator:'shift',obligation,verdict:'pass',sourceRefs:['synthetic:equation-witness']}));
  assert.equal(checkCorrespondence({...correspondence,witnesses},systems).verdict,'pass');
  assert.equal(checkCorrespondence({...correspondence,witnesses:[...witnesses,{...witnesses[0],verdict:'fail'}]},systems).verdict,'fail');
  assert.equal(checkCorrespondence({...correspondence,toRevision:'b0',witnesses},systems).verdict,'unknown');
  assert.equal(checkCorrespondence({...correspondence,objectMap:{a:'undefined-type'},witnesses},systems).verdict,'fail');
  assert.equal(checkCorrespondence({...correspondence,operatorMap:{}},systems).verdict,'unknown');
});

test('720-degree address preserves both turns and generation boundaries, including negative phase',()=>{
  assert.deepEqual([0,360,720,1080,1440].map(x=>[wheelAddress(x).generation,wheelAddress(x).rotation,wheelAddress(x).dialDegrees]),[[0,0,0],[0,1,0],[1,0,0],[1,1,0],[2,0,0]]);
  assert.deepEqual([wheelAddress(-30).generation,wheelAddress(-30).phaseDegrees,wheelAddress(-30).rotation],[-1,690,1]);
  assert.throws(()=>wheelAddress(Infinity),/finite/);
  assert.equal(wheelPoint(30,null,1),null);
  assert.equal(wheelPoint(30,1,null),null);
  assert.throws(()=>wheelPoint(30,-1,1),/nonnegative/);
});

test('torus parameterization satisfies its ring equation and periodicity on a finite grid',()=>{
  for(let i=0;i<=12;i++) for(let j=0;j<=12;j++){
    const u=2*Math.PI*i/12,v=2*Math.PI*j/12;
    const p=torusPoint(u,v,3,1);
    const [x,y,z]=p;
    assert.ok(Math.abs((Math.hypot(x,y)-3)**2+z*z-1)<1e-12);
    const periodic=torusPoint(u+2*Math.PI,v+2*Math.PI,3,1);
    assert.ok(Math.hypot(...p.map((c,k)=>c-periodic[k]))<1e-12);
  }
  assert.throws(()=>torusPoint(0,0,1,1),/ring torus/);
  assert.throws(()=>torusPoint(NaN,0,3,1),/finite/);
  assert.equal(GEOMETRY_SCOPE.soundWaveTopologyEstablished,false);
});

test('finite Sierpinski construction has exactly 4^depth half-scale cells with no infinite claim',()=>{
  const distance=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
  const edge=distance(...sierpinskiTetrahedron(0)[0].slice(0,2));
  for(let depth=0;depth<=4;depth++){
    const cells=sierpinskiTetrahedron(depth);
    assert.equal(cells.length,4**depth);
    for(const cell of cells) assert.ok(Math.abs(distance(cell[0],cell[1])-edge*2**(-depth))<1e-12);
  }
  const mutable=sierpinskiTetrahedron(0); mutable[0][0][0]=999;
  assert.equal(sierpinskiTetrahedron(0)[0][0][0],1);
  assert.throws(()=>sierpinskiTetrahedron(8),/finite approximation/);
  assert.throws(()=>sierpinskiTetrahedron(0.5),/integer/);
  assert.equal(GEOMETRY_SCOPE.infiniteLimitRendered,false);
});

test('derived type-law revisions retain missing dependencies, cycles and superseded records',()=>{
  const law=(id,revision,dependencies=[])=>({id,revision,dependencies,expression:{custom:'open vocabulary'},assumptions:[],sourceRefs:['synthetic:derivation'],status:'candidate'});
  const a=law('a','1',[{id:'b',revision:'1'}]);
  assert.equal(checkLawDependencies([a]).verdict,'unknown');
  const b=law('b','1',[{id:'a',revision:'1'}]);
  const circular=checkLawDependencies([a,b]);
  assert.equal(circular.verdict,'fail'); assert.equal(circular.cycles.length,1);
  const old=law('a','0'); old.status='superseded';
  assert.equal(checkLawDependencies([old,law('a','1')]).verdict,'pass');
  assert.equal(checkLawDependencies([old,law('a','1')]).canonicalPromotion,false);
  assert.throws(()=>checkLawDependencies([a,a]),/duplicate law revision/);
});

const prediction=(id,extra={})=>({id,probability:0.8,baselineProbability:0.5,observed:true,frozenAt:'2026-10-01T00:00:00Z',observedAt:'2026-10-02T00:00:00Z',referenceExposure:'unseen',trainingGroups:['train'],referenceGroup:'holdout',sourceRefs:['synthetic:prediction-log'],...extra});
test('prediction scoring excludes declared leakage, late freezes and invalid probabilities',()=>{
  const result=scorePredictionBatch([
    prediction('clean'), prediction('leaked',{trainingGroups:['holdout']}),
    prediction('late',{frozenAt:'2026-10-03T00:00:00Z'}),
    prediction('seen',{referenceExposure:'seen'}), prediction('invalid',{probability:1.1}),
  ]);
  assert.equal(result.count,1); assert.equal(result.totalSubmitted,5); assert.equal(result.excluded.length,4);
  assert.ok(Math.abs(result.meanBrier-0.04)<1e-12); assert.equal(result.meanBaselineBrier,0.25);
  assert.equal(result.calibration,'not-established'); assert.equal(result.statisticalSignificance,'not-tested');
  assert.equal(result.actualBlindness,'not-established-by-declared-metadata');
});
test('zero valid predictions produces unknown metrics and dependent groups do not become confidence',()=>{
  assert.equal(scorePredictionBatch([]).meanBrier,null);
  const result=scorePredictionBatch([prediction('a'),prediction('b')]);
  assert.deepEqual(result.referenceGroups,['holdout']); assert.equal(result.count,2);
  assert.match(result.aggregation,/not independent/); assert.equal(result.canonicalPromotion,false);
});
