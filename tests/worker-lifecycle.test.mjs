/** Synthetic stdlib processes test ownership/transport only; no Jev inference. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,readFileSync,existsSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {once} from 'node:events';
import {spawnSync} from 'node:child_process';
import {assertOwnedProcessGone} from './worker-identity.mjs';
import Database from 'better-sqlite3';
import {startJevWorker} from '../dist/worker.js';
import {createSunnyServer} from '../dist/server.js';

const project=resolve(fileURLToPath(new URL('..',import.meta.url)));
const executable=join(project,'.venv','Scripts','python.exe');
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const fixture=`import ctypes, json, os, subprocess, sys, time
from ctypes import wintypes
from pathlib import Path

class FILETIME(ctypes.Structure):
    _fields_=[('dwLowDateTime',wintypes.DWORD),('dwHighDateTime',wintypes.DWORD)]

kernel32=ctypes.WinDLL('kernel32',use_last_error=True)
kernel32.GetCurrentProcess.argtypes=[]
kernel32.GetCurrentProcess.restype=wintypes.HANDLE
kernel32.GetProcessTimes.argtypes=[wintypes.HANDLE,ctypes.POINTER(FILETIME),ctypes.POINTER(FILETIME),ctypes.POINTER(FILETIME),ctypes.POINTER(FILETIME)]
kernel32.GetProcessTimes.restype=wintypes.BOOL

def creation_filetime(handle):
    creation,exit_time,kernel,user=FILETIME(),FILETIME(),FILETIME(),FILETIME()
    if not kernel32.GetProcessTimes(wintypes.HANDLE(int(handle)),ctypes.byref(creation),ctypes.byref(exit_time),ctypes.byref(kernel),ctypes.byref(user)):
        raise ctypes.WinError(ctypes.get_last_error())
    return str((int(creation.dwHighDateTime)<<32)|int(creation.dwLowDateTime))

payload=json.loads(sys.stdin.read())
state=payload.get('state', {})
mode=state.get('fixture_mode', 'normal')
tag=state.get('fixture_tag', mode)
child=subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(' + ('0.05' if mode == 'normal' else '60') + ')'])
Path(__file__).resolve().parents[1].joinpath('fixture-' + tag + '.json').write_text(json.dumps({
    'pids':{'interpreter':os.getpid(),'child':child.pid},
    'birth_ticks':{str(os.getpid()):creation_filetime(kernel32.GetCurrentProcess()),str(child.pid):creation_filetime(child._handle)}
}))
if mode == 'normal':
    child.wait()
    print(json.dumps({'status':'invalid','error':'Synthetic transport fixture, not model inference','fallback_decision':None}),file=sys.stderr)
    sys.exit(1)
if mode == 'output':
    print('x' * 20000,flush=True)
time.sleep(60)
`;
function setup(t){
  assert.ok(existsSync(executable),'the existing workspace venv is required for the real launcher regression');
  const root=mkdtempSync(join(tmpdir(),'sunny-worker-test-'));
  mkdirSync(join(root,'scripts'));mkdirSync(join(root,'data'));mkdirSync(join(root,'state'));mkdirSync(join(root,'public'));
  const script=join(root,'scripts','jev_tool.py');writeFileSync(script,fixture);
  const workers=[];
  const birthTicks=new Map();
  t.after(async()=>{
    const results=await Promise.all(workers.map(worker=>worker.stop('shutdown')));
    assert.ok(results.every(result=>result.reaped),'all test workers must be verified closed before fixture removal');
    assert.ok(root.startsWith(join(tmpdir(),'sunny-worker-test-')));rmSync(root,{recursive:true,force:true});
  });
  const input=(mode,tag=mode)=>JSON.stringify({state:{fixture_mode:mode,fixture_tag:tag},questions:[{id:'transport_fixture',type:'boolean',question:'Synthetic transport input only; no inference requested.'}]});
  const run=(mode,options={})=>{const worker=startJevWorker({root,script,executable,input:input(mode),purpose:'Synthetic lifecycle fixture; not inference',timeoutMs:10000,...options});workers.push(worker);return worker;};
  const marker=async(tag)=>{const path=join(root,'fixture-'+tag+'.json');for(let attempt=0;attempt<150&&!existsSync(path);attempt++)await delay(100);assert.ok(existsSync(path),'fixture interpreter and child must start: '+tag);const captured=JSON.parse(readFileSync(path,'utf8'));for(const pid of Object.values(captured.pids))birthTicks.set(pid,captured.birth_ticks[String(pid)]);return captured.pids;};
  const probe=pid=>{
    try{process.kill(pid,0);}catch(error){if(error.code==='ESRCH')return {status:'absent'};throw error;}
    // Read only the current birth/exit identity, never command lines or target state.
    const query="try { $p=[Diagnostics.Process]::GetProcessById("+pid+") } catch [ArgumentException] { [pscustomobject]@{status='absent'} | ConvertTo-Json -Compress; return } catch { [pscustomobject]@{status='unverifiable'} | ConvertTo-Json -Compress; return }; try { [pscustomobject]@{status='observed';birth_ticks=$p.StartTime.ToUniversalTime().ToFileTimeUtc().ToString();has_exited=$p.HasExited} | ConvertTo-Json -Compress } catch { [pscustomobject]@{status='unverifiable'} | ConvertTo-Json -Compress } finally { $p.Dispose() }";
    const result=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-Command',query],
      {encoding:'utf8',timeout:15000,windowsHide:true});
    assert.equal(result.error,undefined,'Read-only fixture identity probe failed');
    assert.equal(result.status,0,'Read-only fixture identity probe exited unsuccessfully');
    return JSON.parse(result.stdout.trim());
  };
  const absent=pids=>{for(const pid of pids)assertOwnedProcessGone(pid,birthTicks.get(pid),probe);};
  return {root,script,workers,input,run,marker,absent};
}

test('fixed worker completion verifies launcher/interpreter exit and preserves fixture output', {timeout:60000},async t=>{
  const fixture=setup(t);const result=await fixture.run('normal').result;
  assert.equal(result.reason,'complete');assert.equal(result.code,1);assert.equal(result.reaped,true);
  assert.match(JSON.parse(result.stderr).error,/Synthetic transport fixture/);
  const ids=await fixture.marker('normal');fixture.absent(Object.values(ids));
});
test('timeout reaps the venv launcher, interpreter and sleeping descendant', {timeout:60000},async t=>{
  const fixture=setup(t);const worker=fixture.run('timeout',{timeoutMs:400});const ids=await fixture.marker('timeout');
  const result=await worker.result;assert.equal(result.reason,'timeout');assert.equal(result.reaped,true);fixture.absent(Object.values(ids));
  assert.equal(result.cleanup.remaining_owned_processes,0);
});
test('output overflow reaps all owned worker processes', {timeout:60000},async t=>{
  const fixture=setup(t);const worker=fixture.run('output',{maxOutputBytes:1024});const ids=await fixture.marker('output');
  const result=await worker.result;assert.equal(result.reason,'output_limit');assert.equal(result.reaped,true);fixture.absent(Object.values(ids));
});
test('explicit shutdown reaps an active fixed worker before resolving', {timeout:60000},async t=>{
  const fixture=setup(t);const worker=fixture.run('shutdown');const ids=await fixture.marker('shutdown');
  const result=await worker.stop();assert.equal(result.reason,'shutdown');assert.equal(result.reaped,true);fixture.absent(Object.values(ids));
});

async function serverFixture(t,timeoutMs=10000){
  const fixture=setup(t);const databasePath=join(fixture.root,'data','sunny.sqlite');new Database(databasePath).close();
  const server=createSunnyServer({root:fixture.root,databasePath,workerTimeoutMs:timeoutMs});
  server.listen(0,'127.0.0.1');await once(server,'listening');
  const url=`http://127.0.0.1:${server.address().port}/api/jev/decide`;
  let closed=false;
  const close=()=>new Promise((resolve,reject)=>{if(closed){resolve();return;}server.close(error=>{closed=true;error?reject(error):resolve();});});
  t.after(close);
  return {...fixture,server,close,post:(mode,tag)=>fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:fixture.input(mode,tag)})};
}
test('HTTP two-worker limit stays reserved during timeout cleanup, then accepts work again', {timeout:60000},async t=>{
  const fixture=await serverFixture(t,800);
  const first=fixture.post('timeout','first');const second=fixture.post('timeout','second');
  const ids=[await fixture.marker('first'),await fixture.marker('second')];
  const busy=await fixture.post('normal','must-not-start');assert.equal(busy.status,429);assert.equal(existsSync(join(fixture.root,'fixture-must-not-start.json')),false);
  assert.deepEqual((await Promise.all([first,second])).map(response=>response.status),[504,504]);
  fixture.absent(ids.flatMap(Object.values));
  const normal=await fixture.post('normal','after-cleanup');assert.equal(normal.status,400);assert.match((await normal.json()).error,/Synthetic transport fixture/);
  await fixture.close();
});
test('HTTP server close waits for active request-worker cleanup', {timeout:60000},async t=>{
  const fixture=await serverFixture(t);
  const response=fixture.post('shutdown','http-shutdown');const ids=await fixture.marker('http-shutdown');
  await fixture.close();fixture.absent(Object.values(ids));
  assert.equal((await response).status,503);assert.match((await(await response).json()).error,/shutdown/);
});
