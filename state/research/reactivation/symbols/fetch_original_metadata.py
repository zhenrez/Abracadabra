from pathlib import Path
import urllib.request,json,hashlib,datetime
ROOT=Path(__file__).resolve().parent
url='https://archive.org/metadata/aramischepapyr02sachuoft'
out={'url':url,'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
try:
 with urllib.request.urlopen(url,timeout=15) as r:b=r.read()
 p=ROOT/'sources/sachau1911-archive-metadata.json';p.write_bytes(b);d=json.loads(b);out.update(sha256=hashlib.sha256(b).hexdigest(),metadata=d.get('metadata'),files=[{k:x.get(k) for k in ['name','size','format']} for x in d.get('files',[]) if any(y in x.get('name','') for y in ['_djvu.txt','scandata','_jp2.zip','_djvu.xml'])])
except Exception as e:out['error']=str(e)
(ROOT/'sachau-metadata-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2)[:7500])
