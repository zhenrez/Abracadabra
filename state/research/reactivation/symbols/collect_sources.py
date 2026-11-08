from pathlib import Path
import hashlib,json,time,urllib.request,concurrent.futures,importlib.util
ROOT=Path(__file__).resolve().parent
SOURCES=[
 ('davies_excerpt','https://assets.cambridge.org/97805214/02484/excerpt/9780521402484_excerpt.pdf','.pdf'),
 ('elephantine_A3_7','https://elephantine.smb.museum/objects/object.php?o=308140','.html'),
 ('elephantine_A3_7_tei','https://p612399.webspaceconfig.de/xml/elephantine_erc_db_308140.tei.xml','.xml'),
 ('unicode16_ch10','https://unicode.org/versions/Unicode16.0.0/core-spec/chapter-10/','.html'),
 ('khan2020','https://books.openbookpublishers.com/10.11647/obp.0163.pdf','.pdf'),
 ('cmudict','https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict','.txt'),
 ('berlin_P23102','https://search.smb.museum/object/obj-2044263','.html'),
]
def fetch(item):
 ident,url,ext=item; started=time.time()
 record={'id':ident,'url':url,'retrieved_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'method':'urllib.request original URL,20s timeout','status':'unavailable'}
 try:
  request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 SUNNY-source-research'})
  with urllib.request.urlopen(request,timeout=20) as response:
   body=response.read();record.update(status='retrieved',final_url=response.url,http_status=response.status,content_type=response.headers.get('Content-Type'),bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
  destination=ROOT/'sources'/(ident+ext);destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(body);record['local_path']=str(destination.relative_to(ROOT))
  if ext=='.pdf' and importlib.util.find_spec('fitz'):
   import fitz
   doc=fitz.open(destination);text='\n'.join('--- PDF page '+str(i+1)+' ---\n'+p.get_text() for i,p in enumerate(doc));(ROOT/'sources'/(ident+'.txt')).write_text(text,encoding='utf-8');record['pdf_pages']=len(doc)
 except Exception as error:record['error']=type(error).__name__+': '+str(error)
 record['elapsed_seconds']=round(time.time()-started,3);return record
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:results=list(executor.map(fetch,SOURCES))
 (ROOT/'source-fetch-manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(results,ensure_ascii=False,indent=2))
