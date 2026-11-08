/** Test-only birth-identity assertions; no process is started or terminated. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';

const helper=new URL('../../../tests/worker-identity.mjs',import.meta.url);
async function load(){
  assert.ok(existsSync(fileURLToPath(helper)),'pure worker birth-identity assertion is absent');
  return import(helper.href);
}
const pid=12345;
const birth='134068232991234567';

test('owned process absence is verified through the injected PID probe',async()=>{
  const {assertOwnedProcessGone}=await load();const seen=[];
  assert.doesNotThrow(()=>assertOwnedProcessGone(pid,birth,queried=>{seen.push(queried);return {status:'absent'};}));
  assert.deepEqual(seen,[pid]);
});

test('a different creation FILETIME establishes PID reuse without killing it',async()=>{
  const {assertOwnedProcessGone}=await load();
  assert.doesNotThrow(()=>assertOwnedProcessGone(pid,birth,()=>({status:'observed',birth_ticks:'134068232991234568',has_exited:false})));
});

test('the original identity may remain queryable after its process has exited',async()=>{
  const {assertOwnedProcessGone}=await load();
  assert.doesNotThrow(()=>assertOwnedProcessGone(pid,birth,()=>({status:'observed',birth_ticks:birth,has_exited:true})));
});

test('live original identity and unverifiable probes fail closed',async()=>{
  const {assertOwnedProcessGone}=await load();
  for(const observation of [
      {status:'observed',birth_ticks:birth,has_exited:false},
      {status:'unverifiable'},undefined,{},
      {status:'observed',birth_ticks:'unreadable',has_exited:false},
      {status:'observed',birth_ticks:birth,has_exited:null}]){
    assert.throws(()=>assertOwnedProcessGone(pid,birth,()=>observation));
  }
  assert.throws(()=>assertOwnedProcessGone(pid,birth,()=>{throw new Error('probe unavailable');}));
});
