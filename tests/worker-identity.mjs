/** Pure test assertion: ownership is a PID plus its exact creation FILETIME. */
import assert from 'node:assert/strict';

export function assertOwnedProcessGone(pid,expectedBirthTicks,probe){
  assert.ok(Number.isSafeInteger(pid)&&pid>0,'Expected a positive owned fixture PID');
  assert.ok(typeof expectedBirthTicks==='string'&&/^[0-9]+$/.test(expectedBirthTicks),
    'Expected an exact creation FILETIME string');
  assert.equal(typeof probe,'function','A read-only identity probe is required');
  const observed=probe(pid);
  if(observed?.status==='absent')return;
  assert.equal(observed?.status,'observed','Original process absence is unverifiable');
  assert.ok(typeof observed.birth_ticks==='string'&&/^[0-9]+$/.test(observed.birth_ticks),
    'Current creation FILETIME is unverifiable');
  assert.equal(typeof observed.has_exited,'boolean','Current exit status is unverifiable');
  if(observed.birth_ticks!==expectedBirthTicks||observed.has_exited)return;
  assert.fail('Original owned fixture birth identity is still running: '+pid);
}
