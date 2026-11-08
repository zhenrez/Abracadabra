"""Append immutable hierarchy source snapshots to the existing provenance/search register."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sqlite3
from ingest import Importer
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    atlas=json.loads((ROOT/'state/reconstruction/hierarchy-atlas-combined.json').read_text(encoding='utf8'))
    images=json.loads((ROOT/'state/reconstruction/hierarchy-inputs.json').read_text(encoding='utf8'))
    candidates=[dict(s) for s in atlas['sources']]
    candidates.extend({'id':r['id'],'path':r['snapshot'],'sha256':r['sha256'],'kind':'user_supplied_image',
      'original_path':r['original_path']} for r in images['occurrences'])
    prepared=[]
    for source in candidates:
        p=Path(source['path']);p=p if p.is_absolute() else ROOT/p;p=p.resolve()
        raw=p.read_bytes()
        if sha(raw)!=source['sha256']:raise ValueError('Source bytes changed: '+source['id'])
        if p.is_relative_to(ROOT/'docs/evidence'):
            snapshot=ROOT/'data/raw/hierarchy-derived'/source['sha256']/p.name
            snapshot.parent.mkdir(parents=True,exist_ok=True)
            if snapshot.exists():
                if snapshot.read_bytes()!=raw:raise ValueError('Snapshot collision')
            else:snapshot.write_bytes(raw)
        else:
            if not p.is_relative_to(ROOT/'data/raw'):raise ValueError('Unexpected source location')
            snapshot=p
        prepared.append((source,snapshot))
    db=sqlite3.connect(ROOT/'data/sunny.sqlite',timeout=30);db.execute('PRAGMA foreign_keys=ON')
    before={t:db.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in ['sources','documents','messages','search_index']}
    message_fingerprint=sha(json.dumps(db.execute('SELECT id,content_sha256 FROM messages ORDER BY id').fetchall()).encode())
    importer=Importer(db);mapping=[]
    try:
        db.execute('BEGIN IMMEDIATE')
        for source,p in prepared:
            importer.import_file(p,source.get('original_path',source.get('url',source['path'])),'hierarchy:'+str(source.get('kind','primary_transcription')))
            row=db.execute('SELECT id,sha256 FROM sources WHERE path=?',(str(p.resolve()),)).fetchone()
            if row is None or row[1]!=source['sha256']:raise ValueError('Registered source mismatch')
            mapping.append({'graph_source_id':source['id'],'database_source_id':row[0],'path':str(p),'sha256':row[1]})
        if importer.errors:raise ValueError('Source extraction requires review: '+json.dumps(importer.errors))
        after={t:db.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in before}
        fingerprint_after=sha(json.dumps(db.execute('SELECT id,content_sha256 FROM messages ORDER BY id').fetchall()).encode())
        if message_fingerprint!=fingerprint_after:raise ValueError('Native message contents or IDs changed')
        if db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Foreign-key violations')
        if after['search_index']!=after['messages']+after['documents']:raise ValueError('FTS count identity failed')
        db.commit()
    except BaseException:db.rollback();raise
    report={'schema':'sunny.hierarchy-source-registration.v1','status':'passed','exit_code':0,
      'recorded_utc':datetime.now(timezone.utc).isoformat(),'before':before,'after':after,
      'message_ids_and_content_unchanged':True,'message_fingerprint':message_fingerprint,
      'mapping':mapping,'new_sources':after['sources']-before['sources'],
      'boundary':'Append-only source/document register and exact byte bindings. Binary preservation, source extraction and mathematical/semantic reconstruction remain separate; generated hierarchy slots are not native account messages.'}
    out=ROOT/'docs/evidence/hierarchy-source-registration.json'
    if out.exists():
        old=out.read_bytes();saved=ROOT/'state/checkpoint-history'/('before-source-registration-'+sha(old)+'.json')
        if not saved.exists():saved.write_bytes(old)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');db.close()
    print(json.dumps({k:v for k,v in report.items() if k!='mapping'}))
if __name__=='__main__':main()
