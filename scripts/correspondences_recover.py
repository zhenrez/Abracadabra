"""Read-only correspondence discovery in the preserved SUNNY corpus."""
from pathlib import Path
import sqlite3, json, hashlib, re
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'/'evidence'
QUERIES={
 'gnostic_names':'Thelesis OR Theletos OR Aeinous OR Ainos OR Makariotes OR Makaria',
 'sri_yantra':'"Sri Yantra" OR "Shri Yantra" OR "nine triples" OR "sixteen petals" OR avarana',
 'sophia':'Sophia AND (Dodecad OR "twelfth" OR "thirtieth" OR "twenty seventh" OR midnight OR class)',
 'adam_roles':'Adam AND (Abel OR Cain OR Seth) AND (class OR "first" OR "zero" OR "0")',
 'ruth_reprise':'Ruth AND (Tamar OR Judah OR reprise OR Perez OR Zerah)',
 'dna':'DNA OR chromosome OR haplotype OR "240000" OR "242193529"',
 'zodiac_calendar':'zodiac AND (calendar OR wheel OR generational OR "36" OR precession)',
 'timeline':'"sacred timeline" OR (nomes AND ("36" OR W72)) OR "Sumerian King"',
 'other_branches':'"I Ching" OR "Yi Jing" OR Sephirot OR Sefirot OR Kabbalah OR bagua OR "Enneagram" OR "Tarot"',
}
def excerpt(text,query):
    words=[word for word in re.findall(r'[A-Za-z]{4,}',query) if word not in ['AND']]
    positions=[text.lower().find(word.lower()) for word in words]
    start=min([n for n in positions if n>=0] or [0]);start=max(0,start-160)
    return text[start:start+1700]
def main():
    c=sqlite3.connect('file:'+str(ROOT/'data'/'sunny.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
    c.execute('PRAGMA query_only=ON')
    report={'generated_utc':datetime.now(timezone.utc).isoformat(),'purpose':'Search pointers only; not adjudicated claims','queries':{},'corpus':{t:c.execute('select count(*) from '+t).fetchone()[0] for t in ['sources','messages','conversations','documents']}}
    select='''SELECT m.*,v.title,s.path AS source_path,s.original_path,s.sha256 AS source_sha256,s.kind AS source_kind
      FROM search_index f JOIN messages m ON m.id=f.id JOIN conversations v ON v.id=m.conversation_id JOIN sources s ON s.id=m.source_id
      WHERE search_index MATCH ? AND m.role='user' ORDER BY m.create_time DESC,m.id'''
    all_hits={}
    for label,query in QUERIES.items():
        rows=[dict(row) for row in c.execute(select,(query,))]
        unique={}
        for row in rows:
            key=row['content_sha256']
            if key not in unique:unique[key]={'representative':row,'occurrence_ids':[]}
            unique[key]['occurrence_ids'].append(row['id']);all_hits[row['id']]=row
        values=list(unique.values())
        report['queries'][label]={'query':query,'matching_user_occurrences':len(rows),'distinct_content_hashes':len(values),'inspected_preview_limit':80,'previews':[{'message_id':r['representative']['id'],'content_sha256':r['representative']['content_sha256'],'title':r['representative']['title'],'date':r['representative']['create_time'],'source_kind':r['representative']['source_kind'],'occurrence_count':len(r['occurrence_ids']),'characters':len(r['representative']['text']),'excerpt':excerpt(r['representative']['text'],query)} for r in values[:80]]}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'correspondences-search.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'correspondences-user-hits.json').write_text(json.dumps(list(all_hits.values()),ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:{a:b for a,b in v.items() if a!='previews'} for k,v in report['queries'].items()},indent=2))
    c.close()
if __name__=='__main__':main()
