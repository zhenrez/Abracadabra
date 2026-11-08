"""Preserve the old task state and bind current reconstruction evidence for resumption."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json,sqlite3,re
ROOT=Path(__file__).resolve().parents[1]

def resolve_superjev_helper():
    """Use the installed plugin version; cache updates remove old directories."""
    base=Path.home()/'.codex/plugins/cache/created-by-me-remote/superjev'
    candidates=list(base.glob('*/skills/superjev/scripts/superjev.py'))
    if not candidates:
        raise FileNotFoundError('No installed SuperJev checkpoint helper')
    return max(candidates,key=lambda p:(tuple(int(x) for x in re.findall(r'\d+',p.parents[3].name)),p.parents[3].name))
def preserve_user_context(state):
    """Fill absent context only; source refresh never supersedes user direction."""
    defaults={
        'current_priority':'Execute the current SUNNY reconstruction and predictive derivation mandate.',
        'latest_user_priority_exact':'',
        'next_actions':[],
        'open_questions':[],
        'completion':'in_progress: mathematical reconstruction requires its own acceptance evidence',
    }
    for key,value in defaults.items():
        state.setdefault(key,value.copy() if isinstance(value,list) else value)
    return state

def main():
    path=ROOT/'state/task.json';raw=path.read_bytes();oldsha=hashlib.sha256(raw).hexdigest();history=ROOT/'state/checkpoint-history';history.mkdir(exist_ok=True)
    previous=history/('task-before-reconstruction-'+oldsha[:16]+'.json')
    if not previous.exists():previous.write_bytes(raw)
    state=json.loads(raw);report=json.loads((ROOT/'docs/evidence/reconstruction-verification.json').read_text(encoding='utf8'))
    if report['status']!='passed':raise ValueError('The current reconstruction has not passed its fidelity audit')
    modelraw=(ROOT/'state/reconstruction/model.json').read_bytes()
    if report['model_sha256']!=hashlib.sha256(modelraw).hexdigest():raise ValueError('Fidelity report does not match the current model')
    model=json.loads(modelraw)
    c=sqlite3.connect((ROOT/'data/sunny.sqlite').as_uri()+'?mode=ro',uri=True)
    counts={t:c.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in ('sources','conversations','messages','documents','nodes','refs','decisions')};c.close()
    preserve_user_context(state)
    state['updated_utc']=datetime.now(timezone.utc).isoformat()
    rule='Close finished owned processes; verify identities and preserve other chats/applications. Actual cloud SuperJev now works (jev-1.14.0); keep it distinct from local AgentJev-0.6B.'
    if rule not in state['constraints']:state['constraints'].append(rule)
    state['checkpoint_reconstruction_evidence']={'status':report['status'],'model_sha256':report['model_sha256'],'scope':'Source-fidelity audit only; does not replace current user context or mathematical acceptance.'}
    state['evidence']=sorted(set(state['evidence']+['docs/reconstruction/CURRENT_MODEL.md','state/reconstruction/model.json','docs/evidence/reconstruction-verification.json','docs/evidence/reconstruction-independent-review.json','docs/evidence/reconstruction-current-sources.json','docs/evidence/reconstruction-image-search.json','docs/evidence/reconstruction-image-fetch.json','docs/evidence/reconstruction-search-publication.json','docs/evidence/reconstruction-delivery-superjev.json','docs/evidence/process-lifecycle-check.json','docs/evidence/browser-process-cleanup.json']))
    state['observed_progress'].update({'source_occurrences':counts['sources'],'conversation_occurrences':counts['conversations'],'message_and_event_records':counts['messages'],'document_occurrences':counts['documents'],'reconstructed_music_records':len(model['components']['music-geometry']['records']),'reconstructed_decision_spans':len(model['components']['decisions']['records']),'reconstructed_comparative_claims':len(model['components']['correspondences']['claims']),'reconstructed_comparative_relations':len(model['components']['correspondences']['relations']),'reconstructed_native_worksheets':len(model['native_workbook_tables']),'reconstructed_transcript_tables':len(model['alignment_source_tables']),'model_fidelity_checks':report['checks'],'model_sha256':report['model_sha256'],'current_model_doc':'docs/reconstruction/CURRENT_MODEL.md','current_jev_route':'SuperJev cloud jev-1.14.0; pinned local service stopped when not needed','software_latest_full_suite':'not_passed: HTTP normal fixture expected400 observed504; exact waiting Node hosts closed; no synthetic result called inference'})
    continuation=ROOT/'CONTINUE.md'
    if continuation.exists():
        state['continuation_document']={'path':'CONTINUE.md','sha256':hashlib.sha256(continuation.read_bytes()).hexdigest(),'purpose':'Small recovery index; source histories remain in their full artifacts.'}
    state['observed_progress']['executed_mathematical_units']=[s['module'] for s in model.get('execution_module_snapshots',[]) if s['module']!='coverage']
    path.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf8')
    helper=resolve_superjev_helper()
    spec=importlib.util.spec_from_file_location('sunny_superjev_checkpoint',helper);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    checkpoint=ROOT/'state/superjev-checkpoint.json'
    if checkpoint.exists():
        prior=checkpoint.read_bytes();saved=history/('before-refresh-superjev-checkpoint-'+hashlib.sha256(prior).hexdigest()+'.json')
        if not saved.exists():saved.write_bytes(prior)
    envelope=module.checkpoint(state);checkpoint.write_text(json.dumps(envelope,ensure_ascii=False,indent=2),encoding='utf8');checked=module.verify_checkpoint(envelope)
    queuepath=ROOT/'state/work-queue.json';queue=json.loads(queuepath.read_text(encoding='utf8'));queue['current_priority']=state['current_priority'];queue['current_reconstruction_evidence']='docs/evidence/reconstruction-verification.json'
    observed={'Q-001':'implemented; latest HTTP worker test failure preserved','Q-002':'verified source/index integrity; exact derived reconstruction retrieval passed','Q-003':'24capabilities reconciled; inspected/executed/unavailable distinctions retained','Q-004':'bounded9-call metadata sensitivity checked; SUNNYdomaincalibration unknown','Q-005':'accessible current model reconstructed and source-fidelity verified; latest image package not retrieved','Q-006':'source-linked current model indexed and exact retrieval passed','Q-007':'current checkpoint and source-backed resume brief written; hash verified','Q-008':'full progressive derivation remains unfinished; recovered conditional results retained','Q-009':'reported current geometric integration retained; complete generational coordinate law not newly derived'}
    for task in queue['tasks']:
        if task['id'] in observed:task.setdefault('current_observed_state',observed[task['id']])
    queue['latest_user_priority_exact']=state['latest_user_priority_exact'];queuepath.write_text(json.dumps(queue,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'checkpoint_status':checked['status'],'checkpoint_sha256':checked['sha256'],'model_sha256':report['model_sha256'],'counts':counts,'prior_task_snapshot':str(previous)},indent=2))
if __name__=='__main__':main()
