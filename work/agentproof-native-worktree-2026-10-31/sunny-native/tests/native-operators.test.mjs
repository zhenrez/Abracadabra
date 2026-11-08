import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createNativeExecutor,NATIVE_GG_SHA256} from '../dist/native-operators.js';

const raw=readFileSync(new URL('../data/raw/archive/SUN_Universal_Archive/Library/SUN_DEEP_RECOVERY/SUN_GG_v1_final.json',import.meta.url));
const sourceId='9e03168cabf04e3887245d93c75f1f9d0034a53bead61e5d8b5a5e0315b259e8';
const native=createNativeExecutor(raw,sourceId);
const q=(numerator,denominator=1)=>({numerator:String(numerator),denominator:String(denominator)});
const ex=(id,payload)=>{const r=native.execute(id,payload);assert.equal(r.status,'executed',r.reason);assert.equal(r.canonicalPromotion,false);assert.equal(r.source.sha256,NATIVE_GG_SHA256);return r.output;};
const affine=(values,sign,offset)=>ex('MEC-02',{values,action:{sign,offset}}).values;
const rev=values=>ex('MEC-03',{values}).values;
const rot=(values,shift)=>ex('MEC-05',{values,shift}).values;

test('exact original registry preserves all 10 mechanisms and 19 native members',()=>{
  const r=native.registry();assert.equal(r.length,10);assert.equal(r.flatMap(x=>x.families).length,19);
  assert.deepEqual(r.map(x=>x.id),Array.from({length:10},(_,i)=>`MEC-${String(i+1).padStart(2,'0')}`));
  assert.ok(r.every(x=>x.source.sourceId===sourceId));assert.ok(r.flatMap(x=>x.families).every(x=>x.system!=='undefined'));
  r[0].families[0].sourceMember.system='changed';assert.equal(native.registry()[0].families[0].system,'SUN scalar kernel');
  assert.throws(()=>createNativeExecutor(Buffer.concat([raw,Buffer.from(' ')]),sourceId),/pinned source/);
});
test('MEC-01 source R,L compose to O exactly; inverse and carrier/unit persist',()=>{
  const a=ex('MEC-01',{value:q(1),factor:q(2,3),carrier:'string length',unit:'relative length'});
  const b=ex('MEC-01',{value:a.value,factor:q(3,4),carrier:a.carrier,unit:a.unit});assert.deepEqual(b.value,q(1,2));
  assert.deepEqual(ex('MEC-01',{value:b.value,factor:q(2),carrier:b.carrier,unit:b.unit}).value,q(1));
  assert.equal(b.unit,'relative length');assert.equal(native.execute('MEC-01',{value:q(1),factor:q(0),carrier:'length'}).status,'invalid');
});
test('MEC-02 D12 defining relations hold; abstract identity does not supply PLR realization',()=>{
  const v=Array.from({length:12},(_,i)=>i);let x=v;for(let i=0;i<12;i++)x=affine(x,1,1);assert.deepEqual(x,v);
  assert.deepEqual(affine(affine(v,-1,0),-1,0),v);
  assert.deepEqual(affine(affine(affine(v,-1,0),1,1),-1,0),affine(v,1,-1));
  assert.equal(native.execute('MEC-02',{realization:'PLR_triad',values:[0,4,7],action:{sign:1,offset:1}}).status,'unknown');
});
test('MEC-03 reversal is involutive, and nonretrogradability stays a predicate',()=>{
  for(const v of [[],[1],[1,2,3],[{a:1},null,'x']])assert.deepEqual(rev(rev(v)),v);
  assert.equal(ex('MEC-03',{values:[1,2,1]}).isFixedPoint,true);
  assert.equal(ex('MEC-03',{values:[1,2,3]}).isFixedPoint,false);
});
test('MEC-04 mutation executes only on a declared pitch-preserving overlap',()=>{
  const a={identity:'test:one-note',pitch:q(1),address:'test:address-a'},b={...a,address:'test:address-b'};
  const mapping=[{from:a,to:b,admissible:true,sourceRefs:['test:declared-overlap']}];
  assert.equal(native.execute('MEC-04',{state:a}).status,'unknown');
  assert.deepEqual(ex('MEC-04',{state:a,mapping}).state,b);
  assert.equal(native.execute('MEC-04',{state:b,mapping}).status,'unknown');
  assert.equal(native.execute('MEC-04',{state:a,mapping:[{...mapping[0],to:{...b,pitch:q(2)}}]}).status,'unknown');
  assert.equal(native.execute('MEC-04',{state:a,mapping:[...mapping,{...mapping[0],to:{...b,address:'test:third'}}]}).status,'unknown');
});
test('MEC-05 seven index starts compose and invert without choosing an origin',()=>{
  const v=['a','b','c','d','e','f','g'];assert.equal(new Set(v.map((_,k)=>JSON.stringify(rot(v,k)))).size,7);
  assert.deepEqual(rot(rot(v,3),5),rot(v,8));assert.deepEqual(rot(rot(v,3),-3),v);
  assert.equal(native.execute('MEC-05',{values:[],shift:0}).status,'unknown');
});
test('MEC-03/05 interacting identity J rho(k) J = rho(-k)',()=>{
  for(let n=1;n<=32;n++){const v=Array.from({length:n},(_,i)=>i);for(let k=-n;k<=n;k++)assert.deepEqual(rev(rot(rev(v),k)),rot(v,-k));}
});
test('MEC-02 pitch-value action commutes with MEC-03 position reversal',()=>{
  const v=[0,7,2,9,4,11];for(const s of [-1,1])for(let o=0;o<12;o++)assert.deepEqual(rev(affine(v,s,o)),affine(rev(v),s,o));
});
test('MEC-06 E(5,13) retains all 13 phases with five onsets and gaps 2 or 3',()=>{
  const out=ex('MEC-06',{slots:13,onsets:5});assert.equal(out.rotations.length,13);assert.match(out.phase,/unspecified/);
  for(const v of out.rotations){assert.equal(v.reduce((a,b)=>a+b,0),5);const indices=v.flatMap((x,i)=>x?[i]:[]);const gaps=indices.map((x,i)=>(indices[(i+1)%5]-x+13)%13);assert.ok(gaps.every(x=>x===2||x===3));}
  assert.deepEqual(ex('MEC-06',{slots:5,onsets:0}).rotations,[[0,0,0,0,0]]);
  assert.deepEqual(ex('MEC-06',{slots:5,onsets:5}).rotations,[[1,1,1,1,1]]);
  assert.equal(native.execute('MEC-06',{slots:5,onsets:6}).status,'invalid');
});
test('MEC-07 De Morgan sieve identity handles negative integers and explicit complement',()=>{
  const universe=Array.from({length:31},(_,i)=>i-15),a={op:'residue',modulus:3,residue:1},b={op:'residue',modulus:5,residue:-1};
  const sieve=expression=>ex('MEC-07',{universe,expression}).values;
  assert.deepEqual(sieve({op:'complement',child:{op:'union',children:[a,b]}}),sieve({op:'intersection',children:[{op:'complement',child:a},{op:'complement',child:b}]}));
  assert.equal(native.execute('MEC-07',{expression:a}).status,'unknown');
  const bad={op:'union',children:[{op:'residue',modulus:1,residue:0},{op:'invented'}]};
  assert.equal(native.execute('MEC-07',{universe:[0],expression:bad}).status,'invalid');
  assert.equal(native.execute('MEC-07',{universe:[],expression:bad}).status,'invalid');
});
test('MEC-08 added duration and dot affect the selected event; insertion keeps exact unit',()=>{
  const events=[{id:'test:a',duration:q(1)},{id:'test:b',duration:q(2),kind:'rest'}];
  const out=ex('MEC-08',{events,unit:'beats',mode:'dot',index:0});assert.deepEqual(out.events[0].duration,q(3,2));assert.deepEqual(out.events[1],events[1]);
  assert.deepEqual(ex('MEC-08',{events,unit:'beats',mode:'add',index:1,delta:q(1,4)}).events[1].duration,q(9,4));
  assert.equal(ex('MEC-08',{events,unit:'beats',mode:'insert',index:1,event:{id:'test:c',duration:q(1,8)}}).events.length,3);
  assert.equal(native.execute('MEC-08',{events,unit:'beats',mode:'add',index:0,delta:q(-1,2)}).status,'unknown');
  assert.deepEqual(events[0].duration,q(1));
});
test('MEC-09 no pair of a three-antecedent rule constitutes its composite',()=>{
  const rule={id:'test:hyperedge',admissible:true,sourceRefs:['test:witness-only'],inputs:['a','b','c'],output:{testComposite:true}};
  for(const available of [['a','b'],['a','c'],['b','c']])assert.equal(native.execute('MEC-09',{rule,available}).status,'unknown');
  const out=ex('MEC-09',{rule,available:['a','b','c']});assert.equal(out.arity,3);assert.deepEqual(out.inputs,rule.inputs);assert.deepEqual(out.declaredComposite,rule.output);
  assert.equal(native.execute('MEC-09',{available:['a','b','c']}).status,'unknown');
});
test('MEC-10 preserves the actual exact distribution and never replaces it with a winner',()=>{
  const kernel={id:'test:kernel',revision:'test:1',sourceRefs:['test:kernel-input-only'],rows:[{context:['a'],distribution:[{event:'b',probability:q(2,3)},{event:'c',probability:q(1,3)}]}]};
  const out=ex('MEC-10',{context:['a'],kernel});assert.deepEqual(out.distribution,kernel.rows[0].distribution);assert.equal(Object.hasOwn(out,'winner'),false);
  assert.equal(native.execute('MEC-10',{context:['x'],kernel}).status,'unknown');
  const bad=structuredClone(kernel);bad.rows[0].distribution[1].probability=q(1,2);assert.equal(native.execute('MEC-10',{context:['a'],kernel:bad}).status,'invalid');
  assert.equal(native.execute('MEC-10',{context:['a']}).status,'unknown');
});
test('bounded API rejects non-JSON, cyclic, unsafe rational input and oversized requests',()=>{
  const cycle={};cycle.x=cycle;assert.equal(native.execute('MEC-03',cycle).status,'invalid');
  assert.equal(native.execute('MEC-03',{values:[()=>1]}).status,'invalid');
  assert.equal(native.execute('MEC-03',{values:['x'.repeat(48001)]}).status,'invalid');
  assert.equal(native.execute('MEC-01',{value:{numerator:1,denominator:1},factor:q(2),carrier:'test'}).status,'invalid');
  assert.equal(native.execute('MEC-unknown',{}).status,'unknown');
});
