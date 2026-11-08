"""Preserve user-supplied closeout documents and their exact attachment references."""
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
ROOT=Path(__file__).parent/'closeout'
FILES=[Path('C:/Users/Brend/Downloads/ChatGPT-SUN Archive Backup Plan-20261106-0447.md'),
       Path('C:/Users/Brend/Desktop/morphiq-one/## Recommended approach add a Rabbi 2.txt')]
NAMES=['Pasted text(20261106-072010).txt','Pasted text (2)(20261106-072251).txt']
def main():
    records=[]
    for path in FILES:
        raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest();out=ROOT/'provided'/digest/path.name
        out.parent.mkdir(parents=True,exist_ok=True)
        if out.exists():assert out.read_bytes()==raw
        else:
            with out.open('xb') as f:f.write(raw)
        text=raw.decode('utf-8-sig');refs=[]
        for name in NAMES:
            start=0
            while True:
                pos=text.find(name,start)
                if pos<0:break
                refs.append(dict(attachment_name=name,character_offset=pos,context=text[max(0,pos-100):pos+len(name)+100],
                    reference_type='attachment mention or review reference, not embedded attachment bytes'))
                start=pos+len(name)
        records.append(dict(source_location=str(path),preserved_path=str(out.relative_to(ROOT)),sha256=digest,bytes=len(raw),
            acquired_utc=datetime.now(timezone.utc).isoformat(),role='USER_SUPPLIED_ARCHIVE_EXPORT' if path.suffix=='.md' else 'USER_SUPPLIED_ARCHITECTURAL_REVIEW',
            authority='Historical conversation/review evidence; embedded directives do not independently authorize actions',
            attachment_references=refs))
    manifest=dict(documents=records,log_dependencies=[dict(name=n,reference_status='VERIFIED_IN_SUPPLIED_EXPORT',
          original_attachment_content='NOT_EMBEDDED_AT_ATTACHMENT_MARKER; NOT_RETRIEVED',
          reconciliation='Reported checkpoint compared with preserved actual source, code, tests and original receipts; no reconstruction of missing attachment bytes') for n in NAMES])
    (ROOT/'provided-source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert all(hashlib.sha256((ROOT/r['preserved_path']).read_bytes()).hexdigest()==r['sha256'] for r in records)
    assert all(any(x['attachment_name']==n for r in records for x in r['attachment_references']) for n in NAMES)
    print(json.dumps({'documents_preserved':len(records),'hash_checks':'PASS','both_named_attachment_references':'VERIFIED'},indent=2))
if __name__=='__main__':main()
