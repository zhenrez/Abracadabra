import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync, mkdirSync, writeFileSync, rmSync, readFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {once} from 'node:events';
import Database from 'better-sqlite3';
import {DatabaseSync as BuiltinDatabase} from 'node:sqlite';
import {createHash} from 'node:crypto';
import {createSunnyServer, isLocalHost} from '../dist/server.js';

test('selected SQLite driver provides required FTS5 independently of the built-in runtime', () => {
  const builtin = new BuiltinDatabase(':memory:');
  const hasBuiltinFts5 = builtin.prepare("SELECT sqlite_compileoption_used('ENABLE_FTS5') AS enabled").get().enabled;
  if (!hasBuiltinFts5) assert.throws(() => builtin.exec('CREATE VIRTUAL TABLE original_failure USING fts5(text)'), /no such module: fts5/);
  builtin.close();
  const selected = new Database(':memory:');
  assert.equal(selected.prepare("SELECT sqlite_compileoption_used('ENABLE_FTS5') AS enabled").get().enabled, 1);
  // Independently execute the actual production schema, including source positions.
  const importer=readFileSync(new URL('../scripts/ingest.py',import.meta.url),'utf8');
  selected.exec(importer.match(/SCHEMA = """([\s\S]*?)"""/)[1]);
  assert.equal(selected.prepare("SELECT count(*) AS n FROM sqlite_master WHERE name='source_positions'").get().n,1);
  assert.ok(selected.prepare('PRAGMA table_info(source_positions)').all().some(row=>row.name==='utf8_byte_start'));
  selected.close();
});

test('read-only source service preserves actual role, text, branches and source locators', async t => {
  const root=mkdtempSync(join(tmpdir(),'sunny-server-test-'));
  mkdirSync(join(root,'data')); mkdirSync(join(root,'state')); mkdirSync(join(root,'public'));
  const databasePath=join(root,'data','sunny.sqlite');
  const db=new Database(databasePath);
  // Jev receipt48 selected a separate fixed HTTP fixture; production schema above.
  db.exec(readFileSync(new URL('fixtures/source-schema.sql',import.meta.url),'utf8'));
  db.prepare('INSERT INTO sources VALUES(?,?,?,?,?,?,?,?,?)').run('source-1','retained/source.json','original/source.json','a'.repeat(64),100,'application/json','fixture','preserved',null);
  db.prepare('INSERT INTO conversations VALUES(?,?,?,?,?,?,?,?,?)').run('conv-1','native-conv','SUNNY <img src=x onerror=alert(1)>','source-1','/0','native-current','1700000000',null,'{}');
  const message=db.prepare('INSERT INTO messages VALUES(?,?,?,?,?,?,?,?,?,?,?,?)');
  message.run('msg-1','conv-1','native-current',null,'user','SUNNY preserve my exact question marks???','content-hash','source-1','/0/mapping/native-current/message','1700000000','current','{"content":{"parts":["SUNNY preserve my exact question marks???"]}}');
  message.run('msg-2','conv-1','native-alternate',null,'assistant','An alternate SUNNY answer','another-hash','source-1','/0/mapping/native-alternate/message','1700000001','alternate','{}');
  db.prepare('INSERT INTO nodes VALUES(?,?,?,?,?,?)').run('conv-1','native-current',null,'[]',1,1);
  db.prepare('INSERT INTO search_index VALUES(?,?,?,?)').run('msg-1','message','SUNNY <img src=x onerror=alert(1)>','SUNNY preserve my exact question marks???');
  db.prepare('INSERT INTO search_index VALUES(?,?,?,?)').run('msg-2','message','SUNNY fixture','An alternate SUNNY answer');
  db.prepare('INSERT INTO documents VALUES(?,?,?,?,?,?)').run('doc-1','source-1','Source document','SUNNY document original text','fixture','extracted');
  db.prepare('INSERT INTO search_index VALUES(?,?,?,?)').run('doc-1','document','Source document','SUNNY document original text');
  db.prepare('INSERT INTO decisions VALUES(?,?,?,?,?,?)').run('decision-1','msg-1','user_direction_candidate','extracted_unreviewed','Preserve my exact question marks???','lexical_screen_only');
  db.prepare('INSERT INTO decisions VALUES(?,?,?,?,?,?)').run('decision-2','msg-1','user_direction_candidate','extracted_unreviewed','Second explicit extracted candidate','lexical_screen_only');
  db.prepare('INSERT INTO coverage VALUES(?,?,?,?)').run('fixture','bounded','Test-only fixture','Not account research evidence.');
  const position=db.prepare('INSERT INTO source_positions VALUES(?,?,?,?,?,?,?,?,?,?,?,?)');
  position.run('msg-1','source-1',20,100,200,'record-hash-1','old-line:1','native-current',1,'physical_source_record_order_only_not_causal_parentage','test-only physical-byte fixture','fixture-not-live-decision');
  position.run('msg-2','source-1',10,0,100,'record-hash-2','old-line:2','native-alternate',2,'physical_source_record_order_only_not_causal_parentage','test-only physical-byte fixture','fixture-not-live-decision');
  db.close();
  writeFileSync(join(root,'state','task.json'),JSON.stringify({goal:'Preserve source fidelity',constraints:['Keep ???'],open_questions:['Unresolved?'],next_actions:['Review evidence']}));
  writeFileSync(join(root,'public','index.html'),'<!doctype html><title>SUNNY test fixture</title>');
  writeFileSync(join(root,'state','private-secret.txt'),'MUST NOT BE SERVED');
  const before=createHash('sha256').update(readFileSync(databasePath)).digest('hex');
  const server=createSunnyServer({root,databasePath});
  server.listen(0,'127.0.0.1'); await once(server,'listening');
  const base=`http://127.0.0.1:${server.address().port}`;
  t.after(async()=>{await new Promise(resolve=>server.close(resolve));assert.ok(root.startsWith(join(tmpdir(),'sunny-server-test-')));rmSync(root,{recursive:true,force:true});});
  const request=async path=>{const response=await fetch(base+path);return {status:response.status,data:await response.json(),headers:response.headers};};

  const summary=await request('/api/summary');
  assert.equal(summary.status,200);assert.equal(summary.data.counts.messages,2);assert.equal(summary.data.counts.artifacts,1);assert.equal(summary.data.account_complete,false);
  const search=await request('/api/search?q=SUNNY&limit=40');
  assert.equal(search.status,200);assert.equal(search.data.total,3);assert.equal(search.data.results.find(row=>row.id==='msg-1').role,'user');
  const paged=[];let offset=0;
  do {const page=await request(`/api/search?q=SUNNY&limit=1&offset=${offset}`);assert.equal(page.data.offset,offset);paged.push(...page.data.results.map(row=>row.id));offset=page.data.next_offset;} while(offset!==null);
  assert.equal(paged.length,3);assert.equal(new Set(paged).size,3);assert.deepEqual(paged,search.data.results.map(row=>row.id),'stable paginated FTS order must match one bounded complete fixture page');
  assert.equal((await request('/api/search?q=SUNNY&limit=1&offset=999')).data.results.length,0);
  const defaultPage1=await request('/api/search?limit=1&offset=0');const defaultPage2=await request('/api/search?limit=1&offset=1');assert.notEqual(defaultPage1.data.results[0].id,defaultPage2.data.results[0].id);
  const original=await request('/api/message?id=msg-1');
  assert.equal(original.data.message.text,'SUNNY preserve my exact question marks???');assert.equal(original.data.message.locator,'/0/mapping/native-current/message');assert.equal(original.data.message.is_current_path,true);assert.equal(original.data.message.raw.content.parts[0],'SUNNY preserve my exact question marks???');
  const alternative=await request('/api/message?id=msg-2');assert.equal(alternative.data.message.is_current_path,false);
  const document=await request('/api/message?id=doc-1');assert.equal(document.data.message.role,'source_document');assert.equal(document.data.message.text,'SUNNY document original text');
  const conversation=await request('/api/conversation?id=conv-1&limit=1');assert.equal(conversation.data.conversation.current_node,'native-current');assert.equal(conversation.data.total,2);assert.equal(conversation.data.truncated,true);assert.equal(conversation.data.next_offset,1);assert.equal(conversation.data.nodes.length,1);
  assert.equal(conversation.data.messages[0].id,'msg-2','physical source position must override append/insertion row order');assert.equal(conversation.data.messages[0].physical_lf_line,10);assert.match(conversation.data.message_order,/not causal parentage/);assert.equal(conversation.data.source_position_count,2);
  const decisions=await request('/api/decisions');assert.equal(decisions.data.results[0].status,'extracted_unreviewed');assert.equal(decisions.data.results[0].message_id,'msg-1');
  const decisionPage1=await request('/api/decisions?limit=1&offset=0');const decisionPage2=await request('/api/decisions?limit=1&offset=1');assert.equal(decisionPage1.data.total,2);assert.equal(decisionPage1.data.next_offset,1);assert.equal(decisionPage2.data.next_offset,null);assert.notEqual(decisionPage1.data.results[0].id,decisionPage2.data.results[0].id);
  const conversationNext=await request('/api/conversation?id=conv-1&limit=1&offset=1');assert.notEqual(conversation.data.messages[0].id,conversationNext.data.messages[0].id);assert.equal(conversationNext.data.next_offset,null);
  const source=await request('/api/source?id=source-1');assert.equal(source.data.source.sha256,'a'.repeat(64));assert.equal(source.data.documents[0].id,'doc-1');
  const state=await request('/api/state');assert.equal(state.data.open_questions[0],'Unresolved?');
  const capabilities=await request('/api/capabilities');assert.equal(capabilities.data.status,'not_available');assert.deepEqual(capabilities.data.plugins,[]);
  const history=await request('/api/jev/history');assert.equal(history.data.status,'not_available');
  assert.equal((await request('/api/artifacts')).data.results[0].original_path,'original/source.json');

  for(const path of ['/api/message?id=missing','/api/message?id='+encodeURIComponent("' OR 1=1 --"),'/api/source?id='+encodeURIComponent('../state/private-secret.txt'),'/state/private-secret.txt','/%2e%2e/state/private-secret.txt','/..%2fstate/private-secret.txt','/public/../state/private-secret.txt']) {
    const result=await request(path);assert.equal(result.status,404,path);assert.ok(!JSON.stringify(result.data).includes('MUST NOT BE SERVED'));
  }
  for(const query of ['" OR 1=1 --','SUNNY OR NOT * : ( )','***','SUNNY; DROP TABLE messages;'])assert.equal((await request('/api/search?q='+encodeURIComponent(query))).status,200,query);
  assert.equal((await request('/api/search?q='+encodeURIComponent('a'.repeat(1001)))).status,400);
  const post=await fetch(base+'/api/state',{method:'POST',body:'{}'});assert.equal(post.status,405);assert.equal(post.headers.get('Allow'),'GET');
  const wrongType=await fetch(base+'/api/jev/decide',{method:'POST',headers:{'Content-Type':'text/plain'},body:'{}'});assert.equal(wrongType.status,415);
  const foreignOrigin=await fetch(base+'/api/jev/decide',{method:'POST',headers:{'Content-Type':'application/json',Origin:'https://foreign.example'},body:'{}'});assert.equal(foreignOrigin.status,403);
  const crossSite=await fetch(base+'/api/jev/decide',{method:'POST',headers:{'Content-Type':'application/json','Sec-Fetch-Site':'cross-site'},body:'{}'});assert.equal(crossSite.status,403);
  const oversized=await fetch(base+'/api/jev/decide',{method:'POST',headers:{'Content-Type':'application/json'},body:'a'.repeat(48001)});assert.equal(oversized.status,413);
  const invalidJson=await fetch(base+'/api/jev/decide',{method:'POST',headers:{'Content-Type':'application/json'},body:'{not json'});assert.equal(invalidJson.status,400);
  const missingState=await fetch(base+'/api/jev/decide',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});assert.equal(missingState.status,400);
  const absentFixedTool=await fetch(base+'/api/jev/decide',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({state:'test',questions:[{id:'choice',type:'choice',question:'Which?',options:{a:'One',b:'Two'}}]})});assert.equal(absentFixedTool.status,503);assert.equal((await absentFixedTool.json()).fallback_decision,null);
  for(const [headers,body,status] of [[{'Content-Type':'text/plain'},'{}',415],[{'Content-Type':'application/json',Origin:'https://foreign.example'},'{}',403],[{'Content-Type':'application/json'},'x'.repeat(48001),413]]){
    assert.equal((await fetch(base+'/api/compare',{method:'POST',headers,body})).status,status);
  }
  const comparisonInput={kernel:{id:'fixture-kernel',version:'1',sha256:'a'.repeat(64),sourceRefs:['source-1']},candidates:[{id:'fixture-candidate',assignment:{position:1},sourceRefs:['source-1']}],constraints:[]};
  const exactInput=JSON.stringify(comparisonInput,null,2)+'\n';
  const comparisonResponse=await fetch(base+'/api/compare',{method:'POST',headers:{'Content-Type':'application/json'},body:exactInput});assert.equal(comparisonResponse.status,503);
  const comparisonFailure=await comparisonResponse.json();assert.equal(comparisonFailure.fallback_decision,null);assert.equal(comparisonFailure.canonicalPromotion,false);assert.match(comparisonFailure.runId,/^[a-f0-9-]{36}$/);
  const run=await request('/api/compare/run?id='+comparisonFailure.runId);assert.equal(run.data.results.length,2);assert.equal(run.data.results[0].phase,'submitted');assert.equal(run.data.results[0].envelope.payload.requestText,exactInput);assert.equal(run.data.results[1].phase,'failed');
  for(const event of run.data.results)assert.equal(createHash('sha256').update(event.payload_json).digest('hex'),event.sha256);
  const comparisonHistory=await request('/api/compare/history');assert.equal(comparisonHistory.data.results[0].run_id,comparisonFailure.runId);
  assert.equal((await request('/api/compare/run?id='+encodeURIComponent('../private'))).status,400);
  assert.equal((await request('/api/compare/example')).status,404,'missing native example must not be fabricated');
  // Jev receipt000010 selected direct validation testing after Node fetch was observed to ignore Host overrides.
  assert.equal(isLocalHost('evil.example'),false);assert.equal(isLocalHost('127.0.0.1:4317'),true);assert.equal(isLocalHost(undefined),false);
  assert.equal(summary.headers.get('Access-Control-Allow-Origin'),null);assert.match(summary.headers.get('Content-Security-Policy'),/frame-ancestors 'none'/);
  const staticPage=await fetch(base+'/');assert.equal(staticPage.status,200);assert.match(await staticPage.text(),/SUNNY test fixture/);
  assert.equal((await request('/api/summary')).data.counts.messages,2);
  assert.equal(createHash('sha256').update(readFileSync(databasePath)).digest('hex'),before,'HTTP reads and refused writes must leave source database bytes unchanged');
});
