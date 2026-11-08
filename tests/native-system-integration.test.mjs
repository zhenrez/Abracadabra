/** Independent preservation and source-scope audit, without electing a SUNNY orientation. */
import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';import {createHash} from 'node:crypto';
const root=fileURLToPath(new URL('../',import.meta.url)),at=p=>path.isAbsolute(p)?p:path.join(root,p),read=p=>fs.readFileSync(at(p)),load=p=>JSON.parse(read(p)),sha=b=>createHash('sha256').update(b).digest('hex');
const graphPath='state/reconstruction/hierarchy-atlas-combined.json',reportPath='docs/evidence/native-system-independent-audit.json';
test('all integrated native systems preserve their source records, declared units and unresolved global assignments',()=>{
 const graphRaw=read(graphPath),g=JSON.parse(graphRaw),integration=g.nativeSystemIntegration;
 const baseline=load(integration.baseline.path),names=['indian-hierarchy','western-expanded','chinese-expanded','native-class-constructors','biblical-genealogies','upper-legion-color-constraints'];
 const modules=Object.fromEntries(names.map(n=>[n,load('state/reconstruction/'+n+'.json')]));
 const maps=Object.fromEntries(['sources','entities','relationships','views'].map(k=>[k,new Map(g[k].map(e=>[e.id,e]))]));
 const checks=[];const check=(name,fn)=>{try{const details=fn();checks.push({name,status:'passed',details:details??{}});}catch(e){checks.push({name,status:'failed',details:{error:e.message}});}};
 check('All six integration module bindings, baseline and integration code match current bytes',()=>{
  assert.equal(sha(read(integration.baseline.path)),integration.baseline.sha256);assert.equal(integration.inputs.length,6);
  for(const b of integration.inputs){const raw=read(b.path);assert.equal(sha(raw),b.sha256,b.path);assert.equal(raw.length,b.bytes);}
  assert.equal(sha(read(integration.code.path)),integration.code.sha256);return {modules:6};
 });
 check('Every baseline source/entity/relation/view survives exactly',()=>{
  const counts={};for(const kind of Object.keys(maps)){for(const e of baseline[kind])assert.deepEqual(maps[kind].get(e.id),e,e.id);counts[kind]=baseline[kind].length;}return counts;
 });
 check('All four native graph modules preserve exact source/entity/relation/view semantics',()=>{
  const counts={};for(const name of names.slice(0,4)){const m=modules[name];counts[name]={entities:m.entities.length,relationships:m.relationships.length,views:m.views.length};
   for(const kind of Object.keys(maps))for(const e of m[kind]){
    if(kind==='sources'){const versions=[maps.sources.get(e.id),...(g.sourceRegistryVariants??[]).filter(v=>v.sourceId===e.id).map(v=>v.record)];assert.ok(versions.some(v=>JSON.stringify(v)===JSON.stringify(e)),name+': '+e.id);}
    else assert.deepEqual(maps[kind].get(e.id),e,name+': '+e.id);
   }
  }return counts;
 });
 check('IDs are unique and every source, endpoint, view, parent and root resolves',()=>{
  for(const kind of Object.keys(maps))assert.equal(maps[kind].size,g[kind].length,kind);
  for(const e of g.entities){assert.ok(e.sourceRefs?.length,e.id);for(const s of e.sourceRefs)assert.ok(maps.sources.has(s),s);if(e.parent!==null&&e.parent!==undefined)assert.ok(typeof e.parent==='string'&&e.parent.length>0&&maps.entities.has(e.parent),e.id);}
  for(const r of g.relationships){assert.ok(maps.entities.has(r.source)&&maps.entities.has(r.target),r.id);assert.ok(r.sourceRefs?.length&&r.viewIds?.length,r.id);for(const id of r.sourceRefs)assert.ok(maps.sources.has(id),id);for(const id of r.viewIds)assert.ok(maps.views.has(id),id);assert.ok(r.type&&r.assertionLayer,r.id);}
  for(const v of g.views){assert.ok(v.roots?.length,v.id);for(const id of v.roots)assert.ok(maps.entities.has(id),id);}return {entities:g.entities.length,relationships:g.relationships.length,views:g.views.length};
 });
 check('Every registered source digest binds the actual source bytes',()=>{
  let checked=0;for(const s of g.sources)if(s.path&&s.sha256){assert.equal(sha(read(s.path)),s.sha256,s.id);checked++;}return {sourceFilesChecked:checked};
 });
 check('Indian2520 note addresses retain degree/mela ancestry and all210 direct Aditya conditions',()=>{
  const m=modules['indian-hierarchy'],notes=m.entities.filter(e=>e.unit==='registered-mela-svara-occurrence');assert.equal(notes.length,2520);
  for(const e of notes){const p=maps.entities.get(e.parent);assert.equal(p.unit,'mela-qualified-svara-membership',e.id);assert.equal(e.absoluteHz,null);assert.equal(e.registeredNote.absoluteHz,null);assert.equal(e.physicalOccurrence,false);assert.equal(e.globalAddress.generationClass,null);assert.ok(e.nativeCoordinates.sthayi);assert.ok(e.nativeCoordinates.melaAddress>=1&&e.nativeCoordinates.melaAddress<=72);}
  assert.equal(notes.filter(e=>e.sourceReadingCondition!==null).length,210);const c=m.census.boundedNoteInstrumentReconciliation;assert.equal(c.sumOfDeclaredLowerUnits,2556);assert.equal(c.unitsAreHeterogeneous,true);assert.equal(m.fullMissionComplete,false);return {registeredNotes:2520,instrumentTypes:36,conditionalAdityaNotes:210};
 });
 check('Western registered degrees, range profiles and MIDI sound addresses remain distinct',()=>{
  const m=modules['western-expanded'],count=u=>m.entities.filter(e=>e.unit===u),notes=count('registered-scale-degree-occurrence');assert.equal(notes.length,2464);
  assert.equal(count('source-visible-range-profile').length,31);assert.equal(count('gm1-sound-program').length,128);assert.equal(count('gm1-percussion-sound-address').length,47);
  for(const e of notes){assert.ok(maps.entities.has(e.parent));assert.equal(e.physicalOccurrence,false);assert.equal(e.globalAddress.generationClass,null);assert.ok(e.nativeCoordinates.midiKey>=21&&e.nativeCoordinates.midiKey<=108);}
  for(const e of count('gm1-sound-program'))assert.equal(e.physicalInstrumentTypeIdentity,null);
  for(const e of count('source-visible-range-profile')){assert.equal(e.rangeLow,null);assert.equal(e.rangeHigh,null);}
  assert.equal(m.census.declaredLowerUnits.sum,2670);assert.equal(m.census.unitsAreHeterogeneous,true);assert.equal(m.wholeMusicalSystemsComplete,false);return {registeredDegrees:2464,profiles:31,programs:128,percussionAddresses:47};
 });
 check('Chinese source-context units reconcile independently from total structural records',()=>{
  const m=modules['chinese-expanded'],actual={};for(const e of m.entities)actual[e.unit]=(actual[e.unit]??0)+1;assert.deepEqual(actual,m.unitCensus);
  const c=m.censusReconciliation;assert.equal(c.entitiesIncludingClassifiersAndContextNodes,m.entities.length);assert.ok(c.noteMembershipUnits<=m.entities.length);
  assert.equal(actual['JingFang-witness-named-lu-standard'],60);assert.equal(actual['JingFang-explicit-gong-shang-zhi-context'],58);assert.equal(actual['source-explicit-context-tone-membership'],174);assert.equal(actual['mode-qualified-tone-membership-occurrence'],300);
  assert.ok(c.noteMembershipMeaning.toLowerCase().includes('not'));if(c.noteMembershipUnits<2500)assert.equal(c.targetMet,false);return {totalRecords:m.entities.length,declaredLowerContextUnits:c.noteMembershipUnits,targetMet:c.targetMet,nativeClassExceptionsRetained:true};
 });
 check('Bible source fields and primary/curated/received qualifications survive integration',()=>{
  const m=modules['biblical-genealogies'];for(const e of m.entities){const got=maps.entities.get(e.id);for(const [k,v]of Object.entries(e))assert.deepEqual(got[k],v,e.id+': '+k);}
  for(const r of m.relationships){const got=maps.relationships.get(r.id);for(const [k,v]of Object.entries(r))assert.deepEqual(got[k],v,r.id+': '+k);}
  assert.equal(m.originalEditionGlobalProjectionAssertions,0);assert.equal(m.ancientInkIndependentlyInspectedAssertions,0);assert.equal(m.wholeBibleGenealogyScientificallyComplete,false);assert.equal(m.historicalOrientationSelected,false);return {entities:m.entities.length,relations:m.relationships.length};
 });
 check('All49 primary and every declared received Bible edge belong to the declared family view',()=>{
  const m=modules['biblical-genealogies'],details=[];let primary=0;
  for(const v of m.views){const primaryIds=v.originalEditionParentageAssertions.map(x=>typeof x==='string'?x:x.id);for(const id of [...v.receivedWitnessRelationIds,...primaryIds])assert.ok(maps.relationships.get(id)?.viewIds.includes(v.id),id);primary+=primaryIds.length;assert.equal(maps.views.get(v.id).coverage.primaryAssertions,primaryIds.length);details.push({viewId:v.id,primaryAssertions:primaryIds.length});}
  assert.equal(primary,49);assert.deepEqual(details.map(x=>x.primaryAssertions),[16,17,16]);return {families:details,totalPrimaryAssertions:primary};
 });
 check('SP remains a Pentateuch comparison without invented New Testament witness scope',()=>{
  const v=modules['biblical-genealogies'].views.find(v=>v.id==='bible:witness-family:SP');assert.equal(v.outsideWitnessScope.NewTestament,'not witnessed by SP');assert.equal(v.gospelComparisonChainIds.length,0);assert.equal(v.completeOriginalWitnessGenealogy,false);
  for(const r of g.relationships.filter(r=>r.viewIds.includes(v.id)))assert.ok(!r.verseRefs?.some(x=>/^(Matt|Luke|Mark|John)\./.test(x)),r.id);return {SPNewTestamentWitness:false};
 });
 check('All12 frozen colors retain five carriers without wavelength/note/global identity promotion',()=>{
  const states=modules['upper-legion-color-constraints'].color.fixedStates;assert.equal(states.length,12);for(const e of states){const got=maps.entities.get(e.id);for(const [k,v]of Object.entries(e))assert.deepEqual(got[k],v,e.id+': '+k);assert.equal(Object.keys(got.carrierPositions).length,5);assert.equal(got.musicalAbsoluteHz,null);assert.equal(got.globalGenerationalClass,null);assert.equal(got.globalW72Phase,null);assert.equal(got.globalSunnyAddress,null);}return {states:12,carriersEach:5};
 });
 check('Known construction depths remain native frames and no global alignment is elected',()=>{
  const known=g.entities.filter(e=>e.position.generation!==null);assert.equal(known.length,11643);assert.ok(known.every(e=>e.witnessId==='Oct23-five-direction-definition'&&e.generationFrame.includes('not biological')));
  for(const name of names.slice(0,3))assert.ok(modules[name].entities.every(e=>e.position.generation===null));assert.equal(integration.globalAlignmentComplete,false);assert.equal(g.globalOrientationSelected,false);return {qualifiedConstructionDepthRecords:known.length};
 });
 check('Upper records and normalized-text coordinates remain recoverable without changing baseline sources',()=>{
  const m=modules['upper-legion-color-constraints'];for(const e of m.proposedGraphExtension.entities)assert.deepEqual(maps.entities.get(e.id),e);
  for(const [i,r]of m.proposedGraphExtension.relationships.entries()){const got=maps.relationships.get(r.id??'systems:goetic-upper:'+i);for(const [k,v]of Object.entries(r))assert.deepEqual(got[k],v);}
  for(const s of m.primaryTextPackets){const versions=[maps.sources.get(s.id),...(g.sourceRegistryVariants??[]).filter(x=>x.sourceId===s.id).map(x=>x.record)];assert.ok(versions.some(v=>Object.entries(s).every(([k,x])=>JSON.stringify(v?.[k])===JSON.stringify(x))),s.id);}
  const slots=g.entities.filter(e=>e.unit==='catalogue-attributed-legion-membership-slot');assert.equal(slots.length,7911);assert.equal(g.census.generatedMembershipSlots,slots.length);assert.equal(g.census.entityRecords,g.entities.length-slots.length);
  return {upperEntities:m.proposedGraphExtension.entities.length,upperRelationships:m.proposedGraphExtension.relationships.length,normalizationPackets:m.primaryTextPackets.length,anonymousMembershipSlots:slots.length};
 });
 assert.equal(sha(read(graphPath)),sha(graphRaw),'Graph changed while audit ran');
 const report={schema:'sunny.native-system-independent-audit.v2',status:checks.every(c=>c.status==='passed')?'passed':'failed',checkedAt:new Date().toISOString(),inputGraphPath:graphPath,inputGraphSha256:sha(graphRaw),auditCodeBinding:{path:'tests/native-system-integration.test.mjs',sha256:sha(read('tests/native-system-integration.test.mjs'))},inputBindings:integration.inputs,baselineBinding:integration.baseline,actualCounts:Object.fromEntries(Object.keys(maps).map(k=>[k,g[k].length])),checks,findings:checks.filter(c=>c.status==='failed'),retainedEarlierAudits:[],execution:{command:'node --test tests/native-system-integration.test.mjs',expectedExitCode:checks.every(c=>c.status==='passed')?0:1,processExitEvidence:'Exact process exit is recorded by the invoking tool; this report does not self-certify its shell exit'},scope:'Independent source/record/typing preservation audit. No mathematical rerun, source-authenticity claim, ancient-ink collation, physical law or full SUNNY completion.',pluginUse:{Supermemory:'Actual continuity search succeeded before audit; current checks use actual files, not historical memory counts.',Jev:'Preserved actual local receipt64 directs the parent source-class task; this deterministic audit is not a fresh model inference.',SuperJevHook:'Unavailable status reported; no hook execution success inferred.'},sourceMathOrIntegrationCodeEdited:false};
 if(fs.existsSync(at(reportPath))){const previous=read(reportPath),old=JSON.parse(previous);const preserved='docs/evidence/native-system-independent-audit.previous-'+sha(previous)+'.json';if(!fs.existsSync(at(preserved)))fs.writeFileSync(at(preserved),previous,{flag:'wx'});report.retainedEarlierAudits=[...(old.retainedEarlierAudits??[]),{path:preserved,sha256:sha(previous),status:old.status,graphSha256:old.inputGraphSha256}];}
 fs.writeFileSync(at(reportPath),JSON.stringify(report,null,2)+'\n');
 fs.writeFileSync(at('docs/evidence/native-system-independent-audit.md'),'# Independent native-system integration audit\n\nStatus: **'+report.status+'**. Graph SHA256: `'+report.inputGraphSha256+'`.\n\n'+checks.map(c=>'- '+c.status+': '+c.name+(c.status==='failed'?' — '+c.details.error:'')).join('\n')+'\n\nPrevious audit bytes and failures remain referenced by hash in the JSON. This checks source/record preservation and declared scope, not historical truth or scientific completion. Actual command: `'+report.execution.command+'`.\n');
 const concise=report.findings.map(c=>({name:c.name,error:c.details.error.split('\n')[0]}));console.log(JSON.stringify({status:report.status,groups:checks.length,failures:concise,graphSha256:report.inputGraphSha256}));assert.equal(report.status,'passed',JSON.stringify(concise));
});
