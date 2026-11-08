"""Prepare a diagnostic-only lifecycle copy and controlled suite argv; no test run."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
source=ROOT/'tests/worker-lifecycle.test.mjs'
raw=source.read_bytes();text=raw.decode('utf-8')
text=text.replace("from '../dist/worker.js'", "from '../../../dist/worker.js'")
text=text.replace("from '../dist/server.js'", "from '../../../dist/server.js'")
text=text.replace("new URL('..',import.meta.url)","new URL('../../../',import.meta.url)")
needle="const result=await worker.result;assert.equal(result.reason,'output_limit');"
replacement="const result=await worker.result;t.diagnostic('Synthetic overflow result: '+JSON.stringify({result,fixture_root:fixture.root,owned_fixture_ids:ids}));assert.equal(result.reason,'output_limit',JSON.stringify(result));"
assert text.count(needle)==1
text=text.replace(needle,replacement)
dest=OUT/'worker-lifecycle-diagnostic.test.mjs';dest.write_text(text,encoding='utf-8')
files=sorted(str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'tests').glob('*.test.mjs'))
other=[p for p in files if p!='tests/worker-lifecycle.test.mjs']
copy=str(dest.relative_to(ROOT)).replace('\\','/')
report= {
 'scope':'Diagnostic preparation only. Same synthetic fixtures and assertions; imports/project root relocated, overflow result printed before assertion. No ownership policy or runtime timeout changes.',
 'source':{'path':str(source),'sha256':hashlib.sha256(raw).hexdigest()},
 'copy':{'path':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()},
 'original_test_files':files,'population_preserved':len(files)==len(other+[copy]),
 'controlled_commands':{
  'serial_original':['node','--test','--test-concurrency=1',*files],
  'serial_diagnostic':['node','--test','--test-concurrency=1',*other,copy],
  'default_concurrency_diagnostic':['node','--test',*other,copy]},
 'interpretation':{
  'serial_pass':'Shows this run passed with one concurrent test file; does not erase the default npm failure or prove its cause.',
  'helper_timeout_error':'Evidence of bounded cleanup-helper timeout, not permission to weaken ownership checks or blindly raise limits.',
  'capture_or_identity_error':'Investigate its precise phase and identity record; do not relabel as load automatically.',
  'intermittent_pass':'Retain both runs; no permanent fix inferred.'},
 'execution_status':'NOT_RUN_BY_AUDITOR; root controls approved runtime and bounded commands.'}
(OUT/'cleanup-diagnostic-plan.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'copy_created':copy,'original_files':len(files),'population_preserved':report['population_preserved'],'runs_started':0}))
