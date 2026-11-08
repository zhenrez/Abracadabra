/** Real isolated browser lifecycle regression; always reaps its own profile. */
import {spawn,spawnSync} from 'node:child_process';
import {mkdtempSync,existsSync,rmSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
const root=resolve(fileURLToPath(new URL('..',import.meta.url)));
const profile=mkdtempSync(join(tmpdir(),'sunny-edge-check-'));
const browser=spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',['--headless=new','--no-first-run','--disable-background-networking','--disable-extensions','--disable-sync','--remote-debugging-address=127.0.0.1','--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'],{windowsHide:true,stdio:'ignore'});
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const close=(path,capture=false)=>spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-File',join(root,'scripts','stop-test-browser.ps1'),'-BrowserPid',String(browser.pid),'-Profile',path,...(capture?['-CaptureOnly']:[])],{windowsHide:true,encoding:'utf8',timeout:20000});
const report={checked_at:new Date().toISOString(),checks:[],scope:'Real dedicated Edge test profile; no user browser or Codex connector touched.'};
try{
  for(let i=0;i<100&&!existsSync(join(profile,'DevToolsActivePort'));i++)await delay(100);
  assert.ok(existsSync(join(profile,'DevToolsActivePort')),'test browser must start');
  const refused=close(tmpdir());assert.notEqual(refused.status,0);assert.equal(browser.exitCode,null);process.kill(browser.pid,0);
  report.checks.push('Unowned profile refused while owned browser remains alive');
  const captured=close(profile,true);assert.equal(captured.status,0,captured.stderr);assert.ok(JSON.parse(captured.stdout.trim()).identities>1);
  browser.kill();await delay(250);
  const stopped=close(profile);assert.equal(stopped.status,0,stopped.stderr);const result=JSON.parse(stopped.stdout.trim());assert.equal(result.remaining_profile_processes,0);assert.equal(result.remaining_known_processes,0);
  report.checks.push('Captured birth identities retained and checked after root process exited');
  report.checks.push('Verified test tree stopped and zero profile processes remain');
  const repeated=close(profile);assert.equal(repeated.status,0,repeated.stderr);assert.deepEqual(JSON.parse(repeated.stdout.trim()).stopped_pids,[]);
  report.checks.push('Repeated cleanup succeeds without touching unrelated processes');report.status='passed';
}catch(error){report.status='failed';report.error=error.stack;process.exitCode=1;}
finally{
  const final=close(profile);report.final_cleanup_exit=final.status;if(final.status!==0){report.status='failed';process.exitCode=1;}
  await delay(250);
  if(resolve(profile).startsWith(resolve(tmpdir())+'\\sunny-edge-check-')){try{rmSync(profile,{recursive:true,force:true,maxRetries:5,retryDelay:200});}catch{}}
  writeFileSync(join(root,'docs','evidence','browser-process-cleanup.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
}
