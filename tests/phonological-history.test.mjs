import test from 'node:test';
import assert from 'node:assert/strict';
import {contactTiming,windowEmpty,windowContains} from '../dist/phonological-history.js';
import {rational} from '../dist/law.js';

const q=(n,d=1)=>rational(String(n),String(d));
const w=(lo=null,hi=null,lc=true,uc=true)=>({lower:lo===null?null:q(lo),upper:hi===null?null:q(hi),lowerClosed:lc,upperClosed:uc});
const any=()=>w();

test('positive attestations alone do not select contact direction',()=>{
  assert.equal(contactTiming(w(null,6),any(),w(null,9)).feasible,true);
  assert.equal(contactTiming(w(null,9),any(),w(null,6)).feasible,true);
});
test('each incompatible additional-bound pair is inclusion-minimal',()=>{
  const cases=[
    [w(4),any(),w(null,3), [[any(),any(),w(null,3)],[w(4),any(),any()]]],
    [any(),w(4),w(null,3), [[any(),any(),w(null,3)],[any(),w(4),any()]]],
    [w(4),w(null,3),any(), [[any(),w(null,3),any()],[w(4),any(),any()]]]
  ];
  for(const [d,k,r,proper] of cases){assert.equal(contactTiming(d,k,r).feasible,false);for(const p of proper)assert.equal(contactTiming(...p).feasible,true);}
});
test('strict, weak and open endpoint equality are distinguished',()=>{
  assert.equal(contactTiming(w(0,0),w(0,0),w(0,0),true).feasible,false);
  assert.equal(contactTiming(w(0,0),w(0,0),w(0,0),false).feasible,true);
  assert.equal(contactTiming(w(0,1,false,true),w(0,0),any(),false).feasible,false);
  assert.equal(contactTiming(w(null,0),w(1,1),w(1,2,false,true)).feasible,true);
  assert.equal(contactTiming(any(),w(1,1),w(0,1,true,false)).feasible,false);
});
test('narrow rational windows remain exact beyond floating-point precision',()=>{
  const point=q('9007199254740993'),upper=q('18014398509481987',2);
  const interval={lower:point,upper,lowerClosed:false,upperClosed:false};
  const result=contactTiming(any(),interval,any());
  assert.equal(result.feasible,true);
  assert.equal(windowContains(interval,result.witness.contact),true);
  assert.equal(result.witness.contact.numerator,'36028797018963973');
  assert.equal(result.witness.contact.denominator,'4');
});
test('empty event windows and malformed rational values do not produce histories',()=>{
  for(const x of [w(2,1),w(0,0,false,true),w(0,0,true,false)]){
    assert.equal(windowEmpty(x),true);assert.equal(contactTiming(x,any(),any()).feasible,false);
  }
  assert.throws(()=>contactTiming({lower:{numerator:'1',denominator:'0'},upper:null,lowerClosed:true,upperClosed:false},any(),any()));
  assert.throws(()=>contactTiming({lower:{numerator:1,denominator:'1'},upper:null,lowerClosed:true,upperClosed:false},any(),any()));
});
test('exact derived witnesses may exceed the input endpoint digit budget',()=>{
  const n=10n**100n;
  const interval={lower:q(1,n+1n),upper:q(1,n),lowerClosed:true,upperClosed:true};
  const result=contactTiming(any(),interval,any());
  assert.equal(result.feasible,true);
  assert.equal(windowContains(interval,result.witness.contact),true);
  assert.ok(result.witness.contact.denominator.length>128);
  assert.throws(()=>contactTiming(any(),{lower:q(1,10n**130n+1n),upper:null,lowerClosed:true,upperClosed:false},any()),RangeError);
});
