"""Read-only native music/geometric source discovery; original bytes stay unchanged."""
import json,sqlite3,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
c=sqlite3.connect('file:'+str(ROOT/'data'/'sunny.sqlite')+'?mode=ro',uri=True); c.row_factory=sqlite3.Row
terms=['chinese','western','huang','zhong','lü','律','sierpinski','torus','toroid','720','generational','music alphabet','pipe','harmonic','spinor','fourth axis','4d','tetrahed']
rx=re.compile('|'.join(re.escape(t) for t in terms),re.I)
catalog=json.loads((ROOT/'state'/'native-sources.json').read_text(encoding='utf8'))
native=[]
for key,g in catalog['groups'].items():
    row=g['copies'][0]; p=Path(row['path']); b=p.read_bytes()
    native.append({'group':key,'source_id':row['id'],'path':str(p),'original_path':row['original_path'],'sha256':hashlib.sha256(b).hexdigest(),'expected_sha256':row['sha256'],'bytes':len(b)})
docs=[]
for r in c.execute('SELECT d.*,s.sha256,s.original_path,s.path FROM documents d JOIN sources s ON s.id=d.source_id'):
    if rx.search(r['title']+' '+r['text']):
        row=dict(r);text=row.pop('text');row['text_characters']=len(text);row['text_sha256']=hashlib.sha256(text.encode('utf8')).hexdigest();docs.append(row)
msgs=[]
for r in c.execute("SELECT m.*,s.sha256 AS source_sha256,s.original_path,s.path,c.title AS conversation_title FROM messages m JOIN sources s ON s.id=m.source_id LEFT JOIN conversations c ON c.id=m.conversation_id WHERE m.role='user'"):
    if rx.search(r['text'] or ''):
        row=dict(r);text=row.pop('text');row.pop('raw_json',None);row['text_characters']=len(text);row['text_sha256']=hashlib.sha256(text.encode('utf8')).hexdigest();msgs.append(row)
out={'native_sources':native,'terms':terms,'documents':docs,'user_messages':msgs,'scope':'Term-discovered identity/hash inventory; exact original text remains in readonly data/sunny.sqlite and preserved source bytes. Matching is not semantic support or user approval.'}
dest=ROOT/'docs'/'evidence'/'music-discovery.json';dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'native':native,'document_occurrences':len(docs),'user_message_occurrences':len(msgs),'output':str(dest)},ensure_ascii=True,indent=2))
print(json.dumps([{'id':d['id'],'title':d['title'],'characters':d['text_characters'],'source_id':d['source_id']} for d in sorted(docs,key=lambda x:x['text_characters'])[:45]],ensure_ascii=True))
