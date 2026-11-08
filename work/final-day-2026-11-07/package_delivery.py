"""Package the current bounded delivery without rewriting the original census."""
from pathlib import Path
from datetime import datetime,timezone
import copy,csv,hashlib,json

ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1]
PREFIX='work/final-day-2026-11-07/'

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def write_json(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def assessment(row):
    key=row['id'];scope=row['scope'];refs=[]
    status='PARTIAL_RETAINED_WITH_DEPENDENCIES'
    remaining=[row['remaining']] if row.get('remaining') else []
    remaining+=['Dependency '+str(x) for x in row.get('dependencies',())]
    if key.startswith('FOUNDATION:') or key in ('EG0','EG1'):
        status='PASSED_BOUNDED_G0_G1_ENGINEERING';refs=['results/delivery-receipt.json','results/original-demonstrations.json']
        remaining+=['Historical interpretation and full mission conclusions remain separate from engineering acceptance.']
    elif key in ('W01','W02','W03','W04','EG2'):
        status='PASSED_BOUNDED_WESTERN_NATIVE_PROFILE';refs=['results/western-native.json','western/source-profiles.json']
        if key=='EG2':remaining+=['Full historical Western profiles remain partial; see W05 and W06.']
    elif key.startswith('C0') or key=='EG3':
        status='PASSED_BOUNDED_CHINESE_NATIVE_PROFILE';refs=['native-east/native-results.json','native-east/source-profiles.json']
        remaining+=['Source-specific generation/function profile; no universal ancient intonation or instrument census inferred.']
    elif key in ('I01','I02','I03','EG4'):
        status='PASSED_SEPARATE_BOUNDED_INDIAN_NATIVE_PROFILES';refs=['native-east/native-results.json','native-east/source-profiles.json']
        remaining+=['Traditional grama units and later melakarta grammar remain separate; frequency tuning and broader raga practice remain source dependent.']
    elif key in ('P01','P02','EG5'):
        status='PASSED_SOURCE_DEFINED_PHONETIC_NUMERIC_CONTROLS';refs=['results/phonetic-numeric-controls.json','controls.py']
        remaining+=['Control covers 25 varga consonants and the selected numerical convention; no acoustic measurements or glyph/music assignment.']
    elif key in ('W05','W06','I04'):
        status='PARTIAL_SOURCE_OR_PERFORMANCE_COVERAGE';refs=['western/source-profiles.json','native-east/source-profiles.json']
        remaining+=['Historical witness transcription, broader performance grammar or measured tuning is not supplied by the finite native control.']
    elif key in ('B01','B02','B03','EG6'):
        status='MEASURED_CONDITIONAL_CODEC; HISTORICAL_MODEL_SELECTION_NOT_EVALUATED'
        refs=['results/coding-baselines.json','results/native-description-measurements.json']
        remaining+=['Compare independently justified musical/linguistic models on source-family-independent withheld material; current codes are conditional representation costs.']
    elif key in ('X01','X02','X03','EG7'):
        status='EXACT_MATHEMATICAL_CONTROLS; HISTORICAL_RECONSTRUCTION_LOCKED'
        refs=['results/mathematical-comparisons.json','results/common-encodings.json','comparisons.py']
        remaining+=['Historical certification needs independently justified source-specific adapters, exposure-aware predictions and external anchors.']
    elif key=='INV02':
        status='VERIFIED_CANONICAL_FEATURE_PIPELINE; HISTORICAL_VALUES_UNCERTAIN'
        refs=['results/canonical-features-v2/manifest.json','results/canonical-features-v2/summary.json','canonical-features/canonical_features.py']
        remaining+=['Coarse15-dimensional articulation retains documented losses; alternatives, sequences and letter names require their typed sidecars.']
    elif key.startswith('INV'):
        status='BOUNDED_INVERSE_CONTROLS; HISTORICAL_ROOT_UNIDENTIFIED'
        refs=['results/coding-baselines.json','results/inverse-identifiability.json',
              '../ariadne-inverse/carrier-statistics.json','../ariadne-inverse/residual-results.json']
        if key=='INV03':remaining+=['Historical glyph stroke topology needs source images; existing modern-font geometry remains a proxy.']
        remaining+=['A frequency-threshold codec basis and finite countermodels do not recover a unique ancient state machine.']
    elif key.startswith('PIPELINE:'):
        status='PRESERVED_PIPELINE_REGRESSIONS_PASSED';refs=['results/checks/preserved-linguistic-pipeline.json']
        remaining+=['Earlier negative and conditional findings remain in their original source scope.']
    elif scope=='original_mathematical_output':
        status='PARTIAL_CONNECTED_ORIGINAL_OUTPUT';refs=['results/eight-outputs/'+key+'.json']
        remaining+=['Linked source-scoped implementations remain conditional; the full original mathematical output is not certified complete.']
    elif scope=='visual_delivery':
        status='LOCAL_INTEGRATED_DASHBOARD; BROADER_VIEWS_PARTIAL'
        refs=['dashboard/SUN_ARIADNE_Workbench.html','dashboard/browser-verification.json']
        remaining+=['Browser evidence covers the integrated native/evidence dashboard; broader original atlas and geometry views retain their own limits.']
    else:
        refs=['results/delivery-receipt.json','audit/deliverables.json']
        remaining+=['Original research/source/global-law conditions remain open; no universal completion is inferred from this package.']
    return {'status':status,'evidence_refs':[PREFIX+p for p in refs],
            'remaining_dependencies':list(dict.fromkeys(remaining)),
            'authority':'Fresh bounded engineering evidence, preserving original requirement and status verbatim'}


def current_rows(census,delivery):
    if delivery.get('full_mission_complete') is not False:raise ValueError('Unjustified full-mission promotion')
    return [{'original':copy.deepcopy(row),'engineering_assessment':assessment(row)} for row in census['requirements']]


def capability_records(include_browser=False):
    def record(name,path,scope,status):
        file=ROOT/path
        return {'capability':name,'receipt':PREFIX+path,'available':file.is_file(),
                'sha256':digest(file) if file.is_file() else None,
                'observed_status':status if file.is_file() else 'NOT_RETRIEVED','scope':scope}
    records=[record('Jev','jev-strategy.json','Actual bounded sequencing inference, not scientific truth or completion certification','LIVE_INFERENCE_RECORDED'),
        record('Wolfram','capability-receipts/wolfram-exact.json','Actual independent exact arithmetic/control results','RESULT_RECORDED'),
        record('Prumo','capability-receipts/prumo-result.json','Local exact arithmetic parser; uncalibrated weights are not truth probabilities','LOCAL_RESULT_RECORDED'),
        record('Julius','capability-receipts/julius-attempt.json','Authentication/error response; no successful numerical result claimed','AUTHENTICATION_RESPONSE_ONLY'),
        record('Proofline','capability-receipts/proofline-verification.json','Exact checkpoint span/hash fidelity only; no historical certification','LOCAL_VERIFIER_RESULT'),
        record('Mathbox','western/computation-001/manifest.json','Actual bounded exact computation; read run.status and validator output','BOUNDED_RUN_RECORDED'),
        record('Jev final sequencing','jev-final-sequence.json','Second live operational choice; no completion or historical verdict','LIVE_INFERENCE_RECORDED')]
    if include_browser:
        records.append(record('Browser','dashboard/browser-verification.json','Actual local headless Chromium interaction; no hosted publication','BROWSER_RECEIPT_PRESENT'))
    return records


def project_test_records():
    return [{'path':PREFIX+str(p.relative_to(ROOT)).replace('\\','/'),'sha256':digest(p),
             'command':load(p).get('command'),'exit_code':load(p).get('exit_code'),
             'observed_counts':load(p).get('observed_counts')}
            for p in sorted((ROOT/'runtime').glob('project*-checks.json'))]


def current_package(census,delivery):
    rows=current_rows(census,delivery)
    # The browser consumes this ledger; its later receipt cannot be a ledger input.
    return {'schema':'sun.current-deliverables.v1','generated_utc':delivery['timestamp_utc'],
        'original_census':'audit/deliverables.json','original_census_sha256':digest(ROOT/'audit/deliverables.json'),
        'delivery_receipt':'results/delivery-receipt.json','delivery_receipt_sha256':digest(ROOT/'results/delivery-receipt.json'),
        'requirements':rows,'requirements_count':len(rows),'full_mission_complete':False,
        'capabilities':capability_records(),'external_publication':'NOT_PERFORMED',
        'project_test_records':project_test_records()}


def main():
    census=load(ROOT/'audit/deliverables.json');delivery=load(ROOT/'results/delivery-receipt.json')
    package=current_package(census,delivery);rows=package['requirements']
    write_json(ROOT/'current-deliverables.json',package)
    with (ROOT/'current-deliverables.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.writer(f);writer.writerow(['id','scope','original_requirement','original_status','current_engineering_assessment','evidence_refs','remaining_dependencies'])
        for row in rows:
            o=row['original'];a=row['engineering_assessment']
            writer.writerow([o['id'],o['scope'],o['requirement'],o['status'],a['status'],json.dumps(a['evidence_refs'],ensure_ascii=False),json.dumps(a['remaining_dependencies'],ensure_ascii=False)])
    lines=['# Original requirements and current evidence','',
        'All original rows and statuses remain verbatim in current-deliverables.json and CSV. This table is a readable view; original audit statuses are retained alongside current engineering assessments. Full mission completion remains false.','',
        '| ID | Original requirement | Original audit status | Current engineering assessment |',
        '| --- | --- | --- | --- |']
    def cell(value):return str(value).replace('|','\\|').replace('\r','').replace('\n',' ')
    for row in rows:
        o=row['original'];a=row['engineering_assessment']
        lines.append('| '+' | '.join(cell(v) for v in (o['id'],o['requirement'],o['status'],a['status']))+' |')
    lines+=['','Exact source and evidence links, dependency conditions and original source hashes are in the JSON register. Native passes are qualified by their admitted profiles. Historical root identification, full geometric law, calendar/zodiac conclusions and independently withheld historical prediction remain open.','']
    (ROOT/'REQUIREMENTS.md').write_text('\n'.join(lines),encoding='utf-8')
    browser=load(ROOT/'dashboard/browser-verification.json') if (ROOT/'dashboard/browser-verification.json').exists() else {}
    browser_text=('Actual local Chromium receipt: '+str(browser.get('status'))+'; '+str(len(browser.get('checks',())))+' check groups; '+str(len(browser.get('page_errors',())))+' page errors.') if browser else 'Browser receipt NOT_RETRIEVED; no browser pass is claimed.'
    checklines='\n'.join('- '+x['name']+': exit '+str(x['exit_code'])+(', '+str(x['observed_tests'])+' observed tests' if x.get('observed_tests') is not None else '') for x in delivery['checks'])
    capabilities='\n'.join('- '+r['capability']+': '+r['observed_status']+'. '+r['scope'] for r in capability_records(True))
    worker=load(ROOT/'runtime/approved-source-change.json') if (ROOT/'runtime/approved-source-change.json').exists() else None
    worker_text='The operational worker completion-timer race and observed cleanup-helper deadline were addressed; capture remains bounded at15seconds, cleanup at30seconds. The test-only ownership assertion uses exact creation identities and fails closed for unverifiable probes. Prior raw-PID failure cause remains unresolved; no claim of observed PID reuse is made. Source/test preimages, before/after hashes and reviews are retained under runtime/. Mathematical kernel files remain protected.' if worker else 'No operational worker exception is recorded.'
    runtime_text='\n'.join('- '+p['path']+': exit '+str(p['exit_code'])+'; '+json.dumps(p['observed_counts'],sort_keys=True) for p in package['project_test_records']) or 'No durable full-project test receipt is available.'
    text=f'''# SUN / ARIADNE final delivery handoff

The integrated evidence and native-model engine runs locally. All {len(rows)} original requirements remain accountable; full mission completion is false. Native mathematical acceptance, source-specific historical support and the broader original research mission are reported separately.

## What was already used

The first linguistic harmonic validator used Sefer Yetzirah's three mother letters, seven doubles and twelve simples: 3+7+12=22, with29stipulated tagged states. The separate frozen SUN scientific taxonomy has three constructors, seven mechanisms and twelve relations. Earlier Western exact-interval prototypes already existed in work/four-orientations/ and work/unit002/; the current Western adapter reuses that core. These structures were retained independently rather than identified from equal counts.

## Delivered artifacts

- current-deliverables.json and CSV preserve all original rows, original statuses, current assessments, evidence references and remaining dependencies.
- REQUIREMENTS.md provides a readable106-row view.
- results/ contains source-bound encodings, measured coding costs, native validations, original Sefer demonstration equality, exact comparisons, finite inverse countermodels and all eight connected mathematical-output registers.
- audit/mathematical-source-versions/ preserves all12initial and12subsequently observed mathematical-state references as14unique byte versions. The two changed states have exact initial archives as well as new snapshots; no old content was reconstructed and no version is automatically historical corroboration.
- results/canonical-features-v2/ contains the exact-source15×36×20 NumPy matrix, masks, normalized values, lossless ordered phonetic sidecars and original source bytes. The validator rederives and checks every raw and derived field; v1 is retained as a superseded engineering checkpoint. Geometry remains explicitly unavailable without an identified image or font proxy.
- dashboard/SUN_ARIADNE_Workbench.html is the local interactive workbench. {browser_text}
- run_delivery.py reproduces the integrated checks. package_delivery.py regenerates the current register and this handoff. verify_delivery.py performs read-only integrity verification; --docs checks documentation.

## Verification actually recorded

{checklines}

The source matrix contains540positions:381populated and159blank, preserving glyph, IPA and English fields. The source hash is `{delivery['matrix_sha256']}`. Original Sefer tests and the full demonstration JSON remain explicit in their receipts. Code/model costs depend on the stated representation and side information; escaped literals are storage, not successful historical predictions.

## Changed files

Original project files changed by this unit: src/worker.ts, its rebuilt dist/worker.js, tests/worker-lifecycle.test.mjs, and the append-only docs/PLUGIN_CAPABILITIES.md. tests/worker-identity.mjs was added. Exact operational preimages and deltas are recorded under runtime/. All other implementation, tests, source profiles, evidence, codecs, native models and workbench changes for this unit are under work/final-day-2026-11-07/. New reading-relations code/tests already present from related workspace work were verified as part of the current project population; they are not attributed to this unit. No commit, merge, release or external publication is claimed.

{worker_text} Project build, worker integration and full-project test outcomes remain separate from native checks. The initial full npm test run recorded98passes and1failure among99tests; its output-overflow cleanup failure remains visible. Root reported a separate live focused6-test pass, without a separately persisted complete transcript. Durable project receipts currently present are:

{runtime_text}

A later serial run is a separate observation and does not erase the initial failure. No missing check is converted into a pass. The dashboard is a local artifact; no external publication is claimed.

## Gate ledger

'''
    text+='\n'.join('- '+k+': '+v for k,v in delivery['gates'].items())+'\n'
    text+='''
## Scientific and source limits

The bounded dictionary search measures a finite family of lossless codes. Constructive one-state transducer countermodels demonstrate that fitting finite observations alone cannot identify a unique historical mechanism. Latent relabeling and differing register scales remain distinct sources of ambiguity. Historical glyph topology, earliest manuscript priority, broader Fludd/Kepler/Completed Harmony interpretation and prospective source-independent historical tests retain explicit gaps. Calendar, zodiac and global-geometric goals remain dependent original requirements; the eight mathematical outputs remain partial or conditional connected implementations.

The complete parent ChatGPT transcript was not retrieved. Available parent preview, current-chat records, corrections, negative results and hypotheses remain preserved. Every signal remains in scope; an execution gate does not delete or adjudicate evidence.

## Actual capability use

'''+capabilities+'''

Superpowers TDD, HUMMBL planning and installed review/evidence guidance were applied as methods. Their use is not a claim of additional hosted model execution. Fresh evidence for other selected runtimes is not inferred from installation, credential presence or automatic observations. Detailed exact receipts remain alongside this handoff and in docs/PLUGIN_CAPABILITIES.md.

## Reproduction and next dependencies

Run the integrated delivery, then regenerate this package, then run the read-only verifier. A final proof run should bind the source files and actual results; documentation checks do not certify history. Preserve all candidates until independently justified constraints discriminate them. The next scientific work concerns source-native historical profiles and independently withheld evidence, with no permission to force a universal musical/root correspondence from counts or compression.
'''
    (ROOT/'HANDOFF.md').write_text(text,encoding='utf-8')
    print(json.dumps({'packaged_original_rows':len(rows),'full_mission_complete':False,'external_publication':'NOT_PERFORMED'}))


if __name__=='__main__':main()
