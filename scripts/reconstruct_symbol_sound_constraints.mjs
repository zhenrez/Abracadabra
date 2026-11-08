/** Source-qualified phonetic alternatives executed by the existing TS law/prediction engine. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {predictOverCandidates} from '../dist/prediction.js';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const sha=x=>crypto.createHash('sha256').update(typeof x==='string'?x:Buffer.from(x)).digest('hex');
const normalize=s=>s.replace(/\s/g,'');

export function buildAlefConstraintCase(testimony,operations,sourceRefs){
  assert.ok(sourceRefs.length&&sourceRefs.every(x=>typeof x==='string'&&x.trim()),'source bindings required');
  const canonical=operations.source_reports.find(x=>Array.isArray(x.canonical_targets)).canonical_targets;
  const listed=testimony.cases.find(x=>x.page==='135-137').passages;
  assert.deepEqual(canonical.map(normalize).sort(),listed.map(normalize).sort(),'canonical loci mismatch');
  const final=testimony.cases.find(x=>x.page==='148');
  assert.equal(canonical.length,4);assert.equal(final.passages.length,3);
  const kernel={id:'source-qualified-alef',version:'1',sha256:sha(JSON.stringify({testimony,operations})),sourceRefs};
  const rows=[...canonical.map(locus=>({locus,witness:'Standard Tiberian, within the two retained mark interpretations',position:'medial',consonantal:true})),
    ...final.passages.map(locus=>({locus,witness:final.witness,position:'word-final',consonantal:false}))]
    .map((row,i)=>({...row,id:'alef-context:'+i,presenceKey:'consonantal:'+i,sourceRefs}));
  const assignment=Object.fromEntries(rows.map(r=>[r.presenceKey,r.consonantal]));
  const candidates=[
    {id:'universal-dot-consonantal',assignment:Object.fromEntries(rows.map(r=>[r.presenceKey,true])),sourceRefs},
    {id:'contextual-consonantal-mark',assignment:{...assignment,markFunction:'consonantal-disambiguation'},sourceRefs},
    {id:'contextual-gemination-mark',assignment:{...assignment,markFunction:'reinforcement-or-gemination'},sourceRefs},
  ];
  const constraints=rows.map(row=>({id:row.id,kernelSha256:kernel.sha256,sourceRefs,
    dependencyGroups:[row.position==='word-final'?'Khan-p148-Arrant-witness':'Khan-p140-144-retained-interpretations'],
    authority:row.position==='word-final'?'source-assertion':'assumption',
    predicate:{op:'eq',key:row.presenceKey,value:row.consonantal}}));
  const targets=[...rows.map(r=>({id:'presence:'+r.id,keys:[r.presenceKey],sourceRefs})),
    {id:'mark-function',keys:['markFunction'],sourceRefs},
    {id:'duration-factor',keys:['measuredDurationFactor'],sourceRefs},
    {id:'absolute-Hz',keys:['absoluteHz'],sourceRefs},
    {id:'waveform',keys:['acousticWaveform'],sourceRefs}];
  const result=predictOverCandidates(candidates,constraints,kernel,targets);
  const groups=new Map();
  for(const candidate of candidates.filter(c=>result.retainedCandidateIds.includes(c.id))){
    const values=rows.map(r=>candidate.assignment[r.presenceKey]),key=JSON.stringify(values);
    const group=groups.get(key)??{values,candidateIds:[]};group.candidateIds.push(candidate.id);groups.set(key,group);
  }
  return {schema:'sunny.source-qualified-symbol-sound.v1',kernel,rows,candidates,constraints,targets,result,
    presenceProjection:[...groups.values()],
    derivation:'The two source-qualified mark grammars have the same seven-component consonantal-realization projection. Its fibre contains both candidates; even a complete observation of that projection cannot distinguish them within this supplied family.',
    requiredAdditionalEvidence:'An independently justified mark-to-articulatory-effect model plus controlled reinforcement/timing contrasts, or additional source-native grammatical/manuscript constraints. Mappiq-only meaning does not itself forbid strengthening for another reason.',
    observationBoundary:'Consonantal realization is a source-reconstructed phonological feature, not a measured closure, waveform, pitch or duration.',
    sourceCondition:'Three word-final values are conditional on Khan\'s reconstruction of the named Cambridge witness. Four medial values are shared premises of the retained standard-reading interpretations. No claim of exhaustive historical candidates.',
    historicalInterpretationSelected:false,blindPrediction:false,canonicalPromotion:false};
}

export function runSymbolSoundConstraints(checkOnly=false){
  const outputPath=path.join(root,'state/reconstruction/symbol-sound-constraints.json');
  const previous=checkOnly?JSON.parse(fs.readFileSync(outputPath,'utf8')):null;
  const snapshots=[];
  const load=(relative,binary=false)=>{
    let binding,raw;
    if(checkOnly){binding=previous.inputSnapshots.find(x=>x.sourceOccurrencePath===relative);assert.ok(binding);raw=fs.readFileSync(path.join(root,binding.snapshotPath));}
    else{
      raw=fs.readFileSync(path.join(root,relative));const digest=sha(raw);
      const snapshotPath=path.posix.join('data/raw/reconstruction-integrations',digest,path.basename(relative));
      const target=path.join(root,snapshotPath);fs.mkdirSync(path.dirname(target),{recursive:true});
      if(!fs.existsSync(target))fs.writeFileSync(target,raw,{flag:'wx'});
      binding={sourceOccurrencePath:relative,snapshotPath,sha256:digest,bytes:raw.length};
    }
    assert.equal(sha(raw),binding.sha256);assert.equal(raw.length,binding.bytes);snapshots.push(binding);
    return binary?raw:JSON.parse(raw.toString('utf8').replace(/^\uFEFF/,''));
  };
  const testimony=load('docs/reconstruction/symbol-sound-census/tiberian-alef-testimony.json');
  const operations=load('state/research/reactivation/symbols/tiberian-alef-operations.json');
  const retainedViewInput=load('docs/evidence/tiberian-alef-score-view.json').view;
  const direction=load('state/research/reactivation/symbols/jev-next-native-question-v2-receipt.json');
  assert.equal(operations.source.original_path,'sources/khan2020.pdf');
  const primaryPdfPath='state/research/reactivation/symbols/sources/khan2020.pdf';
  assert.equal(sha(load(primaryPdfPath,true)),operations.source.sha256,'Primary Khan PDF binding differs');
  const tokenComparison=load('state/research/reactivation/alef-witness/token-comparison.json');
  assert.equal(tokenComparison.rows.length,4);
  const unicodeInputChecks=tokenComparison.rows.map(row=>{
    const bytes=load(row.source.path,true);assert.equal(sha(bytes),row.source.sha256);
    const [start,end]=row.source.token_byte_span_zero_based_half_open;
    assert.equal(bytes.subarray(start,end).toString('utf8'),row.token,'Exact target byte span differs');
    assert.ok(row.alef_clusters.every(c=>c.contains_u05bc));
    return {locus:row.locus,token:row.token,source:row.source,alefClusters:row.alef_clusters,comparison:row.comparison,
      exactByteSpanVerified:true,scope:'Version-bound digital transcription; no phonetic meaning follows from codepoint identity.'};
  });
  const retainedTokenPath=tokenComparison.rows[0].retained_wlc_snapshot.path;
  load(retainedTokenPath);
  const retainedBinding=snapshots.find(x=>x.sourceOccurrencePath===retainedTokenPath);
  assert.ok(tokenComparison.rows.every(r=>r.retained_wlc_snapshot.sha256===retainedBinding.sha256));
  const refs=snapshots.map(s=>s.snapshotPath),calculation=buildAlefConstraintCase(testimony,operations,refs);
  const bindScoreRefs=value=>{
    if(Array.isArray(value))return value.map(bindScoreRefs);
    if(!value||typeof value!=='object')return value;
    return Object.fromEntries(Object.entries(value).map(([key,child])=>[key,key==='sourceRefs'?child.map(ref=>{
      const binding=snapshots.find(s=>s.sourceOccurrencePath===ref);assert.ok(binding,'Unresolved score reference: '+ref);return binding.snapshotPath;
    }):bindScoreRefs(child)]));
  };
  const retainedView=bindScoreRefs(retainedViewInput);
  const known=value=>({status:'known',value,sourceRefs:refs});
  const canonicalRows=calculation.rows.filter(r=>r.position==='medial');
  const scoreViews=[retainedView,...calculation.result.retainedCandidateIds.map(candidateId=>{
    const candidate=calculation.candidates.find(c=>c.id===candidateId);
    return {id:'alef:'+candidateId,system:'Standard Tiberian candidate mark grammar',
      condition:'Conditional source interpretation; no measured pronunciation, timing or musical assignment.',sourceRefs:refs,
      participants:canonicalRows.map(row=>({...structuredClone(retainedView.participants[0]),id:row.id,label:row.locus,sourceRefs:refs,
        role:known('Named written occurrence under '+candidateId),
        coordinates:{witness:known(row.witness),interpretation:known(candidate.assignment.markFunction),consonantalRealization:known(true)}})),
      events:[],order:[],transitions:[]};
  })];
  const codePaths=['scripts/reconstruct_symbol_sound_constraints.mjs','src/law.ts','src/prediction.ts','dist/law.js','dist/prediction.js'];
  const output={...calculation,inputSnapshots:snapshots,codeBindings:codePaths.map(p=>({path:p,sha256:sha(fs.readFileSync(path.join(root,p)))})),
    direction:{receipt:refs[3],statusReported:direction.status,modelReported:direction.resolved_model,
      choice:direction.answers.next_source_question.winner,newInferencePerformed:false,providerAccountAttribution:'unverified; user reports zero charges'},
    reuse:'Existing TypeScript law/prediction and score engines; retained source readings and source-case view, not a new ontology or historical discovery.',
    unicodeInputChecks,primaryPdfBinding:{declaredRelativePath:operations.source.original_path,resolvedOccurrencePath:primaryPdfPath,sha256:operations.source.sha256},
    scoreViews,counts:{sourceContexts:calculation.rows.length,rawCanonicalTokens:unicodeInputChecks.length,retainedGrammarCandidates:calculation.result.retainedCandidateIds.length,
      scoreMembershipOccurrences:scoreViews.reduce((s,v)=>s+v.participants.length,0),distinctSourceOccurrenceIds:new Set(scoreViews.flatMap(v=>v.participants.map(p=>p.id))).size},
    remaining:['Raw manuscript/edition token checks','Matched articulatory measurements and comparison model','Paleo-Hebrew/Aramaic/English native systems and valid bridges','Original intended sound/grammar and musical coupling','Full16goals/8outputs and independent held-out prediction']};
  if(checkOnly)assert.deepEqual(output,previous,'Published symbol/sound execution does not reproduce');
  else{
    if(fs.existsSync(outputPath)){const raw=fs.readFileSync(outputPath),saved=path.join(root,'state/checkpoint-history','before-symbol-sound-'+sha(raw)+'.json');if(!fs.existsSync(saved))fs.writeFileSync(saved,raw,{flag:'wx'});}
    fs.writeFileSync(outputPath,JSON.stringify(output,null,2)+'\n');
  }
  console.log(JSON.stringify({status:checkOnly?'verified-frozen-execution':'executed',exit_code:0,...output.counts,
    rejected:calculation.result.evaluation.rejected,indistinguishablePresenceGrammars:calculation.presenceProjection[0].candidateIds.length,
    missingAcousticTargets:calculation.result.predictions.filter(p=>p.status==='unknown').map(p=>p.targetId),newInferencePerformed:false}));
  return output;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))runSymbolSoundConstraints(process.argv.includes('--check'));
