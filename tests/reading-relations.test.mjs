import test from 'node:test';import assert from 'node:assert/strict';
import {readingDependency,minimalReadingRefinements,queryReadings,readingJoinResidual} from '../dist/reading-relations.js';
const row=(id,values)=>({id,values,sourceRefs:['declared-test-control']});
const examples=[row('keep',{lexeme:'keep',input:'a',mode:'pausal',onset:'m',output:'ɔː',quantity:'ː'}),
 row('eat',{lexeme:'eat',input:'a',mode:'pausal',onset:'χ',output:'eː',quantity:'ː'})];

test('a coarse shared input has an explicit two-row contradiction',()=>{
 const r=readingDependency(examples,['input','mode'],'output');assert.equal(r.status,'contradicted');
 assert.deepEqual(r.counterexamples,[{left:'keep',right:'eat',input:['a','pausal'],outputs:['ɔː','eː']}]);
 for(const x of examples)assert.equal(readingDependency([x],['input','mode'],'output').status,'no-counterexample-on-complete-rows');
});
test('every inclusion-minimal finite refinement is retained',()=>{
 const r=minimalReadingRefinements(examples,['input','mode'],['lexeme','onset'],'output');
 assert.deepEqual(r,[['lexeme'],['onset']]);
 assert.deepEqual(minimalReadingRefinements(examples,['input','mode'],['lexeme','onset'],'quantity'),[[]]);
});
test('unknown input and output remain unresolved instead of selecting a rule',()=>{
 const missing=row('pending',{input:'a',lexeme:null,output:null});
 const rows=[...examples,missing];
 assert.deepEqual(minimalReadingRefinements(rows,['input'],['lexeme'],'output'),[]);
 const result=queryReadings(rows,{lexeme:'keep'},'output');
 assert.deepEqual(result.rowIds,['keep','pending']);assert.equal(result.status,'unresolved-source-values');
 assert.deepEqual(result.outputs,['ɔː']);assert.deepEqual(result.unresolvedRows,['pending']);
});
test('empty strings can carry a known unmarked or silent value',()=>{
 const r=readingDependency([row('unmarked',{input:'a',length:''})],['input'],'length');
 assert.equal(r.status,'no-counterexample-on-complete-rows');assert.deepEqual(r.cells[0].outputs,['']);
 assert.equal(queryReadings([row('silent',{input:'',output:''})],{input:''},'output').status,'single-output-in-admitted-sample');
});
test('dropping lexical context creates exactly two excess sample pairings',()=>{
 const r=readingJoinResidual(examples,['lexeme','input'],['input','output']);
 assert.equal(r.knownOriginalDistinctTuples,2);assert.equal(r.rejoinedDistinctTuples,4);
 assert.deepEqual(r.excessCombinations.map(x=>[x.values.lexeme,x.values.output]),[['keep','eː'],['eat','ɔː']]);
 const repaired=readingJoinResidual(examples,['lexeme','input'],['lexeme','input','output']);
 assert.equal(repaired.rejoinedDistinctTuples,2);assert.deepEqual(repaired.excessCombinations,[]);
});
test('duplicate occurrences retain IDs without inflating distinct relation tuples',()=>{
 const r=readingJoinResidual([...examples,row('keep-second-occurrence',{...examples[0].values})],['lexeme','input'],['input','output']);
 assert.equal(r.knownOriginalDistinctTuples,2);assert.equal(r.rejoinedDistinctTuples,4);
 assert.ok(r.excessCombinations.some(x=>x.leftRowIds.length===2));
});
test('Unicode and inherited object properties do not fabricate equality or evidence',()=>{
 const a=row('greek',{input:'χ',output:'one'}),b=row('latin',{input:'x',output:'two'});
 assert.equal(readingDependency([a,b],['input'],'output').status,'no-counterexample-on-complete-rows');
 assert.equal(readingDependency([row('missing',{})],['toString'],'constructor').status,'no-complete-rows');
 const literal=JSON.parse('{"__proto__":"literal","output":"ok"}');
 assert.equal(queryReadings([row('own',literal)],JSON.parse('{"__proto__":"literal"}'),'output').outputs[0],'ok');
 assert.deepEqual(queryReadings([row('own',literal)],JSON.parse('{"__proto__":"other"}'),'output').rowIds,[]);
});
test('empty samples, malformed rows and target-field refinements cannot certify rules',()=>{
 assert.equal(readingDependency([],['x'],'y').status,'no-complete-rows');
 assert.deepEqual(minimalReadingRefinements([],['x'],['z'],'y'),[]);
 assert.throws(()=>readingDependency([examples[0],examples[0]],['input'],'output'));
 assert.throws(()=>minimalReadingRefinements(examples,['input'],['output'],'output'));
 assert.throws(()=>readingDependency([{id:'bad',values:{x:'a'},sourceRefs:[]}],['x'],'y'));
 assert.throws(()=>readingDependency([{id:'bad',values:'not-an-attribute-map',sourceRefs:['control']}],['x'],'y'));
 for(const malformed of [null,[],['a'],'a'])assert.throws(()=>queryReadings(examples,malformed,'output'),TypeError);
});
