"""Read-only verification of the recovered source snapshots and search index."""
from pathlib import Path
import collections,hashlib,json,sqlite3
ROOT=Path(__file__).resolve().parents[1]
c=sqlite3.connect((ROOT/'data'/'sunny.sqlite').as_uri()+'?mode=ro',uri=True)
ids=collections.Counter(row[0] for row in c.execute('SELECT id FROM search_index'))
report={'archive_member_count':len(json.loads((ROOT/'data'/'archive-manifest.json').read_text(encoding='utf8'))['members']),'counts':{},'source_hash_mismatches':[],'search_duplicate_ids':sum(n>1 for n in ids.values()),'search_missing_messages':sum(row[0] not in ids for row in c.execute('SELECT id FROM messages'))}
for name in ['sources','conversations','messages','nodes','documents','refs','decisions']:
    report['counts'][name]=c.execute('SELECT count(*) FROM '+name).fetchone()[0]
for sid,path,sha in c.execute('SELECT id,path,sha256 FROM sources'):
    actual=hashlib.sha256(Path(path).read_bytes()).hexdigest() if Path(path).is_file() else None
    if actual!=sha: report['source_hash_mismatches'].append({'id':sid,'path':path})
report['integrity']=c.execute('PRAGMA integrity_check').fetchone()[0]
report['foreign_key_violations']=c.execute('PRAGMA foreign_key_check').fetchall()
report['scope']='Integrity of preserved source bytes and index references; not completeness, authenticity, semantic truth or Jev approval.'
(ROOT/'docs'/'evidence'/'recovery-integrity.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
raise SystemExit(0 if report['integrity']=='ok' and not any(report[k] for k in ['source_hash_mismatches','search_duplicate_ids','search_missing_messages','foreign_key_violations']) else 1)
