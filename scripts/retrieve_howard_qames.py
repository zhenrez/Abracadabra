"""Recover one explicitly identified open-access primary publication, without credentials."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,urllib.request
URL='https://www.cambridge.org/core/services/aop-cambridge-core/content/view/4EFF001CB490B361D48186E6DD1F1C99/S0041977X25100992a.pdf/the-qames-a-greater-shift-in-palestinian-hebrew-data-dating-and-diffusion.pdf'
OUT=Path(__file__).resolve().parents[1]/'state/delivery-2026-11-07/symbol-contact/root'
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    record={'url':URL,'retrievedAt':datetime.now(timezone.utc).isoformat(),'author':'Jonathan Howard',
        'title':'The qameṣ (*/aː/ > [ɔː]) shift in Palestinian Hebrew: data, dating, and diffusion',
        'doi':'10.1017/S0041977X25100992','onlineDate':'2025-12-22','issue':'BSOAS89(2),2026,229–239',
        'license':'CC BY-NC-SA4.0 as printed in source; no commercial redistribution claim'}
    try:
        request=urllib.request.Request(URL,headers={'User-Agent':'SUNNY source reconstruction (public publication retrieval)'})
        with urllib.request.urlopen(request,timeout=25) as response:
            raw=response.read(10*1024*1024+1);record.update(httpStatus=response.status,finalUrl=response.url)
        if not raw.startswith(b'%PDF-') or len(raw)>10*1024*1024:raise ValueError('Expected bounded original PDF')
        path=OUT/'howard-2026-qames.pdf';path.write_bytes(raw)
        record.update(status='retrieved',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),path=str(path))
    except Exception as exc:
        record.update(status='unavailable',errorCategory=type(exc).__name__,error=str(exc),sourceNonexistent=False)
    (OUT/'retrieval.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(record,ensure_ascii=False,indent=2))
    return int(record['status']!='retrieved')
if __name__=='__main__':raise SystemExit(main())
