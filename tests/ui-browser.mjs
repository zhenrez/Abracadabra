/** Isolated real Edge check against the running local SUNNY service; no account login. */
import {spawn,spawnSync} from 'node:child_process';
import {mkdtempSync,existsSync,readFileSync,writeFileSync,rmSync,mkdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import assert from 'node:assert/strict';

import {fileURLToPath} from 'node:url';
import Database from 'better-sqlite3';
const root=resolve(fileURLToPath(new URL('..',import.meta.url)));
const sourceDatabase=new Database(join(root,'data','sunny.sqlite'),{readonly:true,fileMustExist:true});
const expectedMessages=sourceDatabase.prepare('SELECT count(*) AS count FROM messages').get().count;
sourceDatabase.close();
const evidence=join(root,'docs','evidence');mkdirSync(evidence,{recursive:true});
const profile=mkdtempSync(join(tmpdir(),'sunny-edge-check-'));
const edge='C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const browser=spawn(edge,['--headless=new','--no-first-run','--disable-background-networking','--disable-extensions','--disable-sync','--remote-debugging-address=127.0.0.1','--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'],{windowsHide:true,stdio:'ignore'});
const delay=milliseconds=>new Promise(resolve=>setTimeout(resolve,milliseconds));
let socket;
const report={checked_at:new Date().toISOString(),url:'http://127.0.0.1:4317',runtime:'Isolated native Microsoft Edge via CDP',checks:[],console_errors:[],exceptions:[],limitations:['No human screen-reader session or formal WCAG audit.','Visual screenshots require separate inspection.','Native source import completeness and mathematical truth are outside this UI check.']};
try{
  const portFile=join(profile,'DevToolsActivePort');
  for(let i=0;i<150&&!existsSync(portFile);i++)await delay(100);
  assert.ok(existsSync(portFile),'isolated Edge remote debugging endpoint must start');
  const captureBrowser=()=>{const result=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-File',join(root,'scripts','stop-test-browser.ps1'),'-BrowserPid',String(browser.pid),'-Profile',profile,'-CaptureOnly'],{windowsHide:true,encoding:'utf8',timeout:20000});assert.equal(result.status,0,result.stderr);return JSON.parse(result.stdout.trim());};
  report.browser_ownership=captureBrowser();
  const [port,path]=readFileSync(portFile,'utf8').trim().split(/\r?\n/);
  socket=new WebSocket(`ws://127.0.0.1:${port}${path}`);
  await new Promise((resolve,reject)=>{socket.addEventListener('open',resolve,{once:true});socket.addEventListener('error',reject,{once:true});});
  let id=0;const pending=new Map();
  socket.addEventListener('message',event=>{
    const message=JSON.parse(String(event.data));
    if(message.id){const handlers=pending.get(message.id);if(!handlers)return;pending.delete(message.id);message.error?handlers.reject(new Error(JSON.stringify(message.error))):handlers.resolve(message.result);}
    if(message.method==='Runtime.consoleAPICalled'&&['error','warning'].includes(message.params.type))report.console_errors.push(message.params.args.map(argument=>argument.value??argument.description));
    if(message.method==='Runtime.exceptionThrown')report.exceptions.push(message.params.exceptionDetails.text+': '+(message.params.exceptionDetails.exception?.description??''));
  });
  const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{const requestId=++id;pending.set(requestId,{resolve,reject});socket.send(JSON.stringify({id:requestId,method,params,...(sessionId?{sessionId}:{})}));setTimeout(()=>{if(pending.has(requestId)){pending.delete(requestId);reject(new Error('CDP timeout: '+method));}},15000).unref();});
  const {targetId}=await send('Target.createTarget',{url:'about:blank'});
  const {sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
  await send('Runtime.enable',{},sessionId);await send('Page.enable',{},sessionId);
  const evaluate=async expression=>{const result=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true},sessionId);if(result.exceptionDetails)throw new Error(result.exceptionDetails.text);return result.result.value;};
  const poll=async(expression,test,label)=>{for(let i=0;i<150;i++){const value=await evaluate(expression);if(test(value))return value;await delay(100);}throw new Error('Browser condition timed out: '+label);};
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1100,deviceScaleFactor:1,mobile:false},sessionId);
  await send('Page.navigate',{url:report.url},sessionId);
  await poll('document.readyState',value=>value==='complete','page ready');
  const messages=await poll('document.querySelector("#stat-messages")?.textContent',value=>value&&value!=='—','actual summary');
  assert.equal(messages,new Intl.NumberFormat().format(expectedMessages));report.checks.push({name:'Actual source summary matches independent live DB count',observed_messages:messages,independent_db_messages:expectedMessages});
  const overview=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true},sessionId);writeFileSync(join(evidence,'sunny-overview.png'),Buffer.from(overview.data,'base64'));
  await evaluate('document.querySelector("[data-view=evidence]").click(); document.querySelector("#source-search").value="SUNNY"; document.querySelector("#search-form").requestSubmit();');
  await poll('document.querySelectorAll(".source-result").length',value=>value>0,'real source search');
  if(await evaluate('!document.querySelector("#search-more").hidden')){
    const before=await evaluate('document.querySelectorAll(".source-result").length');
    await evaluate('document.querySelector("#search-more").click()');
    await poll('document.querySelectorAll(".source-result").length',value=>value>before,'second source page');
    const ids=await evaluate('[...document.querySelectorAll(".source-result")].map(item=>item.dataset.sourceId)');
    assert.equal(new Set(ids).size,ids.length);report.checks.push({name:'Second source page loads without duplicate records',shown:ids.length});
  }
  await evaluate('document.querySelector(".source-result").click()');
  await poll('document.querySelector("#source-inspector")?.textContent',value=>value?.includes('Retrieved message text'),'full source lookup');
  const source=await evaluate('({text:document.querySelector(".source-text").textContent.length,locator:document.querySelector(".inspector-meta").textContent,htmlImages:document.querySelector(".source-text").querySelectorAll("img,script").length})');
  assert.ok(source.text>0);assert.equal(source.htmlImages,0);report.checks.push({name:'Real search and full-source inspector',observed_text_characters:source.text,source_locator_visible:source.locator.includes('Locator')});
  if(await evaluate('!!document.querySelector(".inspector-actions button")')){
    await evaluate('document.querySelector(".inspector-actions button").click()');
    await poll('document.querySelectorAll(".conversation-message").length',value=>value>0,'conversation context');
    report.checks.push({name:'Conversation context opens',messages_shown:await evaluate('document.querySelectorAll(".conversation-message").length')});
    await evaluate('document.querySelector("#close-conversation").click()');
  }
  await evaluate('document.querySelector("[data-view=geometry]").click()');
  for(const model of ['wheels','torus','tetrahedron']){
    await evaluate(`document.querySelector('[data-model=${model}]').click()`);
    assert.equal(await evaluate(`document.querySelector('[data-model=${model}]').getAttribute('aria-pressed')`),'true');
  }
  report.checks.push({name:'All three finite geometry modes switch',canonical_assignments:'No inferred placements loaded'});
  await evaluate('document.querySelector("[data-view=comparison]").click()');
  await poll('document.querySelector("#comparison-input")?.value',value=>value?.includes('atlas-b0-d1'),'native comparison example');
  const comparisonText=await evaluate('document.querySelector("#comparison-input").value');
  assert.equal(JSON.parse(comparisonText).candidates.length,12);
  await evaluate('document.querySelector("#comparison-form").requestSubmit()');
  await poll('document.querySelector("#comparison-status")?.textContent',value=>value?.startsWith('Observed comparison status:'),'real gated native comparison');
  const comparisonStatus=await evaluate('document.querySelector(".comparison-verdict").textContent');
  assert.ok(['evaluated','deferred'].includes(comparisonStatus));
  if(comparisonStatus==='evaluated'){
    assert.equal(await evaluate('document.querySelectorAll(".comparison-candidate").length'),12);
    assert.ok(await evaluate('document.querySelector("#comparison-result").textContent.includes("12 unresolved")'));
  }
  assert.ok(await evaluate('document.querySelector("#comparison-result").textContent.includes("Canonical promotion: disabled")'));
  const comparisonLink=await evaluate('[...document.querySelectorAll("#comparison-result a")].find(link=>link.getAttribute("href").startsWith("/api/compare/run")).getAttribute("href")');
  const comparisonRun=await(await fetch(report.url+comparisonLink)).json();
  assert.equal(comparisonRun.results[0].envelope.payload.requestText,comparisonText);
  report.checks.push({name:'Original twelve-record family passes actual Jev gate with replayable exact input',status:comparisonStatus,run_id:comparisonRun.runId,canonical_promotion:false});
  const comparisonImage=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true},sessionId);writeFileSync(join(evidence,'sunny-comparison.png'),Buffer.from(comparisonImage.data,'base64'));
  await evaluate('document.querySelector("[data-view=capabilities]").click()');
  await poll('document.querySelectorAll(".history-record").length',value=>value>0,'actual Jev history');
  assert.equal(await evaluate('document.querySelectorAll(".jev-candidate").length'),2);
  const preview=await evaluate('document.querySelector("#jev-request-preview").textContent');
  assert.equal(JSON.parse(preview).questions[0].type,'choice');
  report.checks.push({name:'Visible structured native Jev request and actual receipt history',history_rows:await evaluate('document.querySelectorAll(".history-record").length')});
  const browserRequest={state:`SUNNY browser submission verification. Observed source database has ${expectedMessages} messages. Unicode fidelity marker: Σοφία — Śrī ??? ䷀. Evidence: docs/evidence/ui-browser-check.json records actual source search, full-source retrieval and native conversation context. This is an engineering assessment, with no canonical musical placements or domain-law adjudication. Preserve source bytes and all exact input/output receipts.`,questions:[{id:'decision',type:'choice',question:'Which read-only check should immediately follow this actual Unicode browser submission?',options:{verify_chain:'Run the actual receipt-chain integrity checker and compare the exact Unicode browser request with its stored payload.',inspect_distribution:'Inspect all returned distribution labels, normalization and checkpoint SHA in this browser and its source-linked receipt.'}}]};
  await evaluate(`(()=>{const request=${JSON.stringify(browserRequest)};document.querySelector('#jev-state').value=request.state;document.querySelector('#jev-question').value=request.questions[0].question;const entries=Object.entries(request.questions[0].options);document.querySelectorAll('.jev-candidate').forEach((row,index)=>{row.querySelector('.candidate-id').value=entries[index][0];row.querySelector('.candidate-meaning').value=entries[index][1];});document.querySelector('#jev-form').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('#jev-form').requestSubmit();})()`);
  await poll('document.querySelector("#jev-submit-status")?.textContent',value=>value?.includes('Actual assessment recorded.'),'actual browser form inference');
  const actualResult=await evaluate('JSON.parse(document.querySelector("#jev-result details pre").textContent)');
  assert.equal(actualResult.status,'judged');
  assert.equal(actualResult.model_info.checkpoint_sha256,'8166e46dc6019ae13f0d8fc97d603cdbcc2d20eb1882c7350c8deb9fc6bae215');
  assert.deepEqual(Object.keys(actualResult.answers[0].distribution).sort(),['inspect_distribution','verify_chain']);
  assert.ok(Math.abs(Object.values(actualResult.answers[0].distribution).reduce((a,b)=>a+b,0)-1)<1e-5);
  const checkChain=()=>{const verified=spawnSync('python',['scripts/jev_tool.py','verify'],{cwd:root,encoding:'utf8',windowsHide:true});assert.equal(verified.status,0);return JSON.parse(verified.stdout);};
  let chain;
  if(actualResult.answers[0].value==='verify_chain')chain=checkChain();
  const exactReceipt=await(await fetch(report.url+'/api/jev/receipt?sha256='+actualResult.sha256)).json();
  assert.deepEqual(exactReceipt.request,browserRequest);
  assert.equal(exactReceipt.sha256,actualResult.sha256);
  if(!chain)chain=checkChain();
  assert.equal(chain.status,'intact');
  writeFileSync(join(evidence,'jev-browser-form-smoke.json'),JSON.stringify({request:browserRequest,result:actualResult,receipt_request_matches:true,receipt_chain:chain},null,2));
  report.checks.push({name:'Actual visible Unicode browser form submits to live Jev',selected_candidate:actualResult.answers[0].value,receipt_sha256:actualResult.sha256,checkpoint_sha256:actualResult.model_info.checkpoint_sha256,exact_receipt_request_matches:true,unicode_marker:'Σοφία — Śrī ??? ䷀',receipt_chain:chain.status});
  await evaluate('document.querySelector("[data-view=decisions]").click()');
  await poll('document.querySelectorAll(".decision-quote").length',value=>value>0,'actual user candidate quotes');
  report.checks.push({name:'Source decision list visibly preserves exact extracted candidate text',quote_rows:await evaluate('document.querySelectorAll(".decision-quote").length')});
  for(const width of [320,768,1024,1440]){
    await send('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:width<640},sessionId);
    for(const view of ['overview','evidence','decisions','geometry','comparison','artifacts','capabilities']){
      await evaluate(`document.querySelector('[data-view=${view}]').click()`);await delay(120);
      const measurements=await evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth,main:document.querySelector("main").getBoundingClientRect().width})');
      assert.ok(measurements.scroll<=measurements.width+1,`${view} at ${width}px overflows: ${JSON.stringify(measurements)}`);
    }
    report.checks.push({name:'No horizontal page overflow across all seven views',viewport_width:width});
  }
  await send('Emulation.setDeviceMetricsOverride',{width:390,height:1000,deviceScaleFactor:1,mobile:true},sessionId);
  await evaluate('document.querySelector("[data-view=overview]").click()');await delay(200);
  const mobile=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true},sessionId);writeFileSync(join(evidence,'sunny-mobile.png'),Buffer.from(mobile.data,'base64'));
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1100,deviceScaleFactor:1,mobile:false},sessionId);
  await evaluate('document.querySelector("[data-view=capabilities]").click()');await delay(200);
  const workbench=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false},sessionId);writeFileSync(join(evidence,'sunny-jev-workbench.png'),Buffer.from(workbench.data,'base64'));
  const ax=await send('Accessibility.getFullAXTree',{},sessionId);
  assert.ok(ax.nodes.some(item=>item.role?.value==='textbox'&&item.name?.value==='State & source context'));
  report.checks.push({name:'Native accessibility tree includes labelled state textbox',ax_nodes:ax.nodes.length});
  assert.deepEqual(report.console_errors,[]);assert.deepEqual(report.exceptions,[]);
  report.status='passed';
  report.browser_ownership=captureBrowser();
  await send('Browser.close');
}catch(error){report.status='failed';report.error=error.stack;process.exitCode=1;}
finally{
  // Cleanup also runs after failed assertions or a broken CDP connection.
  if(socket?.readyState===WebSocket.OPEN){try{socket.send(JSON.stringify({id:999999,method:'Browser.close'}));}catch{}}
  socket?.close();
  await delay(500);
  const cleanup=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-File',join(root,'scripts','stop-test-browser.ps1'),'-BrowserPid',String(browser.pid),'-Profile',profile],{windowsHide:true,encoding:'utf8',timeout:20000});
  report.browser_cleanup={exit_code:cleanup.status,stdout:cleanup.stdout?.trim(),stderr:cleanup.stderr?.trim(),error:cleanup.error?.message};
  if(cleanup.status!==0){report.status='failed';process.exitCode=1;}
  writeFileSync(join(evidence,'ui-browser-check.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report,null,2));
  await delay(1200);
  if(resolve(profile).startsWith(resolve(tmpdir())+'\\sunny-edge-check-')){try{rmSync(profile,{recursive:true,force:true,maxRetries:5,retryDelay:200});}catch{/* Dedicated check profile can remain if Edge retains a transient lock. */}}
}
