import test from 'node:test';
import assert from 'node:assert/strict';
import {parseComparison,prepareComparison,completeComparison} from '../dist/comparison.js';
const sha='a'.repeat(64);
const fixture=()=>({kernel:{id:'fixture-kernel',version:'1',sha256:sha,sourceRefs:['source']},candidates:[{id:'one',assignment:{position:1},sourceRefs:['source']},{id:'two',assignment:{position:2},sourceRefs:['source']}],constraints:[{id:'declared-fixture-only',kernelSha256:sha,sourceRefs:['source'],authority:'assumption',predicate:{op:'eq',key:'position',value:1}}]});
const lookup=id=>id==='source'?{id,sha256:sha}:undefined;
test('comparison refuses malformed, duplicate and executable predicate shapes',()=>{
  assert.throws(()=>parseComparison({}),TypeError);
  const duplicate=fixture();duplicate.candidates.push(duplicate.candidates[0]);assert.throws(()=>parseComparison(duplicate),/Duplicate/);
  const code=fixture();code.constraints[0].predicate={op:'eval',code:'process.exit()'};assert.throws(()=>parseComparison(code),/Unknown predicate/);
});
test('source identity and actual kernel hash must resolve before definite evaluation',()=>{
  const prepared=prepareComparison(fixture(),()=>undefined);
  assert.equal(completeComparison(prepared,'evaluate_conditional').status,'source_unresolved');
  const wrong=prepareComparison(fixture(),id=>({id,sha256:'b'.repeat(64)}));
  assert.equal(completeComparison(wrong,'evaluate_conditional').evaluation,null);
});
test('conditional calculation retains witnesses and model deferral never promotes law',()=>{
  const prepared=prepareComparison(fixture(),lookup);
  assert.equal(prepared.sourceBindings.status,'resolved');
  assert.equal(completeComparison(prepared,'defer_review').status,'deferred');
  assert.throws(()=>completeComparison(prepared,'invented_action'),/No accepted live Jev/);
  const result=completeComparison(prepared,'evaluate_conditional');
  assert.deepEqual(result.evaluation.admissible,['one']);
  assert.deepEqual(result.evaluation.rejected,['two']);
  assert.equal(result.canonicalPromotion,false);
});
test('undeclared operators and missing values stay unknown with real source references',()=>{
  const body=fixture();body.constraints[0].predicate={op:'custom',name:'unreconstructed operator',payload:{}};
  const result=completeComparison(prepareComparison(body,lookup),'evaluate_conditional');
  assert.deepEqual(result.evaluation.unresolved,['one','two']);
});
