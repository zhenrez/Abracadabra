/** Build a fully offline atlas using the exact compiled hierarchy module and source graph. */
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {fileURLToPath} from 'node:url';
import {validateHierarchyAtlas,hierarchyCensus} from '../dist/hierarchy.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>fs.readFileSync(path.resolve(root,p));const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const source=fs.existsSync(path.join(root,'state/reconstruction/hierarchy-atlas-combined.json'))?'state/reconstruction/hierarchy-atlas-combined.json':'state/reconstruction/hierarchy-atlas.json';
const bytes=read(source),atlas=JSON.parse(bytes.toString('utf8').replace(/^\uFEFF/,''));assert.equal(validateHierarchyAtlas(atlas).valid,true);
const decision=JSON.parse(read('docs/evidence/hierarchy-ui-design-superjev.json').toString('utf8').replace(/^\uFEFF/,''));assert.equal(decision.answers.design.winner,'split_tree_evidence');
const moduleBytes=read('dist/hierarchy.js'),moduleUrl='data:text/javascript;base64,'+moduleBytes.toString('base64');
const sourceBodies={},sourceImages={};for(const s of atlas.sources){
  if(!s.path)continue;const p=path.resolve(root,s.path);if(!fs.existsSync(p)||!fs.statSync(p).isFile())continue;
  const b=fs.readFileSync(p);
  const imageType=b[0]===255&&b[1]===216?'image/jpeg':b[0]===137&&b.subarray(1,4).toString('ascii')==='PNG'?'image/png':null;
  if(imageType&&b.length<=16000000){sourceImages[s.id]={dataUrl:'data:'+imageType+';base64,'+b.toString('base64'),sha256:sha(b),matchesDeclared:!s.sha256||sha(b)===s.sha256};continue;}
  if(b.length>4000000||b.subarray(0,5).toString('ascii')==='%PDF-')continue;
  let text;try{text=new TextDecoder('utf-8',{fatal:true}).decode(b);}catch{continue;}
  sourceBodies[s.id]={text,sha256:sha(b),matchesDeclared:!s.sha256||sha(b)===s.sha256};
}
const payload={atlas,sourceBodies,sourceImages,moduleUrl,provenance:{input:source,inputSha256:sha(bytes),compiledModuleSha256:sha(moduleBytes),jevResult:'docs/evidence/hierarchy-ui-design-superjev.json',jevModel:decision.resolved_model}};
const json=JSON.stringify(payload).replace(/</g,'\\u003c').replace(/\u2028/g,'\\u2028').replace(/\u2029/g,'\\u2029');
const css=read('public/hierarchy-atlas.css').toString('utf8');const client=read('public/hierarchy-atlas-client.js').toString('utf8').replace(/<\/script/gi,'\\u003c/script');
const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline' data:; style-src 'unsafe-inline'; img-src data:; connect-src 'none'; base-uri 'none'"><title>SUNNY · Hierarchy atlas</title><style>${css}</style></head><body>
<a class="skip" href="#atlas-tree">Skip to hierarchy</a><header><span class="eyebrow">SUNNY / SOURCE CENSUS</span><h1>Hierarchy atlas</h1><p>Explore the recorded branches, affiliations and counts. Competing origins and catalogue readings remain independent.</p></header>
<form id="filters" aria-label="Atlas views"><label>Domain view<select id="domain"><option value="comparison">Upper + legions</option><option value="upper">Upper hierarchies</option><option value="legions">Legion catalogues</option><option value="western">Western music</option><option value="chinese">Chinese music</option></select></label><label>Origin interpretation<select id="origin" aria-describedby="independence"></select></label><label>Legion witness<select id="witness" aria-describedby="independence"></select></label><label class="search-label">Find any entity<input id="entity-search" type="search" placeholder="Name, alias or exact entity ID" autocomplete="off"></label></form>
<p id="independence" class="note">Origin and catalogue are separate choices. No cross-tradition identity or connection is inferred by placing roots alongside one another.</p><div id="census" role="status" aria-live="polite"></div>
<main><section class="tree-panel" aria-labelledby="tree-heading"><div class="panel-heading"><h2 id="tree-heading">Recorded branches</h2><button type="button" id="collapse-all">Collapse all</button></div><p class="hint">Expand the arrow to follow a relation. Select a name for its sources, position and affiliations.</p><div id="atlas-tree" tabindex="-1"></div></section><aside id="entity-detail" aria-labelledby="detail-heading"><h2 id="detail-heading">Select a record</h2></aside></main>
<footer><details><summary>Coverage and counting boundaries</summary><div id="coverage"></div></details><p>Offline source atlas · UTF-8 names retained · Unknown joins remain open</p></footer>
<script id="atlas-data" type="application/json">${json}</script><script type="module">${client}</script></body></html>`;
fs.mkdirSync(path.join(root,'deliverables'),{recursive:true});fs.writeFileSync(path.join(root,'deliverables/SUNNY_Hierarchy_Atlas.html'),html);
const receipt={schema:'sunny.hierarchy-ui-build.v1',created_utc:new Date().toISOString(),status:'built-not-browser-verified',input:source,input_sha256:sha(bytes),compiled_module_sha256:sha(moduleBytes),html_sha256:sha(Buffer.from(html)),html_bytes:Buffer.byteLength(html),graph_records:atlas.entities.length,census:hierarchyCensus(atlas),embedded_source_bodies:Object.keys(sourceBodies).length,external_network_required:false,selected_design:decision.answers.design.winner,jev_model:decision.resolved_model};
fs.writeFileSync(path.join(root,'docs/evidence/hierarchy-ui-build.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({status:receipt.status,input:source,entities:atlas.entities.length,bytes:receipt.html_bytes,sha256:receipt.html_sha256}));
