"""Declare a bounded, executable verification contract; no scientific certificate."""
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
python=sys.executable
relative=lambda path:Path(path).relative_to(PROJECT).as_posix()
inputs=set()
for directory in (ROOT,ROOT/'integration',ROOT/'independent-review',ROOT/'western',ROOT/'native-east',
                  ROOT/'canonical-features',ROOT/'dashboard',ROOT/'runtime',PROJECT/'work/unit001',
                  PROJECT/'work/ariadne-inverse',PROJECT/'work/unit002',PROJECT/'work/four-orientations'):
    for path in directory.glob('*'):
        if path.is_file() and (path.suffix in ('.py','.mjs') or path.name in ('workbench.template.html','source-profiles.json','reuse-manifest.json','bindings.json','source-bindings.json')):
            if path.name.startswith('worker-simulated-'):continue
            inputs.add(relative(path))
for folder,pattern in ((PROJECT/'src','*.ts'),(PROJECT/'tests','*.test.mjs')):
    inputs.update(relative(path) for path in folder.glob(pattern))
inputs.add('tests/worker-identity.mjs')
for path in (PROJECT/'work/unit001/frozen',ROOT/'runtime/preimage',ROOT/'canonical-features/preimage',
             ROOT/'results/canonical-features-v2',ROOT/'western/sources',ROOT/'native-east/sources',ROOT/'capability-receipts'):
    for item in path.rglob('*'):
        if item.is_file() and '__pycache__' not in item.parts:inputs.add(relative(item))
for path in (PROJECT/'work/unit001/source-manifest.json',ROOT/'audit/deliverables.json',
             PROJECT/'scripts/stop-jev-worker.ps1',PROJECT/'scripts/process-lifecycle.ps1',
             ROOT/'runtime/approved-source-change.json',ROOT/'runtime/project-final-checks.json',
             ROOT/'runtime/project-checks.json',ROOT/'runtime/project-serial-checks.json',ROOT/'runtime/project-after-repair-checks.json',
             ROOT/'jev-strategy.json',ROOT/'jev-final-sequence.json',PROJECT/'package.json',PROJECT/'tsconfig.json'):
    inputs.add(relative(path))
for path in (ROOT/'dashboard/README.md',ROOT/'canonical-features/README.md'):
    inputs.add(relative(path))
for path in (ROOT/'audit/mathematical-source-versions').rglob('*'):
    if path.is_file():inputs.add(relative(path))
expanded=set()
for name in inputs:
    path=PROJECT/name
    if path.is_dir():expanded.update(relative(item) for item in path.rglob('*') if item.is_file())
    else:expanded.add(name)
inputs=expanded
total_bytes=sum((PROJECT/name).stat().st_size for name in inputs)
if total_bytes>100_000_000:raise ValueError('Declared source scope exceeds proof limit; split the contract without truncating inputs')

def check(identifier,criteria,argv,timeout=180):
    return {'id':identifier,'criteria':criteria,'command':argv,'timeout_seconds':timeout}

base='work/final-day-2026-11-07/'
contract={'workspace':str(PROJECT),'goal':'Verify the executed canonical evidence/native-model delivery, source preservation, measured conditional controls, all106retained requirements, real UI and operational checks. Historical and full SUNNY research certification are excluded.',
          'acceptance':[
              {'id':'native_evidence','description':'Source-bound native and conservation regressions execute with positive test counts; all original source distinctions survive.'},
              {'id':'runtime','description':'The current full project run is source-bound and passing; timer/helper/identity controls retain failures and reject unverifiable ownership.'},
              {'id':'catalog','description':'All106original requirements/statuses survive verbatim beside current assessments, with every unresolved dependency retained.'},
              {'id':'interface','description':'The local workbench embeds exact raw and current evidence separately; real browser interactions and mobile layout are checked.'},
              {'id':'integrity','description':'Current outputs, frozen sources, operational exceptions, original demonstrations and documentation are verified without certifying history.'}],
          'inputs':sorted(inputs),
          'checks':[
              check('native-and-evidence',['native_evidence'],[python,'-B',base+'run_delivery.py']),
              check('runtime-controls',['runtime'],['node','--test',base+'runtime/test_helper_deadline.mjs',base+'runtime/test_timer_race.mjs',base+'runtime/test_worker_identity.mjs']),
              check('current-full-project-receipt',['runtime'],[python,'-B',base+'verify_delivery.py','--runtime']),
              check('canonical-artifacts',['native_evidence'],[python,'-B',base+'verify_delivery.py','--canonical']),
              check('current-catalog',['catalog'],[python,'-B',base+'package_delivery.py']),
              check('workbench-build',['interface'],[python,'-B',base+'dashboard/build_dashboard.py']),
              check('actual-browser',['interface'],['node',base+'dashboard/browser_check.mjs']),
              check('refresh-readable-handoff',['catalog'],[python,'-B',base+'package_delivery.py']),
              check('artifact-integrity',['integrity'],[python,'-B',base+'verify_delivery.py']),
              check('documentation',['integrity'],[python,'-B',base+'verify_delivery.py','--docs']),
              check('focused-static-lint',['integrity'],[python,'-m','ruff','check','--select','E9,F63,F7,F82',
                  *[name for name in sorted(inputs) if name.startswith(base) and name.endswith('.py') and 'preimage' not in Path(name).parts]]),
              check('dependency-consistency',['integrity'],[python,'-m','pip','check'])]}
target=ROOT/'proof-contract.json'
target.write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if json.loads(target.read_bytes())!=contract:raise RuntimeError('Contract readback mismatch')
print(json.dumps({'contract':str(target),'inputs':len(inputs),'input_bytes':total_bytes,'checks':len(contract['checks']),
                  'scope':'Bounded execution/artifact evidence; full mission is not certified'}))
