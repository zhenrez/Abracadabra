"""Record the direct continuation request without replacing the mathematical mandate."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
def main():
    p=ROOT/'state/task.json';raw=p.read_bytes();state=json.loads(raw)
    history=ROOT/'state/checkpoint-history';history.mkdir(exist_ok=True)
    saved=history/('before-continuation-request-'+hashlib.sha256(raw).hexdigest()+'.json')
    if saved.exists():
        if saved.read_bytes()!=raw:raise ValueError('Prior-state snapshot collision')
    else:saved.write_bytes(raw)
    exact='Please continue and proceed. Additionally, create a lightweight context continuation document that you can utilize in the event that you fill your entire context window, so that you know what your state is and what you need to do next and what don\'t need to do over again.'
    additions=state.setdefault('continuation_requests',[])
    if not any(x.get('exact_request')==exact for x in additions):
        additions.append({'exact_request':exact,'recorded_utc':datetime.now(timezone.utc).isoformat(),
          'authority':'Root transcription of current direct user request; not a native chat serialization.',
          'selected_plugins':['Supplement Intelligence','SuperJev','Supermemory','Superpowers','Canonical Memory Verifier','Scout','Sacred Timeline Research'],
          'scope':'Continue SUNNY while maintaining a lightweight task-local recovery document; no abandonment or restart.'})
    old=state.get('favorites_status','')
    if 'question pending' in old:
        state.setdefault('superseded_context',[]).append({'text':old,
          'superseded_utc':datetime.now(timezone.utc).isoformat(),
          'reason':'Current direct mandate and continuation request keep mathematical work active. Preserve the image acquisition gap without a repeated surface-identification question.'})
        state['favorites_status']='All user-designated Favorites and recent80–100image originals remain in acquisition scope; originals not yet retrieved. Failed access loops stopped; mathematical reconstruction continues from retained source evidence.'
    state['updated_utc']=datetime.now(timezone.utc).isoformat()
    p.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'status':'recorded','exit_code':0,'continuation_requests':len(additions),
      'mandate_retained':state['current_instruction']['text_witness_sha256'],
      'previous_task':str(saved),'durable_user_memory_changed':False}))
if __name__=='__main__':main()
