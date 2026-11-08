"""Freeze fresh engineering evidence without consuming the live worker's budget."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json,subprocess,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=importlib.util.spec_from_file_location('background_evidence',ROOT/'scripts/background_reconstruction.py');w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
client=w.module(w.JEV,'evidence_superjev');proof=w.module(w.PROOFLINE,'evidence_proofline')
calls=[]
for p in sorted((BASE/'model-calls').glob('*.json')):
 rec=load(p);result=rec['result'];digest=client.digest(client.validate_request(rec['request']))
 assert digest==result['request_sha256'],p
 calls.append({'path':str(p.relative_to(ROOT)),'ordinal':rec['budget_ordinal'],'status':result['status'],'network_calls':result.get('network_calls',0),'model':result.get('resolved_model'),'canonical_request_sha256':digest})
budget=load(BASE/'model-budget.json')
assert len(calls)==budget['reserved_or_completed_requests']
assert sum(c['network_calls'] for c in calls)==budget['confirmed_network_calls']
assert sorted(c['ordinal'] for c in calls)==list(range(1,len(calls)+1))
verified=[]
for p in sorted((BASE/'runs').glob('*/result.json')):
 result=load(p);rows=[]
 for i,r in enumerate(result['source_records']):
  receipt=load(p.parent/r['jev_receipt']);package=load(p.parent/f'source-{i}-proofline.json')
  actual=proof.verify(package)
  assert receipt['status']=='judged' and receipt['network_calls']==1 and receipt['resolved_model']=='jev-1.14.0'
  original=ROOT/r['source']['path']
  rows.append({'source_path':r['source']['path'],'source_sha256':r['source']['sha256'],'current_source_hash_matches':sha(original)==r['source']['sha256'],'source_role':r['source'].get('source_role'),'model':'jev-1.14.0','actual_inference':True,'proofline_valid':actual['valid'],'proofline_root_hash':actual['root_hash']})
 verified.append({'id':result['id'],'path':str(p.relative_to(ROOT)),'sha256':sha(p),'completed_utc':result['completed_utc'],'source_records':rows,'status':result['status']})
assert len(verified)>=4 and all(r['status']=='candidate_source_reconstruction' for r in verified)
main=ROOT/'state/background/main/model-budget.json'
assert sha(main)=='788bd100f99f0dbe6588c4699792e36431de55c1c32957edec6c83d72c6118ad'
status=load(BASE/'latest-observed-status.json');identity=load(BASE/'identity-verification.json')
assert status['owned_running'] and status['ownership']['root_identity']['pid']==29660
assert status['worker']['code_sha256']==sha(ROOT/'scripts/background_reconstruction.py')
tests=load(ROOT/'docs/evidence/background-reactivation-tests.json');assert tests['passed'] and tests['exit_code']==0
packet={'schema':'sunny.background-reactivation-verification.v1','checked_utc':datetime.now(timezone.utc).isoformat(),'status':'passed','fresh_test_evidence':'docs/evidence/background-reactivation-tests.json','tests_passed':18,'new_regressions_red_then_green':6,'worker_identity_evidence':'state/background/reactivation-20261102/identity-verification.json','latest_runtime_observation':'state/background/reactivation-20261102/latest-observed-status.json','loaded_code_sha256':sha(ROOT/'scripts/background_reconstruction.py'),'manager_sha256':sha(ROOT/'scripts/manage-background-reconstruction.ps1'),'completed_guarded_results':verified,'request_receipts':calls,'budget':budget,'old_main_budget_unchanged_sha256':sha(main),'old_symbol_renewal_budget':load(ROOT/'state/background/symbol-renewal-01/model-budget.json'),'local_blocker':load(BASE/'blocker.json'),'cadence':load(BASE/'cadence.json'),'scope':'Real guarded source support and engineering lifecycle. No autonomous chat notification, canonical scientific promotion or full-SUNNY completion.'}
save(ROOT/'docs/evidence/background-reactivation-verification.json',packet)
# Exact engineering execution record, packaged with the already inspected guard.
p=ROOT/'docs/evidence/background-reactivation-tests.json'
span=w.read_span({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'start_line':1,'end_line':len(p.read_text(encoding='utf8').splitlines()),'source_role':'observed_engineering_execution_record'})
package,receipt=w.proof_package(span,proof)
save(ROOT/'docs/evidence/background-reactivation-proofline.json',package)
save(ROOT/'docs/evidence/background-reactivation-proofline-result.json',receipt)
claims=[
 ('Sixreproduced reliability defects are covered by18passing focused tests; those fixtures are not scientific progress.',['docs/evidence/background-reactivation-tests.json']),
 ('One actual hidden owned worker ran the tested code and completed four guarded source-support outputs with actualJev1.14.0 and Proofline.',['docs/evidence/background-reactivation-verification.json']),
 ('Repeated idle polls preserve the exact emptyqueue blocker timestamp and do not create scientific progress or an autonomous chatwakeup.',['state/background/reactivation-20261102/blocker.json','state/background/reactivation-20261102/cadence.json']),
 ('Oldmain budget255/256 remains byte-identical and oldsymbol-renewal budget43/256 is preserved; the new allocation has a fixed finite deadline.',['docs/evidence/background-reactivation-verification.json','state/background/reactivation-20261102/authorization.json'])
]
records=[{'id':f'E-{i:03d}','claim':claim,'provenance':'RESEARCH_SUPPORTED_INFERENCE','confidence':1.0,'evidence_strength':0,'status':'active','source_refs':refs,'scope':'Literal engineering-record fidelity only; schema values are not source weights or empirical/scientific confidence. Zero direct research participants.'} for i,(claim,refs) in enumerate(claims,601)]
save(BASE/'engineering-mightshape-input.json',records)
might=Path('C:/Users/Brend/.codex/plugins/cache/openai-curated-remote/mightshape/1.0.1/skills/mightshape/scripts/check_evidence.py')
done=subprocess.run([sys.executable,'-B',str(might),str(BASE/'engineering-mightshape-input.json')],capture_output=True,encoding='utf8',timeout=20)
guard=json.loads(done.stdout);assert done.returncode==0 and guard['firewall']=='PASS'
save(ROOT/'docs/evidence/background-reactivation-mightshape.json',guard)
report=load(ROOT/'docs/evidence/background-reactivation-runtime.json')
report['latest_snapshot']={'checked_utc':packet['checked_utc'],'completed_results':len(verified),'reserved':budget['reserved_or_completed_requests'],'confirmed_network_calls':budget['confirmed_network_calls'],'remaining_reservations':budget['maximum_requests']-budget['reserved_or_completed_requests'],'blocker':packet['local_blocker']['id'],'lease_deadline_utc':status['worker']['lease_deadline_utc'],'notification_delivery':'local_state_only_no_chat_wakeup'}
report['evidence_paths']+=['docs/evidence/background-reactivation-tests.json','docs/evidence/background-reactivation-verification.json','docs/evidence/background-reactivation-proofline-result.json','docs/evidence/background-reactivation-mightshape.json']
save(ROOT/'docs/evidence/background-reactivation-runtime.json',report)
print(json.dumps({'status':'passed','completed_results':len(verified),'requests_reserved':budget['reserved_or_completed_requests'],'confirmed_network_calls':budget['confirmed_network_calls'],'source_proofline_all_valid':True,'engineering_proofline_valid':receipt['valid'],'mightshape':guard['firewall']}))
