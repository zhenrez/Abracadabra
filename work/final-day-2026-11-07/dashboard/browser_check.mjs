import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
import path from 'node:path';
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {chromium}=require('C:/Users/Brend/AppData/Local/npm-cache/_npx/1c84c9cc09572e72/node_modules/playwright');
const root=path.dirname(fileURLToPath(import.meta.url));
const html=path.join(root,'SUN_ARIADNE_Workbench.html');
const digest=raw=>crypto.createHash('sha256').update(raw).digest('hex');
const checkedJSON=filename=>{const raw=fs.readFileSync(filename);if(raw.includes(0))throw new Error('NUL bytes in JSON: '+filename);return JSON.parse(raw.toString('utf8'))};
const checkedWriteJSON=(filename,value)=>{fs.writeFileSync(filename,JSON.stringify(value,null,2)+'\n','utf8');assert.deepStrictEqual(checkedJSON(filename),value,'JSON write/readback mismatch')};
const inputPaths={html,template:path.join(root,'workbench.template.html'),build_receipt:path.join(root,'build-receipt.json'),
  source_data:path.resolve(root,'../results/dashboard-data.json'),source_snapshot:path.join(root,'dashboard-data.snapshot.json'),
  current_delivery:path.resolve(root,'../current-deliverables.json'),current_snapshot:path.join(root,'current-deliverables.snapshot.json'),
  sefer_source:path.resolve(root,'../../unit001/final-acceptance/acceptance-receipt.json'),sefer_snapshot:path.join(root,'sefer-baseline.snapshot.json'),
  browser_script:fileURLToPath(import.meta.url)};
const inputHashes=Object.fromEntries(Object.entries(inputPaths).map(([key,file])=>[key,digest(fs.readFileSync(file))]));
const build=checkedJSON(inputPaths.build_receipt),primary=checkedJSON(inputPaths.source_snapshot),current=checkedJSON(inputPaths.current_snapshot),sefer=checkedJSON(inputPaths.sefer_snapshot);
assert.equal(build.status,'READY','A complete current build is required');
assert.equal(build.html_sha256,inputHashes.html,'Built HTML hash changed');
assert.equal(build.template_sha256,inputHashes.template,'Template changed after build');
assert.equal(build.sha256,inputHashes.source_data,'Original evidence changed after build');
assert.equal(inputHashes.source_snapshot,inputHashes.source_data,'Original evidence snapshot changed');
assert.equal(inputHashes.current_snapshot,inputHashes.current_delivery,'Current assessment snapshot differs from current root ledger');
assert.equal(build.current_delivery_sha256,inputHashes.current_delivery,'Current assessment changed after build');
assert.equal(inputHashes.sefer_snapshot,inputHashes.sefer_source,'Sefer snapshot differs from preserved source');
assert.equal(build.sefer_baseline_sha256,inputHashes.sefer_source,'Sefer source changed after build');
const browser=await chromium.launch({headless:true,executablePath:'C:/Users/Brend/AppData/Local/ms-playwright/chromium-1161/chrome-win/chrome.exe'});
const errors=[],checks=[];
try{
  const page=await browser.newPage({viewport:{width:1440,height:1040},deviceScaleFactor:1});
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(pathToFileURL(html).href);
  await page.waitForFunction(()=>Boolean(window.SUN_WORKBENCH));
  const data=await page.evaluate(()=>window.SUN_WORKBENCH.data);
  const metadata=await page.evaluate(()=>window.SUN_WORKBENCH.metadata);
  for(const [key,value] of Object.entries(primary))assert.deepStrictEqual(data[key],value,'An original source field changed: '+key);
  assert.deepStrictEqual(data.current_delivery,current,'Embedded current assessments differ from their exact source');
  assert.deepStrictEqual(data.sefer_baseline.record,sefer,'Embedded Sefer record differs from its exact source');
  assert.equal(data.current_delivery_source.sha256,inputHashes.current_delivery,'Embedded current-assessment source hash mismatch');
  assert.equal(data.sefer_baseline.source.sha256,inputHashes.sefer_source,'Embedded Sefer source hash mismatch');
  assert.equal(metadata.sha256,inputHashes.source_data,'Browser loaded a stale primary evidence bundle');
  assert.equal(metadata.current_delivery_sha256,inputHashes.current_delivery,'Browser loaded stale current assessments');
  assert.equal(metadata.sefer_baseline_sha256,inputHashes.sefer_source,'Browser loaded a stale Sefer baseline');
  if(data.matrix.length!==540||data.requirements.length!==106)throw new Error('Real evidence count mismatch');
  checks.push('Real source contains540positions and106requirements');
  await page.selectOption('#state-filter','blank');
  if(!((await page.textContent('#matrix-count')).startsWith('159 of 540')))throw new Error('Blank filter mismatch');
  checks.push('Blank filter159positions');
  await page.selectOption('#state-filter','unknown');
  if(!((await page.textContent('#matrix-count')).startsWith('4 of 540')))throw new Error('Unknown filter mismatch');
  checks.push('Unknown readings remain4distinct entries');
  await page.selectOption('#state-filter','all');await page.fill('#matrix-search','s³');
  if(!((await page.textContent('#matrix-count')).startsWith('1 of 540')))throw new Error('Unicode source search mismatch');
  await page.locator('[data-record]').first().click();
  if(!(await page.isVisible('#inspector')))throw new Error('Source inspector did not open');
  await page.keyboard.press('Escape');
  if(await page.isVisible('#inspector'))throw new Error('Source inspector did not close');
  checks.push('Unicode search and source inspector keyboard close');
  await page.fill('#matrix-search','');
  await page.screenshot({path:path.join(root,'evidence-desktop.png'),fullPage:true});
  await page.click('[data-tab="models"]');
  if(await page.locator('#mode-select option').count()!==7)throw new Error('Seven native modes missing');
  await page.selectOption('#mode-select','dorian');
  await page.click('[data-model="chinese"]');
  if(await page.locator('#model-content tbody tr').count()!==12)throw new Error('Chinese generation sequence missing');
  await page.click('[data-model="grama"]');
  if(await page.locator('.unit-blocks').count()!==2)throw new Error('Two grama allocations missing');
  await page.click('[data-model="melakarta"]');
  if(await page.locator('[data-mela]').count()!==72)throw new Error('Melakarta configurations missing');
  await page.click('[data-mela="64"]');
  if(!(await page.textContent('#mela-pair')).includes('29'))throw new Error('Madhyama pair mismatch');
  checks.push('Seven Western modes,12lü,two gramas,72melas and29/65pair interactive');
  await page.screenshot({path:path.join(root,'models-desktop.png'),fullPage:true});
  await page.click('[data-model="sefer"]');
  for(const [key,value] of Object.entries({base:'22',expanded:'29',undirected:'231',directed_distinct:'462',ordered_with_self:'484'})){
    if(await page.textContent('[data-count-key="'+key+'"]')!==value)throw new Error('Sefer baseline count mismatch: '+key);
  }
  checks.push('Source-bound Sefer22/29/231/462/484baseline visible separately from pitch models');
  await page.click('[data-tab="compression"]');
  if(await page.locator('#compression-content .compact-list li').count()===0)throw new Error('Actual coding costs missing');
  await page.click('[data-tab="relationships"]');
  if(await page.locator('#relationship-content .card').count()!==2)throw new Error('Exact controls missing');
  await page.click('[data-tab="delivery"]');
  if(await page.locator('.requirement').count()!==106)throw new Error('Full deliverable register missing');
  const eg5=page.locator('[data-requirement-id="EG5"]');
  if(await eg5.getAttribute('data-audit-status')!=='NOT_IMPLEMENTED_AT_AUDIT')throw new Error('Original EG5 audit status changed');
  const eg5Current=await eg5.getAttribute('data-current-status');
  if(eg5Current!=='PASSED_SOURCE_DEFINED_PHONETIC_NUMERIC_CONTROLS')throw new Error('EG5 current assessment stale');
  if(!(await eg5.textContent()).includes('Original audit:'))throw new Error('Original audit label missing');
  await page.selectOption('#requirement-status',eg5Current);
  if(await page.locator('[data-requirement-id="EG5"]').count()!==1)throw new Error('Current-assessment filter mismatch');
  await page.selectOption('#requirement-status','');
  checks.push('EG5currentassessment shown andfiltered separately from exactoriginalauditstatus');
  await page.fill('#requirement-search','INV01');
  if(await page.locator('.requirement').count()!==1)throw new Error('Requirement search mismatch');
  await page.fill('#requirement-search','');
  await page.screenshot({path:path.join(root,'delivery-desktop.png'),fullPage:true});
  checks.push('Measured costs,exactcontrols,106requirementsearch');
  await page.setViewportSize({width:390,height:844});
  await page.click('[data-tab="evidence"]');
  await page.screenshot({path:path.join(root,'evidence-mobile.png'),fullPage:true});
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+1);
  if(overflow)throw new Error('Mobile page overflows viewport');
  checks.push('390px mobile viewport has no page overflow');
  if(errors.length)throw new Error('Browser errors: '+errors.join(';'));
  for(const [key,file] of Object.entries(inputPaths))assert.equal(digest(fs.readFileSync(file)),inputHashes[key],'Input changed during browser checks: '+key);
  const result={status:'PASSED',browser:'Installed cached Playwright Chromium; headless real browser',checks,page_errors:errors,
    screenshots:['evidence-desktop.png','models-desktop.png','delivery-desktop.png','evidence-mobile.png'],
    input_sha256:inputHashes,
    limits:['Screenshots and interactions verify UI behavior; no historical conclusion certified','No external dependency download or hosted12uimodel run']};
  const browserReceipt=path.join(root,'browser-verification.json');
  checkedWriteJSON(browserReceipt,result);
  const screenshots={};
  for(const name of result.screenshots){const filename=path.join(root,name),raw=fs.readFileSync(filename);assert.ok(raw.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])),'Screenshot is not PNG');screenshots[name]={sha256:digest(raw),bytes:raw.length,modified_utc:fs.statSync(filename).mtime.toISOString()}}
  const binding={verified_utc:new Date().toISOString(),status:'PASSED',
    source_sha256:inputHashes.source_data,html_sha256:inputHashes.html,template_sha256:inputHashes.template,
    build_receipt_sha256:inputHashes.build_receipt,browser_receipt_sha256:digest(fs.readFileSync(browserReceipt)),
    current_delivery_sha256:inputHashes.current_delivery,current_delivery_snapshot_sha256:inputHashes.current_snapshot,
    sefer_baseline_sha256:inputHashes.sefer_source,sefer_snapshot_sha256:inputHashes.sefer_snapshot,
    source_snapshot_sha256:inputHashes.source_snapshot,browser_script_sha256:inputHashes.browser_script,
    source_roundtrip:'EXACT',current_delivery_roundtrip:'EXACT',sefer_baseline_roundtrip:'EXACT',
    binding_evidence:'Actual browser loaded exact original fields plus separately hash-bound current assessments and Sefer source; every checked input remained unchanged throughout this run',
    screenshots,visual_inspection:'Programmatic browser interaction and screenshot capture; separate human/model visual inspection is not inferred',
    new_hosted_design_runtime:'NOT_PERFORMED'};
  checkedWriteJSON(path.join(root,'browser-data-bindings.json'),binding);
  console.log(JSON.stringify(result,null,2));
}finally{await browser.close()}
