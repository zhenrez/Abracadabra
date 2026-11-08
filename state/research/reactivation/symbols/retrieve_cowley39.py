from pathlib import Path
import urllib.request,json,hashlib,datetime,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
ident='aramaicpapyrioff00ahikuoft';base='https://archive.org/'
records=[]
for kind,url in [('metadata','https://archive.org/metadata/'+ident),('text',base+'download/'+ident+'/'+ident+'_djvu.txt'),('xml',base+'download/'+ident+'/'+ident+'_djvu.xml')]:
 try:
  with urllib.request.urlopen(url,timeout=20) as r:b=r.read()
  suffix={'metadata':'.json','text':'.txt','xml':'.xml'}[kind];name='sources/cowley1923-'+kind+suffix;(ROOT/name).write_bytes(b);records.append({'url':url,'local_path':name,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'status':'retrieved'})
 except Exception as e:records.append({'url':url,'error':str(e),'status':'unavailable'})
textpath=ROOT/'sources/cowley1923-text.txt'
if textpath.exists():
 t=textpath.read_text(encoding='utf-8');hits=[]
 for pat in ['Shalwah','Shal','Hosea','13462','39.']:
  for m in list(re.finditer(re.escape(pat),t,re.I))[:12]:hits.append({'term':pat,'offset':m.start(),'context':t[max(0,m.start()-200):m.start()+500]})
 (ROOT/'cowley39-text-leads.json').write_text(json.dumps(hits,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(hits,ensure_ascii=False,indent=2)[:12500])
out={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records};(ROOT/'cowley39-retrieval.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
