/** Simulated clock against the actual compiled helper; never spawns a process. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {EventEmitter} from 'node:events';

function simulate(action) {
  const source=readFileSync(new URL('../../../dist/worker.js',import.meta.url),'utf8');
  const start=source.indexOf('function helper(args,');
  const end=source.indexOf('export function startJevWorker',start);
  assert.ok(start>=0&&end>start);
  const timers=[];let now=0;
  const schedule=(fn,delay)=>{const timer={fn,at:now+delay,active:true};timers.push(timer);return timer};
  const cancel=timer=>{timer.active=false};
  const spawn=()=>{
    const child=new EventEmitter();
    child.stdout=new EventEmitter();child.stderr=new EventEmitter();child.stdin=new EventEmitter();
    child.kill=()=>child.emit('close',1);
    child.stdin.end=()=>schedule(()=>{child.stdout.emit('data',Buffer.from('{"status":"reaped"}'));child.emit('close',0)},20000);
    return child;
  };
  const helper=Function('spawn','setTimeout','clearTimeout','HELPER','return ('+source.slice(start,end)+')')(
    spawn,schedule,cancel,'NEVER_EXECUTED');
  const result=helper(['-Action',action]);
  while(timers.some(timer=>timer.active)){
    timers.sort((a,b)=>a.at-b.at);
    const timer=timers.find(timer=>timer.active);timer.active=false;now=timer.at;timer.fn();
  }
  return result;
}

test('verified cleanup may finish after15seconds within its separate bound',async()=>{
  assert.deepEqual(await simulate('stop'),{status:'reaped'});
});
test('ownership capture retains its strict15second timeout',async()=>{
  await assert.rejects(simulate('capture'),/identity helper timed out/);
});
