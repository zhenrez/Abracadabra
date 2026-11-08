"""Jev selects fixed mathematical reconstruction or verification actions."""
import argparse,hashlib,importlib.util,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from jev_tool import evaluate,verify_log
ROOT=Path(__file__).resolve().parents[1]
ACTIONS={
 'native_derivations':{'description':'Execute source-bound Western/Chinese bridge, residual, register/history and registered-return derivations.','command':[sys.executable,'-X','utf8','scripts/reconstruct_native_derivations.py']},
 'orientation_predictions':{'description':'Execute all12recovered transitive completions,144word prediction sets and minimum discriminating phase-observation proofs. Conditional family, not global orientation election.','command':['node','scripts/reconstruct_orientation_predictions.mjs']},
 'generational_constraints':{'description':'Execute source-qualified generation, chronology, temporal and lift constraints without converting years to beats.','command':[sys.executable,'-X','utf8','scripts/reconstruct_generational_constraints.py'],'requires':'scripts/reconstruct_generational_constraints.py'},
 'native_execution':{'description':'Execute the ten source-native mechanism interfaces and explicit unknown historical maps. Requires an up-to-date TypeScript build.','command':['node','scripts/reconstruct_native_execution.mjs'],'requires':'dist/native-operators.js'},
 'algebraic_extension':{'description':'Execute exact source-native root extensions, octave quotient distinctions and residual calculations. Requires an up-to-date TypeScript build.','command':['node','scripts/reconstruct_algebraic_extension.mjs'],'requires':'dist/algebraic-scalar.js'},
 'master_score':{'description':'Execute the source-backed partial master score, preserving native units, frames and unknown assignments. Requires an up-to-date TypeScript build.','command':['node','scripts/reconstruct_master_score.mjs'],'requires':'scripts/reconstruct_master_score.mjs'},
 'receipt_integrity':{'description':'Verify the actual Jev decision receipt chain without source changes.','command':[sys.executable,'scripts/jev_tool.py','verify']},
 'source_integrity':{'description':'Recheck every preserved source hash, database integrity and complete search-index references.','command':[sys.executable,'scripts/verify_recovery.py']},
 'python_checks':{'description':'Run importer and Jev input/response boundary regression checks; fixtures remain synthetic.','command':[sys.executable,'-m','unittest','discover','-s','tests','-p','*_test.py']},
 'application_checks':{'description':'Compile TypeScript and run local mathematical, source-service and decision-gate tests.','command':['npm.cmd' if sys.platform=='win32' else 'npm','test']},
 'checkpoint_integrity':{'description':'Verify the saved SuperJev checkpoint envelope; hash integrity alone does not establish freshness or truth.','command':[sys.executable,r'C:\Users\Brend\.codex\plugins\cache\created-by-me-remote\superjev\0.1.0\skills\superjev\scripts\superjev.py','verify-checkpoint','--input','state/superjev-checkpoint.json']}
}

def cloud_decision(request):
 helper=Path(r'C:\Users\Brend\.codex\plugins\cache\created-by-me-remote\superjev\0.1.0\skills\superjev\scripts\superjev.py')
 spec=importlib.util.spec_from_file_location('sunny_cloud_superjev',helper); module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 cloud={'state':request['state'],'questions':{q['id']:{'type':q['type'],'instructions':q['question'],'criteria':q['options']} for q in request['questions']}}
 result=module.decide(cloud,live=True)
 if result.get('status')!='judged':raise RuntimeError('No live SuperJev judgment: '+str(result.get('status')))
 now=datetime.now(timezone.utc).isoformat()
 payload={'completed_at':now,'request':cloud,'response':result,'semantics':'Actual SuperJev cloud inference; distinct from pinned local AgentJev. Model preferences direct work and do not establish mathematical truth.'}
 sha=hashlib.sha256(module.canonical(payload).encode('utf8')).hexdigest()
 dest=ROOT/'state/jev-cloud-receipts'/(sha+'.json');dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf8')
 answers=[{'id':key,'type':value['type'],'value':value['winner'],'distribution':value['probabilities']} for key,value in result['answers'].items()]
 return {'status':'judged','receipt':str(dest),'sha256':sha,'answers':answers,'model_info':{'provider':'typesafe','requested_model':result['requested_model'],'resolved_model':result.get('resolved_model')}}

def main():
 p=argparse.ArgumentParser(description=__doc__); p.add_argument('command',choices=['status','next']); p.add_argument('--execute',action='store_true');p.add_argument('--provider',choices=['local','superjev-cloud'],default='local');p.add_argument('--scope',choices=['all','mathematics','verification'],default='all'); args=p.parse_args()
 queue=json.loads((ROOT/'state'/'work-queue.json').read_text(encoding='utf8')) if (ROOT/'state'/'work-queue.json').exists() else None
 if args.command=='status': print(json.dumps({'receipt_integrity':verify_log(),'queue':queue,'actions':{k:v['description'] for k,v in ACTIONS.items()}},ensure_ascii=True,indent=2)); return
 current=json.loads((ROOT/'state/task.json').read_text(encoding='utf8'))
 eligible={k:v for k,v in ACTIONS.items() if not v.get('requires') or (ROOT/v['requires']).exists()}
 math_actions={'native_derivations','orientation_predictions','generational_constraints','native_execution','algebraic_extension','master_score'}
 if args.scope=='mathematics':eligible={k:v for k,v in eligible.items() if k in math_actions}
 elif args.scope=='verification':eligible={k:v for k,v in eligible.items() if k not in math_actions}
 if len(eligible)<2:raise ValueError('A Jev choice needs at least two currently available actions in this scope')
 # Preserve the unresolved transport-test failure; do not repeatedly relaunch it.
 if str(current.get('observed_progress',{}).get('software_latest_full_suite','')).startswith('not_passed'):eligible.pop('application_checks',None)
 active_tasks=(queue or {}).get('current_mathematical_tasks',(queue or {}).get('tasks',[]))
 request={'state':{'goal':current.get('current_priority','Execute current SUNNY mathematical mandate.'),'user_constraints':'Actual Jev directs source-native reconstruction, reproducible derivations and discriminating consequences. Preserve all inputs/branches. Do not elect a mathematical orientation by model probability.','current_tasks':[{'id':t['id'],'title':t['title'],'status':t['status'],'depends_on':t.get('depends_on',[])} for t in active_tasks][:12],'scope':'Only the supplied fixed local research/verification actions are executable. Mathematical scripts may write derived artifacts; original sources are unchanged. No arbitrary code, external writes or provisioning.'},'questions':[{'id':'next_check','type':'choice','question':'Which fixed action should advance actual SUNNY mathematical reconstruction now, considering source and verification dependencies?','options':{k:v['description'] for k,v in eligible.items()}}]}
 decision=cloud_decision(request) if args.provider=='superjev-cloud' else evaluate(request,'Quarterback selects next fixed mathematical or verification action')
 print(json.dumps(decision,ensure_ascii=True,indent=2),flush=True)
 if args.execute:
  selected=decision['answers'][0]['value']
  if selected not in eligible: raise ValueError('Jev selected an unavailable action')
  run=subprocess.run(eligible[selected]['command'],cwd=ROOT,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=240,shell=False)
  receipt=Path(decision['receipt']); out={'decision_receipt':str(receipt),'action':selected,'exit_code':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'semantics':'Actual fixed local action; passing checks do not imply complete SUNNY research.'}
  dest=ROOT/'state'/'quarterback-runs'/(receipt.stem+'.json'); dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8'); print(json.dumps({'action':selected,'exit_code':run.returncode,'result':str(dest)},indent=2)); return run.returncode
 return 0

if __name__=='__main__':
 try: raise SystemExit(main())
 except Exception as e: print(json.dumps({'status':'failed','error':str(e),'fallback_action':None}),file=sys.stderr); raise SystemExit(1)
