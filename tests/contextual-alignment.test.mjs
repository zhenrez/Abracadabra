import test from 'node:test';
import assert from 'node:assert/strict';
import {solveContextualAlignment} from '../dist/contextual-alignment.js';

const sourceRefs=['received-ZhouLi22:ritual-prescriptions','Lam2024:2.2'];
const link=(id,from,to,offset)=>({id,from,to,offset,sourceRefs});
const base={id:'ritual-single-context',modulus:12,variables:['c','h','t'],sourceRefs,
  assumptions:['Context-invariant named standards','One common gong per prescription','Fixed modern role offsets'],
  links:[link('A','c','h',4),link('B','c','t',7),link('C','h','t',7)]};

test('source-conditioned three-equation adapter has a nonzero closed-cycle certificate',()=>{
  const result=solveContextualAlignment(base);
  assert.equal(result.status,'inconsistent');
  assert.equal(result.assignmentCount,'0');
  assert.equal(result.cycle.residue,4);
  let cursor=result.cycle.steps[0].from, total=0;
  const start=cursor;
  for(const step of result.cycle.steps){assert.equal(step.from,cursor);cursor=step.to;total+=step.offset;}
  assert.equal(cursor,start);
  assert.equal(((total%12)+12)%12,result.cycle.residue);
  assert.deepEqual([...result.inclusionMinimalCore].sort(),['A','B','C']);
  assert.equal(result.canonicalPromotion,false);
});

test('each proper two-equation subset has twelve complete origin alternatives',()=>{
  for(const removed of base.links){
    const result=solveContextualAlignment({...base,links:base.links.filter(e=>e.id!==removed.id)});
    assert.equal(result.status,'admissible-family');
    assert.equal(result.assignmentCount,'12');
    assert.equal(result.prediction.retainedCandidateIds.length,12);
    assert.ok(result.prediction.predictions.every(p=>p.status==='alternatives'));
  }
});

test('a missing relation is predicted conditionally without electing absolute pitches',()=>{
  const result=solveContextualAlignment({...base,links:base.links.slice(0,2),
    targets:[{id:'t-minus-h',kind:'difference',from:'h',to:'t'}]});
  const target=result.prediction.predictions.find(p=>p.targetId==='t-minus-h');
  assert.equal(target.status,'determined-within-supplied-family');
  assert.deepEqual(target.alternatives[0].value,[3]);
  assert.equal(result.prediction.globalOrientationSelected,false);
});

test('global reversal and integral register changes do not repair the inconsistent cycle',()=>{
  const reversed=solveContextualAlignment({...base,links:base.links.map(e=>({...e,offset:-e.offset}))});
  assert.equal(reversed.status,'inconsistent');
  assert.equal(reversed.cycle.residue,8);
  const lifted=solveContextualAlignment({...base,links:base.links.map((e,i)=>({...e,offset:e.offset+12*(i-1)}))});
  assert.equal(lifted.status,'inconsistent');
  assert.equal(lifted.cycle.residue,4);
});

test('separate-modal ancestral interpretation has twelve admissible origin frames',()=>{
  const offsets=[0,9,7,2];
  const result=solveContextualAlignment({id:'ancestral-separate-modes',modulus:12,
    variables:['alpha','g0','g1','g2','g3'],sourceRefs,
    assumptions:['Later four-piece reading','Declared modern twelve-position concordance'],
    links:offsets.map((n,i)=>link('mode'+i,'alpha','g'+i,n)),
    targets:offsets.map((_,i)=>({id:'relative'+i,kind:'difference',from:'alpha',to:'g'+i}))});
  assert.equal(result.assignmentCount,'12');
  assert.equal(result.status,'admissible-family');
  assert.deepEqual(result.assignments.map(a=>a.alpha).sort((a,b)=>a-b),Array.from({length:12},(_,i)=>i));
  for(let i=0;i<4;i++)assert.deepEqual(result.prediction.predictions.find(p=>p.targetId==='relative'+i).alternatives[0].value,[offsets[i]]);
});

test('large disconnected families remain symbolic rather than truncated to one answer',()=>{
  const result=solveContextualAlignment({id:'disconnected',modulus:12,variables:['x','y'],links:[],sourceRefs,assumptions:[]},{maxAssignments:10});
  assert.equal(result.assignmentCount,'144');
  assert.equal(result.status,'symbolic-family');
  assert.equal(result.assignments,null);
  assert.equal(result.prediction,null);
  assert.equal(result.freeOrigins.length,2);
});

test('redundant equations do not inflate the inclusion-minimal conflict',()=>{
  const result=solveContextualAlignment({...base,links:[...base.links,link('redundant','c','h',4)]});
  assert.equal(result.status,'inconsistent');
  assert.equal(result.inclusionMinimalCore.length,3);
});

test('missing source bindings and malformed domains fail explicitly',()=>{
  assert.throws(()=>solveContextualAlignment({...base,sourceRefs:[]}),/source/i);
  assert.throws(()=>solveContextualAlignment({...base,variables:['c','c']}),/unique/i);
  assert.throws(()=>solveContextualAlignment({...base,modulus:0}),/modulus/i);
  assert.throws(()=>solveContextualAlignment({...base,links:[link('bad','missing','c',0)]}),/variable/i);
});
