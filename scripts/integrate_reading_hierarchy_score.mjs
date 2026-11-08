/** Add identified reading units to the shared atlas and score; preserve every prior view. */
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';import assert from 'node:assert/strict';
import {validateHierarchyAtlas,hierarchyCensus} from '../dist/hierarchy.js';
import {createNativeExecutor} from '../dist/native-operators.js';import {executeMasterScore} from '../dist/score.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>fs.readFileSync(path.join(root,p)),load=p=>JSON.parse(read(p));
const sha=raw=>createHash('sha256').update(raw).digest('hex');
const preserve=p=>{const raw=read(p),digest=sha(raw),target='data/raw/reconstruction-integrations/'+digest+'/'+path.basename(p);
 fs.mkdirSync(path.dirname(path.join(root,target)),{recursive:true});if(!fs.existsSync(path.join(root,target)))fs.writeFileSync(path.join(root,target),raw);else assert.ok(read(target).equals(raw));
 return {sourcePath:p,snapshotPath:target,sha256:digest,bytes:raw.length};};
const unit=load('state/reconstruction/reading-operations.json'),viewId='reading:molin2020',sid='public:molin2020-reading-text';
const graphPath='state/reconstruction/hierarchy-atlas-combined.json',scorePath='state/reconstruction/master-score.json';
const graphBefore=preserve(graphPath),scoreBefore=preserve(scorePath);
const graph=load(graphPath),oldEntityIds=new Set(unit.census.entities.map(e=>e.id));
graph.entities=graph.entities.filter(e=>!oldEntityIds.has(e.id));graph.relationships=graph.relationships.filter(r=>!r.id.startsWith('reading:molin2020:rel:'));
graph.views=graph.views.filter(v=>v.id!==viewId);graph.sources=graph.sources.filter(s=>s.id!==sid);
graph.sources.push({id:sid,title:'Molin2020 §2.4: comparative pausal/contextual reading examples',
 path:'state/delivery-2026-11-07/history-discriminator/exa-loc-fetch.json',sha256:sha(read('state/delivery-2026-11-07/history-discriminator/exa-loc-fetch.json')),
 kind:'connector-rendered-primary-publication',sourceRole:'published-source-report',
 boundary:'Connector text and conditional comparative reconstructions; no original ink, measured sound or specimen chronology.'});
for(const item of unit.census.entities){
 const isRoot=item.id==='molin:section2.4',isExample=item.id==='molin:example7'||item.id==='molin:example8';
 graph.entities.push({...item,aliases:[...new Set([item.nativeName,item.ipa,item.locus].filter(Boolean))],tradition:'Babylonian reading comparanda as interpreted by Molin2020',
  witnessId:'Molin2020-section2.4',sourceRefs:[sid],
  position:{generation:null,sequence:item.ordinalOneBased??null,cyclicCoordinate:null,orientation:null},
  exceptions:[...(isRoot?['Four stated source forms are not reconciled by counting the four comparative IPA records.']:[]),
    'Sequence is a source/analysis address; it is not a global genealogy, acoustic clock or pitch.'],
  assertionLayer:isRoot||isExample?'source-assertion':item.unit==='Published comparative pronunciation'?'source-reconstruction':'analyst-derived-notation-segmentation',
  ...(isRoot?{statedExtent:{value:4,unit:'source-described-forms',reconciled:false}}:{})});
}
unit.census.relationships.forEach((r,i)=>graph.relationships.push({id:'reading:molin2020:rel:'+i,source:r.from,target:r.to,type:r.kind,
 viewIds:[viewId],sourceRefs:[sid],assertionLayer:'source-qualified-analysis'}));
graph.views.push({id:viewId,label:'Molin2020: spelled examples, comparative readings and syllable occurrences',roots:['molin:section2.4'],
 witnessIds:['Molin2020-section2.4'],coverage:{displayedExamples:2,comparativeReadings:4,analysedSyllables:12,sourceStatedForms:4,wholeExtentReconciled:false,universalComplete:false}});
graph.census=hierarchyCensus(graph);assert.equal(graph.census.generatedMembershipSlots,7911);
const graphCheck=validateHierarchyAtlas(graph);assert.equal(graphCheck.valid,true,JSON.stringify(graphCheck.errors));
graph.readingExtension={module:'state/reconstruction/reading-operations.json',jevReceipt:unit.jevReceipt,priorGraph:graphBefore,
 sourceUnitBoundary:unit.census.boundary};
fs.writeFileSync(path.join(root,graphPath),JSON.stringify(graph,null,2)+'\n');

const score=load(scorePath),prefix='reading:molin:';
const priorViews=score.program.views.filter(v=>!v.id.startsWith(prefix));
const K=(value,refs)=>({status:'known',value,sourceRefs:refs}),U=(missing,refs)=>({status:'unknown',missing,sourceRefs:refs});
const refs=['state/reconstruction/reading-operations.json'];
const additions=unit.forms.map(form=>{
 const id='reading:'+form.id;
 const participants=form.syllables.map(s=>({id:form.id+':syllable'+s.ordinalOneBased,
  label:s.onset+s.nucleus+s.lengthMark,sourceRefs:refs,role:K('Syllable in a source-reconstructed comparative reading',refs),
  instrument:U('No performer or instrument supplied.',refs),note:U('A phonetic syllable is not assigned a musical note.',refs),
  register:U('No musical register supplied.',refs),onset:U('Ordinal notation supplies no measured performance onset.',refs),
  duration:U('IPA quantity supplies no measured duration or musical beat ratio.',refs),
  coordinates:{ADR:K({sourceFormId:form.id,syllableOrdinalOneBased:s.ordinalOneBased},refs),
   FUNC:K({comparativeRole:form.role,phoneticNotation:s,sourceRole:form.evidenceRole},refs),
   GEN:U('No generational class is supplied by this source.',refs),TIME:U('No audible or historical clock assigned.',refs)}}));
 const events=participants.map(p=>({id:p.id+':event',participantId:p.id,kind:'source-notation syllable stage',
  at:U('No metric entrance supplied.',refs),sourceRefs:refs}));
 return {id,system:'Molin2020 '+form.parent+' '+form.role,condition:form.evidenceRole+'; notation order and reconstructed phones only, no measured performance or note assignment.',
  sourceRefs:refs,participants,events,order:events.slice(0,-1).map((e,i)=>({id:id+':order:'+i,before:e.id,after:events[i+1].id,
   relation:'next syllable in the declared comparative notation, not a timed musical entrance',sourceRefs:refs})),transitions:[]};
});
score.program.views=[...priorViews,...additions];score.program.sourceRefs=[...new Set([...score.program.sourceRefs,...refs])];
const nativeInfo=load('state/reconstruction/native-execution.json').source;
const native=createNativeExecutor(read(nativeInfo.path),nativeInfo.sourceId),execution=executeMasterScore(score.program,native);
assert.ok(execution.views.every(v=>!v.checks.some(c=>c.verdict==='fail')));
for(const v of priorViews)assert.deepEqual(score.program.views.find(x=>x.id===v.id),v);
score.execution=execution;score.scope='15 source-qualified conditional views, including4untimed comparative-reading annotations; no complete universal master score.';
score.counts={...score.counts,views:score.program.views.length,participants:score.program.views.reduce((n,v)=>n+v.participants.length,0),
 participantMembershipOccurrences:score.program.views.reduce((n,v)=>n+v.participants.length,0),
 distinctParticipantIds:new Set(score.program.views.flatMap(v=>v.participants.map(p=>p.id))).size,readingAnnotationViews:additions.length};
score.readingExtension={module:'state/reconstruction/reading-operations.json',jevReceipt:unit.jevReceipt,priorScore:scoreBefore,
 viewIds:additions.map(v=>v.id),boundary:unit.scoreAnnotationBoundary};
score.unknowns=[...(score.unknowns??[]).filter(x=>!String(x.viewId??'').startsWith(prefix)),
 ...execution.views.filter(v=>v.viewId.startsWith(prefix)).flatMap(v=>v.checks.filter(c=>c.verdict==='unknown').map(c=>({viewId:v.viewId,...c})))];
fs.writeFileSync(path.join(root,scorePath),JSON.stringify(score,null,2)+'\n');
console.log(JSON.stringify({status:'integrated',exit_code:0,graphRecords:graph.entities.length,relationships:graph.relationships.length,
 hierarchyViews:graph.views.length,generatedMembershipSlots:graph.census.generatedMembershipSlots,priorScoreViewsPreserved:priorViews.length,
 newUntimedScoreViews:additions.length,scoreViews:score.counts.views,sourceExtentReconciled:false,fullMissionComplete:false}));
