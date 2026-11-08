/** Deterministic transport simulation against copied worker code, no processes. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
const here=fileURLToPath(new URL('.',import.meta.url));
const fakeSpawn=`
function spawn() {
 const child=new EventEmitter(); child.pid=42;
 child.stdout=new EventEmitter(); child.stderr=new EventEmitter(); child.stdin=new EventEmitter();
 child.stdin.end=()=>setTimeout(()=>child.emit('close',1),2);
 return child;
}
`;
const fakeHelper=`
async function helper(args,input='') {
 if(args[1]==='capture')return {kind:'SYNTHETIC_TRANSPORT_ONLY'};
 await new Promise(resolve=>setTimeout(resolve,80));
 return {status:'reaped',remaining_owned_processes:0,simulation:true};
}
`;
async function load(variant){
 let code=readFileSync(here+'worker-'+variant+'.mjs','utf8');
 code=code.replace("import { spawn } from 'node:child_process';", "import {EventEmitter} from 'node:events';\n"+fakeSpawn);
 const start=code.indexOf('function helper(args,');const end=code.indexOf('export function startJevWorker',start);
 assert.ok(start>=0&&end>start);
 code=code.slice(0,start)+fakeHelper+'\n'+code.slice(end);
 const name='worker-simulated-'+variant+'.mjs';writeFileSync(here+name,code);
 return import('./'+name);
}
const options={root:here,executable:'NEVER_EXECUTED',script:'NEVER_EXECUTED',input:'synthetic',purpose:'No child process can run in this test',timeoutMs:20};
test('original copied worker reproduces timeout after child already completed',async()=>{
 const {startJevWorker}=await load('observed');
 const result=await startJevWorker(options).result;
 assert.equal(result.reason,'timeout');assert.equal(result.code,1);assert.equal(result.reaped,true);
});
test('proposed copied worker preserves complete across slow cleanup',async()=>{
 const {startJevWorker}=await load('proposed');
 const result=await startJevWorker(options).result;
 assert.equal(result.reason,'complete');assert.equal(result.code,1);assert.equal(result.reaped,true);
});
