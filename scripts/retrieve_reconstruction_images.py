"""Bounded same-origin retrieval of source-linked originals; never log signed URLs."""
from pathlib import Path
import hashlib,json,re,urllib.request,urllib.parse,urllib.error
ROOT=Path(__file__).resolve().parents[1]
SOURCE_ID='7d5a026c9df7d3fdf06382c966729a7cf3da22dbc4a1276c9f809f7a139ce965'
SOURCE=ROOT/'data/raw/reconstruction-recovered/73b3171aa010c78121f2d7798011ce36f6e4891f4ef1409d25ed98aaca16fcfc/ChatGPT-Comparative Research Protocol-20261030-1502.md'

def main():
    text=SOURCE.read_text(encoding='utf-8-sig')
    urls=list(dict.fromkeys(re.findall(r'!\[[^\]]*\]\((https://chatgpt\.com/backend-api/estuary/content\?[^\s\)]+)\)',text)))
    records=[]
    for url in urls:
        parsed=urllib.parse.urlparse(url); identifier=urllib.parse.parse_qs(parsed.query).get('id',[''])[0]
        if not re.fullmatch(r'file_[0-9a-f]+',identifier):continue
        record={'file_id':identifier,'status':'not_retrieved'}
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'image/*'})
            with urllib.request.urlopen(request,timeout=12) as response:
                kind=response.headers.get('Content-Type',''); data=response.read(25_000_001)
                if not kind.startswith('image/') or len(data)>25_000_000:raise ValueError('Not a bounded image response')
                dest=ROOT/'data/raw/reconstruction-images'/(identifier+('.png' if 'png' in kind else '.jpg'));dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
                record.update(status='retrieved_original',bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),path=str(dest),content_type=kind)
        except urllib.error.HTTPError as error:record.update(http_code=error.code,error_class=type(error).__name__)
        except Exception as error:record.update(error_class=type(error).__name__)
        records.append(record)
        # One access-denial establishes this unauthenticated route; do not hammer20URLs.
        if record.get('http_code') in (401,403):break
    report={'source_id':SOURCE_ID,'linked_image_count':len(urls),'attempts':records,'signed_urls_logged':False,'boundary':'Same chatgpt.com content links from preserved research source. No browser cookies, user credentials or unrelated account data used. A denial is retrieval failure, not absence.'}
    (ROOT/'docs/evidence/reconstruction-image-fetch.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
