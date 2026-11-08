"""Preserve selected primary-source text and inspect the official method parameters."""
from pathlib import Path
import hashlib, json, re, sys
from html.parser import HTMLParser
import pdfplumber
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
class Text(HTMLParser):
 def __init__(self): super().__init__(); self.bits=[]
 def handle_starttag(self, tag, attrs):
  if tag in {"p","div","dt","dd","h1","h2","h3","code","br","address"}: self.bits.append("\n")
 def handle_endtag(self,tag):
  if tag in {"p","div","dt","dd","h1","h2","h3","code","address"}: self.bits.append("\n")
 def handle_data(self,data): self.bits.append(data)
def extract_html(path):
 p=Text(); p.feed(path.read_text(encoding="utf8"))
 return re.sub(r"\n[ \t]*\n+","\n", "".join(p.bits)).strip()+"\n"
if __name__ == "__main__":
 for ident in ["praat_source_filter","praat_spectrogram","praat_bada"]:
  path=ROOT/"sources"/(ident+".html")
  (ROOT/"sources"/(ident+".txt")).write_text(extract_html(path),encoding="utf8")
 formant=ROOT.parent/"symbols"/"sources"/"praat_formant.html"
 (ROOT/"sources"/"praat_formant.reused.txt").write_text(extract_html(formant),encoding="utf8")
 selected=[2,3,24,25,26,29,30,31,45,46,47,48,49,50,51,77,78,79,80,81,82,105,106,107,108,109,110]
 pdf=ROOT/"sources"/"garellek2013.pdf"
 pages=[]
 with pdfplumber.open(pdf) as doc:
  for i in selected:
   pages.append({"pdf_page":i+1,"printed_page":None if i<21 else i-20,"text":doc.pages[i].extract_text() or ""})
 payload={"source_path":"sources/garellek2013.pdf","source_sha256":hashlib.sha256(pdf.read_bytes()).hexdigest(),"method":"pdfplumber selected-page extraction; normalized text is not the original PDF.","selected_pages":pages}
 (ROOT/"sources"/"garellek2013.selected-pages.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf8")
 text="\n".join(f"--- PDF page {p['pdf_page']}; printed {p['printed_page']} ---\n{p['text']}" for p in pages)
 (ROOT/"sources"/"garellek2013.selected-pages.txt").write_text(text,encoding="utf8")
 print(json.dumps({"pages_extracted":len(pages),"source_sha256":payload["source_sha256"],"reused_formant_sha256":hashlib.sha256(formant.read_bytes()).hexdigest()}))
