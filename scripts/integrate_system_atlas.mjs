/** Merge native systems without silently inventing cross-system identities or generations. */
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';import assert from 'node:assert/strict';
import {validateHierarchyAtlas,hierarchyCensus} from '../dist/hierarchy.js';
const root=fileURLToPath(new URL('../',import.meta.url)),at=p=>path.join(root,p);
const read=p=>fs.readFileSync(at(p)),load=p=>JSON.parse(read(p)),sha=b=>createHash('sha256').update(b).digest('hex');
const graphPath='state/reconstruction/hierarchy-atlas-combined.json',baseline='state/research/native-class/atlas-before-native-expansion.json';
if(!fs.existsSync(at(baseline))){fs.mkdirSync(path.dirname(at(baseline)),{recursive:true});fs.writeFileSync(at(baseline),read(graphPath),{flag:'wx'});}
const original=load(baseline),graph=structuredClone(original),bindings=[];
const frozen=p=>{const raw=read(p);bindings.push({path:p,sha256:sha(raw),bytes:raw.length});return JSON.parse(raw);};
const maps=Object.fromEntries(['sources','entities','relationships','views'].map(k=>[k,new Map(graph[k].map(e=>[e.id,e]))]));
function append(kind,row){assert.ok(row.id,kind+' needs ID');const previous=maps[kind].get(row.id);if(previous){
 if(JSON.stringify(previous)!==JSON.stringify(row)){
  // A retained source has different registry metadata; retain both without changing the baseline record.
  if(kind==='sources'&&(!previous.sha256||!row.sha256||previous.sha256===row.sha256)){
   graph.sourceRegistryVariants??=[];
   if(!graph.sourceRegistryVariants.some(x=>x.sourceId===row.id&&JSON.stringify(x.record)===JSON.stringify(row)))graph.sourceRegistryVariants.push({sourceId:row.id,record:structuredClone(row),boundary:'Additional registry metadata preserved; the baseline source record remains unchanged.'});
   return;
  }
  throw Error('Conflicting '+kind+': '+row.id);
 }return;}
 maps[kind].set(row.id,row);graph[kind].push(row);}
for(const name of ['indian-hierarchy','western-expanded','chinese-expanded','native-class-constructors']){
 const unit=frozen('state/reconstruction/'+name+'.json');
 for(const k of ['sources','entities','relationships','views'])for(const row of unit[k])append(k,structuredClone(row));
}
const bible=frozen('state/reconstruction/biblical-genealogies.json');
for(const row of bible.sources)append('sources',row);
append('sources',{id:'7d5a026c9df7d3fdf06382c966729a7cf3da22dbc4a1276c9f809f7a139ce965',path:'data/raw/reconstruction-recovered/73b3171aa010c78121f2d7798011ce36f6e4891f4ef1409d25ed98aaca16fcfc/ChatGPT-Comparative Research Protocol-20261030-1502.md',sha256:'73b3171aa010c78121f2d7798011ce36f6e4891f4ef1409d25ed98aaca16fcfc',sourceRole:'Recovered research conversation supplying the inherited conditional chronology; not a primary historical witness.'});
const bibleBase='bible:curated-comparison',blank={generation:null,sequence:null,cyclicCoordinate:null,orientation:null};
function editorialEntity(id,name,unit,sid,witness){return {id,nativeName:name,aliases:[],unit,tradition:'Source-scoped comparative registry',witnessId:witness,position:{...blank},sourceRefs:[sid],exceptions:[],assertionLayer:'editorial-container'};}
const src='theographic:CSV/People.csv';
append('entities',editorialEntity('bible:comparison:root','Whole-Bible curated entity and relationship index','editorial-collection',src,'Theographic-KJV-comparison'));
append('views',{id:bibleBase,label:'Whole-Bible curated comparison and explicit verse claims',roots:['bible:comparison:root'],witnessIds:['Theographic-KJV-comparison'],coverage:{completePrimaryWitnessCollation:false,curatedEntityRecords:3067,boundary:'A curated comparison index; no universal biological or manuscript genealogy is inferred.'}});
for(const e of bible.entities){
 const family=e.witnessFamily??(e.id.startsWith('bible:received-lineage:')?e.id.split(':')[3]:null);
 append('entities',{...e,aliases:e.aliases??[],tradition:family?'Biblical inherited witness '+family:'Biblical curated/verse-local comparison',
  witnessId:family??'Theographic-KJV-comparison',position:{...blank,sequence:e.namedEntryOrdinalOneBased??e.sourceRecordOrdinalOneBased??null},
  assertionLayer:family?'received-conditional-occurrence':'curator-or-textual-occurrence',exceptions:e.disambiguationNote?[String(e.disambiguationNote)]:[],
  globalSunnyAddress:null,sourceOccurrenceRetained:true});
 // Registry membership lists records; it makes no ancestry claim.
 append('relationships',{id:'systems:index:'+e.id,source:'bible:comparison:root',target:e.id,type:'indexes-source-record',viewIds:[bibleBase],sourceRefs:e.sourceRefs,assertionLayer:'editorial-index'});
}
const bibleViews=new Map(bible.views.map(v=>[v.id,v]));
for(const v of bible.views){
 const family=v.id.split(':').at(-1),vid=v.id,rootId=vid+':root';
 append('entities',editorialEntity(rootId,v.label+' — inherited lineage / edition comparison','editorial-witness-container','received:expanded-lineage-2026-10-23',family));
 const relIds=new Set([...(v.receivedWitnessRelationIds??[]),...(v.originalEditionParentageAssertions??[]).map(x=>typeof x==='string'?x:x.id)]);
 const related=bible.relationships.filter(r=>relIds.has(r.id)||r.id.startsWith('bible:primary-begetting:'+family+':'));
 const members=new Set(related.flatMap(r=>[r.source,r.target]));const child=new Set(related.map(r=>r.target));
 const roots=[...members].filter(id=>!child.has(id));
 append('views',{...v,roots:[rootId],witnessIds:[family],coverage:{scope:v.scope,completeOriginalWitnessGenealogy:false,primaryAssertions:related.filter(r=>r.type==='edition-textual-genealogical-begetting').length,boundary:v.comparisonRelationStatus}});
 for(const target of roots)append('relationships',{id:'systems:family-root:'+family+':'+target,source:rootId,target,type:'lists-native-lineage-root',viewIds:[vid],sourceRefs:['received:expanded-lineage-2026-10-23'],assertionLayer:'editorial-index'});
}
for(const r of bible.relationships){
 const views=[bibleBase];for(const v of bible.views)if((v.receivedWitnessRelationIds??[]).includes(r.id)||(v.originalEditionParentageAssertions??[]).some(x=>(typeof x==='string'?x:x.id)===r.id)||(r.id.startsWith('bible:primary-begetting:'+v.id.split(':').at(-1)+':')))views.push(v.id);
 append('relationships',{...r,viewIds:views});
}
const upper=frozen('state/reconstruction/upper-legion-color-constraints.json');
for(const s of upper.primaryTextPackets)append('sources',s);
for(const e of upper.proposedGraphExtension.entities)append('entities',e);
for(const [i,r]of upper.proposedGraphExtension.relationships.entries())append('relationships',{...r,id:r.id??'systems:goetic-upper:'+i,viewIds:r.viewIds??['catalogue:'+r.witnessId]});
const colorBinding=upper.sourceBindings.find(x=>x.path.endsWith('Color_Carriers_FROZEN_v1.json'));
const colorSrc='source:frozen-color-carriers';append('sources',{...colorBinding,id:colorSrc,title:'Retained frozen linear-light color carriers; conditional experiment input',kind:'recovered-experimental-input'});
const colorRoot='color:frozen:root',colorView='color:frozen-carriers';
append('entities',editorialEntity(colorRoot,'Frozen color states and five candidate coordinate carriers','experimental-carrier-registry',colorSrc,'Color-Carriers-FROZEN-v1'));
append('views',{id:colorView,label:'Color — twelve frozen states / five candidate carriers',roots:[colorRoot],witnessIds:['Color-Carriers-FROZEN-v1'],coverage:{stateCount:12,carrierCount:5,uniqueGlobalVortexOrientation:false}});
for(const e of upper.color.fixedStates){
 append('entities',{...e,aliases:[],tradition:'Frozen linear-light sRGB experimental carrier',witnessId:'Color-Carriers-FROZEN-v1',position:{...blank,sequence:e.nativeOrdinalZeroBased},sourceRefs:[colorSrc],exceptions:['A display mixture is not a uniquely identified spectral wavelength, musical frequency or universal generation.'],assertionLayer:'recovered-experimental-input',globalSunnyAddress:null});
 append('relationships',{id:'systems:color:'+e.id,source:colorRoot,target:e.id,type:'has-frozen-mixture-state',viewIds:[colorView],sourceRefs:[colorSrc],assertionLayer:'recovered-experimental-input'});
}
const checked=validateHierarchyAtlas(graph);assert.equal(checked.valid,true,JSON.stringify(checked.errors.slice(0,30)));
// Every original occurrence survives byte-for-byte as a record; extras do not elect identities.
for(const kind of ['entities','relationships','views'])for(const e of original[kind])assert.deepEqual(maps[kind].get(e.id),e);
for(const binding of bindings)assert.equal(sha(read(binding.path)),binding.sha256,'Input changed during integration');
graph.schema='sunny.hierarchy-atlas-combined.v2';graph.generatedAt=new Date().toISOString();graph.census=hierarchyCensus(graph);
graph.nativeSystemIntegration={baseline:{path:baseline,sha256:sha(read(baseline))},inputs:bindings,code:{path:'scripts/integrate_system_atlas.mjs',sha256:sha(read('scripts/integrate_system_atlas.mjs'))},preservedOriginalCounts:{entities:original.entities.length,relationships:original.relationships.length,views:original.views.length},globalAlignmentComplete:false,layerBoundary:'Native addresses, construction depth, register, chronology, manuscript order and command remain different typed frames.'};
fs.writeFileSync(at(graphPath),JSON.stringify(graph,null,2)+'\n');
const report={status:'passed',exit_code:0,generatedAt:graph.generatedAt,sha256:sha(read(graphPath)),entities:graph.entities.length,relationships:graph.relationships.length,views:graph.views.length,sources:graph.sources.length,preserved:graph.nativeSystemIntegration.preservedOriginalCounts,generatedMembershipSlots:graph.census.generatedMembershipSlots,fullMissionComplete:false};
fs.writeFileSync(at('docs/evidence/native-system-integration.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
