"""Read-only specification audit; writes only its own derived audit directory."""
from pathlib import Path
import hashlib,json,re

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
DOCS={
 'master':Path(r'C:\Users\Brend\.codex\attachments\ab6716f8-59fa-4e47-9a32-ccb6786bd683\Pasted text.txt'),
 'reconciliation':Path(r'C:\Users\Brend\.codex\attachments\d8e68053-ce05-4af4-8b89-f7564f1ebfe1\Pasted text.txt'),
 'rabbi_review':Path(r'C:\Users\Brend\Desktop\morphiq-one\## Recommended approach add a Rabbi.txt'),
 'rabbi_review_2':Path(r'C:\Users\Brend\Desktop\morphiq-one\## Recommended approach add a Rabbi 2.txt'),
}

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
TEXT={k:p.read_bytes().decode('utf-8') for k,p in DOCS.items()}
def locator(key,start,end):
 text=TEXT[key]
 return dict(path=str(DOCS[key]),sha256=digest(DOCS[key]),character_start=start,character_end=end,
             byte_start=len(text[:start].encode('utf-8')),byte_end=len(text[:end].encode('utf-8')),
             line_start=text[:start].count('\n')+1,line_end=text[:end].count('\n')+1)
def named_locators(term):
 result=[]
 for key,text in TEXT.items():
  match=re.search(re.escape(term),text,re.I)
  if match:result.append(locator(key,match.start(),match.end()))
 return result
def section(key,number):
 text=TEXT[key];pat=r'^# '+re.escape(str(number))+r'\.'
 match=re.search(pat,text,re.M)
 if not match:raise ValueError((key,number))
 end=re.search(r'^# ',text[match.end():],re.M)
 return locator(key,match.start(),match.end()+end.start() if end else len(text))

# A section-level ledger preserves the complete concrete specification alongside
# finer acceptance groups. Runtime success belongs to the root's fresh receipt.
BUNDLES=[
 ('scope_namespaces',('I','II','XIV','XVI'),(1,7,12,17),['evidence.py','sefer.py','contracts.py','frozen/context/SUN_Final_Hypergraph_and_Template_Results_v1.md','CURRENT_CHAT_RECONCILIATION.json'],['test_g0.G0Tests.test_06_local_ordinal_is_not_alignment','test_g1.G1Tests.test_no_fake_mdl'],'STATIC_PRESENT','Scope limits execution; retain all signals, earlier negative findings, and future-model evidence without forced equivalence.'),
 ('source_recovery_checkpoint',('II',),(2,),['source-manifest.json','eu001r-before.json','list-completion/before-manifest.json','closeout/authority-correction.json'],[],'STATIC_PRESENT','Original decoded conversation table and serialized event preserved. Duplicate-log dependency resolved by direct authority correction. No Git metadata or GitHub action is established.'),
 ('raw_grid_normalized_layers',('III','IV'),(4,9),['evidence.py','kernel.py','frozen/source/matrix-message.txt','frozen/source/matrix-event.jsonl'],['test_g0.G0Tests.test_02_all_fields_and_source_roundtrip','test_kernel.KernelTests.test_T01_matrix'],'STATIC_PRESENT','Separate source, parsed grid, and typed evidence; current migrated claim links inspected after root fix.'),
 ('g0_twenty_invariants',('V','XI'),(9,15),['evidence.py','test_g0.py','test_list_completion.py'],['test_g0.G0Tests.test_16_g0_full_validation'],'AWAITING_FRESH_EXECUTION','All20 invariants have defined checks plus original20 unit tests. Latest fixes still need fresh acceptance evidence.'),
 ('source_immutability_and_provenance',('IV',),(4,5),['kernel.py','evidence.py','test_kernel.py','test_list_completion.py'],['test_list_completion.ListCompletionTests.test_derivation_provenance','test_list_completion.ListCompletionTests.test_source_lineage_provenance','test_list_completion.ListCompletionTests.test_source_encoding','test_list_completion.ListCompletionTests.test_unknown_mutable_container_rejected','test_list_completion.ListCompletionTests.test_migrated_claims_are_core_links'],'AWAITING_FRESH_EXECUTION','Six root red tests reproduced prior gaps; current implementation changes inspected, no independent run claimed.'),
 ('g1_original_and_cases_A_J',('VI','VII','XI'),(10,15),['sefer.py','frozen/sefer/harmonic_verifier.py','frozen/sefer/test_harmonic_verifier.py','frozen/sefer/harmonic-demo.json','test_g1.py','test_final_acceptance.py'],['test_g1.G1Tests.test_A_complete','test_g1.G1Tests.test_B_missing_mem_legacy','test_g1.G1Tests.test_C_original_ambiguity','test_g1.G1Tests.test_D_resh','test_g1.G1Tests.test_E_duplicate','test_g1.G1Tests.test_F_overflow','test_g1.G1Tests.test_G_no_profile','test_g1.G1Tests.test_H_candidate_exhaustion','test_g1.G1Tests.test_I_multiple','test_g1.G1Tests.test_J_stability'],'AWAITING_FRESH_EXECUTION','Source-bound native encoding and exact frozen legacy oracle exist. Required fresh6 original tests+3demonstrations pending root.'),
 ('four_axis_receipts_and_mdl',('VIII',),(10,11),['contracts.py','sefer.py','test_g1.py'],['test_g1.G1Tests.test_B_missing_mem_legacy','test_g1.G1Tests.test_no_fake_mdl'],'STATIC_PRESENT','Structural validity, preference, identifiability and history remain distinct; describe returns NOT_EVALUATED and bits null.'),
 ('g7_authorization_denial',('IX',),(13,),['contracts.py','test_g0.py','test_final_acceptance.py','test_closeout.py'],['test_g0.G0Tests.test_17_registry_lock','test_final_acceptance.FinalAcceptanceTests.test_g7_no_environment_bypass','test_closeout.HistoricalControls.test_g7_denied'],'AWAITING_FRESH_EXECUTION','Registry empty and no unlock API; deserialize/config/environment paths denied by code. No cross-orientation adapters populated.'),
 ('experiment_contract_and_exposure',('IV','VIII'),(4,11),['kernel.py','test_kernel.py'],['test_kernel.KernelTests.test_exposure_cannot_be_blind'],'GAP_IDENTIFIED','Contract holds most metadata, but selection_method and candidate-set result lack explicit documented encoding/tests; evaluation_group accepts arbitrary strings.'),
 ('prior_experiments_and_quarantine',('II',),(3,),['CURRENT_CHAT_RECONCILIATION.json','eu001r-verification.json','frozen/earlier-derived','../ariadne-inverse/residual-results.json'],[],'STATIC_PRESENT','All reported findings remain classified; four Etruscan unknowns+one Sabaic unresolved label close381 accounting. Quarantine retains hypotheses, does not delete evidence.'),
 ('asset_registry',('XII',),(6,),['asset-registry.json','list-completion/spec-audit/asset-registry-supplement.json'],[],'SUPPLEMENT_PREPARED','Existing153 entries preserved without changes. Explicit candidate inventory and all8 adoption categories; unavailable metadata marked rather than invented.'),
 ('historical_representation_controls',('IV','XII'),(7,8,10),['closeout_fixtures.py','test_closeout.py','closeout/source-manifest.json'],['test_closeout.HistoricalControls.test_four_real_controls_roundtrip','test_closeout.HistoricalControls.test_epigraphy_unresolved','test_closeout.HistoricalControls.test_orientation_footnote_not_medieval_assertion'],'STATIC_PRESENT','Four real source controls plus synthetic fixtures; history support stays source-specific. Earliest surviving manuscripts not established.'),
 ('verification_procedure',('X','XI'),(14,15),['final_acceptance.py','list-completion/red-receipt.json','list-completion/before-manifest.json'],[],'AWAITING_FRESH_EXECUTION','Required fresh focused/full/original/pipeline/demo/integrity/dependency/documentation checks pending root. Static checker and independent review scope must be reported honestly.'),
 ('handoff_and_gate_ledger',('XII','XV'),(16,),['final-acceptance/HANDOFF.md','list-completion'],[],'AWAITING_FRESH_HANDOFF','Prior handoff is history. New receipt must bind current files and actual outputs; G2-G7 execution remains locked in this unit.'),
 ('failure_policy',('XIII','XVI'),(15,17),['LIST_COMPLETION_PLAN.md','closeout/authority-correction.json'],[],'STATIC_PRESENT','Preserve evidence and explicit missing dependencies; do not force historical equivalence or silently broaden execution.'),
]

def ledger():
 rows=[]
 for ident,master,eu,files,tests,status,note in BUNDLES:
  rows.append(dict(requirement_id=ident,source_sections=[section('master',n) for n in master]+[section('reconciliation',n) for n in eu],
                   artifacts=[dict(path=f,exists=(ROOT/f).exists()) for f in files],checks=tests,status=status,note=note))
 # T04 requires two real assignments of the same22 identities; a count of five
 # classes does not test that contract. Other fixtures may remain synthetic.
 fixtures=[]
 for n in range(1,13):
  fixtures.append(dict(id=f'T{n:02}',evidence='test_g0.py + test_kernel.py' if n==1 else 'kernel.py:schema_fixtures; test_kernel.KernelTests.test_T02_to_T12_representability',
     status='GAP_IDENTIFIED' if n in (4,6) else 'STATIC_PRESENT_AWAITING_FRESH_EXECUTION',
     note='Only three letter_ids and numeric class counts; full common22-carrier memberships not demonstrated' if n==4 else 'Alternative rational not linked to independently identified source; permitted synthetic replacement must retain separate source roles' if n==6 else 'Synthetic fallback explicitly permitted; do not promote to historical validation' if n>1 else 'Original381 populated+159blank positions'))
 gaps=[
  dict(id='T04_full_dual_partition',severity='required',section='EU8+10',evidence='kernel.py:schema_fixtures T04',action='Represent full22letter identities with separate3/7/12 and five-class memberships; keep unsupported source assignments provisional.'),
  dict(id='Resh_claim_sources',severity='evidence_boundary',section='EU10',evidence='T04 resh_realizations claim-A/claim-B',action='Historical Resh pronunciation claims not retrieved in current controls; register source acquisition as unresolved, never identify with r:1. Synthetic fallback allowed for contract testing.'),
  dict(id='T06_independent_alternative_source',severity='required',section='EU8',evidence='T06 ratio and alternative both bare values',action='Demonstrate independent source role for alternative, using labeled synthetic sources if actual source unavailable.'),
  dict(id='experiment_metadata',severity='required',section='EU11',evidence='ExperimentReceipt',action='Explicit selection method and candidate-set results, typed three-group validation or documented tested equivalents.'),
  dict(id='registry_metadata',severity='required',section='EU6',evidence='All153 original assets BIBLIOGRAPHIC_LEAD',action='Use prepared supplement preserving all old entries and explicit unresolved candidate metadata; no mass ingestion.'),
 ]
 return dict(version='EU001R-independent-static-audit-v1',audit_method='Static read of concrete specification, code, tests and captured source metadata; no broad suites or independent historical certification run',
   source_documents=[dict(key=k,path=str(p),sha256=digest(p),bytes=p.stat().st_size) for k,p in DOCS.items()],requirements=rows,representability=fixtures,findings=gaps,
   execution_boundary='The root must bind this ledger to fresh observed acceptance results; static presence alone is not a pass',
   signal_retention='All supplied signals, negative/inconclusive findings and future-stage assets retained. Stage locks restrict execution, not review or preservation.',
   plugin_use={'Riqor evidence-engineering':'SKILL.md inspected and applied to independent read-only audit','automatic_SuperJev':'Not treated as routing or certification','native_plan_tool':'Not available in tool catalog; no native plan update claimed'})

def assets():
 base_path=ROOT/'asset-registry.json';base=json.loads(base_path.read_text(encoding='utf-8'))
 # Keep original dictionaries intact; supplemental metadata never rewrites them.
 original=base['assets']
 vocab=['G0_SAMPLE','G1_SOURCE','FUTURE_NATIVE_MODEL','FUTURE_BLIND_VALIDATION','FUTURE_CROSS_ORIENTATION','NEGATIVE_CONTROL','BIBLIOGRAPHIC_LEAD','RESTRICTED_OR_UNVERIFIED']
 candidates=[
  ('CACCHT',['CACCHT'],'historical_language'),('ETCBC BHSA',['bhsa'],'historical_language'),('ETCBC phono',['/phono'],'historical_language'),('ETCBC Targum',['targum'],'historical_language'),
  ('Lexibank',['lexibank.clld.org'],'historical_language'),('UniMorph',['unimorph.github.io'],'historical_language'),('etymology-db',['droher/etymology-db'],'historical_language'),
  ('documented Aramaic',['aramaic'],'historical_language'),('Egyptian/Coptic datasets',['coptic','egyptian'],'historical_language'),
  ('Paleo-Hebrew Seals v2',['paleo','seals'],'epigraphy'),('Arad ostraca',['arad'],'epigraphy'),('Dead Sea Scroll images',['deadseascroll','dss'],'epigraphy'),('DASI',['dasi'],'epigraphy'),('Karatepe',['karatepe'],'epigraphy'),('Tel Lachish',['lachish'],'epigraphy'),('Proto-Sinaitic editions',['sinaitic'],'epigraphy'),('historical Hebrew paleography datasets',['paleograph'],'epigraphy'),
  ('BibleNLP',['BibleNLP'],'textual'),('eBible',['ebible'],'textual'),('manuscript-specific textual editions',['manuscript'],'textual'),('Sefaria Export',['Sefaria/Sefaria-Export'],'textual'),('Theographic',['theographic'],'textual'),('Geniza manuscript collections',['geniza.princeton.edu'],'textual'),
  ('Sefer Yetzirah recensions',['sefaria.org/Sefer_Yetzirah','seferyetzirah'],'symbolic'),('Exodus 14:19–21',['Exodus'],'symbolic'),("Ibn Ezra's orientation variants",['Ibn_Ezra'],'symbolic'),('Ilanot/Maps of God',['ilanot.org'],'symbolic'),('manuscript-identified 72-name',['72'],'symbolic'),('seal witnesses',['seal'],'symbolic'),('Zohar editions',['zohar'],'symbolic'),
  ('Open 777',['open_777'],'later_comparative'),('Golden Dawn correspondences',['golden'],'later_comparative'),('Tarot mappings',['tarot'],'later_comparative'),('Hermetic diagrams',['hermetic'],'later_comparative'),('modern numerical comparison datasets',['gematria'],'later_comparative')]
 supplements=[]
 for num,(name,patterns,family) in enumerate(candidates,1):
  # Source URLs are copied from supplied reviews. They are NOT newly verified.
  matches=[(i,a) for i,a in enumerate(original) if any(p.lower() in a['url'].lower() for p in patterns) and 'favicons' not in a['url']]
  locs=named_locators(name)
  if not locs:
   for pattern in patterns:
    locs+=named_locators(pattern)
  supplements.append(dict(asset_id=f'candidate:{num:02}',name=name,family=family,category='BIBLIOGRAPHIC_LEAD',
    actual_source_urls=[a['url'] for _,a in matches],source_url_status='REPORTED_URL_NOT_INDEPENDENTLY_VERIFIED' if matches else 'NOT_RETRIEVED',
    original_registry_indices=[i for i,_ in matches],revision='NOT_RETRIEVED',maintainer='NOT_RETRIEVED',license='UNVERIFIED',
    original_or_derivative='NOT_EVALUATED',manuscript_or_textual_ancestry='NOT_RETRIEVED',quality='NOT_EVALUATED',
    candidate_use='Later source-family-aware acquisition or small architecture sample; no ingestion authorized by registration',
    known_leakage='Previously exposed in supplied reviews/mandate; candidate itself not a prospective historical holdout',
    chronological_coverage='LATER_TRADITION_UNTIL_SPECIFIC_EVIDENCE' if family=='later_comparative' else 'UNVERIFIED',
    permitted_evidence_role='discovery lead only',uncertainty='Candidate identity and URL match require source inspection; no revision or historical attestation inferred',
    source_locators=locs,acquired=False))
 controls=json.loads((ROOT/'closeout/source-manifest.json').read_text(encoding='utf-8'))
 pinned=[]
 for meta in controls:
  path=ROOT/'closeout'/meta['path'];assert digest(path)==meta['sha256']
  pinned.append(dict(asset_id='captured:'+meta['id'],name=meta['id'],category='RESTRICTED_OR_UNVERIFIED' if meta['authority']=='FAILED_HTTP_CAPTURE' else 'G0_SAMPLE',
     actual_source_urls=[meta['url']],revision=meta['sha256'],maintainer='Sefaria' if 'sefaria.org' in meta['url'] else 'NOT_VERIFIED',license=meta['license'],
     original_or_derivative=meta['authority'],manuscript_or_textual_ancestry={'hebrew_edition':meta['hebrew_version'],'english_edition':meta['english_version'],'source':meta['version_source']},
     quality='FAILED_SOURCE_ACQUISITION' if meta['authority']=='FAILED_HTTP_CAPTURE' else 'SOURCE_IDENTIFIED_REPRESENTATION_ONLY',candidate_use=meta['role'],
     known_leakage='Previously captured and exposed; not blind',chronological_coverage=meta['age_scope'],permitted_evidence_role=meta['role'],
     uncertainty='Edition-level capture; earliest surviving witness not established. Failed HTML capture is not PDF.',path=str(path.relative_to(ROOT)),sha256=digest(path)))
 excerpt=ROOT/'closeout/Lachish-inspected-excerpt.txt'
 pinned.append(dict(asset_id='captured:Lachish-inspected-excerpt',name='Lachish scholarly uncertainty control',category='G0_SAMPLE',actual_source_urls=['https://doi.org/10.52486/01.00008.2'],revision=digest(excerpt),maintainer='NOT_VERIFIED',license='UNVERIFIED',original_or_derivative='HOST_TRANSCRIPTION_OF_INSPECTED_PRIMARY_SCHOLARLY_SOURCE',manuscript_or_textual_ancestry='Basket B736 Locus C283 as described by publication; original artifact photo not retrieved',quality='ATTRIBUTED_EXCERPT_ONLY',candidate_use='Architecture competing-readings control',known_leakage='Previously exposed',chronological_coverage='Publication-level; artifact chronology not independently certified',permitted_evidence_role='Represent publication claims and competing totals; no original epigraphic-collation claim',uncertainty='Direct original PDF capture failed; excerpt not original PDF bytes',path=str(excerpt.relative_to(ROOT)),sha256=digest(excerpt)))
 frozen=ROOT/'frozen/sefer/harmonic_verifier.py'
 pinned.append(dict(asset_id='captured:original-Sefer-engine',name='Original frozen Sefer implementation',category='G1_SOURCE',actual_source_urls=[],source_url_status='LOCAL_IMPLEMENTATION_SOURCE',revision=digest(frozen),maintainer='Project baseline; authorship provenance retained in source manifest',license='NOT_SEPARATELY_DECLARED',original_or_derivative='ORIGINAL_FROZEN_EXECUTABLE_BASELINE',manuscript_or_textual_ancestry='Stipulated engineering model, not a manuscript witness',quality='REGRESSION_ORACLE',candidate_use='Exact6tests+3demonstrations compatibility',known_leakage='Training/reference fixture; not blind',chronological_coverage='Local implementation version',permitted_evidence_role='Engineering regression only',uncertainty='Historical and harmonic identifications are not certified by regression',path=str(frozen.relative_to(ROOT)),sha256=digest(frozen)))
 return dict(version='EU001R-assets-supplement-v1',base_registry={'path':str(base_path),'sha256':digest(base_path),'original_entry_count':len(original),'preserved_entries':original},
   adoption_categories=vocab,candidates=supplements,pinned_sources=pinned,bulk_ingestion=False,
   source_documents=[dict(path=str(p),sha256=digest(p)) for p in DOCS.values()],
   policy='Preserve every signal and original entry; source-role correction supplements rather than deletes. URL strings copied verbatim from supplied material, not proof of current availability.')

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 data=ledger();asset=assets()
 for name,value in [('requirements-ledger.json',data),('asset-registry-supplement.json',asset)]:
  (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 text=['# Independent specification audit','',
 'Both complete supplied specifications were read against current implementation and test definitions. This is static acceptance mapping; root fresh execution receipts must establish success. No broad suites, source acquisition, frozen-file mutations, model inference or independent historical certification were performed.','',
 '| Requirement | Static audit status | Evidence |','|---|---|---|']
 for row in data['requirements']:text.append('| '+row['requirement_id']+' | '+row['status']+' | '+', '.join(x['path'] for x in row['artifacts'])+' |')
 text+=['','Required findings communicated to root:']
 for gap in data['findings']:text.append('- '+gap['id']+': '+gap['action'])
 text+=['','The asset supplement preserves all153 old registry entries verbatim as JSON values, registers35 named candidate families and8 pinned local sources, declares all8 adoption categories, and supplies exact source hashes/locators. Missing URLs/revisions/maintainers remain explicit. Registration neither acquires data nor validates history.','',
 'Every signal remains eligible evidence: hypotheses, contradictions, negative results, ambiguity and future-stage material are retained. G2–G7 locks govern execution, not retention.','',
 'Plugin evidence: installed Riqor evidence-engineering skill read and applied to this bounded audit. Automatic SuperJev observations were not counted as task routing or certification. Native plan tool absent.']
 (OUT/'AUDIT.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
 print(json.dumps(dict(requirement_groups=len(data['requirements']),representability_cases=len(data['representability']),findings=len(data['findings']),preserved_original_assets=len(asset['base_registry']['preserved_entries']),candidate_families=len(asset['candidates']),pinned_sources=len(asset['pinned_sources']))))

if __name__=='__main__':main()
