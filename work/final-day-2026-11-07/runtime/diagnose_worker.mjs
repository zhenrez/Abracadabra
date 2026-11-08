/** Owned synthetic processes only. No model inference or project-source writes. */
import {mkdirSync,writeFileSync,readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {resolve,join} from 'node:path';
import {spawn} from 'node:child_process';
const here=fileURLToPath(new URL('.',import.meta.url));
const project=resolve(here,'../../..');
const variant=process.argv[2]??'observed',mode=process.argv[3]??'normal';
if(!['observed','proposed'].includes(variant)||!['normal','output'].includes(mode))throw Error('Unsupported bounded fixture');
const {startJevWorker}=await import('./worker-'+variant+'.mjs');
const stamp=Date.now(),root=join(here,`fixture-${variant}-${mode}-${stamp}`);
mkdirSync(join(root,'scripts'),{recursive:true});
const script=join(root,'scripts','jev_tool.py');
writeFileSync(script,`import json,os,sys,subprocess,time
from pathlib import Path
payload=json.loads(sys.stdin.read())
mode=payload['mode']
child=subprocess.Popen([sys.executable,'-c','import time;time.sleep('+('0.05' if mode=='normal' else '60')+')'])
Path(__file__).resolve().parents[1].joinpath('owned.json').write_text(json.dumps({'interpreter':os.getpid(),'child':child.pid}))
if mode=='normal':
 child.wait()
 print(json.dumps({'status':'invalid','error':'Synthetic lifecycle transport; no inference'}),file=sys.stderr)
 sys.exit(1)
print('x'*20000,flush=True)
time.sleep(60)
`);
globalThis.__workerTrace=[];globalThis.__ownedRecords=[];
const options={root,script,executable:join(project,'.venv','Scripts','python.exe'),input:JSON.stringify({mode}),purpose:'Owned synthetic diagnostic; no inference',timeoutMs:mode==='normal'?800:10000,maxOutputBytes:mode==='normal'?4_000_000:1024};
const result=await startJevWorker(options).result;
const receipt={variant,mode,options:{...options,input:'synthetic mode only'},started:stamp,ended:Date.now(),result,trace:globalThis.__workerTrace,owned_records:globalThis.__ownedRecords,manual_cleanup:[]};
if(!result.reaped){
 for(const {record,args}of globalThis.__ownedRecords){
  const log=await new Promise(resolve=>{
   const helper=spawn('powershell.exe',['-NoProfile','-NonInteractive','-File',join(project,'scripts','stop-jev-worker.ps1'),'-Action','stop',...args],{windowsHide:true,shell:false,stdio:['pipe','pipe','pipe']});
   let stdout='',stderr='';helper.stdout.on('data',c=>stdout+=c);helper.stderr.on('data',c=>stderr+=c);
   helper.on('error',e=>resolve({error:String(e)}));helper.on('close',code=>resolve({code,stdout,stderr}));helper.stdin.on('error',()=>{});helper.stdin.end(JSON.stringify(record));
  });receipt.manual_cleanup.push(log);
 }
}
try{receipt.fixture_ids=JSON.parse(readFileSync(join(root,'owned.json'),'utf8'));}catch{receipt.fixture_ids=null;}
receipt.absence_checks=[];
for(const pid of Object.values(receipt.fixture_ids??{})){
 let absent=false;try{process.kill(pid,0);}catch(error){absent=error.code==='ESRCH';}
 receipt.absence_checks.push({pid,absent});
}
const output=join(here,`${variant}-${mode}-${stamp}.json`);writeFileSync(output,JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({receipt:output,variant,mode,reason:result.reason,error:result.error,reaped:result.reaped,elapsed:receipt.ended-stamp,trace:receipt.trace,absence:receipt.absence_checks}));
if(receipt.absence_checks.some(x=>!x.absent))process.exitCode=2;
