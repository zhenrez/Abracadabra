import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=p=>fs.readFileSync(path.join(root,p));
const load=p=>JSON.parse(read(p));
const sha=p=>createHash('sha256').update(read(p)).digest('hex');
const evidence='state/delivery-2026-11-07/pausal-operations/integration-review';

test('reading extension preserves all prior graph and score records and source-qualified unknowns',()=>{
 const graphPath='state/reconstruction/hierarchy-atlas-combined.json',scorePath='state/reconstruction/master-score.json',unitPath='state/reconstruction/reading-operations.json';
 const graph=load(graphPath),score=load(scorePath),unit=load(unitPath);
 const recoverBaseline=(current,field,count,target)=>{
   let ref=current.readingExtension[field];const chain=[],seen=new Set();
   while(true){
     assert.ok(!seen.has(ref.sha256),'snapshot reference cycle');seen.add(ref.sha256);
     assert.equal(sha(ref.snapshotPath),ref.sha256,'preserved snapshot hash');
     const prior=load(ref.snapshotPath);chain.push({...ref,recordCount:count(prior)});
     if(count(prior)===target)return {prior,ref,chain};
     assert.ok(count(prior)>target&&prior.readingExtension?.[field],'original baseline not reachable');
     ref=prior.readingExtension[field];
   }
 };
 const gb=recoverBaseline(graph,'priorGraph',g=>g.entities.length,9493),sb=recoverBaseline(score,'priorScore',s=>s.program.views.length,11);
 const priorGraphRef=gb.ref,priorScoreRef=sb.ref,oldGraph=gb.prior,oldScore=sb.prior;
 assert.equal(oldGraph.entities.length,9493);assert.equal(oldGraph.relationships.length,10233);assert.equal(oldGraph.views.length,22);
 assert.equal(oldScore.program.views.length,11);
 const entities=new Map(graph.entities.map(x=>[x.id,x])),relationships=new Map(graph.relationships.map(x=>[x.id,x]));
 assert.equal(entities.size,graph.entities.length);assert.equal(relationships.size,graph.relationships.length);
 for(const x of oldGraph.entities)assert.deepEqual(entities.get(x.id),x,'preserve entity '+x.id);
 for(const x of oldGraph.relationships)assert.deepEqual(relationships.get(x.id),x,'preserve relationship '+x.id);
 for(const x of oldGraph.views)assert.deepEqual(graph.views.find(v=>v.id===x.id),x,'preserve hierarchy view '+x.id);
 for(const x of oldScore.program.views)assert.deepEqual(score.program.views.find(v=>v.id===x.id),x,'preserve score view '+x.id);
 for(const x of oldScore.execution.views)assert.deepEqual(score.execution.views.find(v=>v.viewId===x.viewId),x,'preserve score execution '+x.viewId);
 const oldIds=new Set(oldGraph.entities.map(x=>x.id)),readingIds=new Set(unit.census.entities.map(x=>x.id)),newEntities=graph.entities.filter(x=>!oldIds.has(x.id)&&readingIds.has(x.id));
 const oldRelIds=new Set(oldGraph.relationships.map(x=>x.id)),newRelationships=graph.relationships.filter(x=>!oldRelIds.has(x.id)&&x.viewIds.includes('reading:molin2020'));
 assert.ok(graph.entities.length>=9512);assert.ok(graph.relationships.length>=10251);assert.ok(graph.views.length>=23);assert.equal(score.program.views.length,15);
 assert.equal(newEntities.length,19);assert.equal(newRelationships.length,18);
 assert.deepEqual(new Set(newEntities.map(x=>x.id)),new Set(unit.census.entities.map(x=>x.id)));
 const sourceIds=new Set(graph.sources.map(s=>s.id));
 for(const x of [...newEntities,...newRelationships])for(const ref of x.sourceRefs)assert.ok(sourceIds.has(ref),'source reference resolves '+ref);
 for(const rel of newRelationships){assert.ok(entities.has(rel.source));assert.ok(entities.has(rel.target));assert.deepEqual(rel.viewIds,['reading:molin2020']);}
 const rootId='molin:section2.4',incoming=new Map();
 for(const rel of newRelationships){const inc=incoming.get(rel.target)??[];inc.push(rel.source);incoming.set(rel.target,inc);}
 for(const x of newEntities){
   assert.equal(incoming.get(x.id)?.length??0,x.id===rootId?0:1,'single declared parent '+x.id);
   const visited=new Set();let cursor=x.id;
   while(cursor!==rootId){assert.ok(!visited.has(cursor),'parent cycle');visited.add(cursor);cursor=incoming.get(cursor)[0];}
 }
 const newViews=score.program.views.filter(v=>!oldScore.program.views.some(x=>x.id===v.id));
 assert.equal(newViews.length,4);let syllables=0;const syllableIds=[];
 for(const form of unit.forms){
   const v=newViews.find(v=>v.id==='reading:'+form.id);assert.ok(v);assert.equal(v.participants.length,3);assert.equal(v.events.length,3);assert.equal(v.order.length,2);
   assert.equal(form.measured,false);assert.equal(form.absoluteHz,null);assert.equal(form.audibleDuration,null);assert.equal(form.pitchClass,null);
   for(const [index,p] of v.participants.entries()){
     const sid=form.id+':syllable'+(index+1),entity=entities.get(sid),syllable=form.syllables[index];
     assert.equal(p.id,sid);assert.ok(entity);assert.equal(incoming.get(sid)[0],form.id);
     assert.deepEqual(p.coordinates.FUNC.value.phoneticNotation,syllable);
     assert.deepEqual(p.coordinates.ADR.value,{sourceFormId:form.id,syllableOrdinalOneBased:index+1});
     assert.equal(p.label,syllable.onset+syllable.nucleus+syllable.lengthMark);
     for(const field of ['instrument','note','register','onset','duration']){assert.equal(p[field].status,'unknown');assert.ok(!Object.hasOwn(p[field],'value'));}
     for(const field of ['GEN','TIME']){assert.equal(p.coordinates[field].status,'unknown');assert.ok(!Object.hasOwn(p.coordinates[field],'value'));}
     const event=v.events.find(e=>e.participantId===sid);assert.ok(event);assert.equal(event.at.status,'unknown');assert.ok(!Object.hasOwn(event.at,'value'));
     assert.equal(entity.position.generation,null);assert.equal(entity.position.cyclicCoordinate,null);assert.equal(entity.position.orientation,null);
     syllables++;syllableIds.push(sid);
   }
 }
 assert.equal(syllables,12);assert.equal(new Set(syllableIds).size,12);
 assert.equal(entities.get(rootId).statedExtent.value,4);assert.equal(entities.get(rootId).statedExtent.reconciled,false);
 assert.equal(graph.views.find(v=>v.id==='reading:molin2020').coverage.wholeExtentReconciled,false);
 assert.equal(unit.originalSoundSystemRecovered,false);assert.equal(unit.historicalOperatorSelected,false);assert.equal(unit.fullMissionComplete,false);
 const report={schema:'sunny.independent-reading-integration-review.v1',checkedAt:new Date().toISOString(),status:'passed',exit_code:0,
  hashes:{[graphPath]:sha(graphPath),[scorePath]:sha(scorePath),[unitPath]:sha(unitPath),'tests/reading-integration.test.mjs':sha('tests/reading-integration.test.mjs'),[priorGraphRef.snapshotPath]:priorGraphRef.sha256,[priorScoreRef.snapshotPath]:priorScoreRef.sha256},
  preserved:{entities:9493,relationships:10233,hierarchyViews:22,scoreViews:11,priorScoreExecutions:oldScore.execution.views.length},
  baselineRecovery:{graph:gb.chain,score:sb.chain,boundary:'Replay preserves a hash-linked prior-state chain. The immediate prior snapshot may already contain the extension; equality checks use the recovered original9493/11baseline.'},
  added:{entities:19,relationships:18,hierarchyViews:1,untimedReadingViews:4,individuallyAddressedSyllables:12},
  sharedSyllableIds:syllableIds,allNewNodesRootReachable:true,parentsAndScoreIdsMatch:true,unknownAcousticsAndTimingPreserved:true,
  sourceExtentReconciled:false,fullMissionComplete:false,
  guardUse:{plugin:'Supermemory',operation:'search_memory',success:true,scope:'Retrieved continuity during this independent review; not historical certification.'},
  boundary:'Snapshot/record equality, identified parentage and unknown preservation only. No original ink, phonetic intention, clock, musical assignment or global alignment certified.'};
 fs.mkdirSync(path.join(root,evidence),{recursive:true});fs.writeFileSync(path.join(root,evidence,'result.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({status:'passed',exit_code:0,preserved:report.preserved,added:report.added,unknownAcousticsAndTimingPreserved:true}));
});
