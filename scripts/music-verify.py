"""Verify literal reconstruction pointers, excerpts, source bytes, IDs and counts."""
import collections,hashlib,json,sqlite3
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'state/reconstruction/music-geometry.json';model=json.loads(p.read_text(encoding='utf8'))
c=sqlite3.connect('file:'+str(ROOT/'data/sunny.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
sha=lambda b:hashlib.sha256(b).hexdigest()
canonical=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
source_text={};source_objects={};source_hashes={};errors=[];checks=collections.Counter()
for s in model['source_catalog']:
    raw=Path(s['path']).read_bytes();h=sha(raw);checks['source_bytes_checked']+=1
    if h!=s['sha256']:errors.append({'source_id':s['id'],'issue':'raw hash mismatch'})
    db=c.execute('SELECT sha256 FROM sources WHERE id=?',(s['id'],)).fetchone()
    if not db or db['sha256']!=h:errors.append({'source_id':s['id'],'issue':'indexed source identity mismatch'})
    source_text[s['id']]=raw.decode('utf-8-sig');source_hashes[s['id']]=h
    try:source_objects[s['id']]=json.loads(source_text[s['id']])
    except json.JSONDecodeError:pass
ids=[r['id'] for r in model['records']]
if len(ids)!=len(set(ids)):errors.append({'issue':'duplicate reconstruction IDs'})
for r in model['records']:
    for e in r['evidence']:
        checks['evidence_records_checked']+=1;quote=e['quote']; sid=e['source_id']
        text=source_text.get(sid)
        if e.get('message_id'):
            row=c.execute('SELECT text,source_id,role FROM messages WHERE id=?',(e['message_id'],)).fetchone()
            if not row or row['source_id']!=sid or quote not in row['text']:errors.append({'record':r['id'],'issue':'message quote/source mismatch'})
            continue
        if text is None:errors.append({'record':r['id'],'issue':'unregistered source'});continue
        if text[e['char_start']:e['char_end']]!=quote:errors.append({'record':r['id'],'issue':'exact quote span mismatch'})
        if sha(quote.encode('utf8'))!=e['quote_sha256']:errors.append({'record':r['id'],'issue':'quote hash mismatch'})
        if source_hashes[sid]!=e['source_sha256']:errors.append({'record':r['id'],'issue':'source evidence hash mismatch'})
        if 'json_pointer' in e:
            value=source_objects[sid]
            for part in e['json_pointer'].strip('/').split('/'):
                part=part.replace('~1','/').replace('~0','~')
                value=value[int(part)] if isinstance(value,list) else value[part]
            checks['json_pointer_values_checked']+=1
            if value!=r['value'] or json.loads(quote)!=value or sha(canonical(value).encode('utf8'))!=e['value_sha256']:errors.append({'record':r['id'],'issue':'literal JSON value mismatch'})
checks['reconstruction_records']=len(model['records'])
report={'status':'passed' if not errors else 'failed','checked_utc':datetime.now(timezone.utc).isoformat(),'artifact_sha256':sha(p.read_bytes()),'checks':dict(checks),'errors':errors,'scope':'Literal source-byte integrity, exact quote spans and materialized JSON equality. Not an independent proof of all source claims or full account completeness.'}
dest=ROOT/'docs/evidence/music-reconstruction-verification.json';dest.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2));raise SystemExit(bool(errors))
