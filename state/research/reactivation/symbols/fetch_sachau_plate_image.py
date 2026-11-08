from pathlib import Path
import urllib.request,urllib.parse,json,hashlib,datetime,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
d=json.loads((ROOT/'sources/sachau1911-archive-metadata.json').read_text(encoding='utf-8'))
objects=ET.parse(ROOT/'sources/sachau1911_djvu.xml').getroot().findall('.//OBJECT')
obj=objects[36];name=obj.find('PARAM[@name="PAGE"]').get('value').replace('.djvu','.jp2')
params={'zip':d['dir']+'/aramischepapyr02sachuoft_jp2.zip','file':'aramischepapyr02sachuoft_jp2/'+name,'scale':'1','rotate':'0'}
url='https://'+d['d1']+'/BookReader/BookReaderImages.php?'+urllib.parse.urlencode(params)
out={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'url':url,'selection':'OCR object36 PAGE parameter, verified file suffix0039; expected plate13 based on OCR, to verify visually','status':'unavailable'}
try:
 with urllib.request.urlopen(url,timeout=20) as r:b=r.read();ct=r.headers.get('Content-Type')
 p=ROOT/'sources/sachau1911-leaf0039.jpg';p.write_bytes(b);out.update(status='retrieved',sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),content_type=ct,local_path=str(p.relative_to(ROOT)))
except Exception as e:out['error']=str(e)
(ROOT/'sachau-image-retrieval.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
