"""Make the completed derived reconstruction retrievable through existing search."""
from pathlib import Path
import hashlib,json,sqlite3
from ingest import Importer
ROOT=Path(__file__).resolve().parents[1]
def main():
    original=ROOT/'docs/reconstruction/CURRENT_MODEL.md';raw=original.read_bytes();sha=hashlib.sha256(raw).hexdigest()
    snapshot=ROOT/'data/raw/reconstruction-derived'/sha/original.name;snapshot.parent.mkdir(parents=True,exist_ok=True)
    if snapshot.exists() and snapshot.read_bytes()!=raw:raise ValueError('Derived snapshot path has different bytes')
    if not snapshot.exists():snapshot.write_bytes(raw)
    c=sqlite3.connect(ROOT/'data/sunny.sqlite',timeout=30);c.execute('PRAGMA foreign_keys=ON');imp=Importer(c)
    try:
        c.execute('BEGIN IMMEDIATE');imp.import_file(snapshot,original,'derived_current_model_reconstruction');c.commit()
    except BaseException:c.rollback();raise
    row=c.execute('SELECT s.id,d.id,d.text FROM sources s JOIN documents d ON d.source_id=s.id WHERE s.path=?',(str(snapshot.resolve()),)).fetchone()
    found=c.execute('SELECT id FROM search_index WHERE search_index MATCH ? AND id=?',('"reconstructed current model"',row[1])).fetchall()
    report={'selection_evidence':'docs/evidence/reconstruction-delivery-superjev.json','source_id':row[0],'document_id':row[1],'snapshot':str(snapshot),'sha256':sha,'retrieved_text_matches':row[2]==raw.decode('utf-8-sig'),'fts_match_count':len(found),'source_kind':'derived_current_model_reconstruction','foreign_key_violations':c.execute('PRAGMA foreign_key_check').fetchall(),'boundary':'Derived editorial reconstruction, not a new native user source or independent corroboration. No new endpoint/UI or orientation selection.'}
    (ROOT/'docs/evidence/reconstruction-search-publication.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,indent=2));c.close()
    if not report['retrieved_text_matches'] or len(found)!=1 or report['foreign_key_violations']:raise ValueError('Derived model search publication failed')
if __name__=='__main__':main()
