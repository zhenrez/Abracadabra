/** Preserve source-native reading operations and execute only their declared finite relations. */
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';import assert from 'node:assert/strict';
import {readingDependency,minimalReadingRefinements,queryReadings,readingJoinResidual} from '../dist/reading-relations.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),base='state/delivery-2026-11-07/pausal-operations';
const read=p=>fs.readFileSync(path.join(root,p)),load=p=>JSON.parse(read(p));
const sha=raw=>createHash('sha256').update(raw).digest('hex');
const transport='state/delivery-2026-11-07/history-discriminator/exa-loc-fetch.json';
const source=load(transport).content[0].text;
const reviewed=load(base+'/review/result.json');
const relationReview=load(base+'/review/relation-review.json');
assert.equal(relationReview.status,'passed');
assert.equal(reviewed.status,'passed');assert.equal(sha(read(transport)),reviewed.inputHashes[transport]);
function exact(span){assert.equal(source.slice(span.startCodePoint,span.endCodePointExclusive),span.text);return span;}

// These declarations concern the four inspected CV transcriptions, not an unrestricted IPA grammar.
function cvAnalysis(ipa,onsets){
 const symbols=[...ipa],syllables=[];let cursor=0;
 for(const [i,onset]of onsets.entries()){
  let stressed=false;if(symbols[cursor]==='ˈ'){stressed=true;cursor++;}
  assert.equal(symbols[cursor++],onset);
  const nucleus=symbols[cursor++];assert.ok(['a','e','o','ɔ','u'].includes(nucleus));
  const lengthMark=symbols[cursor]==='ː'?(cursor++,'ː'):'';
  syllables.push({ordinalOneBased:i+1,onset,nucleus,lengthMark,primaryStress:stressed});
 }
 assert.equal(cursor,symbols.length);assert.equal(syllables.filter(s=>s.primaryStress).length,1);
 const recomposed=syllables.map(s=>(s.primaryStress?'ˈ':'')+s.onset+s.nucleus+s.lengthMark).join('');
 assert.equal(recomposed,ipa);return syllables;
}
const entities=[{id:'molin:section2.4',nativeName:'Molin2020 §2.4',unit:'Published example group',sourceRefs:[transport],
 statedExtent:{value:4,unitAsWritten:'forms',meaningNotFullyResolved:true},
 reconciliation:'Two spelled examples are displayed here. Their four comparative IPA strings are not four separately attested bowl forms. The stated corpus extent is not fully reconciled.'}];
const relationships=[],forms=[],rows=[];
for(const record of reviewed.wordCases){
 exact(record.wordSpan);exact(record.ipaSpans.pausal);exact(record.ipaSpans.contextual);
 const caseId='molin:example'+record.example,onsets=record.example===7?['ʃ','m','r']:['t','χ','l'];
 entities.push({id:caseId,nativeName:record.word,unit:'Spelled example attributed by the publication to bowl evidence',
  citation:record.citation,locus:record.reference,sourceRefs:[transport],sourceSpan:record.wordSpan,
  originalInkCollated:false,normalizedBhsComparator:record.normalizedBhsComparator});
 relationships.push({from:'molin:section2.4',to:caseId,kind:'contains-displayed-example'});
 const analyses={};
 for(const role of ['contextual','pausal']){
  const id=caseId+':'+role,ipa=record[role],syllables=cvAnalysis(ipa,onsets);
  analyses[role]=syllables;
  const form={id,parent:caseId,role,ipa,syllables,sourceRefs:[transport],sourceSpan:record.ipaSpans[role],
   evidenceRole:role==='pausal'?'Molin conditional pronunciation reconstructed from the cited spelling':'Babylonian-manuscript comparandum cited by Molin; not a contextual token on the same bowl',
   measured:false,absoluteHz:null,audibleDuration:null,pitchClass:null};
  forms.push(form);entities.push({...form,nativeName:ipa,unit:'Published comparative pronunciation'});
  relationships.push({from:caseId,to:id,kind:role==='pausal'?'source-reconstructed-reading':'compared-with-manuscript-reading'});
  for(const syllable of syllables){
   const sid=id+':syllable'+syllable.ordinalOneBased;
   entities.push({id:sid,parent:id,nativeName:syllable.onset+syllable.nucleus+syllable.lengthMark,
    unit:'Analysed CV syllable occurrence',...syllable,sourceRefs:[transport],
    clock:'Ordinal sequence only; no measured entrance, duration or beat value',absoluteHz:null});
   relationships.push({from:id,to:sid,kind:'contains-analysed-syllable'});
  }
 }
 const contextualStress=analyses.contextual.find(s=>s.primaryStress).ordinalOneBased;
 const pausalStress=analyses.pausal.find(s=>s.primaryStress).ordinalOneBased;
 assert.equal(contextualStress,3);assert.equal(pausalStress,2);
 assert.equal(analyses.contextual[1].nucleus,'a');
 assert.equal(analyses.contextual[1].lengthMark,'');assert.equal(analyses.pausal[1].lengthMark,'ː');
 rows.push({id:caseId,sourceRefs:[transport],values:{
  family:'Molin comparative Babylonian reading cases; shared operator is conditional',lexeme:record.reference,
  inputNucleus:'a',targetMode:'pausal',medialOnset:onsets[1],comparandumId:record.comparativeFootnote,
  targetDerivedVowelClass:record.example===7?'qames-corresponding':'ṣere-corresponding',
  outputNucleus:analyses.pausal[1].nucleus+analyses.pausal[1].lengthMark,
  outputLengthMark:analyses.pausal[1].lengthMark,stressShift:String(pausalStress-contextualStress)}});
}
assert.equal(entities.length,19);assert.equal(relationships.length,18);assert.equal(forms.length,4);
const inputs=['inputNucleus','targetMode'];
const coarse=readingDependency(rows,inputs,'outputNucleus');assert.equal(coarse.status,'contradicted');
const refinements=minimalReadingRefinements(rows,inputs,['lexeme','medialOnset','comparandumId'],'outputNucleus');
assert.equal(refinements.length,3);assert.ok(refinements.every(k=>k.length===1));
const residual=readingJoinResidual(rows,['lexeme','inputNucleus'],['inputNucleus','outputNucleus']);
assert.equal(residual.rejoinedDistinctTuples,4);assert.equal(residual.excessCombinations.length,2);
const repaired=readingJoinResidual(rows,['lexeme','inputNucleus'],['lexeme','inputNucleus','outputNucleus']);
assert.equal(repaired.rejoinedDistinctTuples,2);assert.equal(repaired.excessCombinations.length,0);
const stableComponents=['outputLengthMark','stressShift'].map(output=>readingDependency(rows,inputs,output));
assert.ok(stableComponents.every(r=>r.status==='no-counterexample-on-complete-rows'));
const prosody=load(base+'/prosody/result.json');
for(const evidence of prosody.evidence){const [start,end]=evidence.source_offsets_codepoints_half_open;
 assert.equal(sha(Buffer.from(source.slice(start,end),'utf8')),evidence.region_sha256_utf8);}
const tibRows=prosody.counterexamples.filter(c=>c.id.startsWith('ZAQEF-')).map(c=>({id:'tiberian:'+c.id,sourceRefs:[transport],
 values:{writtenAccent:c.written_accent,form:c.form,locus:String(c.locus),proposedDomain:c.source_proposed_domain}}));
const accentDependency=readingDependency(tibRows,['writtenAccent'],'form');assert.equal(accentDependency.status,'contradicted');
const result={schema:'sunny.native-reading-operations.v1',jevReceipt:'state/jev-receipts/000062-5fcc72f3ccd7.json',
 sourceRole:'Connector-extracted primary-publication text; reconstructed phones, not original ink or measured sound',
 sourceUrl:reviewed.sourceUrl,conditions:[
  'Each publication, witness tradition, lexical case, comparative role and phonetic reconstruction remains identified.',
  'The contextual IPA strings are manuscript comparanda, not two additional bowl forms.',
  'A shared operation across these comparative pairs is a conditional investigative premise; Babylonian manuscripts need not form one homogeneous phonological system.',
  'IPA quantity and stress notation do not assign milliseconds, a fixed2:1duration ratio, musical pitch, waveform or original sacred intention.'
 ],
 census:{entities,relationships,displayedBowlExamples:2,comparativePronunciationForms:4,analysedSyllableOccurrences:12,
  sourceStatedForms:4,sourceStatedUnit:'forms',fullStatedExtentReconciled:false,
  boundary:'The four comparative pronunciation records cannot be substituted for the four stated source forms.'},
 forms,operationRows:rows,
 nativeTiberianProsody:{source:prosody.source,domains:prosody.native_domains,operations:prosody.source_native_operations,
  publishedCounterexamples:prosody.counterexamples,accentDependency,transferLimits:prosody.transfer_limits,
  boundary:'Published source analysis of Tiberian conditions; no automatic transfer to the Babylonian bowl comparison.'},
 derivedConstraints:{coarseDependency:coarse,minimalRefinementsOnAdmittedSample:refinements,
  refinementStatus:'All three distinguish these two admitted cases. Lexical/provenance identifiers are sample keys, not proof of a causal linguistic rule; no unique additional state selected.',
  targetLeakageControl:{field:'targetDerivedVowelClass',status:'excluded-from-input-refinement-search',
   reason:'The class is assigned from the currently exposed pausal reading; using it does not establish independent prediction.'},
  stableProjectionComponents:stableComponents,
  factorizationProof:'If a deterministic operation factors through the coarse input projection, equal projected inputs must have equal outputs. The two admitted rows have identical[a,pausal]inputs and different outputs. Thus that factorization fails under the shared-family premise. A relation retaining both outputs remains defined.',
  minimumDistinguishingStates:2,scope:'Conditional finite-source consistency, not recovery of a unique ancient operator.'},
 transformationRegister:{coarseProjection:['inputNucleus','targetMode'],
  projectedRelation:queryReadings(rows,{inputNucleus:'a',targetMode:'pausal'},'outputNucleus'),
  projectionRejoinResidual:residual,lexemeRetainingRejoin:repaired,
  consequence:'Discarding the distinguishing address and rejoining through the shared surface nucleus creates two excess sample pairings. This is a quantified adapter failure, not evidence that those pairings are historically impossible in every other context.'},
 queries:[
  {input:{inputNucleus:'a',targetMode:'pausal'},result:queryReadings(rows,{inputNucleus:'a',targetMode:'pausal'},'outputNucleus')},
  ...rows.map(r=>({input:{lexeme:r.values.lexeme,inputNucleus:'a'},result:queryReadings(rows,{lexeme:r.values.lexeme,inputNucleus:'a'},'outputNucleus')})),
  {input:{outputNucleus:'ɔː'},output:'lexeme',result:queryReadings(rows,{outputNucleus:'ɔː'},'lexeme')}
 ],
 scoreAnnotationBoundary:{layer:'Source-qualified syllable/order/stress annotations',noteAssignments:0,measuredOnsets:0,measuredDurations:0,
  attachment:'An annotation adapter may carry these into the master score; no phonetic symbol is silently assigned a musical note.'},
 priorArt:{scholarlyBaseline:base+'/p0a-baseline.json',functionalDependencySource:'https://cs186berkeley.net/notes/note13/',
  method:'Established finite functional-dependency and projection/rejoin criteria; not a new general theorem.',
  sourceCounterparts:'Molin2020§2.4 and cited Yeivin1985comparanda; exact source editions and ink remain pending.'},
 unresolved:['Original bowl/cited-manuscript collation','Exact9.9and684.14locator expansion','Individual specimen dates',
  'Which distinguishing argument the historical operation used','Complete four-form source extent','A justified musical/acoustic adapter'],
 originalSoundSystemRecovered:false,historicalOperatorSelected:false,blindPrediction:false,fullMissionComplete:false};
const sourceInputs=[transport,base+'/review/result.json',base+'/p0a-baseline.json',base+'/functional-dependency-prior-art.json',
 base+'/review/relation-review.json',base+'/prosody/result.json',base+'/prosody/validation.json','state/jev-receipts/000062-5fcc72f3ccd7.json'];
result.inputSnapshots=sourceInputs.map(p=>{const raw=read(p),hash=sha(raw),dest='data/raw/reconstruction-integrations/'+hash+'/'+path.basename(p);
 fs.mkdirSync(path.dirname(path.join(root,dest)),{recursive:true});if(fs.existsSync(path.join(root,dest)))assert.ok(read(dest).equals(raw));else fs.writeFileSync(path.join(root,dest),raw);
 return {sourcePath:p,snapshotPath:dest,sha256:hash,bytes:raw.length};});
result.codeBindings=['src/reading-relations.ts','dist/reading-relations.js','scripts/derive_reading_operations.mjs','scripts/integrate_reading_hierarchy_score.mjs','tests/reading-relations.test.mjs']
 .map(p=>({path:p,sha256:sha(read(p))}));
const raw=JSON.stringify(result,null,2)+'\n';
for(const p of [base+'/reading-operations.json','state/reconstruction/reading-operations.json'])fs.writeFileSync(path.join(root,p),raw);
console.log(JSON.stringify({status:'passed',exit_code:0,sourceWordCases:2,comparativeForms:4,syllableOccurrences:12,
 coarseOperatorContradicted:true,retainedMinimalRefinements:3,projectedRejoinTuples:4,excessSampleCombinations:2,wholeSourceExtentReconciled:false}));
