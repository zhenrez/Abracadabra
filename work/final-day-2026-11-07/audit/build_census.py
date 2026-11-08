"""Source-bound deliverable census. No analytic engine or frozen artifact mutation."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
def read(path):return json.loads((ROOT/path).read_bytes().decode('utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path,needle=None):
 p=ROOT/path;raw=p.read_bytes();text=raw.decode('utf-8');r={'path':path,'sha256':sha(p),'bytes':len(raw)}
 if needle is not None:
  start=text.find(needle)
  if start<0:raise ValueError((path,needle))
  end=start+len(needle);r.update(character_start=start,character_end=end,byte_start=len(text[:start].encode('utf-8')),byte_end=len(text[:end].encode('utf-8')),line_start=text[:start].count('\n')+1)
 return r
def file_evidence(paths):return [dict(path=p,exists=(ROOT/p).is_file(),sha256=sha(ROOT/p) if (ROOT/p).is_file() else None) for p in paths]

MISSION=read('state/mission.json');TASK=read('state/task.json');MODEL=read('state/reconstruction/model.json')
OLD=read('state/delivery-2026-11-07/acceptance.json')
MANDATE='data/raw/mandate-inputs/99dabf2083b9a04c7f7302546651726548a29f5c10a5c7f7a934f983a6e58f63/Pasted text.txt'
ORIENTATION='work/unit001/frozen/source/orientation-context.txt'
rows=[]
def add(ident,scope,requirement,acceptance,code,evidence,status,dependencies=(),remaining='',source=None):
 rows.append(dict(id=ident,scope=scope,requirement=requirement,acceptance=acceptance,code=code,evidence=file_evidence(evidence),
                  status=status,dependencies=list(dependencies),remaining=remaining,source=source,
                  verification_boundary='Static census plus explicitly attributed existing receipts; final-day root checks must establish current execution.'))

def build_rows():
 # The initiating inverse-reconstruction question is broader than either the
 # common evidence foundation or later native musical engineering contracts.
 inverse=[
  ('INV01','Inverse glyph–phoneme state-machine hypothesis','Recover candidate root bases, typed operators and residuals from the supplied table; distinguish a fitted deterministic model from an established historical generative mechanism',
   ['work/ariadne-inverse/README.md','work/ariadne-inverse/carrier-statistics.json'],'BOUNDED_PROTOTYPE; HISTORICAL_ROOT_UNRESOLVED'),
  ('INV02','IPA vectorization','Fixed15-feature articulation vectors, atomic emphatic units, explicit alternatives/sequences, missing-value masks, deterministic normalization and preserved script-local alignment',
   ['work/ariadne-inverse/features.py','work/ariadne-inverse/numpy_pipeline.py'],'IMPLEMENTED_WITH_DECLARED_COARSE_FEATURE_LIMITS'),
  ('INV03','Glyph topology','Endpoints,junctions,segments,holes and symmetry derived from identified glyph representations; source images or scholarly forms needed for historical geometry',
   ['work/ariadne-inverse/numpy_pipeline.py','work/ariadne-inverse/results-v2/measured.json'],'MODERN_FONT_PROXY_ONLY; HISTORICAL_TOPOLOGY_UNRESOLVED'),
  ('INV04','Root/operator/residual inference','PCA, entropy and explicit description lengths with actual costs; nonzero residuals and failure of full-inventory permutation retained',
   ['work/ariadne-inverse/extract_carrier.py','work/ariadne-inverse/residual_analysis.py','work/ariadne-inverse/permutation.py'],'BOUNDED_MEASURED_OUTPUTS; UNIVERSAL_ZERO_RESIDUAL_NOT_ESTABLISHED'),
  ('INV05','Identifiability and rigorous tests','Distinguish parameter gauges, equivalent roots, source-family leakage, unsupported syllabic/proxy projections and out-of-sample identifiability',
   ['work/unit001/kernel.py','work/unit001/contracts.py','work/ariadne-inverse/test_models.py'],'PARTIAL_CONTRACTS; GLOBAL_IDENTIFIABILITY_AND_NEW_HISTORICAL_HOLDOUTS_UNRESOLVED'),
  ('INV06','Reproducible bounded execution and protected SUN','Source-bound measured outputs, original inputs and existing matrix preserved; frozen SUN kernel unchanged',
   ['work/unit001/list-completion/completion-receipt.json','work/unit001/source-manifest.json'],'ACCEPTED_BOUNDED_ENGINEERING_EVIDENCE')]
 for ident,name,accept,evidence,status in inverse:
  add(ident,'original_inverse_reconstruction',name,accept,[p for p in evidence if p.endswith('.py')],evidence,status,[],
      'Original exploratory inverse-model aim remains in scope; engineering infrastructure and native gates do not themselves establish a historical root.',
      ref('work/unit001/CURRENT_CHAT_RECONCILIATION.json'))
 # The original two purposes cannot disappear when later engineering gates pass.
 for i,text in enumerate(MISSION['original_two_purposes'],1):
  add('PURPOSE'+str(i),'original_product',text,'Recover source/decision/derivation on demand and execute typed comparisons with candidate/residual receipts',
      ['src/server.ts','src/comparison.ts','src/prediction.ts'],['docs/evidence/mission-semantics-source-review.json','state/reconstruction/model.json'],
      'PARTIAL_EXISTING_SYSTEM',['G09','G11','G13'],'No universal comparison or account-wide semantic reconstruction demonstrated',ref('state/mission.json',text))
 # All16 current goals retain literal requirements and original status limits.
 indexed={x['id']:x for x in OLD['items']}
 for g in MISSION['goals']:
  old=indexed[g['id']]
  add(g['id'],'SUNNY_goal',g['text'],old['completionEvidenceNeeded'],[],old['evidence'],
      'OPEN_DEPENDENT' if old['status']=='open-dependent' else 'PARTIAL_SOURCE_SCOPED',
      ['G06','G16'] if g['id'] in ('G05','G07') else [],old['notYetSatisfied'],ref('state/mission.json',g['text']))
 # All eight original mathematical outputs: existence is not completion.
 code_by_unit={'native-execution':'scripts/reconstruct_native_execution.mjs','native-derivations':'scripts/reconstruct_native_derivations.py',
  'generational-constraints':'scripts/reconstruct_generational_constraints.py','orientation-predictions':'scripts/reconstruct_orientation_predictions.mjs',
  'master-score':'scripts/reconstruct_master_score.mjs','contextual-alignment':'scripts/execute_contextual_alignment.mjs',
  'symbol-sound-constraints':'scripts/reconstruct_symbol_sound_constraints.mjs','score-anchor-constraints':'scripts/derive_score_anchors.py'}
 for i,item in enumerate(MODEL['mandated_output_status'],1):
  add(f'M{i:02}','original_mathematical_output',item['output'],
      'Connected executable register with exact inputs, source conditions, units, derivations, counterexamples, alternatives and downstream dependencies at the complete stated scope',
      [code_by_unit[u] for u in item['units'] if u in code_by_unit],['state/reconstruction/'+u+'.json' for u in item['units']],
      item['status'].upper(),['G04','G06','G11','G12'],item['remaining'],ref(MANDATE,item['output']))
 # G0/G1 closeout is reused as its concrete requirement ledger, not rebuilt.
 prior=read('work/unit001/list-completion/requirements-closeout.json')
 for item in prior['requirements']:
  add('FOUNDATION:'+item['requirement_id'],'ARIADNE_foundation',item.get('note',item['requirement_id']),
      'Original concrete source sections and acceptance tests remain bound in the retained closeout ledger',
      ['work/unit001/'+(f['path'] if isinstance(f,dict) else f) for f in item.get('artifacts',[])],
      ['work/unit001/list-completion/requirements-closeout.json','work/unit001/list-completion/completion-receipt.json'],
      'ACCEPTED_BOUNDED_G0_G1',[],source={'source_sections':item.get('source_sections',[])})
 for item in read('work/unit001/CURRENT_CHAT_RECONCILIATION.json')['completed_stages']:
  paths=[str(Path(e['path']).relative_to(ROOT)).replace('\\','/') for e in item['evidence']]
  add('PIPELINE:'+item['id'],'earlier_linguistic_pipeline',item['title'],
      'Preserve exact earlier inputs, implementations, measured outputs and scientific limits; replay existing tests without changing frozen conclusions',
      [p for p in paths if p.endswith('.py')],paths,'EXISTING_SOURCE_SCOPED_IMPLEMENTATION',[],item['status'],
      ref('work/unit001/CURRENT_CHAT_RECONCILIATION.json',item['title']))
 gate_rows=[
  ('EG0','Lossless evidence architecture','All540 positions,381populated/159blank, exact original fields/Unicode/source hashes, external claims/genealogy, immutable reversible serialization',
   ['work/unit001/evidence.py','work/unit001/kernel.py'],['work/unit001/list-completion/completion-receipt.json'],'ACCEPTED_BOUNDED_SCOPE',[]),
  ('EG1','Sefer compatibility','Original6tests+3demonstrations exact; actual assignments,22slots/29taggedstates,231/462/484spaces, ambiguity, sourcebindings and four-axis receipts',
   ['work/unit001/sefer.py'],['work/unit001/list-completion/acceptance/acceptance-receipt.json'],'ACCEPTED_BOUNDED_SCOPE',['EG0']),
  ('EG2','Western native orientation','Interval composition/inversion, mode transformations, register distinction and exact-ratio nonclosure under independently selected tuning/source profile',
   ['work/unit002/western.py','work/four-orientations/native_models.py'],['work/unit002/native-results.json','work/unit002/CONTEXT_RECTIFICATION.md'],'PARTIAL_NATIVE_CORE',['EG1']),
  ('EG3','Chinese native orientation','Correct generator direction and2/3vs4/3, generation sequence, modal-role separation,12references/5functions and independent60contexts',
   ['work/four-orientations/native_models.py','src/contextual-alignment.ts'],['state/reconstruction/contextual-alignment.json'],'PARTIAL_NATIVE_CORE',['EG2']),
  ('EG4','Indian native orientations','Separate witness-specificgrama22unit allocations,7svara grouping, admissible72melakarta grammar and36Madhyama involutive pairs',
   ['work/four-orientations/native_models.py'],['work/four-orientations/checkpoint.json'],'PARTIAL_NATIVE_CORE',['EG3']),
  ('EG5','Independent phonetic/numerical controls','Documented Sanskrit5×5 articulatory features and Katapayadi encoding/decoding examples with own source rules and exceptions',
   [],[],'NOT_IMPLEMENTED_AT_AUDIT',['EG4']),
  ('EG6','Historical baseline and model comparison','Sameobservations/evaluation splits/coding conventions for conventional and proposed models; actual model+adapter+residual costs, chronology/sourcefamily holds and counterexamples',
   ['work/ariadne-inverse/extract_carrier.py'],['work/ariadne-inverse/carrier-statistics.json'],'NOT_CERTIFIED; EARLIER_CONDITIONAL_CODES_ONLY',['EG2','EG3','EG4','EG5']),
  ('EG7','Cross-orientation certification','Nativefreeze receipts, explicittyped adapters, fixedtolerances, operatorcommutation residuals, outofsampletests, negativecontrols and four-axis evidence receipts',
   ['work/unit001/contracts.py','work/four-orientations/comparison.py'],['work/four-orientations/checkpoint.json'],'LOCKED_PENDING_PREREQUISITES',['EG0','EG1','EG2','EG3','EG4','EG5','EG6'])]
 for ident,name,accept,code,evidence,status,deps in gate_rows:
  add(ident,'ARIADNE_engine_gate',name,accept,code,evidence,status,deps,
      'Final-day direct mandate authorizes continuation but does not waive prerequisite evidence; previous frozen gate receipts retain scope.',ref(ORIENTATION))
 # Native subcontracts make the requirements executable rather than just labels.
 native=[
 ('W01','Intervals and ratios','Exactfrequency fifth3/2,fourth4/3,octave2; length2/3,3/4,1/2; reciprocal units kept distinct','EG2',['work/unit002/western.py'],'PARTIAL_REUSABLE'),
 ('W02','Diatonic/chromatic modes','Sevenselectedclasses and12-class labeluniverse; sevenmode rotations with exact tuning','EG2',['work/unit002/western.py'],'PARTIAL_REUSABLE'),
 ('W03','Transformations','Transposition,inversion,octaveshift and reversible register transport','EG2',['work/unit002/western.py'],'PARTIAL_REUSABLE'),
 ('W04','Nonclosure','12fifths/7octaves exact531441/524288; finiteclass closure must retain comma','EG2',['work/unit002/western.py'],'REUSABLE_BOUNDED_TESTS'),
 ('W05','Historical Western profiles','AncientGreek tetrachords,Fluddcosmicmonochord,Keplerdynamicharmony,CompletedHarmony as independent sourceprofiles; no retroactive12TET','EG2',['src/native-operators.ts'],'SOURCE_PROFILE_GAPS'),
 ('W06','Composition and performance','Rhythmictransformation,polyphony,voiceleading,register,voice,duration and explicit source-bound operations','EG2',['src/score.ts','src/native-operators.ts'],'BROADER_PARTIAL_SYSTEM'),
 ('C01','Length generation','D=2/3,U=4/3; DU=8/9 distinct fromSUNRL=1/2; U=L inverse','EG3',['work/four-orientations/native_models.py'],'REUSABLE_EXACT_CORE'),
 ('C02','Sequence and classification','Twelve lü generation sequence and native6+6labels must not be inferred from arbitrary displayindex parity','EG3',['src/contextual-alignment.ts'],'SOURCE_NATIVE_GAPS'),
 ('C03','Modal functions','Twelve reference pitches ×fivegong/shang/jue/zhi/yu functions; reference andfunctionrotation independent','EG3',['work/four-orientations/native_models.py','src/contextual-alignment.ts'],'REUSABLE_EXACT_CORE'),
 ('C04','Residuals','Retainfifthcycle nonclosure, sourcepipe variants, unexplainedmodal assignments;60formalcontexts not60attestedpipes','EG3',['src/contextual-alignment.ts'],'PARTIAL_SOURCE_EXECUTION'),
 ('I01','Grama/shruti','Seven named svaras;22allocatedunits groupedinto7noteintervals; witnessspecificallocations and tonalshifts; no7→22surjection','EG4',[],'MISSING_NATIVE_ADAPTER'),
 ('I02','Melakarta','6orderedRiGa ×2Ma ×6DhaNi =72uniqueadmissible7positionconfigurations','EG4',['work/four-orientations/native_models.py'],'REUSABLE_EXHAUSTIVE_GRAMMAR'),
 ('I03','Madhyama pairing','36involutivepairsswitchonlyMa; noW72correspondence inferredfrom72','EG4',['work/four-orientations/native_models.py'],'REUSABLE_EXHAUSTIVE_GRAMMAR'),
 ('I04','Intonation uncertainty','Sourcechosen profiles only; retain raga exceptions and no22equalfrequencyassumption','EG4',['work/four-orientations/native_models.py'],'INPUT_GAP_EXPLICIT'),
 ('P01','Sanskrit varga','5places×5stop/nasalseries; aspiration/voicing distinct; ownsourceexamples','EG5',[],'MISSING_NATIVE_ADAPTER'),
 ('P02','Katapayadi','Consonantdigitmap,placevaluereversal,nameconvention; Maya5+1→15; vowel/conjunct/variant rules documented','EG5',[],'MISSING_NATIVE_ADAPTER'),
 ('B01','Historical linguistic baseline','Datedglyphwitnesses, knownborrowingedges, phonemecorrespondences anduncertaintyalignments withoutmusicconstraints','EG6',['work/unit001/kernel.py'],'SCHEMA_ONLY_FOR_COMPARISON'),
 ('B02','Description length','Fixedcodebook L(M)+sum[L(adapter)+L(data|M,adapter)] withmodelcost andexceptions; nohardcodedbitcounts','EG6',[],'MISSING_COMPARABLE_CODING_SCHEME'),
 ('B03','Evaluation split','Holdoutentirerelatedwitness/artifact/sourcefamilies; recordknownexposure and chronologicalconstraints','EG6',['work/unit001/kernel.py'],'CONTRACT_EXISTS_NO_CERTIFIED_NEW_HOLDOUT'),
 ('X01','Operator preservation','Comparebothcompositionpaths ontypedcomposabledomain,exactrationalortolerancederror asdeclared','EG7',['work/four-orientations/comparison.py'],'BOUNDED_SYNTHETIC_CONTROL_ONLY'),
 ('X02','Reconstruction receipts','Structuralvalidity,modelpreference,identifiability,historicalsupport separate; preserveequivalence andcontradictions','EG7',['work/unit001/contracts.py'],'REUSABLE_COMMON_CONTRACT'),
 ('X03','Negative controls','Unrelatedinventories,permissibleorderpermutations,similarcomplexity incompatiblegenealogies; pre-registertolerance/split','EG7',[],'MISSING_EVALUATED_CROSSMODEL_TRIAL')]
 for ident,name,accept,gate,code,status in native:
  add(ident,'native_acceptance',name,accept,code,['work/four-orientations/README.md','work/unit002/CONTEXT_RECTIFICATION.md'],status,[gate],source=ref(ORIENTATION))
 # Additional signals are retained as individually addressable candidate work.
 signals=[('S01','Sefer231-gate relational compression','Formalpossibilitygraphvsattestedrelations; owncompressionpass withoutinventedattestations','work/unit001/sefer.py'),
 ('S02','Sefer32paths','10sefirot+22letters distincttypes','work/four-orientations/native_models.py'),
 ('S03','OldPersian36countermodel','3purevowels+22neutral/a+4i+7u, notuniformCVtriplication','work/unit001/evidence.py'),
 ('S04','WesternD12','Transposition/inversionorbitsandstabilizers,order24','src/native-operators.ts'),
 ('S05','Generational12→13','Retainunwrappedphase/generation/register throughlocalcycleclosure','src/geometry.ts'),
 ('S06','SUNW72','12×3×2addresses,36binaryfibers, possiblevsattestedpairings','src/prediction.ts'),
 ('S07','Alternativepartitions','3+6+9+4=22,4×3=6×2=12 remainhypothesiswithoutsemanticpreassignment',None),
 ('S08','Calendarcandidatecounts','24,36,108,144,216,260,360,364,365 undernativecountingwitness',None),
 ('S09','SUNoperatorgrammar','10generativefamiliesand13supportingrelationsretainseparateddefinition/version/source','src/native-operators.ts')]
 for ident,name,accept,code in signals:
  add(ident,'additional_retained_signal',name,accept,[code] if code else [],['work/unit001/frozen/source/orientation-context.txt'],
      'RETAINED_CANDIDATE_OR_BOUNDED_COMPONENT',['EG6','EG7'],'No equivalence created fromcardinalityalone',ref(ORIENTATION))
 # Every original completion criterion remains accountable.
 mandate=(ROOT/MANDATE).read_bytes().decode('utf-8')
 completion=mandate.split('## IV. Mission I completion conditions',1)[1].split('## V.',1)[0]
 for i,line in enumerate(re.findall(r'^- (.+)$',completion,re.M),1):
  add(f'MI{i:02}','original_Mission_I_acceptance',line,'Concrete source-bound execution and independent acceptance at full stated scope',[],
      ['state/delivery-2026-11-07/acceptance.json','state/reconstruction/model.json'],'PARTIAL_NOT_FULL_MISSION_CERTIFIED',['G01','G09','G11','G12'],source=ref(MANDATE,line))
 # Visuals are presentation deliverables, never substitutes for model proof.
 for ident,text,code in [('V01','Connected master-score view','web/delivery-2026-11-07/index.html'),
  ('V02','Native Western/Chinese/Indian/Sefer views with exactratios/typedroles','web/delivery-2026-11-07/app.js'),
  ('V03','Hierarchy atlas withsource tracing andA/B/Calternatives','deliverables/SUNNY_Hierarchy_Atlas.html'),
  ('V04','Generationalgeometryview withphase/register uncertainty','web/delivery-2026-11-07/app.js'),
  ('V05','Evidence/derivation/residual/candidate inspectors','web/delivery-2026-11-07/app.js')]:
  add(ident,'visual_delivery',text,'Renderablelocalartifact, source-linkedstate, visibleunknowns, realbrowserinteractionverification and nofabricatedsourceassignments',[code],[code,'state/delivery-2026-11-07/acceptance.json'],
      'EXISTING_VISUAL_REQUIRES_FRESH_INTEGRATION_REVIEW',['G09','G11','G15'],source=ref('state/task.json',TASK['latest_user_priority_exact']))

def planning():
 priority=[('P0','Preserveallsource/frozenartifacts and usercorrections; noprematurehistoricalcertification'),
 ('P1','Deliverreusablecommoncontractnativeengines withfreshindependentchecks'),('P2','Deliverhonestbaselinecoding,splits,negativecontrols andconditionalcrossmodelreceipts'),
 ('P3','Integrateoriginal8outputs/currentvisuals/actualJev intooneusablehandoff'),('P4','Advancebroader16goals whereactualsourcesandmathematicssuffice; localizeunresolvedglobalclaims')]
 tools=[('What & Why','Completeoriginaldeliverableswithoutrebuild; engineacceptanceandfullSUNNYcompletionseparatelytraceable'),
 ('Who','Userownsmission,rootintegrates,domainagentsnativecode,independentreviewerchecks;Jevdirectssubstantiveforks'),
 ('When','TodayNovember7Phoenix; elapsedphasebudgetsbelowareplanninglimits,notmeasuredcompletionestimates'),
 ('Where','ExistingSUNworkspace;newfinal-daydirectory;frozenSUNandG0/G1reusedunchanged'),
 ('Define Limits','Fourconcurrencyslots,network/provideraccesssubjecttolivecapability;unknownmanuscriptscannotbeinvented'),
 ('Schedule','CriticalpathEG2→EG3→EG4→EG5→EG6→EG7; sourceprofileauditandvisualreusecanruninparallel'),
 ('Budget','Noexplicitfinancialbudgetgiven;reuseexistingdependencies;boundedmodelqueriesandnoautomaticpaidservicesubscriptions'),
 ('Responsibilities','Rootintegrationandtestreceipts;nativeworkerslocalacceptance;auditorfullrequirements;reviewerfixedsourceindependence'),
 ('What Could Go Wrong?','Scopeconfusion,sourceleakage,overclaimednativeprofiles,visualproofconfusion,unavailablemathtoolsandprovideraccountgaps'),
 ('Prioritizing Possible Pitfalls','Firstpreservationandidentity;thenprerequisitegate/sourceleakage;thenliveintegration;cosmeticpolishlast'),
 ('How to Handle It','Hashcheckbefore/after;fixedprofiles/codebooks;failclosedgates;abstainwherepremisesmissing;returntypedpartialreceipts'),
 ('Mock It Up','ReuseexistingUnit002,fourorientationcore,13modulereconstructionanddeliveryvisuals;constructsmallintegrationtrial'),
 ('Test Run','Focusednativepositive/negativechecks;sourcefamilyheldoutprotocol;independentmathreplay;browseractualinteractions'),
 ('Check “What Matters”','Compareeverycensusrowagainstactualreceipt;fullcompletionfalsewhereanyrequiredscopeunmet'),
 ('Follow Through','Executecriticalpathnow;updatereceiptsandlocalcontinuationateachmaterialmilestone'),
 ('Dig into Details','Nativeindependentreviewofratios,gramaallocation,Katapayadirules,MDLcoding/splitandcommutation'),
 ('Discuss the Big Picture','Currentdirectrequestalreadyauthorizesexecution;communicateunresolvedscientificclaimswithoutrepeatedpermissionorartificialstop')]
 schedule=[('A',0,30,'Recovercompletecensusandfreezeacceptedinputs',['audit','root'],'RequirementsmappedandactualJevstrategyreceiptretained'),
 ('B',30,150,'Reuse/fillnativeEG2-EG4 contracts withindependent tests',['nativeworker','root'],'Eachnativeprofilefrozenonlyafteritsownchecks;independentworkparallel'),
 ('C',150,240,'CompleteEG5controlsandEG6fixedcodebook/evaluationsplits',['root','controlsworker'],'Sourceexamplesandnegativecontrols;adapter/modelcostsmeasured'),
 ('D',240,330,'Evaluateonlyprerequisite-admissibleEG7typedadapters',['root','reviewer'],'Commutationresidualsandambiguitypreserved;nohistoricalpromotion'),
 ('E',330,450,'Integrate8outputs/currentvisualsandindependentproofchecks',['root','visualworker'],'Workingartifactlinksandrealbrowser/nativeverification'),
 ('F',450,510,'Rerequirementaudit,frozenintegrity,handoffanddocumentchecks',['root','reviewer'],'Everyrowpassedorspecificunresolveddependency;noinventedfullmissionclosure')]
 return dict(date='2026-11-07',timezone='America/Phoenix',priority_list=[dict(id=i,requirement=t) for i,t in priority],
  better_plans_tools=[dict(tool=t,applied_output=o) for t,o in tools],
  schedule=[dict(phase=p,planned_elapsed_minutes=[a,b],work=w,owners=o,exit_criterion=e) for p,a,b,w,o,e in schedule],
  schedule_boundary='Elapsedminuteallocationsarecontrolbudgetsfromhandoff,notbenchmarkedestimates;rootmustadapttoactualremainingdayandobservedfailures.',
  failure_bounds=[
   {'trigger':'Nativecheckfails','action':'Repairsmallestnativecontractandrerunfocusedcheck;donotcross-certifyusinganotherorientation'},
   {'trigger':'Sourceunavailableorprovenanceunclear','action':'Preserveretrievalgap;useclearlystipulatedprofileforengineeringandwithholdhistoricalcertification'},
   {'trigger':'Historicalholdoutalreadyexposed','action':'Reclassifyknownoriginal/adversarial;neverclaimprospectiveblindness'},
   {'trigger':'Providerormathbackendunavailable','action':'Recordactualfailureonce;useauthorizeddeterministicfallbackforcomputation;nofakepluginexecution'},
   {'trigger':'Globalorientationunderdetermined','action':'Returnsurvivingequivalenceclassanddiscriminatingconstraint;continueindependentmodules'},
   {'trigger':'Deadlineapproachesbeforefullscientificclosure','action':'Deliverallimplementedartifactsandexactremainingcriteria;neverclaimuniversaltheoryorhistoricalrestorationcomplete'}],
  scout_material_gap='A completeengineeringrun cannot supply lostindependent historicalevidence. Bind eachG7receipttoitsactualevaluationpopulation: exposedmatrixcontrolsandnewhistoricalholdoutsarenotinterchangeable.',
  plan_status='Readyforexecution;native/model/visualvalidationstatusmustbeupdatedbyrootobservedreceipts')

def main():
 OUT.mkdir(parents=True,exist_ok=True);build_rows();plan=planning()
 sources=[MANDATE,ORIENTATION,'state/mission.json','state/task.json','docs/reconstruction/SUNNY_GOALS.md','state/reconstruction/model.json',
  'docs/evidence/mission-semantics-source-review.json','work/unit001/list-completion/requirements-closeout.json',
  'work/unit001/list-completion/completion-receipt.json','work/four-orientations/native_models.py','work/unit002/western.py','state/delivery-2026-11-07/acceptance.json']
 result=dict(schema='sunny.final-day-complete-deliverable-census.v1',date='2026-11-07',timezone='America/Phoenix',
  source_manifest=[ref(p) for p in sources],requirements=rows,counts={scope:sum(r['scope']==scope for r in rows) for scope in sorted({r['scope'] for r in rows})},
  full_mission_complete=False,scope_boundary='Enginegates,originalproductpurposes,16SUNNYgoals,8mathematicaloutputs,visuals,andoriginalcompletioncriteriaareseparatelyaccountable;noquietnarrowingtoboundedG0/G1.',
  current_reuse_decision=ref('work/final-day-2026-11-07/jev-strategy.json'),
  source_status_policy='Directsourcesandcurrentcodeinspected;existingtestreceiptsattributed,notnewlyexecutedbythisaudit;inaccessibleparentnotabsence.')
 (OUT/'deliverables.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (OUT/'planning-snapshot.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 text=['# Final-day deliverables and execution handoff — November7,2026','',
 '## Charter','Complete the acceptance/reuse/dependency census for every original deliverable. Descriptive research: the project is known; requirements must be reconciled to current artifacts. Initial recovery reads predated loading ResearchMethodology; this charter governs the remaining audit, not a retrospective claim.','',
 '## Canonical sources','Rank1: originating nativebuild request, user-adopted mandate, current16goal register and exactorientation design. Rank3: currentcode and pinnedtest/source receipts. Prior assistantreports supply leads and retain their original status.','',
 '## Findings ledger','F1: OriginalSUNNY demands continuity and a typedrecognition/execution system; bothremainpartial (initialsource plus mission).',
 'F2: All16goals and8mathematicaloutputs remain accountable, with source-scoped executable partials (mission/model/earlieracceptance).',
 'F3: AcceptedG0/G1 andfour-orientation/Unit002 prototypes provide reuse; remainingnativecontracts, controls,codebook andcrossmodeltrials requireactualchecks.',
 'F4: Existing13modulemodel,scoreanchorconstraints and connectedvisualdelivery are reusable existingwork, not absent.',
 'F5: Broad historicalrectification andglobalorientation requireindependentconstraints; a deadline cannot provide them.','',
 '## Scope filter','Nothing discarded. Engine gates and broaderSUNNY goals remain distinct; allnegativefindings, hypotheses andfuture-stage signals remain retained.','',
 '## Object filter','Codeexistence and earlierreceipts were qualified as existing/source-scoped. No newnativepass, browserpass, blindprediction orhistoricaltruth is inferred by thisaudit.','',
 '## Conclusions','Reuseacceptedfoundationandnativecores (F3,F4), executecriticalpath in dependencyorder, and bind eachcensusrowtofreshreceipts (F1–F5). Thecomplete machine-readable ledger is deliverables.json.','',
 '## Next steps / Risks','Root executes plannedphases and adjusts toactualremainingday. Planning allocationsbelowareelapsedcontrolbudgets,notmeasuredestimates. Eachphase hasanobservableexitcriterion.','',
 '| Phase | Plannedelapsedminutes | Work | Exit |','|---|---:|---|---|']
 for s in plan['schedule']:text.append(f"| {s['phase']} | {s['planned_elapsed_minutes'][0]}–{s['planned_elapsed_minutes'][1]} | {s['work']} | {s['exit_criterion']} |")
 text+=['','All17BetterPlans tools were considered and applied at proportionaldepth in planning-snapshot.json; no tools were silently omitted. Budget has no inventedAPIprice or spend. User remainsauthority; actualJev directs substantiveforks.','',
 'Better Plans progress:','✓ Define What Matters','✓ Map Your Resources','✓ Prepare Against Problems','● Mock Up & Try','● Pull It Together','● Review With Others','',
 'Scout:','- Risk: Exposedmatrixreplays cannot become newhistoricalholdouts by hiding the answers again. Record everytrial sourcefamily/exposure before cross-model claims.','',
 'This subtask changed only audit artifacts. Root native/historical/completionreceipts must supply execution evidence.']
 # The human handoff may be refined after the static census; do not overwrite it.
 if not (OUT/'FINAL_DAY_HANDOFF.md').exists():
  (OUT/'FINAL_DAY_HANDOFF.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
 print(json.dumps({'requirements':len(rows),'counts':result['counts'],'full_mission_complete':False}))

if __name__=='__main__':main()
