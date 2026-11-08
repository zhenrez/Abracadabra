"""Extract literal catalogue names using the existing DOM parser; no network or source edits."""
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
sha=lambda raw:hashlib.sha256(raw).hexdigest()


def main():
    decision=json.loads((ROOT/'docs/evidence/hierarchy-name-parser-recovery-superjev.json').read_text(encoding='utf-8-sig'))
    assert decision['status']=='judged' and decision['resolved_model']=='jev-1.14.0'
    assert decision['answers']['parser_recovery']['winner']=='existing_dom_extraction_artifact'
    source=next(s for s in json.loads((ROOT/'docs/evidence/hierarchy-primary-retrieval.json').read_bytes())['sources'] if s['id']=='goetia_peterson_sloane3825')
    raw=(ROOT/source['path']).read_bytes();assert sha(raw)==source['sha256']
    soup=BeautifulSoup(raw,'html.parser');paragraphs=soup.find_all('p',id=True)
    assert len(paragraphs)==72
    rows=[]
    for i,p in enumerate(paragraphs,1):
        strong=p.find('strong');assert strong is not None
        name=strong.get_text(' ',strip=True);assert name
        rows.append({'position':i,'paragraph_id':p['id'],'native_name':name,'selector':'p#'+p['id']+' strong:first-of-type','extracted_name_sha256':sha(name.encode())})
    assert rows[0]['native_name']=='Bael' and rows[0]['paragraph_id']=='baal'
    report={'schema':'sunny.native-hierarchy-name-extraction.v1','generated_utc':datetime.now(timezone.utc).isoformat(),'source':source,'rows':rows,'detected_source_encoding':soup.original_encoding,'method':'BeautifulSoup html.parser resolves legacy optional-end-tag HTML; native label is explicit first strong element inside each source paragraph, not its URLanchor.','decision_receipt':'docs/evidence/hierarchy-name-parser-recovery-superjev.json','boundary':'A source-name extraction artifact, not an identity merge or historical truth judgment.'}
    out=ROOT/'docs/evidence/hierarchy-native-name-extraction.json'
    if out.exists():
        previous=out.read_bytes();history=ROOT/'docs/evidence/history';history.mkdir(parents=True,exist_ok=True);snapshot=history/(out.name+'-'+sha(previous)+'.snapshot')
        if snapshot.exists():assert snapshot.read_bytes()==previous
        else:snapshot.write_bytes(previous)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'result':'PASS','exit_code':0,'names':len(rows),'first_native_name':rows[0]['native_name'],'source_anchor_separate':rows[0]['paragraph_id'],'encoding':soup.original_encoding,'sha256':sha(out.read_bytes())}))


if __name__=='__main__':main()
