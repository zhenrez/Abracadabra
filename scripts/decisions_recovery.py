"""Read-only, provenance-preserving source inventory for decision reconstruction."""
import argparse, hashlib, json, re, sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'/'evidence'; OUT.mkdir(parents=True,exist_ok=True)
TITLES={
 'Branch · Mapping Primordials to Music','Branch · SUN Model Discussion',
 'Correct Zodiac Mapping','Mapping Primordials to Music','Mapping Zodiacal Music Structure',
 'Compare Ophiuchus SUN V4','Articulate SUNNY Specification',
 'Branch · Trace Fludd Kepler Clue','Comparative Research Protocol','Evidence Atlas Design',
 'Begin Field Enumeration','Stress test primitives','Discuss Boolean Architecture',
 'Synthesize Relational Architectures','Branch · Branch · Synthesize Relational Architectures',
 'Adaptive Epistemic Resolution','Recall Naming Rationale','Everything Is A Node',
 'Articulate Musical Transitions','Branch · Comparative Research Protocol',
}
TERMS=re.compile(r'\b(?:SUN|SUNNY|SOL|SOFI|SOPHIA|SATURN|W72|W144|pleroma|Sierpinski|Monad)\b',re.I)
def sha(text):return hashlib.sha256(text.encode('utf8')).hexdigest()
def main():
 c=sqlite3.connect('file:'+str(ROOT/'data'/'sunny.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
 rows=c.execute('SELECT m.rowid source_order,m.*,c.title,c.native_id conversation_native_id,s.path source_path,s.original_path,s.sha256 source_sha256,s.kind source_kind FROM messages m JOIN conversations c ON c.id=m.conversation_id JOIN sources s ON s.id=m.source_id WHERE m.role=\'user\'').fetchall()
 selected=[]; candidates=[]
 for row in rows:
  d=dict(row); text=d['text'] or ''
  is_title=d['title'] in TITLES
  is_codex=('Codex ' in d['title'] and '\\ChatGPT\\SUN' in d['title'] and len(text)<150000)
  if not (is_title or (is_codex and TERMS.search(text))):continue
  if len(text)>150000:continue # oversized pasted exports require separate source-native traversal
  stamp=re.match(r'^(\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2}:\d{2} [AP]M)',text)
  d['recorded_display_time']=stamp.group(1) if stamp else None
  d['timestamp_precision']='literal displayed second; timezone unspecified' if stamp else 'source metadata only'
  d['text_sha256']=sha(text)
  selected.append(d)
 groups={}
 for row in selected:groups.setdefault(row['text_sha256'],[]).append(row)
 for digest,occ in groups.items():
  primary=occ[0];text=primary['text'];body=re.sub(r'^\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2}:\d{2} [AP]M\s*','',text)
  candidates.append({'key':digest[:16],'text':text,'body':body,'title':primary['title'],'display_time':primary['recorded_display_time'],'occurrences':[{k:r[k] for k in ('id','conversation_id','conversation_native_id','source_id','source_path','original_path','source_sha256','locator','create_time','branch_status','source_order','source_kind')} for r in occ]})
 result={'schema':'sunny.decisions-source-inventory.v1','all_user_message_occurrences':len(rows),'selected_occurrences':len(selected),'unique_selected_texts':len(candidates),'selected_titles':sorted({r['title'] for r in selected}),'selection_method':'Exact declared title pool plus bounded relevant user turns in local SUN Codex snapshots; full corpus not semantically screened. Duplicate text grouped without deleting occurrence provenance.','candidates':candidates}
 (OUT/'decisions-source-inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 listing=[]
 for r in candidates:
  b=r['body']; para=b.split('\n\n')[0]
  if len(para)<70:para=b[:550]
  listing.append({'key':r['key'],'date':r['display_time'],'title':r['title'],'chars':len(b),'excerpt':para[:800]})
 (OUT/'decisions-candidate-list.json').write_text(json.dumps(listing,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps({k:v for k,v in result.items() if k!='candidates'},ensure_ascii=True));c.close()
if __name__=='__main__':main()
