from pathlib import Path
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
import datetime,hashlib,json
ROOT=Path(__file__).resolve().parent
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,x):self.parts.append(x)
def source(name):
 p=ROOT/'sources'/name;b=p.read_bytes();return {'path':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def htmltext(name):
 p=Text();p.feed((ROOT/'sources'/name).read_text(encoding='utf-8'));return ' '.join(' '.join(p.parts).split())
ns={'t':'http://www.tei-c.org/ns/1.0'}
tree=ET.parse(ROOT/'sources/elephantine_A3_7_tei.xml').getroot()
edition=next(x for x in tree.findall('.//t:div',ns) if x.get('type')=='edition')
blocks=edition.findall('t:ab',ns)
recto=next(x for x in blocks if x.get('n')=='a' and x.find('t:lb',ns).get('n')=='1')
verso=next(x for x in blocks if x.find('t:lb',ns).get('n')=='vso1')
rt=' '.join(''.join(recto.itertext()).split());vt=' '.join(''.join(verso.itertext()).split());cal=htmltext('cal_A3_7.html')
tokens={'tei_recto':'עברכי','tei_verso':'עבדכי','cal_recto':'עבדכי'}
checks={'tei_recto_contains_reported_resh':tokens['tei_recto'] in rt,'tei_verso_contains_reported_dalet':tokens['tei_verso'] in vt,'cal_contains_dalet_token':tokens['cal_recto'] in cal,'cal_contains_resh_token':tokens['tei_recto'] in cal,'tei_recto_servant_tag':any(x.get('key')=='servant' and ''.join(x.itertext())=='עבר' for x in recto.findall('t:rs',ns))}
out={'schema':'sunny.symbol-source-discrepancy.v1','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'case':'TAD A3.7/Pap.Cairo EM JdE43473; normalized-text disagreement at recto address servant token','sources':[source('elephantine_A3_7_tei.xml'),source('cal_A3_7.html')],'tokens':{k:{'text':v,'codepoints':[f'U+{ord(c):04X}' for c in v]} for k,v in tokens.items()},'tei_recto_text':rt,'tei_verso_text':vt,'checks':checks,'observed_difference':'Third character: museum TEI recto U+05E8 HEBREW LETTER RESH; CAL and TEI verso U+05D3 HEBREW LETTER DALET. No source file changed.','source_report':'Museum TEI tags recto עבר as servant; CAL displays עבדכי; museum TEI verso displays עבדכי with עבד tagged servant.','inference':'This is an editorial/transcription disagreement requiring original-sign collation. A parser that normalizes both without recording the difference loses a distinction relevant to phonetic and lexical hypotheses.','not_established':['The actual ancient ink sign at the disputed position','That the historical scribe changed a sign','The original vowel realization or acoustic waveform','A hidden name or genealogical identity'],'deduction_changed':'Carry two source-qualified transcription branches at the disputed token. Do not use the display discrepancy alone to infer a historical phonetic substitution, mistransmission, merged identity or mathematical operator.','exposure':'Existing project hypotheses, scholarly baseline and both editions already seen; not blind.','next_evidence':'Original papyrus image or original TAD/Sachau facsimile at the exact recto address position; identify the dalet/resh sign without silently following either normalized edition.'}
(ROOT/'context-discrepancy.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
