"""Recover the exact current direct-user correction from the known native task log."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
SESSION=Path('C:/Users/Brend/.codex/sessions/2026/10/30/rollout-2026-10-30T17-44-55-01a18f6a-af21-78c1-83e2-02117c13aa7a.jsonl')
MARKER='I require background reconstruction to continue between turns.'
def main():
    found=[]
    with SESSION.open('rb') as stream:
        for number,raw in enumerate(stream,1):
            if MARKER.encode() not in raw:continue
            try:record=json.loads(raw)
            except ValueError:continue
            p=record.get('payload',{})
            if record.get('type')!='response_item' or p.get('type')!='message' or p.get('role')!='user':continue
            content=p.get('content',[])
            text='\n'.join(x.get('text','') for x in content if isinstance(x,dict) and x.get('type') in ('input_text','text'))
            if MARKER in text:found.append((number,raw,record,text))
    if not found:raise ValueError('Current native user correction not present in the known session log; no synthetic replacement created')
    occurrences=[]
    for number,raw,record,text in found:
        digest=hashlib.sha256(raw).hexdigest();out=ROOT/'data/raw/directions/semantics-2026-11-01'/digest;out.mkdir(parents=True,exist_ok=True)
        for name,b in [('native-user-record.jsonl',raw),('user-message.txt',text.encode('utf8'))]:
            p=out/name
            if p.exists():
                if p.read_bytes()!=b:raise ValueError('Immutable native-user snapshot collision')
            else:p.write_bytes(b)
        occurrences.append({'source_path':str(SESSION),'source_line':number,'source_role':'user',
          'timestamp':record.get('timestamp'),'record_sha256':digest,
          'record_snapshot':(out/'native-user-record.jsonl').relative_to(ROOT).as_posix(),
          'text_snapshot':(out/'user-message.txt').relative_to(ROOT).as_posix(),
          'text_sha256':hashlib.sha256(text.encode('utf8')).hexdigest(),'text_characters':len(text)})
    report={'schema':'sunny.current-semantics-native-user.v1','preserved_utc':datetime.now(timezone.utc).isoformat(),
      'occurrences':occurrences,'selected_latest':occurrences[-1],
      'boundary':'Exact native role=user response record and extracted text from the known task log. Quoted research examples remain source assertions; current user corrections govern mission interpretation.'}
    dest=ROOT/'docs/evidence/current-semantics-native-user.json'
    dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'preserved','exit_code':0,'native_occurrences':len(occurrences),'latest':occurrences[-1]},ensure_ascii=False))
if __name__=='__main__':main()
