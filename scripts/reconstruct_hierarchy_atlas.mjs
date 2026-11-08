/** Materialize recovered hierarchy views and explicit, non-identifying membership occurrence slots. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {validateHierarchyAtlas,hierarchyCensus,reconcileLegionCatalogue,LEGION_SLOT_UNIT,LEGION_COMMAND_RELATION} from '../dist/hierarchy.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const bytes=p=>fs.readFileSync(path.resolve(root,p));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const json=p=>JSON.parse(bytes(p).toString('utf8').replace(/^\uFEFF/,''));
const recoveryPath='docs/evidence/hierarchy-origin-witness-recovery.json';
const recovery=json(recoveryPath);
const jev=json('docs/evidence/hierarchy-implementation-superjev.json');
assert.equal(jev.status,'judged');assert.equal(jev.resolved_model,'jev-1.14.0');
assert.equal(jev.answers.hierarchy_representation.winner,'witness_scoped_graph_and_occurrence_slots');
const sources=[],entities=[],relationships=[],views=[];
const sourceIds=new Set();
const addSource=s=>{if(sourceIds.has(s.id))return;sources.push(s);sourceIds.add(s.id);};
for(const s of recovery.source_spans){
 assert.equal(sha(fs.readFileSync(s.source_path)),s.source_sha256);
 assert.equal(sha(Buffer.from(s.exact_quote)),s.quote_sha256);
 addSource({id:s.source_id,title:s.title??s.conversation_title,path:s.source_path,sha256:s.source_sha256,kind:'preserved-research-source',sourceRole:s.role??s.source_role});
}
for(const s of recovery.public_sources){assert.equal(sha(bytes(s.path)),s.sha256);addSource({id:'public:'+s.id,title:s.id,path:s.path,sha256:s.sha256,url:s.url,kind:'historical-digital-transcription',sourceRole:s.source_role});}
addSource({id:'derived:hierarchy-source-recovery',title:'Exact hierarchy source recovery',path:recoveryPath,sha256:sha(bytes(recoveryPath)),kind:'derived-source-register'});
const span=id=>recovery.source_spans.find(s=>s.id===id);
const sourceABC=span('USER-PRIMORDIAL-PAIRINGS').source_id;
const sourceChinese=span('CHINESE-NATIVE-ORDER-VS-ADAPTER').source_id;
const csvSource=recovery.legion_witnesses.uploaded_repository;
assert.equal(sha(fs.readFileSync(csvSource.path)),csvSource.sha256);
addSource({id:csvSource.source_id,title:'Uploaded72gatesCSV',path:csvSource.path,sha256:csvSource.sha256,kind:'imported-editorial-table',sourceRole:'Recovered uploaded source; correspondences are imported, not independently established.'});
const entity=(id,nativeName,unit,tradition,witnessId,sourceRefs,options={})=>{
 const e={id,nativeName,aliases:[],unit,tradition,witnessId,position:{generation:null,sequence:null,cyclicCoordinate:null,orientation:null},sourceRefs,exceptions:[],assertionLayer:'source-assertion',...options};entities.push(e);return e;
};
const edge=(source,target,type,viewIds,sourceRefs,assertionLayer='source-assertion')=>{
 const e={id:'rel:'+relationships.length,source,target,type,viewIds,sourceRefs,assertionLayer};relationships.push(e);return e;
};
const view=(id,label,roots,witnessIds,coverage,extra={})=>{const v={id,label,roots,witnessIds,coverage,...extra};views.push(v);return v;};
function production(id,inputs,outputs,viewIds,sourceRefs,witnessId,layer='source-assertion',type='production'){
 entity(id,inputs.map(x=>entities.find(e=>e.id===x)?.nativeName??x).join(' + ')+' → '+outputs.map(x=>entities.find(e=>e.id===x)?.nativeName??x).join(' + '),'production-event','Valentinian source views',witnessId,sourceRefs,{assertionLayer:layer,exceptions:['An explicit joint-event representation, not another aeon or a claim that each input is sufficient by itself.']});
 for(const x of inputs)edge(x,id,type+'-input',viewIds,sourceRefs,layer);
 for(const x of outputs)edge(id,x,type+'-output',viewIds,sourceRefs,layer);
}

// I.1 is a native witness view; competing origin constructions remain separately marked hypotheses.
const i1='Irenaeus-I.1', i1source='public:irenaeus_i_1';
const upperViews=['upper:I1','origin:A','origin:B','origin:C'];
const groups=recovery.I1_source_groups;
const memberIds=new Map();
for(const [group,pairs] of Object.entries(groups)){
 const groupId='i1:group:'+group;
 entity(groupId,group.replace('I1-',''),'aeon-collective','Valentinian',i1,[i1source],{statedExtent:{value:pairs.length*2,unit:'source-member-positions'},exceptions:['Collective description; not another individual aeon.']});
 let seq=0;
 for(const pair of pairs){
  const ids=[];
  for(const name of pair){
   const id='i1:'+group+':'+(++seq);memberIds.set(group+':'+name,id);ids.push(id);
   const aliases=group==='I1-Ogdoad'&&name==='Bythos'?['Proarche','Propator']:group==='I1-Ogdoad'&&name==='Sige'?['Ennoea','Charis']:group==='I1-Ogdoad'&&name==='Nous'?['Monogenes','Father','Beginning']:[];
   entity(id,name,'aeon-member-position','Valentinian',i1,[i1source],{aliases,position:{generation:null,sequence:seq,cyclicCoordinate:null,orientation:null},exceptions:['Sequence is position inside this source group, not an imposed global generation or cyclic coordinate.',...(name==='Monogenes'?['Contextual Decad member; do not merge it with the earlier Nous/Monogenes alias by spelling alone.']:[])]});
   edge(groupId,id,'has-source-member',upperViews,[i1source]);
  }
  edge(ids[0],ids[1],'source-syzygy',upperViews,[i1source]);
 }
}
const og=name=>memberIds.get('I1-Ogdoad:'+name);
production('i1:event:first',[og('Bythos'),og('Sige')],[og('Nous'),og('Aletheia')],upperViews,[i1source],i1);
production('i1:event:logos',[og('Nous')],[og('Logos'),og('Zoe')],upperViews,[i1source],i1);
production('i1:event:anthropos',[og('Logos'),og('Zoe')],[og('Anthropos'),og('Ecclesia')],upperViews,[i1source],i1);
production('i1:event:decad',[og('Logos'),og('Zoe')],['i1:group:I1-Decad'],upperViews,[i1source],i1);
production('i1:event:dodecad',[og('Anthropos'),og('Ecclesia')],['i1:group:I1-Dodecad'],upperViews,[i1source],i1);
view('upper:I1','Irenaeus I.1: source-native thirty-aeon membership and branching production',[og('Bythos'),og('Sige'),'i1:group:I1-Ogdoad'],[i1],{status:'bounded-complete-for-declared-thirty-position-list',individualPositions:30,syzygies:15,collectives:3,universalComplete:false});
for(const alternative of recovery.primordial_alternatives){
 const letter=alternative.id.slice(-1),v='origin:'+letter,refs=[sourceABC,'derived:hierarchy-source-recovery'];
 const rootId='origin:'+letter+':condition';
 entity(rootId,alternative.historical_label,'proposed-origin-configuration','SUNNY origin hypotheses','PRIM-'+letter,refs,{assertionLayer:'research-hypothesis',position:{generation:null,sequence:null,cyclicCoordinate:null,orientation:letter},exceptions:['One alternative configuration record; not a new named historical being.','This origin axis is not paired with any legion witness.']});
 const parts=[];
 if(letter==='B'){
  for(const [i,b] of alternative.ordered_boundaries.entries()){
   const id='origin:B:boundary:'+i;parts.push(id);
   entity(id,b.label,'proposed-functional-boundary','SUNNY origin hypotheses','PRIM-B',refs,{assertionLayer:'research-hypothesis',position:{generation:null,sequence:i,cyclicCoordinate:null,orientation:'B'},statedExtent:{value:b.address,unit:'candidate-boundary-label'},exceptions:['The0,1,1,2label is not a native birth census, physical measurement or proven Fibonacci generation.']});
   edge(rootId,id,'has-proposed-stage',[v],refs,'research-hypothesis');
   if(i)edge(parts[i-1],id,'hypothesized-enables-next',[v],refs,'research-hypothesis');
  }
  production('origin:B:event:next',[parts.at(-1)],[og('Nous'),og('Aletheia')],[v],refs,'PRIM-B','research-hypothesis','hypothesized-condition');
 }else{
  for(const [i,pair] of recovery.user_primordial_pairings.pairings.entries()){
   const id='origin:'+letter+':pairing:'+i;parts.push(id);
   entity(id,pair.join(' + '),'proposed-primordial-role-bundle','SUNNY origin hypotheses','PRIM-'+letter,refs,{assertionLayer:'research-hypothesis',position:{generation:null,sequence:i,cyclicCoordinate:null,orientation:letter},exceptions:['Functional pairing, not two newly established independent source entities.']});
   edge(rootId,id,'has-proposed-role-bundle',[v],refs,'research-hypothesis');
  }
  if(letter==='A'){
   edge(og('Bythos'),parts[0],'hypothesized-role-reading',[v],refs,'research-hypothesis');edge(og('Bythos'),parts[1],'hypothesized-role-reading',[v],refs,'research-hypothesis');
   edge(og('Sige'),parts[2],'hypothesized-role-reading',[v],refs,'research-hypothesis');
   entity('origin:A:will-exception','Thelesis / Will remains witness-dependent','unresolved-role-identity','SUNNY origin hypotheses','PRIM-A',refs,{assertionLayer:'research-hypothesis',exceptions:['I.1 does not establish Thelesis as an alias of Sige/Ennoea/Charis. Preserve the fourth pairing without inventing that identification.']});
   edge(parts[3],'origin:A:will-exception','has-unresolved-identity',[v],refs,'research-hypothesis');
  }else production('origin:C:event:joint',parts,[og('Nous'),og('Aletheia')],[v],refs,'PRIM-C','research-hypothesis','hypothesized-joint-condition');
 }
 view(v,alternative.historical_label,[rootId],[i1,'PRIM-'+letter],{status:'competing-origin-hypothesis-with-declared-I1-comparison',originResolved:false,universalComplete:false},{orientation:letter});
}

// A source-specific Monad occurrence must not be silently identified with another recension's Monad.
const i11='Irenaeus-I.11.3',s11='public:irenaeus_i_11',v11='upper:I11-Monad';
for(const [i,name] of ['Monotes','Henotes','Monas / Monad','Hen'].entries())entity('i11:power:'+i,name,'source-named-primordial-power','Valentinian',i11,[s11],{exceptions:['I.11.3reported power, not automatically identical to any Sethian or geometric Monad.']});
entity('i11:company','Remaining company of aeons','source-reported-collective','Valentinian',i11,[s11],{exceptions:['Member names and extent not supplied by this clause; no fabricated census.']});
production('i11:event:monad',['i11:power:0','i11:power:1'],['i11:power:2'],[v11],[s11],i11,'source-assertion','qualified-nonexternal-production');
edge('i11:power:2','i11:power:3','coexists-same-essence',[v11],[s11]);
production('i11:event:company',['i11:power:0','i11:power:1','i11:power:2','i11:power:3'],['i11:company'],[v11],[s11],i11);
view(v11,'Irenaeus I.11.3: Monotes/Henotes → Monad; coexisting Hen',['i11:power:0','i11:power:1'],[i11],{status:'bounded-clause-reconstruction',completeNamedCompany:false,universalComplete:false});

const i12='Irenaeus-I.12.1',s12='public:irenaeus_i_12',v12='upper:I12-thought-will';
for(const [i,name] of ['Bythos','Ennoea','Thelesis','Nous / Monogenes','Aletheia'].entries())entity('i12:power:'+i,name,'source-named-power-or-aeon','Valentinian',i12,[s12]);
edge('i12:power:0','i12:power:1','has-reported-consort',[v12],[s12]);edge('i12:power:0','i12:power:2','has-reported-consort',[v12],[s12]);
production('i12:event:thought-will',['i12:power:1','i12:power:2'],['i12:power:3','i12:power:4'],[v12],[s12],i12);
view(v12,'Irenaeus I.12.1: differentiated Thought/Will production',['i12:power:0'],[i12],{status:'bounded-opening-production',completeHierarchy:false,universalComplete:false});

// Source-native Chinese sequence and distributed functions are not a ladder of ten new beings.
const cv='native:Chinese-early-source-register',cw='Chinese-recovered-source-locked-calibration';
const chinese=[['Dao / nebulous void','source-condition'],['Space-time','continuum'],['Primordial qi / One','carrier'],['Clear Heaven / yang tendency','differentiated-pole'],['Turbid Earth / yin tendency','differentiated-pole'],['Combined essences / yin–yang interaction','relational-field'],['Four seasons','seasonal-collective'],['Wanwu / ten thousand things','manifest-multiplicity'],['Wuxing','phase-field'],['sheng','generation-operator'],['ke','regulation-operator'],['Twelve lü','pitch-standard-collection'],['ganying','distributed-resonance'],['Human / sage-ruler','embodied-regulator']];
for(const [i,[name,unit]] of chinese.entries())entity('chinese:'+i,name,unit,'Chinese',cw,[sourceChinese],{assertionLayer:'editorial',exceptions:['Recovered source-locked research calibration, not a fresh ancient-source adjudication or identity with a sefirah.',...(i===7?['Ten thousand is manifest-multiplicity language here, not10000independently enumerated people.']:[])]});
for(const [a,b] of [[0,1],[1,2],[2,3],[2,4],[3,5],[4,5],[5,6],[6,7]])edge('chinese:'+a,'chinese:'+b,'precedes-in-recovered-native-production',[cv],[sourceChinese],'editorial');
for(const i of [8,9,10,11,12])edge('chinese:'+i,'chinese:7','organizes-or-transmits-across-field',[cv],[sourceChinese],'editorial');
edge('chinese:7','chinese:13','contains-embodied-regulator',[cv],[sourceChinese],'editorial');
view(cv,'Chinese native sequence, operators, pitch standards and embodied regulation',['chinese:0'],[cw],{status:'source-locked-research-reconstruction',laterPantheonsIncluded:false,tenBeingLadder:false,universalComplete:false});

function csv(text){
 const rows=[];let row=[],cell='',quoted=false;
 for(let i=0;i<text.length;i++){
  const c=text[i];if(c==='"'){if(quoted&&text[i+1]==='"'){cell+='"';i++;}else quoted=!quoted;}
  else if(c===','&&!quoted){row.push(cell);cell='';}
  else if((c==='\n'||c==='\r')&&!quoted){if(c==='\r'&&text[i+1]==='\n')i++;row.push(cell);if(row.some(Boolean))rows.push(row);row=[];cell='';}
  else cell+=c;
 }
 assert.equal(quoted,false);if(cell||row.length){row.push(cell);rows.push(row);}const header=rows.shift();
 return rows.map(r=>{assert.equal(r.length,header.length);return Object.fromEntries(header.map((h,i)=>[h,r[i]]));});
}
const imported=csv(fs.readFileSync(csvSource.path,'utf8').replace(/^\uFEFF/,''));assert.equal(imported.length,72);
const namePath='docs/evidence/hierarchy-native-name-extraction.json',nameExtraction=json(namePath);
const nativeNameSource=recovery.public_sources.find(s=>s.id==='goetia_peterson_sloane3825');
assert.equal(nameExtraction.source.sha256,nativeNameSource.sha256);assert.equal(nameExtraction.rows.length,72);
const nameDecision=json('docs/evidence/hierarchy-name-parser-recovery-superjev.json');assert.equal(nameDecision.status,'judged');assert.equal(nameDecision.answers.parser_recovery.winner,'existing_dom_extraction_artifact');
const petersonNames=new Map(nameExtraction.rows.map(r=>{assert.equal(sha(Buffer.from(r.native_name)),r.extracted_name_sha256);return[r.paragraph_id,r.native_name];}));assert.equal(petersonNames.size,72);
addSource({id:'derived:peterson-native-name-extraction',title:'Literal Peterson names from pinned source DOM',path:namePath,sha256:sha(bytes(namePath)),kind:'derived-source-extraction',sourceRole:nameExtraction.method});
const witnesses=[['uploaded-repository','Uploaded repository and primary-rank table',csvSource.source_id,'uploaded_repository'],['de-laurence-1916','deLaurence1916 current digital main reading','public:goetia_de_laurence_1916','goetia_de_laurence_1916'],['peterson-sloane3825','Peterson Sloane3825 current digital main reading','public:goetia_peterson_sloane3825','goetia_peterson_sloane3825']];
for(const [w,label,sourceId,key] of witnesses){
 const v='catalogue:'+w,collection=w+':catalogue';
 entity(collection,label,'catalogue-collection','Solomonic Goetia',w,[sourceId],{statedExtent:{value:72,unit:'catalogue-chief-positions'},exceptions:['A witness-scoped collection, not an additional chief.']});
 const ranks=new Map();
 const rankGroups=w==='de-laurence-1916'?recovery.native_rank_enumeration.groups:w==='uploaded-repository'?[...new Set(imported.map(r=>r.goetic_rank))].map(rank=>({native_label:rank,member_positions:imported.filter(r=>r.goetic_rank===rank).map(r=>Number(r.gate))})):[];
 for(const [i,g] of rankGroups.entries()){
  const rid=w+':rank:'+i;ranks.set(g.native_label,rid);
  entity(rid,g.native_label,w==='uploaded-repository'?'imported-primary-rank-group':'source-rank-group','Solomonic Goetia',w,[sourceId],{assertionLayer:w==='uploaded-repository'?'editorial':'source-assertion',statedExtent:{value:g.member_positions.length,unit:'rank-membership-occurrences'},exceptions:['Rank membership is distinct from biological generation and catalogue sequence; group order is not a total rank order.']});
  edge(collection,rid,'lists-rank-group',[v],[sourceId],w==='uploaded-repository'?'editorial':'source-assertion');
 }
 for(let i=0;i<72;i++){
  const count=recovery.legion_witnesses.vectors[key][i],id=w+':chief:'+(i+1),rawRow=recovery.legion_witnesses.rows[key]?.[i];
  const title=w==='peterson-sloane3825'?petersonNames.get(rawRow.selector.paragraph_id):rawRow?.source_text_with_editorial_brackets.match(/^\(\d+\.?\)\s*(.*?)(?:\s*—|\.—)/s)?.[1]?.replace(/\s+/g,' ').replace(/\.$/,'')??imported[i].demon;
  assert.ok(typeof title==='string'&&title.length>0,'native source name must resolve');
  entity(id,title,'catalogue-chief','Solomonic Goetia',w,[sourceId],{aliases:[imported[i].demon],position:{generation:null,sequence:i+1,cyclicCoordinate:null,orientation:null},statedExtent:{value:count,unit:'primary-legion-command-count',uniqueLegions:'unknown',uniquePersonnel:'unknown'},exceptions:['Sequence is source catalogue position, not a genealogical generation or proved musical placement.','Counted slots do not establish disjoint real legions.',...(i===8?['Paimon primary200and secondary accompanying25remain separate;25is not added to this primary extent.']:[]),...(w==='peterson-sloane3825'?['Full source-specific multiple-rank enumeration is not claimed by this catalogue view; raw rank text remains in the witness source.']:[])],sourceLocator:rawRow?.selector??{csvDataRow:i+1},comparisonName:imported[i].demon});
  edge(collection,id,'lists-catalogue-chief',[v],[sourceId]);
  for(const g of rankGroups)if(g.member_positions.includes(i+1))edge(ranks.get(g.native_label),id,'has-rank-member',[v],[sourceId],w==='uploaded-repository'?'editorial':'source-assertion');
  for(let n=1;n<=count;n++){
   const sid=id+':attributed-slot:'+n;
   entity(sid,'Catalogue-attributed legion slot '+n+' of '+title,LEGION_SLOT_UNIT,'Solomonic Goetia',w,[sourceId],{assertionLayer:'generated',position:{generation:null,sequence:n,cyclicCoordinate:null,orientation:null},exceptions:['Generated address for this command-count membership occurrence; no invented individual name or source identity.','Unique legions across commands/witnesses and personnel remain unknown.']});
   edge(id,sid,LEGION_COMMAND_RELATION,[v],[sourceId],'generated');
  }
 }
 view(v,label,[collection],[w],{status:'complete72chief-and-primary-command-vector',chiefPositions:72,primaryCommandCount:recovery.legion_witnesses.vectors[key].reduce((a,b)=>a+b,0),nativeRankMemberships:w==='de-laurence-1916'?79:null,globalUniqueLegions:null,fullUniverseComplete:false});
}
if(jev.answers.imported_angel_table.winner==='explicit_editorial_view'){
 const v='imported:angel-table-order',w='uploaded-gate-table';entity('imported:angel-collection','Imported72angel names in gate-table order','imported-name-collection','Imported cross-system table',w,[csvSource.source_id],{assertionLayer:'editorial'});
 for(const [i,r] of imported.entries()){
  const id='imported:angel:'+r.gate;entity(id,r.angel,'imported-angel-name-at-gate','Imported cross-system table',w,[csvSource.source_id],{assertionLayer:'editorial',position:{generation:null,sequence:Number(r.gate),cyclicCoordinate:null,orientation:null},exceptions:['Literal uploaded-table order only, not an ancient native angelic generation/rank or proven divine identity.','Imported Goetic/Shem/choir/clock attributions are not independently promoted.']});
  edge('imported:angel-collection',id,'lists-imported-name',[v],[csvSource.source_id],'editorial');
  edge(id,'uploaded-repository:chief:'+(i+1),'co-indexed-in-imported-table',[v],[csvSource.source_id],'editorial');
 }
 view(v,'Imported angel-name table order (editorial witness, native angel hierarchy unresolved)',['imported:angel-collection'],[w,'uploaded-repository'],{status:'complete-imported-name-column',nativeAngelicHierarchy:false,universalComplete:false});
}
const atlas={schema:'sunny.hierarchy-atlas.v1',generatedAt:new Date().toISOString(),decisionReceipt:'docs/evidence/hierarchy-implementation-superjev.json',sources,entities,relationships,views,
 independence:{primordialOrientationAxis:['A','B','C'],legionWitnessAxis:witnesses.map(x=>x[0]),paired:false,permittedCombinations:9,sourceIndependence:'Goetic versions share transmission ancestry; not independent empirical confirmations.'},
 unresolved:[{id:'GAP-ABC-MONAD-JOIN',detail:'No source-independent identification of all primordial alternatives with one Monad or source-native cross-tradition birth chain.'},{id:'GAP-FULL-ARCHON-GRAPH',detail:'Complete named critical-edition archon/angel/demon parentage and appointment graphs remain to be recovered, not invented.'},{id:'GAP-NATIVE-ANGEL-ORDER',detail:'Imported72names retained separately; full native angelic hierarchy/order requires selected source witnesses.'},{id:'GAP-CHINESE-PANTHEONS',detail:'Early native sequence/operators are separate from later Chinese pantheons and the Western hierarchy.'},{id:'GAP-UNIQUE-LEGIONS',detail:'Commands/witnesses may overlap. Unique legion and personnel populations are unknown.'},{id:'GAP-MUSICAL-JOINS',detail:'Musical source trees may be merged as separate views; no numerical-total correspondence or invented parentage supplies their bridge.'}],
 coverage:{completeUniversalHierarchy:false,semanticCorpusComplete:false,scope:'Declared source-native and explicit hypothesis views, full72chiefcatalogues and anonymous command-count occurrence slots only.'}};
const validity=validateHierarchyAtlas(atlas);assert.equal(validity.valid,true,validity.errors.join('\n'));
const reconciliations=witnesses.map(w=>reconcileLegionCatalogue(atlas,w[0]));assert.ok(reconciliations.every(r=>r.valid));
assert.deepEqual(reconciliations.map(r=>r.generatedMembershipSlotCount),[2648,2645,2618]);
const nativeCensus=hierarchyCensus(atlas,{viewIds:['catalogue:de-laurence-1916']});assert.equal(nativeCensus.chiefRecords,72);assert.equal(nativeCensus.rankMembershipOccurrences,79);
atlas.verification={validity,reconciliations,census:hierarchyCensus(atlas),nativeRankCensus:nativeCensus,sourceArtifactSha256:sha(bytes(recoveryPath)),scope:'Executed shape/reference/count checks, not historical certification or universal prediction.'};
const out=path.join(root,'state/reconstruction/hierarchy-atlas.json');
if(fs.existsSync(out)){const previous=fs.readFileSync(out);const dir=path.join(root,'state/checkpoint-history');fs.mkdirSync(dir,{recursive:true});const name=path.join(dir,'before-hierarchy-atlas-'+sha(previous)+'.snapshot');if(!fs.existsSync(name))fs.writeFileSync(name,previous,{flag:'wx'});}
fs.writeFileSync(out,JSON.stringify(atlas,null,2)+'\n');
const doc=['# Executable hierarchy atlas','',
 'This source-bound atlas now provides inspectable graph views, count reconciliation, independent A/B/C and legion-witness selection, and individually addressable anonymous command-count occurrence slots. It remains an incomplete universal hierarchy.','',
 '## Current views','', '| View | Scope |','|---|---|',...views.map(v=>'| `'+v.id+'` | '+v.label+' |'),'',
 'The three complete chief vectors reproduce2648,2645and2618primary legion-command occurrences. Generated slots enumerate those declared extents; they do not invent names, distinct real legions, disjoint commands or personnel. Source-native deLaurence ranks have72chiefs but79rank memberships. The uploaded primary-rank projection and imported angel-name order remain editorial source views.','',
 'I.1 preserves its thirty contextual aeon positions, syzygies, collectives and branching joint-production events. The I.11Monad and I.12Thought/Will structures are separate source witnesses. A/B/C are explicitly marked hypotheses; neither a source alias nor the total34elects one. The Chinese native-order/operator view remains separate from an imposed ten-being ladder and later pantheons.','',
 '## Executable interface','', '`validateHierarchyAtlas`, `filterHierarchy`, `hierarchyCensus`, `ancestorsOf`, and `reconcileLegionCatalogue` are exported by `src/hierarchy.ts`. Select multiple view IDs to combine independent origin and witness views; other explicitly supplied filters intersect that union. Cycles are reported by traversal without hanging. Count reconciliation rejects missing, multiply commanded, mis-sourced or wrongly indexed slots.','',
 'Validation covers shape, provenance references, declared dependencies and exact source-vector arithmetic. It does not adjudicate historical authenticity, infer cross-witness identity or choose a musical orientation. Actual Jev choices are preserved in the decision receipt; they are not mathematical proof.','',
 '## Explicit missing joins','',...atlas.unresolved.map(x=>'- '+x.id+': '+x.detail),'',
 'Build then reproduce: `npm run build` and `node scripts/reconstruct_hierarchy_atlas.mjs`. Source definitions, raw transcriptions, exact quotes, native ranks and all vector readings remain in `docs/evidence/hierarchy-origin-witness-recovery.json`. No source bytes, task priorities, database records or external systems are changed by the atlas build.',''];
fs.writeFileSync(path.join(root,'docs/reconstruction/HIERARCHY_ATLAS.md'),doc.join('\n'));
console.log(JSON.stringify({result:'PASS',exit_code:0,views:views.length,entityRecords:atlas.verification.census.entityRecords,generatedMembershipSlots:atlas.verification.census.generatedMembershipSlots,primaryCommandSums:reconciliations.map(x=>x.primaryCommandCountSum),nativeRankMemberships:79,universalComplete:false,atlasSha256:sha(fs.readFileSync(out))}));
