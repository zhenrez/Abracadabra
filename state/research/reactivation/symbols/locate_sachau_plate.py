from pathlib import Path
import urllib.request,xml.etree.ElementTree as ET,json,hashlib,datetime
ROOT=Path(__file__).resolve().parent
base='https://archive.org/download/aramischepapyr02sachuoft/'
records=[]
for suffix in ['scandata.xml','djvu.txt','djvu.xml']:
 name='aramischepapyr02sachuoft_'+suffix;url=base+name
 try:
  with urllib.request.urlopen(url,timeout=15) as r:b=r.read()
  (ROOT/'sources'/('sachau1911_'+suffix)).write_bytes(b);records.append({'url':url,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'local_path':'sources/sachau1911_'+suffix})
 except Exception as e:records.append({'url':url,'error':str(e)})
p=ROOT/'sources/sachau1911_scandata.xml'
if p.exists():
 tree=ET.parse(p).getroot();pages=[{'leaf':x.get('leafNum'),'pageNumber':x.findtext('pageNumber'),'type':x.findtext('pageType')} for x in tree.findall('.//pageData/page')];print(json.dumps(pages[:65],ensure_ascii=False,indent=2))
 (ROOT/'sachau-scanned-leaves.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
out={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records}
(ROOT/'sachau-plate-retrieval.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
