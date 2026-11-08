"""Adopt the exact latest clarification while preserving prior task/plan/continuation bytes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(p):
    raw=p.read_bytes();q=ROOT/'state/checkpoint-history'/('before-mission-v2-'+p.name+'-'+hashlib.sha256(raw).hexdigest()+'.snapshot')
    q.parent.mkdir(exist_ok=True)
    if q.exists():
        if q.read_bytes()!=raw:raise ValueError('Immutable prior-state collision')
    else:q.write_bytes(raw)
    return {'path':q.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(raw).hexdigest()}
def main():
    mission=json.loads((ROOT/'state/mission.json').read_text(encoding='utf8'))
    authority=json.loads((ROOT/mission['authority']['current_user_record']).read_text(encoding='utf8'))['selected_latest']
    if digest(ROOT/authority['text_snapshot'])!=mission['authority']['current_user_text_sha256']:raise ValueError('Current native-user text digest mismatch')
    prior={name:snapshot(ROOT/name) for name in ('state/task.json','PLAN.md','CONTINUE.md')}
    p=ROOT/'state/task.json';state=json.loads(p.read_text(encoding='utf8'))
    adoption={'schema':mission['schema'],'native_user_record':'docs/evidence/current-semantics-native-user.json',
      'native_user_text':authority['text_snapshot'],'native_user_text_sha256':authority['text_sha256'],
      'mission_path':'state/mission.json','mission_sha256':digest(ROOT/'state/mission.json'),
      'adopted_utc':datetime.now(timezone.utc).isoformat(),'prior':prior,
      'boundary':'Latest clarification refines operational semantics; prior instructions/results survive within their scopes. No raw input, mathematical component or archived model is deleted or recanonicalized.'}
    history=state.setdefault('instruction_history',[])
    if not any(x.get('native_user_text_sha256')==authority['text_sha256'] for x in history):history.append(adoption)
    state['mission_semantics']=adoption
    state['goal']=mission['purpose']
    state['current_priority']='Continue mature hypothesis-led alignment with paired finite calendar and symbol/sound investigations, while historical forensics repairs relevant dependencies in parallel. Preserve simultaneous native Western/Chinese music, source-qualified Completed Harmony/TOL use and scoped holdouts, and non-presumptive Ophiuchus treatment.'
    state['latest_user_priority_exact']='The main purpose centers around several hypothesis\', which we are to be testing from multiple directions.'
    state['next_actions']=[
      'Select one source-documented calendar continuity/change scenario and execute its finite alternative trajectories with frames, anchors and intervention rules explicit.',
      'Select one witnessed Paleo-Hebrew/Aramaic/English symbol-sound comparison, retain dated alternatives and test a consequence not used to choose its mapping.',
      'Run targeted omission/bridge-scope forensics in the owned background worker; merge only source-verified dependency repairs and preserve unresolved classifications.',
      'Continue source-native hierarchy and geometric alignment where required premises are available, including alternative Ophiuchus roles without a presumed extra sector.',
      'Use actual Jev to choose high-information next cases; preserve full receipts, local failure conditions, alternatives and the distinction between exposed and withheld tests.']
    state['completion']='in_progress: continuing mature alignment and explicit calendar/phonetic outcomes with parallel forensic support; full intended architecture and predictive capability unfinished'
    state['background_requested']=True
    state['evidence']=sorted(set(state['evidence']+['state/mission.json','docs/reconstruction/MISSION_SEMANTICS.md',
      'docs/reconstruction/STRATEGY_OPTIONS.md','docs/evidence/current-semantics-native-user.json',
      'docs/evidence/mission-semantics-source-review.json','docs/evidence/strategy-options-verification.json']))
    state['updated_utc']=datetime.now(timezone.utc).isoformat()
    p.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf8')
    plan=ROOT/'PLAN.md';text=plan.read_text(encoding='utf8')
    old='- [1%] Complete the source-preserving ledger and source-linked mathematical reconstruction; implement progressive law, global candidate evaluation, Jev integration, source-native hierarchy censuses, and systemic/generational architecture under the current mandate.'
    new='- [1%] Continue the mature Jev-directed hypothesis investigation and native hierarchy alignment, prioritizing finite calendar-continuity and symbol/sound packets; run source-history repair in parallel and progressively derive laws, constraints and systemic/generational relationships.'
    if old in text:text=text.replace(old,new,1)
    elif new not in text:raise ValueError('Current plan wording changed; preserve and reconcile before replacement')
    plan.write_text(text,encoding='utf8')
    out=ROOT/'docs/evidence/mission-v2-adoption.json';out.write_text(json.dumps(adoption,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'adopted','exit_code':0,'mission_sha256':adoption['mission_sha256'],
      'prior_states_preserved':len(prior),'native_user_sha256':authority['text_sha256'],'mathematical_components_changed':False}))
if __name__=='__main__':main()
