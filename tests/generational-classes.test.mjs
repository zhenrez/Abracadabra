import test from 'node:test';import assert from 'node:assert/strict';
import {compositionCount,compositions,mathematicalPredecessors,pentagonalEndpoint,rotatePentagonalAddress,balancedInheritance} from '../dist/generational-classes.js';
test('complete source-defined classes retain counts and their genuine predecessors',()=>{
 for(let n=0;n<=14;n++){const states=compositions(5,n);assert.equal(BigInt(states.length),compositionCount(5,n));for(const m of states){assert.equal(m.reduce((a,b)=>a+b,0),n);for(const p of mathematicalPredecessors(m))assert.equal(p.counts.reduce((a,b)=>a+b,0),n-1);}}
 assert.equal(compositionCount(5,3),35n);assert.equal(compositionCount(5,4),70n);
});
test('five rotations preserve native depth and exact algebraic endpoint action',()=>{
 for(const m of compositions(5,5)){const p=pentagonalEndpoint(m);let q=m;for(let i=0;i<5;i++)q=rotatePentagonalAddress(q);assert.deepEqual(q,m);
  assert.equal(p.zeroEndpoint,m.every(x=>x===m[0]));const r=pentagonalEndpoint(rotatePentagonalAddress(m)).cyclotomicBasis,[a,b,c,d]=p.cyclotomicBasis;assert.deepEqual(r,[-d,a-d,b-d,c-d].map(x=>x===0?0:x));}
});
test('balanced inheritance preserves raw endpoint and changes history and normalized observable',()=>{
 const x=balancedInheritance([10,0,0,0,0]);assert.deepEqual(x.before.cyclotomicBasis,x.after.cyclotomicBasis);assert.equal(x.addedConstructionSteps,5);assert.deepEqual(x.normalizedEndpointFactor,{numerator:'10',denominator:'15'});assert.equal(x.after.acousticFrequency,null);
 assert.equal(balancedInheritance([0,0,0,0,0]).normalizedEndpointFactor,null);
});
test('a finite display budget cannot masquerade as a complete unbounded class enumeration',()=>{
 assert.throws(()=>compositions(5,14,100),/budget/);assert.equal(compositionCount(5,14),3060n);
 assert.throws(()=>compositions(0,2),/generator/);assert.throws(()=>pentagonalEndpoint([1,2,3]),/five/);
 assert.throws(()=>mathematicalPredecessors([0,-1,0,0,0]),/nonnegative/);
});
