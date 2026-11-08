"""Retrieve fixed public primary-method papers; no account data or credentials."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'state/delivery-2026-11-07/history-discriminator/primary'
SOURCES=[
 ('erdem-2005','https://arxiv.org/pdf/cs/0508129','Temporal Phylogenetic Networks and Logic Programming','Esra Erdem; Vladimir Lifschitz; Don Ringe'),
 ('angluin-1988','https://homepages.math.uic.edu/~lreyzin/papers/angluin88.pdf','Queries and Concept Learning','Dana Angluin'),
 ('dechter-1991','https://ftp.cs.ucla.edu/pub/stat_ser/r113-L-reprint.pdf','Temporal constraint networks','Rina Dechter; Itay Meiri; Judea Pearl')]

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rows=[]
    for key,url,title,authors in SOURCES:
        p=OUT/(key+'.pdf')
        if p.exists():
            raw=p.read_bytes();status='preserved-existing';http=None
        else:
            req=urllib.request.Request(url,headers={'User-Agent':'SUNNY primary-source research/1.0'})
            with urllib.request.urlopen(req,timeout=35) as response:
                raw=response.read(8_000_001);http=response.status;final=response.url
            assert len(raw)<=8_000_000 and raw.startswith(b'%PDF'),(url,len(raw))
            p.write_bytes(raw);status='retrieved'
        rows.append({'id':key,'title':title,'authors':authors,'url':url,'path':str(p.relative_to(ROOT)).replace('\\','/'),
            'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'status':status,'httpStatus':http,
            'retrievedAt':datetime.now(timezone.utc).isoformat(),'scope':'Primary-method paper bytes, not evidence of a Hebrew historical event'})
    report=OUT/'retrieval.json'
    if report.exists():
        old=report.read_bytes();history=OUT/'history';history.mkdir(exist_ok=True)
        saved=history/('retrieval-'+hashlib.sha256(old).hexdigest()+'.json')
        if saved.exists():assert saved.read_bytes()==old
        else:saved.write_bytes(old)
    report.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'retrieved','exit_code':0,'sources':rows}))

if __name__=='__main__':main()
