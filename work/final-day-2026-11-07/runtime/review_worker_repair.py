"""Independent static/simulated review; never launches a real worker or CIM."""
from pathlib import Path
import difflib,hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
oldw=(OUT/'preimage/worker.ts').read_text(encoding='utf-8');neww=(ROOT/'src/worker.ts').read_text(encoding='utf-8')
oldt=(OUT/'preimage/worker-lifecycle.test.mjs').read_text(encoding='utf-8');newt=(ROOT/'tests/worker-lifecycle.test.mjs').read_text(encoding='utf-8')
assert re.sub(r'timeout:(30000|45000)','timeout:60000',oldt)==newt
assert oldt.count("test('")==newt.count("test('")==6
assert "const helperTimeout = args[1] === 'stop' ? 30000 : 15000;" in neww
assert 'clearTimeout(timer);\n      const completionReason = stopReason;' in neww
base={p.replace('\\','/'):h for p,h in json.loads((OUT/'before-manifest.json').read_text()).items()}
helpers={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==base[p]for p in ['scripts/stop-jev-worker.ps1','scripts/process-lifecycle.ps1']}
assert all(helpers.values())
command=[r'C:\Program Files\nodejs\node.exe','--test',str(OUT/'test_timer_race.mjs'),str(OUT/'test_helper_deadline.mjs')]
p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
(OUT/'worker-repair-simulated-review.log').write_text(p.stdout+p.stderr,encoding='utf-8')
assert p.returncode==0,p.stdout+p.stderr
counts={k:int(v)for k,v in re.findall(r'^# (tests|pass|fail) (\d+)$',p.stdout+p.stderr,re.M)}
diagnostic=json.loads((OUT/'cleanup-diagnostic-checks.json').read_text(encoding='utf-8'))
assert 'Worker identity helper timed out.'in diagnostic['output'] and diagnostic['exit_code']==1
r={'review_date':'2026-11-07','reviewer':'independent /root/spec_audit','scope':'Operational worker timer/cleanup deadline repair; no frozen math mutation',
 'worker_diff':list(difflib.unified_diff(oldw.splitlines(),neww.splitlines(),fromfile='worker-preimage',tofile='worker-current',lineterm='')),
 'test_diff':list(difflib.unified_diff(oldt.splitlines(),newt.splitlines(),fromfile='test-preimage',tofile='test-current',lineterm='')),
 'original_six_tests_and_assertions_preserved':True,'ownership_helpers_unchanged':helpers,
 'source_hashes':{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()for path in [ROOT/'src/worker.ts',ROOT/'tests/worker-lifecycle.test.mjs',OUT/'preimage/worker.ts',OUT/'preimage/worker-lifecycle.test.mjs']},
 'history':['Restricted capture denied by Windows policy; no algorithm failure inferred','Parent original focused4PASS2FAIL','Independent copied-code timer race reproduced','Parent focused after timer repair6PASS','Default after timer repair99tests98PASS1FAIL','Parent serial control97PASS2FAIL','Durable verbose overflow diagnostic identifies Worker identity helper timed out; code4294967295'],
 'guardrails':{'capture_deadline_ms':15000,'stop_deadline_ms':30000,'bounded':True,'no_policy_or_identity_bypass':True,'no_assertions_removed':True,'capacity_reserved_until_reaped':True,'execution_timer_cleared_before_cleanup':True},
 'simulated_tests':{'command':command,'exit_code':p.returncode,'counts':counts,'scope':'Actual compiled helper virtual clock plus copied worker fake transport; no real worker, CIM or model'},
 'conclusion':'Small coherent operational repair supported by exact timeout diagnostic and independent finite tests.30seconds is an explicit bounded allowance, not a measured worst-case guarantee.',
 'pending':'Root fresh default npm acceptance after repair; no all-tests-pass claim by this review.'}
(OUT/'worker-repair-independent-review.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'counts':counts,'exit_code':p.returncode,'assertions_preserved':True,'ownership_helpers_unchanged':helpers,'full_npm':'PENDING_ROOT_RESULT'}))
