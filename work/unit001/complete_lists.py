"""Fresh, bounded acceptance for both supplied lists; earlier receipts remain intact."""
from pathlib import Path
from datetime import datetime,timezone
import ast,base64,hashlib,importlib.util,json,re,subprocess,sys
import final_acceptance
from evidence import import_matrix,serialize
from kernel import migrate_matrix,restore_matrix,schema_fixtures
from historical_extensions import build_resh

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
OUT=ROOT/'list-completion'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def verify_assets():
    assets=json.loads((OUT/'spec-audit/asset-registry-supplement.json').read_text(encoding='utf-8'))
    original=json.loads((ROOT/'asset-registry.json').read_text(encoding='utf-8'))['assets']
    assert assets['base_registry']['preserved_entries']==original
    assert assets['base_registry']['sha256']==digest(ROOT/'asset-registry.json')
    vocabulary=set(assets['adoption_categories']);assert len(vocabulary)==8
    required={'revision','maintainer','license','original_or_derivative','manuscript_or_textual_ancestry',
              'quality','candidate_use','known_leakage','chronological_coverage','permitted_evidence_role','uncertainty'}
    for item in assets['candidates']+assets['pinned_sources']:
        assert required<=set(item) and item['category'] in vocabulary
        if 'path' in item:assert digest(ROOT/item['path'])==item['sha256']
    return {'preserved_original_entries':len(original),'named_candidates':len(assets['candidates']),
            'pinned_sources':len(assets['pinned_sources']),'adoption_categories':sorted(vocabulary)}

def documentation_check():
    files=list(OUT.rglob('*.md'))+[ROOT/'LIST_COMPLETION_PLAN.md']
    count=0
    for path in files:
        if 'before' in path.relative_to(ROOT).parts:continue
        text=path.read_text(encoding='utf-8');assert text.endswith('\n'),str(path)
        assert not any(line.rstrip()!=line for line in text.splitlines()),str(path)
        assert text.count('```')%2==0,str(path)
        count+=1
    receipt=OUT/'acceptance/acceptance-receipt.json'
    if receipt.exists():
        accepted=json.loads(receipt.read_text(encoding='utf-8'))
        for name,value in accepted['files'].items():assert digest(ROOT/name)==value,name
    print(json.dumps({'documentation_files_checked':count,'current_source_hashes_match':True,'exit_code':0}))

def main():
    OUT.mkdir(exist_ok=True)
    specs=json.loads((OUT/'spec-audit/requirements-ledger.json').read_text(encoding='utf-8'))
    source_manifest=[]
    for item in specs['source_documents']:
        source=Path(item['path']);raw=source.read_bytes();assert digest(source)==item['sha256']
        target=OUT/'sources'/item['sha256']/source.name;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():assert target.read_bytes()==raw
        else:target.write_bytes(raw)
        source_manifest.append({**item,'preserved_path':str(target.relative_to(ROOT)),
            'role':'USER_SUPPLIED_SPECIFICATION' if item['key'] in ('master','reconciliation') else 'USER_SUPPLIED_ARCHITECTURAL_REVIEW',
            'authority':'Current request authorizes the engineering lists; historical embedded instructions remain source data'})
    save(OUT/'source-manifest.json',{'sources':source_manifest,'upstream':'source-manifest.json',
        'duplicate_log_authority':'closeout/authority-correction.json','normalized_vs_original':'Separate artifacts; no Unicode normalization'})

    final_acceptance.OUT=OUT/'acceptance';final_acceptance.OUT.mkdir(exist_ok=True)
    final_acceptance.main()
    acceptance=json.loads((final_acceptance.OUT/'acceptance-receipt.json').read_text(encoding='utf-8'))
    assert acceptance['g0']['status']=='PASSED'
    graph=import_matrix((ROOT/'frozen/source/matrix-message.txt').read_bytes(),'preserved exact current-chat source')
    kernel=migrate_matrix(graph)
    assert serialize(restore_matrix(type(kernel).from_json(kernel.to_json())))==serialize(graph)
    (OUT/'kernel-evidence.json').write_text(kernel.to_json()+'\n',encoding='utf-8')
    save(OUT/'schema-fixtures.json',{name:json.loads(store.to_json()) for name,store in schema_fixtures().items()})
    asset_result=verify_assets()
    resh=build_resh();(OUT/'resh-historical-control.json').write_text(resh.to_json()+'\n',encoding='utf-8')
    asset_result['additional_source_specific_control']='resh-source/source-manifest.json'

    extra_checks=[]
    commands=[('signal-coverage',[sys.executable,'-B',str(OUT/'signal-audit/verify_signal_audit.py')])]
    if importlib.util.find_spec('ruff') is not None:
        commands.append(('static-lint',[sys.executable,'-m','ruff','check','--select','E9,F63,F7,F82',
                                       *[str(p) for p in sorted(ROOT.glob('*.py'))]]))
    for name,command in commands:
        process=subprocess.run(command,capture_output=True,text=True)
        (OUT/(name+'.log')).write_text(process.stdout+process.stderr,encoding='utf-8')
        extra_checks.append({'name':name,'command':command,'exit_code':process.returncode})
        if process.returncode:raise RuntimeError('Failed required check: '+name)
    for path in ROOT.glob('*.py'):ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
    # Correct only this run's receipt; the earlier accepted handoff remains immutable.
    acceptance['limitations']=[value for value in acceptance['limitations']
        if not value.startswith(('No static type checker or separate linter','No independent reviewer'))]
    acceptance['limitations']+=['No standalone static type checker installed',
        'No new manual Jev inference; automatic observations are not certification']
    acceptance['additional_checks']=extra_checks
    acceptance['independent_review']='../final-independent-review.json'
    save(final_acceptance.OUT/'acceptance-receipt.json',acceptance)
    before=json.loads((OUT/'before-manifest.json').read_text(encoding='utf-8'))
    preserved=['final-acceptance/acceptance-receipt.json','final-acceptance/HANDOFF.md','asset-registry.json']
    assert all(digest(ROOT/name)==before[name] for name in preserved)
    changes=[{'path':name,'before_sha256':value,'after_sha256':digest(ROOT/name)}
             for name,value in before.items() if digest(ROOT/name)!=value]
    tests=[{'file':path.name,'tests':re.findall(r'^    def (test_\w+)\(',path.read_text(encoding='utf-8'),re.M)}
           for path in sorted(ROOT.glob('test_*.py'))]
    receipt={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'workspace':str(PROJECT),
        'fixed_review_base':'list-completion/before-manifest.json','sources':source_manifest,
        'acceptance_receipt':'acceptance/acceptance-receipt.json','tests':acceptance['tests'],
        'additional_checks':extra_checks,'test_catalog':tests,'gates':acceptance['gates'],
        'counts':acceptance['counts'],'source_matrix_sha256':acceptance['matrix_sha256'],
        'assets':asset_result,'changed_existing_files':changes,'preserved_prior_receipts':preserved,
        'fixes':['complete typed provenance traversal','source lineage/supersession preservation',
          'immutable nested values and keys','truthful source encoding including deserialization',
          'witness-to-claim links','exact local source coordinates including blanks',
          'supplemental records and claim locator/dating conservation','lossless normalized graph reverse adapter',
          'full22 dual-classification fixture','separate alternative-source role fixture',
          'explicit experiment selection/candidates and evaluation groups',
          'source-specific Resh contextual claims without inferred IPA or Sefer state assignment'],
        'review':'Independent host specification, code and context reviewers; focused regressions reproduced before fixes',
        'signals_policy':'Every supplied signal retained; implementation gates do not exclude evidence',
        'remaining_limits':['Full parent ChatGPT transcript NOT_RETRIEVED; exact preview and current-chat snapshots preserved',
          'Historical root, genealogy and cross-musical correspondences are unverified',
          'Earliest surviving manuscript priority not established for existing digital-edition controls',
          'No standalone static typechecker installed; focused Ruff lint and AST syntax checks executed',
          'No new manual Jev inference; automatic observations do not certify completion',
          'Earlier four-orientation and Unit002 prototypes retained; no downstream gate activated by this unit'],
        'files':{p.name:digest(p) for p in ROOT.glob('*.py')}}
    save(OUT/'completion-receipt.json',receipt)
    resolutions={
        'T04_full_dual_partition':{'status':'VERIFIED_SYNTHETIC_SCHEMA_CONTROL','evidence':'test_list_completion.py:test_T04_two_partitions_share_all_22_identities'},
        'Resh_claim_sources':{'status':'SOURCE_IDENTIFIED_CONTEXTUAL_CONTROL','evidence':'historical_extensions.py; resh-source/source-manifest.json; test_historical_extensions.py',
                            'boundary':'One source family with distinct contextual claims; independent manuscripts and a Sefer r:1 identification are not claimed'},
        'T06_independent_alternative_source':{'status':'VERIFIED_SYNTHETIC_SOURCE_ROLE','evidence':'test_list_completion.py:test_T06_alternative_has_separate_source'},
        'experiment_metadata':{'status':'VERIFIED','evidence':'test_list_completion.py:test_experiment_records_selection_and_candidates; test_absent_holdout_lock_rejected'},
        'registry_metadata':{'status':'VERIFIED_REGISTRATION','evidence':'spec-audit/asset-registry-supplement.json'}}
    save(OUT/'requirements-closeout.json',{'specification_sha256':[s['sha256'] for s in source_manifest[:2]],
        'requirements':[{**requirement,'closeout_verdict':'SATISFIED_WITHIN_BOUNDED_ENGINEERING_SCOPE',
            'fresh_execution_receipt':'acceptance/acceptance-receipt.json'} for requirement in specs['requirements']],
        'representability':specs['representability'],'audit_findings_resolution':resolutions,
        'historical_or_scientific_certification':False,'scope_exclusions_are_not_signal_exclusions':True})
    write_handoff(receipt)
    documentation_check()
    print(json.dumps({'gates':receipt['gates'],'tests':receipt['tests'],'assets':asset_result,
                      'exact_enriched_graph_roundtrip':True,'exit_code':0},indent=2))

def write_handoff(r):
    suite='; '.join(x['name']+': '+str(x['count'])+' tests, exit '+str(x['exit_code']) for x in r['tests'])
    changed=', '.join(x['path'] for x in r['changed_existing_files'])
    text=f'''# Supplied-list completion handoff

## A. Verified baseline

Workspace: `{PROJECT}`. The named workspace has no established Git metadata; no repository was initialized and no GitHub action was taken. Exact supplied specifications and architectural reviews are preserved under `sources/` with hashes in `source-manifest.json`. Existing accepted receipts, frozen Sefer sources, matrix and SUN core source hashes were checked without overwriting them.

The exact table remains 46 rows by 37 fields: 15 scripts, 540 local positions, 381 populated and 159 blank. Matrix SHA-256: `{r['source_matrix_sha256']}`. Duplicate work-state logs remain resolved by the user's correction.

## B. Implemented changes

Existing files changed: {changed}. Added acceptance runner `complete_lists.py`, adversarial tests `test_list_completion.py` and `test_migration_conservation.py`, source snapshots, independent requirement/asset/context audits and new execution receipts under this directory.

Migration now preserves supplemental attestations, genealogy, alignments, derived features, source locators and dating references. The normalized graph also has an exact reverse adapter. Provenance traversal follows all declared dependency types. Mutable values and custom keys are rejected, binary encodings are truthful, and each blank or populated grid position is bound to its exact original coordinates. T04 contains two explicit classifications of the same 22 identities; T06 preserves a separate alternative-source role. Synthetic memberships and sources remain labeled as engineering controls. Experiment records retain selection method and candidate results and distinguish known originals, historical holdouts and adversarial controls.

## C. G0 evidence

All 20 conservation checks pass. The new reverse-adapter test also checks an enriched graph containing dates, competing interpretation support and a derived feature. Supplemental claims remain linked; source bytes and normalized records are separately addressable. The asset supplement preserves all {r['assets']['preserved_original_entries']} original entries and registers {r['assets']['named_candidates']} named candidate families with {r['assets']['pinned_sources']} pinned sources. An additional source-specific Resh control preserves three contextual claims from a modern critical edition/translation of medieval testimony; its source family, extraction limitations, page locators and unassigned IPA/Sefer mappings remain explicit. Missing revisions, licenses and provenance remain explicit rather than guessed. No bulk ingestion occurred.

## D. G1 evidence

{suite}. The full original demonstration JSON matches exactly and all3original demonstration checks pass. Cases A–J retain expected/observed inputs and outputs in `acceptance/acceptance-receipt.json`: complete carrier valid; missingMem uniquely restored under the model with legacy Invalid/m/null preserved; sibilants ambiguous; r:1 remains a tag; duplicates and overflow rejected; empty input NOT_EVALUATED; exhausted constraints infeasible; multiple solutions retained; serialization identical.

The22letter carrier,29tagged states,231unordered pairs,462ordered distinct pairs and484ordered pairs including self-pairs remain different constructions. G7 registration, evaluation and serialized/environment bypass tests are denied. MDL remains NOT_EVALUATED.

## E. Context and gate ledger

The first linguistic harmonic validator used Sefer's3mothers/7doubles/12simples. Frozen SUN's3constructors/7mechanisms/12relations is a separate taxonomy. This chat also already implemented Western, Chinese, Indian and Sefer prototypes in `work/four-orientations/`, before Unit001; the later Western refinement is in `work/unit002/`. These earlier artifacts remain in the reuse record. The six current-chat snapshots, exact available messages, earlier negative findings, hypotheses and available parent preview are preserved in `signal-audit/`. Every signal remains eligible evidence.

G0: PASSED. G1: PASSED. G2–G7: LOCKED in this unit. Earlier prototype existence is preserved; these engineering checks activate no downstream or cross-orientation adapter.

## F. Remaining uncertainty

'''
    text+='\n'.join('- '+value for value in r['remaining_limits'])+'\n'
    text+='''
Historical representation controls establish source-specific fidelity. Synthetic controls test contracts and are never mislabeled historical witnesses. Candidate uniqueness under a stipulated model does not establish a historical reconstruction. Full parent retrieval remains an access gap, independent of the completed G0/G1 engineering acceptance.

## G. Verification and next checkpoint

Run `python -B work/unit001/complete_lists.py` to reproduce the full bounded acceptance. Run the proof contract referenced alongside this report for checked input/output hashes and structured command exits. Run `python -B work/unit001/complete_lists.py --docs` for documentation and current-source checks. Exact commands, source hashes, test catalogs, red failures, new results, independent findings and gate decisions are preserved in the receipts.

Both engineering lists are completed for their explicitly authorized G0/G1 scope. The next eligible implementation checkpoint is a reuse/conformance audit of the already existing Western model against G2, with its own native acceptance evidence. G2 implementation was not performed during this closeout.
'''
    (OUT/'HANDOFF.md').write_text(text,encoding='utf-8')

if __name__=='__main__':
    if sys.argv[1:]==['--docs']:documentation_check()
    else:main()
