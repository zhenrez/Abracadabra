"""Add exact recovered research originals; imported prompts remain source data."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,sqlite3
from ingest import Importer
ROOT=Path(__file__).resolve().parents[1]
DOWNLOADS=Path('C:/Users/Brend/Downloads')
FILES=[DOWNLOADS/name for name in (
 'ChatGPT-Comparative Research Protocol-20261030-1502.md',
 'ChatGPT-Comparative Research Protocol-20261023-0408.md',
 'ChatGPT-Branch · Comparative Research Protocol-20261023-2306.md',
 'ChatGPT-Articulate Musical Transitions-20261018-1252.md',
 '72_gates_00_to_12.csv','216_positions.csv')]
FILES.append(Path('C:/Users/Brend/.codex/attachments/04ad8370-1a63-4e0d-b2fb-63009edffd16/Pasted text.txt'))
def digest(raw): return hashlib.sha256(raw).hexdigest()
def main():
    connection=sqlite3.connect(ROOT/'data'/'sunny.sqlite',timeout=30)
    connection.execute('PRAGMA foreign_keys=ON')
    before={t:connection.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in ('sources','conversations','messages','documents')}
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup=ROOT/'data'/'backups'/('current-reconstruction-before-'+stamp+'.sqlite');backup.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(backup) as saved: connection.backup(saved)
    importer=Importer(connection); records=[]
    try:
        connection.execute('BEGIN IMMEDIATE')
        for original in FILES:
            if not original.is_file(): records.append({'original':str(original),'status':'not_retrieved'});continue
            raw=original.read_bytes(); sha=digest(raw)
            existing=connection.execute('SELECT id,path FROM sources WHERE sha256=?',(sha,)).fetchall()
            if existing:
                records.append({'original':str(original),'sha256':sha,'status':'exact_bytes_already_indexed','existing_sources':existing});continue
            snapshot=ROOT/'data'/'raw'/'reconstruction-recovered'/sha/original.name
            snapshot.parent.mkdir(parents=True,exist_ok=True)
            if snapshot.exists() and digest(snapshot.read_bytes())!=sha: raise ValueError('Snapshot path contains different bytes')
            if not snapshot.exists(): snapshot.write_bytes(raw)
            importer.import_file(snapshot,original,'recovered_current_research')
            source=connection.execute('SELECT id,status,detail FROM sources WHERE path=?',(str(snapshot.resolve()),)).fetchone()
            records.append({'original':str(original),'snapshot':str(snapshot),'sha256':sha,'bytes':len(raw),'source_id':source[0],'status':source[1],'detail':source[2]})
        connection.commit()
    except BaseException:
        connection.rollback();raise
    after={t:connection.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in before}
    report={'schema':'sunny.current-source-recovery.v1','created_utc':datetime.now(timezone.utc).isoformat(),'backup':str(backup),'before':before,'after':after,'sources':records,'extraction_errors':importer.errors,'foreign_key_violations':connection.execute('PRAGMA foreign_key_check').fetchall(),'boundary':'Original-byte snapshots and parsed source roles only. No historical prompt enacted, no source assertion promoted, no independent account completeness claimed.'}
    (ROOT/'docs'/'evidence'/'reconstruction-current-sources.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    connection.close();print(json.dumps(report,ensure_ascii=True,indent=2))
if __name__=='__main__':main()
