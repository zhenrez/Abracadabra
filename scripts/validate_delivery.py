"""Final bounded delivery acceptance: retain failures and verify their exact recoveries."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];WEB=ROOT/'web/delivery-2026-11-07'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))

def main():
    data=load('web/delivery-2026-11-07/data.json');model=load('state/reconstruction/model.json')
    fidelity=load('docs/evidence/reconstruction-verification.json');browser=load('docs/evidence/delivery-2026-11-07/browser-check.json')
    assert fidelity['status']=='passed' and not fidelity['errors']
    assert fidelity['model_sha256']==sha((ROOT/'state/reconstruction/model.json').read_bytes())
    assert data['goals']==load('state/mission.json')['goals'] and len(data['goals'])==16 and len(data['registers'])==8
    for binding in data['manifest']['inputs']:
        if binding['path'] in ['state/reconstruction/model.json','state/delivery-2026-11-07/acceptance.json']:
            assert sha((ROOT/binding['path']).read_bytes())==binding['sha256'],binding['path']
    assert len(model['mathematical_execution'])==22
    integration=load('docs/evidence/native-system-integration.json')
    assert integration['status']=='passed' and integration['sha256']==sha((ROOT/'state/reconstruction/hierarchy-atlas-combined.json').read_bytes())
    assert [len(data['graph'][key]) for key in ['entities','relationships','views']]==[integration[key] for key in ['entities','relationships','views']]
    assert data['graph']['census']['generatedMembershipSlots']==7911
    assert len(data['modules']['master-score']['program']['views'])==15
    for name,value in model['mathematical_execution'].items():
        assert (data['graph'] if name=='hierarchy-atlas-combined' else data['modules'][name])==value,name
    for name,digest in browser['inputs'].items():assert sha((WEB/name).read_bytes())==digest,name
    assert 'reading-operations.js' in browser['inputs']
    assert 'phase-probes.js' in browser['inputs']
    assert any(c['name']=='Minimal phase observation designs preserve historical uncertainty and explicit collisions' for c in browser['checks'])
    groups=len(browser['checks'])
    assert groups==48 and all(c['status']=='passed' for c in browser['checks'])
    assert any(c['name']=='Five exact history controls retain unknown historical bounds' for c in browser['checks'])
    reading_check=next(c for c in browser['checks'] if c['name']=='Source-qualified reading queries and19native reading atlas records retain conditional outputs')
    assert reading_check['readingQueries']=={'coarse':'ɔː|eː','qualifiedNum':'ɔː','qualifiedLev':'eː'}
    assert reading_check['atlasRecords']==19 and reading_check['analysedSyllables']==12
    assert not browser['exceptions'] and not browser['consoleErrors'] and not browser['externalRequests']
    if browser['status']=='failed':
        # Do not turn an original exit1 into an exit0. Verify the separate recovery.
        assert browser.get('cleanupError') and not browser.get('error')
        cleanup=load('state/delivery-2026-11-07/browser-cleanup-current.json')
        assert cleanup['profile']==browser['ownership']['profile']
        assert cleanup['status']=='reaped' and cleanup['remaining_known_processes']==cleanup['remaining_profile_processes']==0
        browser_scope=f'{groups}functional groups passed; original browser command exited1 at cleanup; separate identity-bound cleanup follow-up passed'
    else:
        assert browser['status']=='passed';cleanup=browser['cleanup'];browser_scope=f'{groups}functional groups and captured-browser cleanup passed'
    images=0;occurrences=0
    for figure in data['figures']:
        path=(WEB/figure['url']).resolve();assert path.is_relative_to(WEB.resolve())
        assert sha(path.read_bytes())==figure['sha256']
        with Image.open(path) as image:assert image.width>0 and image.height>0;image.verify()
        for occurrence in figure['occurrences']:
            source=Path(occurrence['path']);assert source.parent.resolve()==Path('C:/Users/Brend/Downloads').resolve()
            assert sha(source.read_bytes())==figure['sha256'];occurrences+=1
        images+=1
    assert images==30 and occurrences==36
    for module in ['score-anchor-constraints','phonological-context-constraints','phonological-history-constraints','reading-operations']:
        unit=model['mathematical_execution'][module]
        for item in unit['inputSnapshots']:assert sha((ROOT/item['snapshotPath']).read_bytes())==item['sha256']
        for item in unit['codeBindings']:assert sha((ROOT/item['path']).read_bytes())==item['sha256']
    from jev_tool import verify_log
    jev=verify_log();assert jev['status']=='intact' and jev['count']>=62
    bowl=load('state/delivery-2026-11-07/symbol-contact/bowls/connector-acquisition/primary-text-record.json')
    transport=Path(bowl['transport_path']).read_bytes()
    assert sha(transport)==bowl['transport_sha256']
    content=json.loads(transport)['content'][0]['text']
    assert sha(content.encode('utf8'))==bowl['text_sha256_utf8']
    start,end=bowl['target_spelling_span']
    assert content[start:end]=='שומורו'
    assert [bowl['counts'][key]['waw_count'] for key in ['published_connector_reading','earlier_secondary_discovery_lead','BHS_comparator_letters_normalized_from_fragmented_row']]==[3,2,1]
    import importlib.util
    guard=load('state/delivery-2026-11-07/symbol-contact/bowls/connector-acquisition/proofline-validation.json')
    plugin=Path(guard['verifier_path']);assert sha(plugin.read_bytes())==guard['verifier_sha256']
    spec=importlib.util.spec_from_file_location('delivery_primary_span_proofline',plugin)
    proof=importlib.util.module_from_spec(spec);spec.loader.exec_module(proof)
    primary_span=proof.verify(load('state/delivery-2026-11-07/symbol-contact/bowls/connector-acquisition/proofline-package.json'))
    assert primary_span['valid'] and primary_span['root_hash']==guard['verification']['root_hash']
    guide=load('docs/evidence/delivery-2026-11-07/guide-browser-check.json')
    assert guide['schema']=='sunny.system-guide-browser.v1' and guide['status']=='passed'
    assert len(guide['checks'])==7 and all(c['status']=='passed' for c in guide['checks'])
    assert len(guide['views'])==len(data['graph']['views'])
    guide_interactions=sum(v['unitsChecked'] for v in guide['views'])
    assert next(c['unitInteractions'] for c in guide['checks'] if 'unitInteractions' in c)==guide_interactions
    assert not guide.get('exceptions',[]) and not guide.get('consoleErrors',[]) and not guide.get('externalRequests',[])
    for name,digest in guide['inputs'].items():assert sha((WEB/name).read_bytes())==digest,name
    assert guide['cleanup']['remaining_known_processes']==guide['cleanup']['remaining_profile_processes']==0
    systems=load('docs/evidence/delivery-2026-11-07/systems-browser-check.json')
    assert systems['status']=='passed' and len(systems['checks'])==13
    assert not systems['exceptions'] and not systems['consoleErrors'] and not systems['externalRequests']
    for name,digest in systems['inputs'].items():assert sha((WEB/name).read_bytes())==digest,name
    for name,digest in systems['sourceInputs'].items():assert sha((ROOT/name).read_bytes())==digest,name
    assert systems['cleanup']['remaining_known_processes']==systems['cleanup']['remaining_profile_processes']==0
    independent=load('docs/evidence/native-system-independent-audit.json')
    assert independent['status']=='passed'
    contract=load('state/delivery-2026-11-07/guards/native-systems-contract.json')
    # The installed plugin is outside this workspace; read/execute only, with no cache edit.
    check_runner=Path('C:/Users/Brend/.codex/plugins/cache/created-by-me-remote/superjev/0.1.5/skills/superjev/scripts/proof.py')
    check_spec=importlib.util.spec_from_file_location('delivery_superjev_checks',check_runner)
    check_guard=importlib.util.module_from_spec(check_spec);check_spec.loader.exec_module(check_guard)
    checked=check_guard.verify(contract,ROOT/'state/delivery-2026-11-07/guards/native-systems/85bc5320751741a1a7347a8f086d02b7.receipt.json')
    assert checked['checks_verified'] is True and checked['completion_verified'] is False
    from verify_native_large_bindings import main as verify_large
    verify_large()
    known=['README.md','CONTINUE.md','state/task.json','state/superjev-checkpoint.json','docs/HUMMBL_PLAN.md','docs/PLUGIN_CAPABILITIES.md',
        'scripts/assemble_current_model.py','scripts/verify_reconstruction.py','state/reconstruction/model.json',
        'state/reconstruction/score-anchor-constraints.json','state/reconstruction/phonological-context-constraints.json','state/reconstruction/phonological-history-constraints.json','state/reconstruction/reading-operations.json',
        'scripts/derive_phase_probe_designs.mjs','tests/phase-probe-designs.test.mjs','tests/reading-integration.test.mjs','state/reconstruction/orientation-predictions.json','src/reading-relations.ts','dist/reading-relations.js','scripts/derive_reading_operations.mjs','scripts/integrate_reading_hierarchy_score.mjs','tests/reading-relations.test.mjs',
        'src/phonological-history.ts','dist/phonological-history.js','scripts/derive_phonological_history.mjs','scripts/retrieve_temporal_prior_art.py','tests/phonological-history.test.mjs',
        'docs/reconstruction/CURRENT_MODEL.md','docs/evidence/reconstruction-verification.json']
    known += ['scripts/'+name for name in ['build_delivery.py','delivery_server.py','start-delivery.ps1','derive_score_anchors.py',
        'build_delivery_acceptance.py','guard_delivery_evidence.py','checkpoint_delivery.py','retrieve_howard_qames.py','derive_phonological_context.py','validate_delivery.py']]
    known += ['tests/'+name for name in ['delivery_test.py','delivery-browser.mjs','score_anchors_independent.py','phonological_context_independent.py']]
    known += ['state/reconstruction/'+name+'.json' for name in ['indian-hierarchy','western-expanded','chinese-expanded','native-class-constructors','biblical-genealogies','upper-legion-color-constraints']]
    known += ['src/generational-classes.ts','dist/generational-classes.js','scripts/derive_native_classes.mjs','scripts/integrate_system_atlas.mjs','scripts/checkpoint_native_systems.py','scripts/verify_native_large_bindings.py','tests/generational-classes.test.mjs','tests/native-system-integration.test.mjs','tests/delivery-data-hydration.test.mjs','tests/delivery-systems-browser.mjs']
    for folder in ['web/delivery-2026-11-07','docs/delivery-2026-11-07','state/delivery-2026-11-07']:
        known += [str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/folder).rglob('*') if p.is_file() and p.name!='final-validation.json']
    changes=[{'path':p,'sha256':sha((ROOT/p).read_bytes()),'bytes':(ROOT/p).stat().st_size} for p in sorted(set(known)) if (ROOT/p).is_file()]
    report={'schema':'sunny.delivery-validation.v1','checkedAt':datetime.now(timezone.utc).isoformat(),'status':'passed-with-recorded-recovery','exit_code':0,
        'modelSha256':fidelity['model_sha256'],'sourceFidelity':{'modules':len(model['mathematical_execution']),'errors':0,'scope':fidelity['boundary']},
        'browser':{'functionalGroups':groups,'scope':browser_scope,'capturedBrowserProcessesRemaining':0,'newInferenceInThisReplay':False},
        'visualGuide':{'functionalGroups':len(guide['checks']),'sourceViews':len(guide['views']),'viewUnitInteractions':guide_interactions,'currentHashesMatch':True,'capturedBrowserProcessesRemaining':0},
        'nativeSystemsBrowser':{'functionalGroups':len(systems['checks']),'httpAndOffline':True,'capturedBrowserProcessesRemaining':0},
        'boundedMathematicalChecks':{'focusedTests':47,'exactHydrationTests':1,'independentNativeIntegrationGroups':14,'independentPhaseProbePairs':10296,'guardStatus':checked['status'],'completeMissionCertified':False},
        'images':{'originalOccurrences':occurrences,'distinctImagesDecoded':images,'sourceBytesMatch':True},
        'jevReceiptChain':jev,'changedOrGeneratedFiles':changes,
        'primaryPublicationText':{'exactSpellingSpan':'שומורו','wawCounts':[3,2,1],'prooflineValid':primary_span['valid'],
            'sourceLayer':bowl['source_layer'],'originalPdfAcquired':False,'independentInkCollation':False},
        'scientificCompletion':False,'remaining':'See the unchanged16goal/8output full-scope acceptance matrix. Original sound/grammar, complete global geometry/alignment, full native hierarchies, downstream rectification and blind prediction remain unresolved.',
        'unverified':['Whole-project test suite','Complete semantic corpus coverage','Manuscript authenticity and original phonetic intention','Hosted provider account/billing','Uninterrupted background cadence'],
        'scope':'Current scoped artifacts and exact recovery evidence. The earlier failed browser commands remain failed; this is a separate aggregate check.'}
    (ROOT/'state/delivery-2026-11-07/final-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='changedOrGeneratedFiles'},ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
