"""Read-only validation of the latest delivery, source conservation and package."""
from pathlib import Path
import ast,csv,hashlib,json,sys

ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1]

def require(condition,message):
    if not condition:raise ValueError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def inside(root,name):
    base=Path(root).resolve();path=(base/name).resolve()
    require(path.is_relative_to(base),'Reference escapes declared evidence directory')
    return path


def verify_receipt_outputs(output_directory,receipt):
    require(isinstance(receipt.get('outputs'),dict) and bool(receipt['outputs']),'No declared receipt outputs')
    for name,digest in receipt['outputs'].items():
        path=inside(output_directory,name)
        require(path.is_file() and sha(path)==digest,'Output missing or changed: '+name)
    return len(receipt['outputs'])


def verify_rows(census,current):
    rows=current.get('requirements',())
    require(len(rows)==len(census['requirements'])==106,'Original requirement count changed')
    require([r['original'] for r in rows]==census['requirements'],'An original requirement or original status changed')
    require(len({r['original']['id'] for r in rows})==106,'Duplicate requirement identity')
    for row in rows:
        assessment=row.get('engineering_assessment',{})
        require(bool(assessment.get('status')) and bool(assessment.get('evidence_refs')),'Current assessment/evidence absent')
        require(isinstance(assessment.get('remaining_dependencies'),list),'Dependency status absent')
    return len(rows)


def docs():
    paths=[ROOT/'HANDOFF.md',ROOT/'REQUIREMENTS.md',ROOT/'PLAN.md',ROOT/'ACTIVE_CHECKPOINT.md',
           ROOT/'dashboard/README.md',ROOT/'canonical-features/README.md']
    for path in paths:
        text=path.read_text(encoding='utf-8')
        require(text.endswith('\n') and not any(line.rstrip()!=line for line in text.splitlines()),'Documentation whitespace invalid: '+path.name)
        require(text.count('```')%2==0,'Unclosed documentation code fence')
    require(len((ROOT/'REQUIREMENTS.md').read_text(encoding='utf-8').splitlines())>=110,'Requirement view incomplete')
    print(json.dumps({'documentation_files':len(paths),'status':'PASSED','read_only':True}))


def verify_runtime():
    receipt=load(ROOT/'runtime/project-final-checks.json')
    require(receipt.get('exit_code')==0 and receipt.get('inputs_unchanged') is True,'Final full-project check did not pass')
    counts=receipt.get('observed_counts',{})
    require(type(counts.get('tests')) is int and counts['tests']>=99 and counts.get('pass')==counts['tests'] and all(counts.get(name)==0 for name in ('fail','cancelled','skipped')),'Final complete project population was not fully observed')
    require(bool(receipt.get('checked_inputs')),'Project source bindings absent')
    for name,digest in receipt['checked_inputs'].items():
        require(sha(inside(PROJECT,name))==digest,'Checked runtime input changed: '+name)
    print(json.dumps({'runtime_status':'PASSED','tests':counts['tests'],'read_only':True,'historical_failures_preserved':True}))


def verify_canonical():
    folder=ROOT/'results/canonical-features-v2';manifest=load(folder/'manifest.json')
    for name,record in manifest['files'].items():
        path=inside(folder,name)
        require(path.stat().st_size==record['bytes'] and sha(path)==record['sha256'],'Canonical payload changed: '+name)
    sys.path.insert(0,str(ROOT/'canonical-features'))
    import canonical_features
    import numpy as np
    with np.load(folder/'matrix.npz',allow_pickle=False) as arrays:
        bundle={name:arrays[name].copy() for name in ('vector','mask','normalized')}
    bundle.update(sidecar=load(folder/'vectors.json'),source_bytes=(folder/'source.tsv').read_bytes())
    require(canonical_features.verify_bindings(bundle),'Canonical source/derived binding failed')
    require(sha(folder/'source.tsv')==manifest['source']['sha256'],'Canonical original source bytes changed')
    print(json.dumps({'canonical_features':'PASSED','shape':[15,36,20],'geometry':'STRICT_UNAVAILABLE','read_only':True}))


def verify():
    verify_runtime()
    verify_canonical()
    receipt=load(ROOT/'results/delivery-receipt.json')
    count=verify_receipt_outputs(ROOT/'results',receipt)
    require(receipt.get('full_mission_complete') is False,'Full mission incorrectly certified')
    for check in receipt['checks']:
        require(check['exit_code']==0,'Failed required execution: '+check['name'])
        detail=load(inside(ROOT/'results',check['output_ref']))
        require(detail['exit_code']==check['exit_code'] and detail['command']==check['command'],'Command receipt mismatch')
        if 'unittest' in check['command']:
            require(type(check.get('observed_tests')) is int and check['observed_tests']>0,'Unverified unit-test count')
    original=next(c for c in receipt['checks'] if c['name']=='original-Sefer')
    require(original['observed_tests']==6,'Original Sefer suite not fully observed')
    require(receipt['historical_registry_empty'] and receipt['unsupported_historical_call_denied'],'Historical authorization guard failed')

    base=PROJECT/'work/unit001';manifest=load(base/'source-manifest.json')
    source=base/'frozen/source/matrix-message.txt'
    require(sha(source)==manifest['source']['sha256']==receipt['matrix_sha256'],'Matrix source hash changed')
    sys.path.insert(0,str(base))
    from evidence import import_matrix,roundtrip_source,verify_g0_conservation
    graph=import_matrix(source.read_bytes(),manifest['source']['locator'])
    require(roundtrip_source(graph)==source.read_bytes() and verify_g0_conservation(graph)['status']=='PASSED','Source conservation failed')
    require(receipt['counts']=={'positions':540,'populated':381,'empty':159},'Source reconciliation changed')
    for group in ('baseline','earlier_derived','context'):
        for item in manifest[group].values():require(sha(base/item['path'])==item['sha256'],'Frozen source changed: '+item['path'])
    for item in (manifest['source']['event'],manifest['attachment']):
        require(sha(base/item['path'])==item['sha256'],'Frozen event/attachment changed')
    changes=[]
    for name,digest in {**manifest['src_hashes'],**manifest['existing_work_hashes']}.items():
        if sha(PROJECT/name)==digest:continue
        require(name.replace('\\','/')=='src/worker.ts','Unexpected protected source change: '+name)
        change=load(ROOT/'runtime/approved-source-change.json')
        require(change['before_sha256']==digest and change['after_sha256']==sha(PROJECT/name),'Worker delta lacks source binding')
        require(sha(PROJECT/change['preserved_before'])==digest,'Worker preimage does not match frozen original')
        require(change in receipt.get('protected_source_exceptions',()),'Latest delivery omitted the operational source exception')
        changes.append(name)
    require(receipt.get('original_demo_equal') is True and receipt.get('original_demo_cases')==3,'Original demonstration verification missing')
    demos=load(ROOT/'results/original-demonstrations.json')
    require(demos['exit_code']==0 and demos['full_json_equal'] is True and len(demos['cases'])==3,'Full demo/adapter receipt invalid')
    for case in demos['cases']:
        require(case.get('passed',True) and case['expected']==case['observed'],'Legacy demonstration output changed')

    current=load(ROOT/'current-deliverables.json');census=load(ROOT/'audit/deliverables.json')
    sys.path.insert(0,str(ROOT))
    import mathematical_sources
    version_path=ROOT/'audit/mathematical-source-versions/version-manifest.json'
    versions=mathematical_sources.load_registry(version_path,census,PROJECT)
    require(receipt['mathematical_source_versions']['sha256']==sha(version_path),'Mathematical source-version registry changed')
    for requirement in census['requirements']:
        if requirement['scope']!='original_mathematical_output':continue
        view=load(ROOT/('results/eight-outputs/'+requirement['id']+'.json'))
        expected=[mathematical_sources.resolve_source(item,versions,PROJECT,requirement['id']) for item in requirement['evidence']]
        require(view['source_versions']==expected,'Original/current mathematical versions were collapsed or changed')
    rows=verify_rows(census,current)
    for row in current['requirements']:
        for ref in row['engineering_assessment']['evidence_refs']:
            require((PROJECT/ref).is_file(),'Current assessment evidence missing: '+ref)
    require(current['original_census_sha256']==sha(ROOT/'audit/deliverables.json'),'Original census hash changed')
    require(current['delivery_receipt_sha256']==sha(ROOT/'results/delivery-receipt.json'),'Package is stale relative to latest delivery')
    require(current.get('full_mission_complete') is False and current['external_publication']=='NOT_PERFORMED','Packaging scope changed')
    with (ROOT/'current-deliverables.csv').open(encoding='utf-8',newline='') as f:csvrows=list(csv.DictReader(f))
    require(len(csvrows)==106,'CSV requirement count differs')
    for csvrow,row in zip(csvrows,current['requirements']):
        require(csvrow['id']==row['original']['id'] and csvrow['original_requirement']==row['original']['requirement'] and csvrow['original_status']==row['original']['status'],'CSV altered an original value')
    for name,validation in receipt['native_validations'].items():require(validation['status']=='VALID','Native profile invalid: '+name)
    west=load(ROOT/'results/western-native.json');east=load(ROOT/'native-east/native-results.json')
    require(west['native_gate']=='PASSED_BOUNDED_G2_NATIVE' and west['nonclosure']['comma']=='531441/524288','Western native result missing')
    require(east['melakarta']['count']==72 and len(east['melakarta']['madhyama_pairs'])==36,'Indian native counts changed')
    require(len(east['chinese']['twelve_lu'])==12,'Chinese generation changed')
    for path in ROOT.rglob('*.py'):ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
    browser_path=ROOT/'dashboard/browser-verification.json'
    browser={'status':'NOT_RETRIEVED'}
    if browser_path.is_file():
        browser=load(browser_path)
        require(browser['status']=='PASSED' and not browser['page_errors'],'Browser receipt is not a pass')
        for name in browser['screenshots']:require(inside(ROOT/'dashboard',name).is_file(),'Browser screenshot missing')
        build=load(ROOT/'dashboard/build-receipt.json')
        require(sha(ROOT/'dashboard/SUN_ARIADNE_Workbench.html')==build['html_sha256'],'Dashboard build hash changed')
        binding=load(ROOT/'dashboard/browser-data-bindings.json')
        names={'html_sha256':'dashboard/SUN_ARIADNE_Workbench.html','template_sha256':'dashboard/workbench.template.html',
            'build_receipt_sha256':'dashboard/build-receipt.json','browser_receipt_sha256':'dashboard/browser-verification.json',
            'source_sha256':'results/dashboard-data.json','source_snapshot_sha256':'dashboard/dashboard-data.snapshot.json',
            'current_delivery_sha256':'current-deliverables.json','current_delivery_snapshot_sha256':'dashboard/current-deliverables.snapshot.json',
            'sefer_snapshot_sha256':'dashboard/sefer-baseline.snapshot.json','browser_script_sha256':'dashboard/browser_check.mjs'}
        for key,name in names.items():require(binding.get(key)==sha(ROOT/name),'Browser evidence is stale: '+key)
        for name,record in binding['screenshots'].items():require(sha(inside(ROOT/'dashboard',name))==record['sha256'],'Screenshot changed')
        require(binding['sefer_baseline_sha256']==sha(PROJECT/'work/unit001/final-acceptance/acceptance-receipt.json'),'Sefer source binding changed')
    for record in current.get('project_test_records',()):
        require(sha(PROJECT/record['path'])==record['sha256'],'Project test receipt changed after packaging')
    docs()
    print(json.dumps({'status':'PASSED','read_only':True,'receipt_output_hashes':count,'original_rows':rows,
                      'source_positions':540,'worker_exceptions':changes,'browser_status':browser['status'],
                      'full_mission_complete':False,'verification_scope':'Artifact integrity; recorded project failures remain failures',
                      'project_test_records':current.get('project_test_records',[])}))


if __name__=='__main__':
    try:
        if sys.argv[1:]==['--docs']:docs()
        elif sys.argv[1:]==['--runtime']:verify_runtime()
        elif sys.argv[1:]==['--canonical']:verify_canonical()
        elif not sys.argv[1:]:verify()
        else:raise ValueError('Only --docs or read-only default verification is supported')
    except (ValueError,KeyError,FileNotFoundError,AssertionError) as error:
        print(json.dumps({'status':'FAILED','error':str(error),'read_only':True}));raise SystemExit(1)
