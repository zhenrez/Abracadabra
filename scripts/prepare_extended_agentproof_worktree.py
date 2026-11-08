"""Preflight an authorized existing-HEAD worktree and add exact actual native test inputs."""
from pathlib import Path
import hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];SCOPE=ROOT/'work/agentproof-native-worktree-2026-10-31'
plugin=Path(r'C:\Users\Brend\.codex\plugins\cache\openai-curated-remote\agentproof\0.1.0\skills\agentproof\scripts')
sys.path.insert(0,str(plugin))
from agentproof_runtime.capture import resolve_repository_root,snapshot_repository
assert resolve_repository_root(SCOPE)==SCOPE.resolve()
assert not (SCOPE/'.agentproof/agent-session.json').exists()
names=['src/native-operators.ts','src/law.ts','dist/native-operators.js','dist/law.js','tests/native-operators.test.mjs','package.json','data/raw/archive/SUN_Universal_Archive/Library/SUN_DEEP_RECOVERY/SUN_GG_v1_final.json']
rows=[]
for name in names:
 src=ROOT/name;dst=SCOPE/'sunny-native'/name
 assert src.is_file() and not src.is_symlink() and not dst.exists()
 raw=src.read_bytes();dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw)
 rows.append({'source':str(src),'snapshot':str(dst),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
snapshot=snapshot_repository(SCOPE)
for row in rows:assert snapshot[str(Path(row['snapshot']).relative_to(SCOPE)).replace('\\','/')]==Path(row['source']).read_bytes()
request={'action':'capture','model':'gpt-6.1-sol','sandbox':'read-only','prompt':'This is an explicitly authorized detached worktree of the already trusted AgentJev HEAD, with exact actual SUNNY calculation files copied under sunny-native. Parent guard coordination used actual SuperJev, Proofline, MightShape, Mathbox and independent source review. In one bounded action run node --test sunny-native/tests/native-operators.test.mjs from this root, then report the actual pass/fail totals and stop. Do not edit files, start services or browsers, launch other agents, do network research, inspect credentials/private configuration, install dependencies, or create persistent processes. Keep this read-only calculation check narrowly scoped.'}
control=SCOPE/'.agentproof';control.mkdir(exist_ok=True)
assert not (control/'request.json').exists()
(control/'request.json').write_text(json.dumps(request,indent=2),encoding='utf8')
report={'schema':'sunny.agentproof-existing-head-worktree-scope.v1','scope':str(SCOPE),'original_repository':'runtime/agent-jev','base_commit':'fbe1bc97c76873d08f0820adf0dead55e95d5fc6','detached':True,'new_commit_created':False,'trust_settings_changed':False,'selected_by':'docs/evidence/extended-agentproof-worktree-superjev.json','actual_files':rows,'profile_preflight':{'status':'passed','included_files':len(snapshot),'included_bytes':sum(len(v) for v in snapshot.values()),'maximum_file_bytes':max(len(v) for v in snapshot.values()),'all_actual_copied_inputs_observed':True},'old_receipt_sha256':hashlib.sha256((ROOT/'runtime/agent-jev/.agentproof/agent-session.json').read_bytes()).hexdigest(),'capture_started':False,'limits':'Preflight is repository-profile support, not new child trust acceptance or mathematical/capture success.'}
(ROOT/'docs/evidence/extended-agentproof-worktree-scope.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({'profile_preflight':report['profile_preflight'],'scope':str(SCOPE),'actual_files':len(rows)}))
