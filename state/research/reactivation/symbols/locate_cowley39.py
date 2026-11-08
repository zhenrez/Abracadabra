from pathlib import Path
import json,xml.etree.ElementTree as ET,datetime
ROOT=Path(__file__).resolve().parent
meta=json.loads((ROOT/'sources/cowley1923-metadata.json').read_text(encoding='utf-8'))
zipfile=next(x for x in meta['files'] if x['name'].endswith('_jp2.zip'))
objects=ET.parse(ROOT/'sources/cowley1923-xml.xml').getroot().findall('.//OBJECT')
records=[]
for i,x in enumerate(objects):
 text=' '.join(w.text or '' for w in x.findall('.//WORD'))
 if 'Selava' in text and i<230:
  records.append({'object_index':i,'page_file':x.get('usemap'),'text':text})
out={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'zip':{'name':zipfile['name'],'size':int(zipfile['size'])},'pages':records,'scope':'OCR locates printed page; it does not adjudicate Hebrew letter shape.'}
(ROOT/'cowley39-page-locator.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'zip':out['zip'],'pages':[{'object_index':x['object_index'],'page_file':x['page_file'],'text':x['text'][:2200]} for x in records]},ensure_ascii=False,indent=2))
