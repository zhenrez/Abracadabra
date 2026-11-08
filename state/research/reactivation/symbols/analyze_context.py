from pathlib import Path
import xml.etree.ElementTree as ET
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parent
NS={'t':'http://www.tei-c.org/ns/1.0'}
tree=ET.parse(ROOT/'sources/elephantine_A3_7_tei.xml').getroot()
edition=next(x for x in tree.findall('.//t:div',NS) if x.get('type')=='edition')
lines=[]
for ab in edition.findall('t:ab',NS):
 lines.append({'section':ab.get('n'),'line':ab.find('t:lb',NS).get('n'),'normalized_text':' '.join(''.join(ab.itertext()).split()),'word_or_title_tags':[{'text':''.join(x.itertext()),'editor_gloss':x.get('key')} for x in ab.findall('t:rs',NS)],'restorations':[{'text':''.join(x.itertext()),'attributes':x.attrib} for x in ab.findall('.//t:supplied',NS)]})
out={'schema':'sunny.symbol-context-extraction.v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'sources/elephantine_A3_7_tei.xml','sha256':hashlib.sha256((ROOT/'sources/elephantine_A3_7_tei.xml').read_bytes()).hexdigest(),'scope':'Edition text and editorial annotations only; no reconstructed waveform and no original-glyph collation.','lines':lines,'first_displayed_character':{'character':lines[0]['normalized_text'][0],'codepoint':f'U+{ord(lines[0]["normalized_text"][0]):04X}'},'important_condition':'Do not silently collapse editorial restoration into visible ink or normalized script into original glyph form.'}
(ROOT/'context-extraction.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'lines':len(lines),'first_displayed_character':out['first_displayed_character'],'title_glosses':sorted({x['editor_gloss'] for line in lines for x in line['word_or_title_tags']})},ensure_ascii=False))
