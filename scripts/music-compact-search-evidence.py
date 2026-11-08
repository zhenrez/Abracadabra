"""Remove redundant generated corpus copies; original evidence and model stay intact."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
report=[]
for name in ('music-discovery.json','music-chinese-user-turns.json','music-geometry-user-turns.json','music-focused-documents.json'):
    p=ROOT/'docs/evidence'/name
    if not p.exists():continue
    old_bytes=p.stat().st_size;obj=json.loads(p.read_text(encoding='utf8'))
    groups=[obj] if isinstance(obj,list) else [obj['documents'],obj['user_messages']]
    for rows in groups:
        for row in rows:
            text=row.pop('text',None);row.pop('raw_json',None)
            if text is not None:row.update(text_characters=len(text),text_sha256=hashlib.sha256(text.encode('utf8')).hexdigest())
    if isinstance(obj,dict):obj['scope']='Lexical discovery inventory only. Full original text remains in readonly data/sunny.sqlite and preserved source files; these IDs/hashes are not verified semantic claims.'
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8');report.append({'file':name,'before_bytes':old_bytes,'after_bytes':p.stat().st_size})
(ROOT/'docs/evidence/music-generated-evidence-compaction.json').write_text(json.dumps({'scope':'Only generated redundant search copies compacted; original sources, source DB and reconstructed model unchanged.','files':report},indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
