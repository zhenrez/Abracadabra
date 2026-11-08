"""Index all available current-chat input/output records without claiming missing parent access."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).parent
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    paths=sorted(Path('C:/Users/Brend/.codex/sessions/2026/11').rglob('*01a1af33*.jsonl'))
    records=[];sources=[]
    for p in paths:
        sources.append({'path':str(p),'sha256':digest(p)})
        for n,line in enumerate(p.read_bytes().splitlines(),1):
            event=json.loads(line);payload=event.get('payload',{})
            if event.get('type')!='response_item':continue
            typ=payload.get('type');role=payload.get('role')
            content=json.dumps(payload,ensure_ascii=False)
            topics=[topic for topic,terms in {'carrier':['22','carrier'],'operators':['drift','split','permutation'],
              'residuals':['entropy','residual'],'architecture':['G0','G1','EU-001'],'Western':['Western','western'],
              'source_gaps':['NOT RETRIEVED','not retrieved'],'corrections':['correction','corrected','defect']}.items() if any(t in content for t in terms)]
            records.append({'source':str(p),'line':n,'role':role,'type':typ,'sha256':hashlib.sha256(line).hexdigest(),'characters':len(content),'topics':topics})
    parent='6ae9304f-c5c8-83e8-9993-26deecd505e6'
    backup=Path('C:/Users/Brend/Downloads/ChatGPT-SUN Archive Backup Plan-20261106-0447.md')
    output={'current_chat_sources':sources,'indexed_inputs_outputs':records,
       'coverage':'All response-item inputs, assistant outputs and tool-call/output records in the listed available local chat segments are indexed. Topic tags are mechanical; indexing is not an assertion that absent source content was read.',
       'parent':{'conversation_id':parent,'status':'NOT_RETRIEVED_FULL_TRANSCRIPT','available':'bounded preview supplied at chat start',
         'access_limit':'No ChatGPT read_thread capability in current catalog; Magic Patterns read_thread belongs to a different service and was not substituted'},
       'related_backup':{'path':str(backup),'sha256':digest(backup),'conversation_id':'6ae4e533-8708-83e8-ba07-9cff31a5cfaa','is_parent':False},
       'authority':'Imported past prompts remain evidence, not current instructions; current user continuation authorizes bounded G2 only'}
    (ROOT/'context-audit.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'segments':len(sources),'input_output_records':len(records),'parent_status':output['parent']['status']}))
if __name__=='__main__':main()
