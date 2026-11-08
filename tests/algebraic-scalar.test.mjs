import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createAlgebraicScalar} from '../dist/algebraic-scalar.js';
const raw=readFileSync(new URL('../data/raw/archive/SUN_Universal_Archive/Library/SUN_DEEP_RECOVERY/SUN_GG_v1_final.json',import.meta.url));
const a=createAlgebraicScalar(raw,'9e03168cabf04e3887245d93c75f1f9d0034a53bead61e5d8b5a5e0315b259e8');
const q=(n,d=1)=>({numerator:String(n),denominator:String(d)});
const one=a.make([]),two=a.fromRational(q(2)),three=a.fromRational(q(3));
const root=a.make([{prime:'2',exponent:q(1,12)}]);
test('source q is exact and q^12=2 although q is not in G',()=>{
 assert.ok(a.equal(a.power(root,q(12)),two));assert.equal(a.inG(root),false);assert.equal(a.inH(root),true);assert.equal(a.asRational(root).status,'non-rational');
 assert.equal(a.source.pointer,'/generative_registry/0');assert.throws(()=>createAlgebraicScalar(Buffer.concat([raw,Buffer.from(' ')]),'x'),/pinned source/);
});
test('prime normal form combines/cancels exponents and preserves exact inverses',()=>{
 const x=a.make([{prime:'3',exponent:q(2,3)},{prime:'2',exponent:q(-1,12)},{prime:'3',exponent:q(1,3)}]);
 assert.deepEqual(x.powers,[{prime:'2',exponent:q(-1,12)},{prime:'3',exponent:q(1)}]);assert.ok(a.equal(a.multiply(x,a.inverse(x)),one));assert.ok(a.equal(a.power(a.power(x,q(3)),q(1,3)),x));
 assert.throws(()=>a.make([{prime:'4',exponent:q(1)}]),/prime/);
});
test('G generator lattice reconstructs2,3, sanfen and retained bridge inputs',()=>{
 const R=a.fromRational(q(2,3)),L=a.fromRational(q(3,4));assert.ok(a.equal(a.multiply(R,L),a.fromRational(q(1,2))));
 assert.ok(a.equal(a.inverse(a.multiply(R,L)),two));assert.ok(a.equal(a.multiply(a.power(R,q(-2)),a.inverse(L)),three));
 assert.ok(a.equal(a.inverse(L),a.fromRational(q(4,3))));
 assert.deepEqual(a.asRational(a.divide(a.fromRational(q(16,15)),a.fromRational(q(81,80)))),{status:'rational',value:q(256,243)});
});
test('H/G has exactly12 cosets and keeps arbitrary integer3powers within G',()=>{
 const residues=[];for(let k=0;k<12;k++){const x=a.multiply(a.power(root,q(k)),a.power(three,q(100+k)));residues.push(a.hCoordinates(x).quotientByG.rootStepMod12);assert.equal(a.inG(x),k===0);}
 assert.deepEqual(residues,Array.from({length:12},(_,i)=>i));assert.equal(a.hCoordinates(a.power(root,q(12))).quotientByG.rootStepMod12,0);
});
test('integer-octave quotient retains fractional2powers and unbounded3coordinate',()=>{
 assert.ok(a.equal(a.moduloOctaves(a.power(root,q(7))).representative,a.power(root,q(7))));
 assert.deepEqual(a.moduloOctaves(a.make([{prime:'2',exponent:q(-1,12)}])),{representative:a.make([{prime:'2',exponent:q(11,12)}]),removedOctaves:'-1'});
 for(let b=-40;b<=40;b++){const x=a.multiply(a.power(root,q(7)),a.power(three,q(b)));const c=a.hCoordinates(x);assert.equal(c.quotientByIntegerOctaves.prime3Exponent,String(b));assert.equal(c.rootStepMod12,7);}
 assert.equal(a.equal(a.moduloOctaves(three).representative,one),false);
});
test('root-fifth discriminator gives the inverse twelve-fifths comma exactly',()=>{
 const pure=a.fromRational(q(3,2)),equalTempered=a.power(root,q(7)),delta=a.divide(equalTempered,pure);
 assert.equal(a.equal(pure,equalTempered),false);assert.deepEqual(delta,a.make([{prime:'2',exponent:q(19,12)},{prime:'3',exponent:q(-1)}]));
 const comma=a.divide(a.power(pure,q(12)),a.power(two,q(7)));
 assert.deepEqual(a.asRational(a.power(delta,q(12))),{status:'rational',value:q(524288,531441)});assert.ok(a.equal(a.multiply(a.power(delta,q(12)),comma),one));
 assert.equal(a.equal(a.moduloOctaves(pure).representative,a.moduloOctaves(equalTempered).representative),false);
});
test('bounded exact output never coerces irrational expressions to floats',()=>{
 assert.equal(a.asRational(a.power(two,q(40000))).status,'out-of-scope');
 assert.equal(a.hCoordinates(a.make([{prime:'5',exponent:q(1)}])).status,'outside-source-H');
 assert.throws(()=>a.fromRational(q(0)),/positive/);assert.throws(()=>a.make([{prime:'2',exponent:{numerator:1,denominator:12}}]),/integer strings/);
});
