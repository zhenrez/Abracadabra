"""Check that the small recovery index, task, model and checkpoint agree now."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,re
from refresh_reconstruction_checkpoint import resolve_superjev_helper
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='docs/evidence/continuation-verification.json')
    args=parser.parse_args();target=(ROOT/args.output).resolve()
    if not target.is_relative_to(ROOT):raise ValueError('Report must remain inside task workspace')
    task=json.loads((ROOT/'state/task.json').read_text(encoding='utf8'))
    envelope=json.loads((ROOT/'state/superjev-checkpoint.json').read_text(encoding='utf8'))
    helper=resolve_superjev_helper()
    spec=importlib.util.spec_from_file_location('sunny_continuation_verify',helper)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    checks=[]
    def check(name,ok,detail=None):checks.append({'check':name,'passed':bool(ok),'detail':detail})
    integrity=module.verify_checkpoint(envelope)
    check('checkpoint_integrity',integrity.get('status')=='intact',integrity)
    check('checkpoint_matches_current_task',envelope.get('payload')==task)
    mandate=task['current_instruction'];witness=ROOT/mandate['text_witness_path']
    check('current_mandate_witness',digest(witness)==mandate['text_witness_sha256'])
    note=ROOT/'CONTINUE.md';note_sha=digest(note)
    check('continuation_bound_in_task',task.get('continuation_document',{}).get('sha256')==note_sha,note_sha)
    check('continuation_lightweight',note.stat().st_size<=10000,{'bytes':note.stat().st_size,'maximum_bytes':10000})
    model=ROOT/'state/reconstruction/model.json';model_sha=digest(model)
    report=json.loads((ROOT/'docs/evidence/reconstruction-verification.json').read_text(encoding='utf8'))
    check('model_fidelity_report_current',report.get('status')=='passed' and report.get('model_sha256')==model_sha)
    check('task_model_reference_current',task.get('observed_progress',{}).get('model_sha256')==model_sha)
    references=['PLAN.md','docs/HUMMBL_PLAN.md','docs/PLUGIN_CAPABILITIES.md',
      'docs/reconstruction/CURRENT_MODEL.md','state/reconstruction/derived-laws.json',
      'state/reconstruction/native-execution.json','state/reconstruction/algebraic-extension.json',
      'state/reconstruction/generational-constraints.json','state/reconstruction/master-score.json']
    check('resume_artifacts_exist',all((ROOT/p).is_file() for p in references),
      {'missing':[p for p in references if not (ROOT/p).is_file()]})
    steps=[line for line in (ROOT/'PLAN.md').read_text(encoding='utf8').splitlines() if line.startswith('- ')]
    matches=[re.fullmatch(r'- \[(\d{1,3})%\] .+',line) for line in steps]
    percents=[int(m.group(1)) for m in matches if m]
    check('plan_prefixes_and_single_active',bool(steps) and all(matches) and
      all(0<=p<=100 for p in percents) and sum(0<p<100 for p in percents)==1,percents)
    check('latest_continuation_request_retained',any('lightweight context continuation document' in x.get('exact_request','') for x in task.get('continuation_requests',[])))
    check('stale_favorites_question_not_active','question pending' not in task.get('favorites_status',''))
    result={'schema':'sunny.continuation-verification.v1','checked_utc':datetime.now(timezone.utc).isoformat(),
      'status':'passed' if all(c['passed'] for c in checks) else 'failed',
      'checks':checks,'passed':sum(c['passed'] for c in checks),'total':len(checks),
      'hashes':{'CONTINUE.md':note_sha,'state/task.json':digest(ROOT/'state/task.json'),'state/reconstruction/model.json':model_sha},
      'boundary':'Current task/checkpoint/file consistency and declared fidelity result only. Not complete source semantics, all historical inputs, mathematical truth or Mission I completion.'}
    target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':result['status'],'exit_code':int(result['status']!='passed'),
      'passed':result['passed'],'total':result['total'],'failed':[c['check'] for c in checks if not c['passed']],'report':str(target)}))
    return int(result['status']!='passed')
if __name__=='__main__':raise SystemExit(main())
