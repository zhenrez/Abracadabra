/** Populate only recovered score views. No clock, instrument, Hz or ontology completion. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {createNativeExecutor} from '../dist/native-operators.js';
import {executeMasterScore} from '../dist/score.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const raw=p=>fs.readFileSync(path.resolve(root,p));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const load=p=>JSON.parse(raw(p).toString('utf8').replace(/^\uFEFF/,''));
const decision=load('docs/evidence/master-score-design-superjev.json');
assert.equal(decision.answers.representation.winner,'typed_source_views');
const music=load('state/reconstruction/music-geometry.json'),gen=load('state/reconstruction/generational-constraints.json');
const nativeRecord=load('state/reconstruction/native-execution.json').source;
const native=createNativeExecutor(raw(nativeRecord.path),nativeRecord.sourceId);
const cn=music.records.find(r=>r.id==='MG-LATEST-CHINESE-TRIAD');
const sol=music.records.find(r=>r.id==='MG-SOL-PITCH-LOCK');
assert.ok(cn&&sol);
const bindings=[];
for(const record of [cn,sol])for(const e of record.evidence){
  const source=music.source_catalog.find(s=>s.id===e.source_id);assert.ok(source);
  const bytes=fs.readFileSync(source.path);assert.equal(sha(bytes),e.source_sha256);
  const quote=Array.from(bytes.toString('utf8')).slice(e.char_start,e.char_end).join('');
  assert.equal(quote,e.quote);assert.equal(sha(Buffer.from(quote,'utf8')),e.quote_sha256);
  bindings.push({recordId:record.id,sourceId:e.source_id,sourcePath:source.path,sha256:e.source_sha256,locator:e.locator,quoteSha256:e.quote_sha256});
}
for(const id of ['cainan_stage_witnesses','cainan_macro_transport','generation_address_distinction']){
  const e=gen.sources.find(s=>s.id===id);assert.ok(e);
  assert.equal(sha(fs.readFileSync(e.source_path)),e.source_sha256);
  assert.equal(sha(Buffer.from(e.exact_quote,'utf8')),e.quote_sha256);
  bindings.push({recordId:id,sourceId:e.source_id,messageId:e.message_id,sourcePath:e.source_path,sha256:e.source_sha256,locator:e.locator,quoteSha256:e.quote_sha256});
}
const q=(n,d=1)=>({numerator:String(n),denominator:String(d)});
const K=(value,sourceRefs)=>({status:'known',value,sourceRefs});
const U=(missing,sourceRefs)=>({status:'unknown',missing,sourceRefs});
const qty=(n,carrier,unit,reference,d=1)=>({value:q(n,d),dimension:carrier.includes('frequency')?'frequency':carrier==='ideal-pipe-length'?'length':carrier==='biological-descent-depth'?'count':'time',carrier,unit,reference});
const note=(label,value,sourceRefs)=>K({label,relativeFrequency:K(value,sourceRefs),absoluteHz:U('No absolute acoustic frequency or physical calibration is supplied.',sourceRefs)},sourceRefs);
const coords=(refs,GEN,TIME,ADR)=>({GEN:GEN??U('No generation/class coordinate is assigned by this source view.',refs),TIME:TIME??U('No performance clock or chronological date is assigned.',refs),ADR:ADR??U('No unique global address or justified clock type is assigned.',refs)});
const cnRefs=cn.source_refs,cnFrame='Chinese ideal reciprocal construction; illustrative base length81';
const length=n=>qty(n,'ideal-pipe-length','illustrative-length-unit',cnFrame);
const freq=n=>qty(n,'relative-pitch-frequency','relative-frequency-unit',cnFrame);
const chinese={id:'chinese-native-construction',system:'Retained Chinese pitch-pipe construction',condition:'Ideal reciprocal length/frequency model; construction order differs from seasonal order and is not an audible event duration.',sourceRefs:cnRefs,
  participants:['Huangzhong','Linzhong','Taicu'].map((label,i)=>({id:'cn:'+i,label,sourceRefs:cnRefs,
    role:K('Pitch standard in the explicitly ordered native construction',cnRefs),instrument:U('Performance instrumentation and orchestration are unassigned; the represented object is an ideal pitch-pipe standard.',cnRefs),
    note:note(label,freq([8,12,9][i]),cnRefs),register:U('No absolute acoustic register is assigned.',cnRefs),
    onset:U('Construction order supplies no audible onset or elapsed construction time.',cnRefs),duration:U('No audio duration or construction duration is supplied.',cnRefs),
    coordinates:coords(cnRefs,undefined,undefined,K({constructionIndex:i,length:length([81,54,72][i])},cnRefs))})),
  events:[0,1,2].map(i=>({id:'cn:event:'+i,participantId:'cn:'+i,kind:'construction stage',at:U('No metric construction clock is supplied.',cnRefs),sourceRefs:cnRefs})),
  order:[0,1].map(i=>({id:'cn:order:'+i,before:'cn:event:'+i,after:'cn:event:'+(i+1),relation:'native construction precedes; not calendar or audio order',sourceRefs:cnRefs})),
  transitions:[
    {id:'cn:length:81-54',relation:'native length multiplication2/3',input:K(length(81),cnRefs),factor:K(q(2,3),cnRefs),expected:K(length(54),cnRefs),sourceRefs:cnRefs},
    {id:'cn:length:54-72',relation:'native length multiplication4/3',input:K(length(54),cnRefs),factor:K(q(4,3),cnRefs),expected:K(length(72),cnRefs),sourceRefs:cnRefs},
    {id:'cn:frequency:8-12',relation:'reciprocal frequency multiplication3/2',input:K(freq(8),cnRefs),factor:K(q(3,2),cnRefs),expected:K(freq(12),cnRefs),sourceRefs:cnRefs},
    {id:'cn:frequency:12-9',relation:'reciprocal frequency multiplication3/4',input:K(freq(12),cnRefs),factor:K(q(3,4),cnRefs),expected:K(freq(9),cnRefs),sourceRefs:cnRefs},
  ]};
const timeSource=gen.sources.find(s=>s.id==='cainan_stage_witnesses');
const cases=gen.constraints.find(x=>x.id==='GT-TIME-OVERLAP').witness_executions;
assert.equal(cases.length,5);
const chronological=cases.map(w=>{
  const refs=[timeSource.source_id],id='chronology:'+w.witness,reference='Arpachshad birth origin; '+w.witness+' reported chronology';
  const time=n=>qty(n,'chronological-lifetime','reported-year',reference);
  const a=w.parameters.a,b=w.parameters.b,names=w.witness.startsWith('Greek')?['Arpachshad','Cainan II','Shelah']:['Arpachshad','Shelah','Eber'];
  const pids=[0,1,2].map(i=>id+':'+['A','B','C'][i]);
  const participants=names.map((label,i)=>({id:pids[i],label,sourceRefs:refs,role:K('Genealogical participant; conditional voice'+['A','B','C'][i],refs),
    instrument:U('No audible instrument is assigned to this historical participant.',refs),
    note:note(['R(C)','C','L(C)'][i],qty([8,12,9][i],'relative-pitch-frequency','relative-frequency-unit','Declared Cainan local voicing'),refs),
    register:U('Relative8:12:9 voicing is known; absolute acoustic register is not assigned.',refs),onset:K(time([0,a,a+b][i]),refs),duration:K(time(w.lifespans[i]),refs),
    coordinates:coords(refs,K(qty(i,'biological-descent-depth','generation-step',reference+' local chain'),refs),K(time([0,a,a+b][i]),refs),undefined)}));
  const events=w.ordered_events.map(([kind,t])=>({id:id+':'+kind,participantId:pids['ABC'.indexOf(kind.at(-1))],kind,at:K(time(t),refs),sourceRefs:refs}));
  return {id,system:w.witness+' genealogical chronology',condition:w.model_condition+'; the computed intervals are chronological lifetimes, not audible sustain.',sourceRefs:refs,participants,events,
    order:events.slice(0,-1).map((e,i)=>({id:id+':order:'+i,before:e.id,after:events[i+1].id,relation:'strict source chronology under the declared experiment',sourceRefs:refs})),transitions:[]};
});
const solRefs=sol.source_refs,solFrame='Retained SOL working lock; Sophia F_upper is unit relative reference';
const sf=(n,d=1)=>qty(n,'relative-pitch-frequency','relative-frequency-unit',solFrame,d);
const sophia={id:'sophia-working-lock',system:'Retained adopted SOL relative pitch labels',condition:sol.status+'; no unique cosmological address, absoluteHz or performance chronology is inferred.',sourceRefs:solRefs,
  participants:sol.assignments.map((a,i)=>({id:'sol:'+i,label:a.referent,sourceRefs:solRefs,role:K('Referent in the source-qualified working pitch lock',solRefs),
    instrument:U('No instrument assignment is supplied by this working lock.',solRefs),note:note(a.pitch_class,[sf(1),sf(1,2),sf(3,4)][i],solRefs),register:K(a.register,solRefs),
    onset:U('Pitch relation does not supply an onset or genealogy event.',solRefs),duration:U('Pitch relation does not supply a performance duration.',solRefs),coordinates:coords(solRefs)})),
  events:[],order:[],transitions:[
    {id:'sol:octave-seam',relation:'F_upper to F_lower; relative octave descent',input:K(sf(1),solRefs),factor:K(q(1,2),solRefs),expected:K(sf(1,2),solRefs),sourceRefs:solRefs},
    {id:'sol:fifth-above',relation:'Sabaoth C_lower a pure fifth above Yaldabaoth F_lower; inverseR',input:K(sf(1,2),solRefs),factor:K(q(3,2),solRefs),expected:K(sf(3,4),solRefs),sourceRefs:solRefs},
  ]};
const levisson=load('docs/evidence/levisson-score-view.json');
const symbols=load('state/reconstruction/symbol-sound-constraints.json');
for(const binding of symbols.inputSnapshots){
  assert.equal(sha(raw(binding.snapshotPath)),binding.sha256);
  bindings.push({recordId:'symbol-sound-constraints',sourcePath:binding.snapshotPath,sha256:binding.sha256});
}
const program={id:'SUNNY-source-master-score-v1',sourceRefs:[...new Set([...cnRefs,...solRefs,timeSource.source_id,...levisson.sourceRefs,...symbols.kernel.sourceRefs])],views:[chinese,...chronological,sophia,levisson,...symbols.scoreViews],
  links:chronological.map(v=>({id:'pattern:Chinese-to-'+v.id,fromView:chinese.id,toView:v.id,fromParticipants:chinese.participants.map(p=>p.id),toParticipants:v.participants.map(p=>p.id),
    normalization:'divide-by-first-within-each-declared-frame',preserves:['ordered relative8:12:9 pitch ratios'],missingRelations:['No participant identity mapping','No construction-to-performance clock','No genealogy-to-construction equivalence','No shared instrumentation'],sourceRefs:[...cnRefs,timeSource.source_id],condition:'Source compares these native ratio configurations; no equal historical role or timing is asserted.'}))};
const execution=executeMasterScore(program,native);assert.equal(execution.status,'partial-source-backed-instantiation');
assert.ok(execution.views.every(v=>!v.checks.some(c=>c.verdict==='fail')));assert.ok(execution.links.every(l=>l.verdict==='pass'));
for(const w of cases){const view=execution.views.find(v=>v.viewId==='chronology:'+w.witness);assert.deepEqual(view.overlapWindows.map(x=>Number(x.duration.value.numerator)/Number(x.duration.value.denominator)),w.durations);}
const products=[81,54,72].map((value,i)=>native.execute('MEC-01',{value:q(value),factor:q([8,12,9][i]),carrier:'declared ideal length-frequency product',unit:'illustrative-length-unit × relative-frequency-unit'}));
for(const p of products){assert.equal(p.status,'executed');assert.deepEqual(p.output.value,q(648));}
const output={schema:'sunny.master-score-reconstruction.v1',created_utc:new Date().toISOString(),
  scope:program.views.length+' source-backed conditional views and their executable relations; not a complete universal master score.',
  implementationEnvelope:'Known/unknown fields, quantities, events and relations are data contracts; they do not prescribe the discovered cosmological type laws.',
  provenance:{jev_request:'docs/evidence/master-score-design-request.json',jev_result:'docs/evidence/master-score-design-superjev.json',jev_model:decision.resolved_model,
    input_hashes:Object.fromEntries(['state/reconstruction/music-geometry.json','state/reconstruction/generational-constraints.json','state/reconstruction/native-execution.json','state/reconstruction/symbol-sound-constraints.json','docs/evidence/levisson-score-view.json'].map(p=>[p,sha(raw(p))])),native_source:nativeRecord},
  evidenceBindings:bindings,program,execution,sourceMathChecks:{chineseNativeOrder:{lengths:[81,54,72],relativeFrequencies:[8,12,9],products:products.map(x=>x.output.value),productConstant:q(648),condition:'Illustrative ideal reciprocal construction; not a universal dimensional acoustic constant.'}},
  counts:{views:program.views.length,chronologicalWitnesses:5,participants:program.views.reduce((a,v)=>a+v.participants.length,0),
    participantMembershipOccurrences:program.views.reduce((a,v)=>a+v.participants.length,0),
    distinctParticipantIds:new Set(program.views.flatMap(v=>v.participants.map(p=>p.id))).size,
    countBoundary:'IDs describe source-qualified occurrences; alternative-view memberships are not additional unique historical entities.',
    sourceBoundTransitions:6,explicitRatioLinks:program.links.length,chronologicalWindows:25},
  unknowns:execution.missingVariables,universalCompletion:false,missionIComplete:false,blindPrediction:false,canonicalPromotion:false};
const masterPath=path.join(root,'state/reconstruction/master-score.json');
if(fs.existsSync(masterPath)){
  const old=fs.readFileSync(masterPath),saved=path.join(root,'state/checkpoint-history','before-symbol-master-score-'+sha(old)+'.json');
  if(!fs.existsSync(saved))fs.writeFileSync(saved,old,{flag:'wx'});
}
fs.writeFileSync(masterPath,JSON.stringify(output,null,2)+'\n');
const doc=`# Executable source-backed master score\n\nThe score now executes ${program.views.length} sourced views covering the Chinese construction, five genealogical witness readings, the retained Sophia working pitch lock and the first Levisson Haftarah staff, and three source-qualified Alef interpretation views. It carries participants, roles, instruments, notes, registers, entrances, durations, overlaps, transitions and GEN/TIME/ADR fields. Unassigned values remain explicit missing variables. This is a partial instantiation, not the universal master score.\n\nThe Alef addition contributes eleven membership occurrences across seven source-occurrence IDs. Its two mark interpretations preserve the same consonantal-realization observations; pitch, acoustic duration and waveform remain unknown. Full score membership occurrences and distinct IDs are counted separately.\n\nThe Levisson view associates 12 written notes with nine syllable occurrences. Its clock measures quarter-note units. Performed timestamps and tuning remain open.\n\nThe Chinese view preserves generation order: lengths81 →54 →72 correspond to relative frequencies8 →12 →9. Native scalar actions reproduce all four changes; every ideal length/frequency pair has the illustrative product648. Construction order supplies no audio durations, and seasonal order is not substituted for construction order.\n\nEach chronological view sorts the six reported birth/death events and computes five half-open overlap windows. The reproduced durations are ${cases.map(w=>w.witness+': ['+w.durations.join(', ')+']').join('; ')}. Those intervals are chronological lifetimes under the declared experiment, with witness-specific year units and references. They are not audible sustain or beats. The relative8:12:9 pitch comparisons do not equate people with Chinese construction stages.\n\nThe Sophia view retains F_upper, Yaldabaoth F_lower and Sabaoth C_lower. With Sophia as a relative unit reference only, the exact relations give1,1/2,3/4. The octave seam and fifth relation execute; absoluteHz, timing, instruments, genealogy and a unique address remain unassigned.\n\nThe engine rejects scalar, ordering and overlap calculations across mismatched carriers, units or references. Explicit cross-system links compare only ordered relative pitch ratios, normalized separately within each declared frame. Every link lists the identity, timing and instrumentation relations it does not supply. Cyclic partial orders fail even when timestamps are unknown.\n\nThe retained Jev receipt reports the representation choice. Provider-account attribution remains unverified; this integration made no new inference call. The source-native executor, original source hashes, exact evidence spans, conditional witness data and all execution results are retained in the JSON companion.\n`;
fs.writeFileSync(path.join(root,'docs/reconstruction/MASTER_SCORE.md'),doc);
console.log(JSON.stringify({status:execution.status,...output.counts,missingVariables:output.unknowns.length,universalCompletion:false}));
