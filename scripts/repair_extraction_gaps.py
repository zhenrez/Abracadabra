"""Jev-selected, source-preserving repair for the observed SUNNY import gaps."""
from __future__ import annotations
import argparse, collections, hashlib, json, sqlite3, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path
from ingest import canonical, stable, flatten, safe_zip_name, Importer

ROOT=Path(__file__).resolve().parents[1]
PIN='8166e46dc6019ae13f0d8fc97d603cdbcc2d20eb1882c7350c8deb9fc6bae215'
safe_member_name=safe_zip_name
POSITION_SCHEMA='''
CREATE TABLE IF NOT EXISTS source_positions(
 message_id TEXT PRIMARY KEY REFERENCES messages(id),source_id TEXT NOT NULL REFERENCES sources(id),
 physical_lf_line INTEGER NOT NULL,utf8_byte_start INTEGER NOT NULL,utf8_byte_end INTEGER NOT NULL,
 raw_record_sha256 TEXT NOT NULL,legacy_locator TEXT,legacy_native_id TEXT,native_ordinal INTEGER,
 sequence_semantics TEXT NOT NULL,mapping_basis TEXT NOT NULL,
 decision_receipt TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS source_locator_history(
 id TEXT PRIMARY KEY,message_id TEXT NOT NULL REFERENCES messages(id),source_id TEXT NOT NULL REFERENCES sources(id),
 previous_locator TEXT NOT NULL,previous_basis TEXT NOT NULL,new_locator TEXT NOT NULL,new_basis TEXT NOT NULL,
 decision_receipt TEXT NOT NULL,recorded_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS extraction_repairs(
 id TEXT PRIMARY KEY,source_id TEXT NOT NULL REFERENCES sources(id),method TEXT NOT NULL,
 previous_state_json TEXT NOT NULL,new_state_json TEXT NOT NULL,decision_receipt TEXT NOT NULL,recorded_at TEXT NOT NULL);
'''

def sha(raw): return hashlib.sha256(raw).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()

def physical_records(raw):
    """LF framing preserves legal U+2028/U+2029 inside JSON string values."""
    start=0
    for line_no,line in enumerate(raw.split(b'\n'),1):
        end=start+len(line)
        if line.strip():
            yield {'line':line_no,'start':start,'end':end,'raw':line,'record':json.loads(line)}
        start=end+1

def verified_source(db,sid):
    row=db.execute('SELECT path,sha256 FROM sources WHERE id=?',(sid,)).fetchone()
    if not row: raise ValueError('Unknown source '+sid)
    raw=Path(row[0]).read_bytes()
    if sha(raw)!=row[1]: raise ValueError('Source bytes changed: '+row[0])
    return Path(row[0]),raw

def repair_jsonl_source(db,sid,receipt,policy):
    if policy!='revise_with_history': raise ValueError('This repair implements only the selected history-preserving revision policy')
    for statement in POSITION_SCHEMA.split(';'):
        if statement.strip(): db.execute(statement)
    path,raw=verified_source(db,sid)
    conv=db.execute('SELECT id,title FROM conversations WHERE source_id=?',(sid,)).fetchall()
    if len(conv)!=1: raise ValueError('Expected one native snapshot conversation per source')
    cid,title=conv[0]
    rows=db.execute('''SELECT m.id,m.native_id,m.locator,m.raw_json,p.physical_lf_line
        FROM messages m LEFT JOIN source_positions p ON p.message_id=m.id
        WHERE m.source_id=? ORDER BY COALESCE(p.physical_lf_line,CAST(m.native_id AS INTEGER)),m.id''',(sid,)).fetchall()
    by_hash=collections.defaultdict(collections.deque)
    for mid,nid,locator,raw_json,position in rows:
        by_hash[sha(raw_json.encode())].append((mid,nid,locator))
    added=[]; mapped=changed=0
    for item in physical_records(raw):
        record=item['record']; serialized=canonical(record); key=sha(serialized.encode())
        known=by_hash[key].popleft() if by_hash[key] else None
        if known: mid,nid,old_locator=known
        else:
            nid='physicalLF:'+str(item['line']); mid=stable(cid,nid); old_locator=None
            if db.execute('SELECT 1 FROM messages WHERE id=?',(mid,)).fetchone(): raise ValueError('Recovered message ID collision')
            payload=record.get('payload',{}); role=payload.get('role') or payload.get('type') or record.get('type','unknown')
            if role in ('function_call','custom_tool_call'): role='tool_call'
            text=flatten(payload['content']) if 'content' in payload else canonical(payload)
            # Source sequence is known; a native causal/parent relationship is not
            # inferred merely because two JSON records occupy adjacent lines.
            Importer(db).message(cid,nid,None,role,text,sid,'pending_exact_position',record.get('timestamp'),'recovered_native_sequence',record)
            added.append({'message_id':mid,'native_id':nid,'physical_lf_line':item['line'],'record_type':record.get('type'),'native_ordinal':record.get('ordinal')})
        locator=f'physicalLF:{item["line"]};utf8bytes:[{item["start"]},{item["end"]})'
        existing=db.execute('SELECT physical_lf_line,utf8_byte_start,utf8_byte_end,raw_record_sha256 FROM source_positions WHERE message_id=?',(mid,)).fetchone()
        position=(item['line'],item['start'],item['end'],sha(item['raw']))
        if existing and existing!=position: raise ValueError('A recorded exact position changed')
        if not existing:
            ordinal=record.get('ordinal')
            db.execute('INSERT INTO source_positions VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(mid,sid,*position,old_locator,nid if known else None,ordinal if type(ordinal) is int else None,'physical_source_record_order_only_not_causal_parentage','canonical_raw_json_hash_and_source_order',receipt))
        if old_locator is not None and old_locator!=locator:
            hid=stable(mid,old_locator,locator)
            db.execute('INSERT OR IGNORE INTO source_locator_history VALUES(?,?,?,?,?,?,?,?,?)',(hid,mid,sid,old_locator,'python_str_splitlines_legacy',locator,'physical_lf_utf8_bytes',receipt,now()))
            changed+=1
        db.execute('UPDATE messages SET locator=? WHERE id=?',(locator,mid)); mapped+=1
    leftovers=sum(len(v) for v in by_hash.values())
    if leftovers: raise ValueError(f'{leftovers} existing records could not be mapped to unchanged source bytes')
    detail={'method':'physical_lf_utf8_byte_positions','source_id':sid,'mapped_records':mapped,'added_records':added,'revised_existing_locators':changed,'old_coordinate_basis':'Python str.splitlines, including Unicode separators','new_coordinate_basis':'one-based physical LF line and half-open UTF8byte range','causal_parentage':'not inferred for newly recovered records','decision_receipt':receipt}
    db.execute('INSERT OR REPLACE INTO coverage VALUES(?,?,?,?)',('gap_positions:'+sid,'positions_repaired',str(path),canonical(detail)))
    return detail

def npz_metadata(path):
    import numpy as np
    # Check archive allocations before NumPy is allowed to read array storage.
    with zipfile.ZipFile(path) as z:
        members=z.infolist()
        if len(members)>4096 or sum(i.file_size for i in members)>64*1024*1024 or any(i.file_size>16*1024*1024 for i in members): raise ValueError('NPZ allocation bound exceeded')
    with np.load(path,allow_pickle=False) as arrays:
        records=[]
        for name in arrays.files:
            value=arrays[name]
            records.append({'name':name,'dtype':str(value.dtype),'shape':list(value.shape),'elements':int(value.size),'numeric_values_indexed':False})
    return {'format':'numpy_npz','numpy_version':np.__version__,'allow_pickle':False,'arrays':records,'scope':'typed metadata only; values remain in unchanged original NPZ and prior read-only inspection evidence'}

def zip_inventory(path):
    with zipfile.ZipFile(path) as z:
        infos=z.infolist(); total=sum(i.file_size for i in infos)
        if len(infos)>4096 or total>64*1024*1024 or any(i.file_size>16*1024*1024 for i in infos): raise ValueError('Inventory read bounds exceeded')
        members=[]
        for info in infos:
            try: safe_path=str(safe_member_name(info.filename)); path_status='safe_if_extraction_later_authorized'
            except ValueError: safe_path=None; path_status='unsafe_for_extraction'
            digest=None
            if not info.is_dir():
                h=hashlib.sha256()
                with z.open(info) as stream:
                    for block in iter(lambda:stream.read(1024*1024),b''): h.update(block)
                digest=h.hexdigest()
            members.append({'member':info.filename,'bytes':info.file_size,'compressed_bytes':info.compress_size,'crc32':info.CRC,'sha256':digest,'directory':info.is_dir(),'safe_local_path':safe_path,'path_status':path_status,'content_indexed':False})
    return {'format':'zip_member_inventory','member_count':len(infos),'uncompressed_bytes':total,'members':members,'scope':'immediate member metadata and hashes only; no filesystem expansion, recursive content indexing or embedded code execution'}

def metadata_document(db,sid,metadata,extractor,status,receipt):
    path,_=verified_source(db,sid); old=db.execute('SELECT status,detail FROM sources WHERE id=?',(sid,)).fetchone()
    text=canonical(metadata); did=stable(sid,'gap_metadata_v1')
    exists=db.execute('SELECT text FROM documents WHERE id=?',(did,)).fetchone()
    if exists and exists[0]!=text: raise ValueError('Metadata extraction version changed without a new version ID')
    if not exists:
        db.execute('INSERT INTO documents VALUES(?,?,?,?,?,?)',(did,sid,path.name+' · source metadata',text,extractor,'metadata_only'))
        db.execute('INSERT INTO search_index VALUES(?,?,?,?)',(did,'document',path.name+' · source metadata',text))
    rid=stable(sid,extractor)
    db.execute('INSERT OR IGNORE INTO extraction_repairs VALUES(?,?,?,?,?,?,?)',(rid,sid,extractor,canonical({'status':old[0],'detail':old[1]}),canonical({'status':status,'document_id':did}),receipt,now()))
    db.execute('UPDATE sources SET status=?,detail=? WHERE id=?',(status,'Original bytes retained; metadata-only policy selected by '+receipt,sid))
    return {'source_id':sid,'document_id':did,'new_document':not bool(exists),'status':status,'metadata':metadata}

def read_receipt(path,expected):
    r=json.loads(path.read_text(encoding='utf8'))
    payload={k:v for k,v in r.items() if k not in ('status','sha256')}
    if r.get('status')!='judged' or sha(canonical(payload).encode())!=r.get('sha256') or r.get('server_info',{}).get('checkpoint_sha256')!=PIN: raise ValueError('Invalid actual Jev receipt')
    log=sqlite3.connect(ROOT/'state'/'jev-decisions.sqlite')
    stored=log.execute('SELECT payload_json FROM decisions WHERE sha256=?',(r['sha256'],)).fetchone(); log.close()
    if not stored or json.loads(stored[0])!=payload: raise ValueError('Receipt is not in the actual decision log')
    answers={a['id']:a['value'] for a in r['response']['results'][0]['answers']}
    if any(answers.get(k)!=v for k,v in expected.items()): raise ValueError('Implementation does not match selected Jev method; no fallback applied')
    return str(path.resolve())

def counts(db):
    return {t:db.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in ('sources','conversations','messages','documents','search_index')}

def search_integrity(db):
    index=collections.Counter(row[0] for row in db.execute('SELECT id FROM search_index'))
    messages={row[0] for row in db.execute('SELECT id FROM messages')}
    documents={row[0] for row in db.execute('SELECT id FROM documents')}
    return {'search_duplicate_ids':sum(n>1 for n in index.values()),'messages_missing_search':len(messages-index.keys()),'documents_missing_search':len(documents-index.keys()),'orphan_search_ids':len(index.keys()-(messages|documents))}

def verify_repair(db,backup,methods,positions,verification_receipt=None):
    evidence=ROOT/'docs'/'evidence'; report_before=evidence/'gaps-recovery-report-before.json'
    mismatches=[]
    for sid,path,expected in db.execute('SELECT id,path,sha256 FROM sources'):
        p=Path(path); actual=sha(p.read_bytes()) if p.is_file() else None
        if actual!=expected: mismatches.append({'source_id':sid,'path':path})
    old=sqlite3.connect(backup.resolve().as_uri()+'?mode=ro',uri=True); before=counts(old); changed_payloads=[]
    for row in old.execute('SELECT id,text,content_sha256,raw_json FROM messages'):
        current=db.execute('SELECT id,text,content_sha256,raw_json FROM messages WHERE id=?',(row[0],)).fetchone()
        if current!=row: changed_payloads.append(row[0])
    old.close()
    invalid_positions=[]; source_bytes={}
    for mid,sid,start,end,digest,raw_json in db.execute('''SELECT p.message_id,p.source_id,p.utf8_byte_start,p.utf8_byte_end,p.raw_record_sha256,m.raw_json
            FROM source_positions p JOIN messages m ON m.id=p.message_id'''):
        if sid not in source_bytes: source_bytes[sid]=verified_source(db,sid)[1]
        raw=source_bytes[sid][start:end]
        if sha(raw)!=digest or canonical(json.loads(raw))!=raw_json: invalid_positions.append(mid)
    repairs=[json.loads(row[0]) for row in db.execute("SELECT detail FROM coverage WHERE id LIKE 'gap_positions:%'")]
    metadata=[{'source_id':sid,'document_id':did,'status':status,'metadata':json.loads(text)} for did,sid,text,status in db.execute("SELECT id,source_id,text,status FROM documents WHERE extractor IN ('numpy_npz_metadata_allow_pickle_false_v1','zip_immediate_member_inventory_v1')")]
    search=search_integrity(db)
    report={'generated_at':now(),'backup':str(backup.resolve()),'previous_report_snapshot':str(report_before),'previous_report_sha256':sha(report_before.read_bytes()),'method_receipt':methods,'position_receipt':positions,'verification_receipt':verification_receipt,'before_counts':before,'after_counts':counts(db),'source_hash_mismatches':mismatches,'changed_existing_message_payloads':changed_payloads,'invalid_exact_positions':invalid_positions,'integrity':db.execute('PRAGMA integrity_check').fetchone()[0],'foreign_key_violations':db.execute('PRAGMA foreign_key_check').fetchall(),**search,'position_rows':db.execute('SELECT count(*) FROM source_positions').fetchone()[0],'locator_history_rows':db.execute('SELECT count(*) FROM source_locator_history').fetchone()[0],'jsonl_repairs':repairs,'metadata_documents':metadata,'remaining_boundaries':['NPZ values are not indexed under the actual selected metadata-only policy; exact bytes and inspection values are preserved.','ZIP member contents remain unindexed under the selected inventory-only policy.','Original legacy native_id values remain splitline indices, not native upstream ordinals.','External references, hidden/deleted/unexported data and live-account completeness are not resolved by this repair.']}
    (evidence/'gaps-repair-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('metadata_documents','jsonl_repairs')},indent=2))
    if mismatches or changed_payloads or invalid_positions or report['integrity']!='ok' or report['foreign_key_violations'] or any(search.values()): raise ValueError('Post-repair integrity checks failed; report preserved')
    return report

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--methods-receipt',required=True,type=Path); parser.add_argument('--positions-receipt',required=True,type=Path); parser.add_argument('--apply',action='store_true'); parser.add_argument('--verify-existing-backup',type=Path); parser.add_argument('--verification-receipt',type=Path); args=parser.parse_args()
    methods=read_receipt(args.methods_receipt,{'npz_method':'metadata_only','zip_method':'inventory_only','jsonl_method':'native_byte_ranges'})
    positions=read_receipt(args.positions_receipt,{'position_policy':'revise_with_history'})
    dbpath=ROOT/'data'/'sunny.sqlite'
    if args.verify_existing_backup:
        if args.apply or not args.verification_receipt: parser.error('Verification-only mode needs its real Jev receipt and cannot be combined with --apply')
        verification=read_receipt(args.verification_receipt,{'verification_strategy':'exact_set_check'})
        db=sqlite3.connect(dbpath.resolve().as_uri()+'?mode=ro',uri=True,timeout=30)
        verify_repair(db,args.verify_existing_backup,methods,positions,verification); db.close(); return
    db=sqlite3.connect(dbpath,timeout=30); db.execute('PRAGMA foreign_keys=ON')
    targets=('7d238ce055467ea882309255187115ec9800af7c16c7ec6884cee3cb2abcd4b8','1bf427a3695d99792ec14efa7f6db2c51f78b20aaaa8836559f5a2f2d53f5292','bd6e143dade95252bfe372ca835593f418adc57d8dfe113fd792a92e7437a6c2')
    pending=db.execute("SELECT id,path FROM sources WHERE id IN (?,?,?) AND status IN ('preserved_extraction_pending','preserved_unexpanded')",targets).fetchall()
    codex=db.execute("SELECT id,path FROM sources WHERE original_path LIKE '%01a17a00-f6af%' OR original_path LIKE '%01a17b1c-bcae%'").fetchall()
    if not args.apply:
        print(json.dumps({'status':'preview','pending_sources':pending,'jsonl_sources':codex,'methods_receipt':methods,'positions_receipt':positions})); return
    evidence=ROOT/'docs'/'evidence'; evidence.mkdir(exist_ok=True)
    old_report=ROOT/'data'/'recovery-report.json'; report_before=evidence/'gaps-recovery-report-before.json'
    if not report_before.exists(): report_before.write_bytes(old_report.read_bytes())
    backupdir=ROOT/'data'/'backups'; backupdir.mkdir(exist_ok=True)
    backup=backupdir/('gaps-before-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.sqlite')
    print('Creating source-preserving database backup',flush=True)
    with sqlite3.connect(backup) as target: db.backup(target)
    # The backup provides an exact pre-mutation comparison without retaining
    # every existing payload in host memory.
    db.executescript(POSITION_SCHEMA)
    try:
        db.execute('BEGIN IMMEDIATE')
        for sid,path in pending:
            if Path(path).suffix.lower()=='.npz':
                metadata_document(db,sid,npz_metadata(Path(path)),'numpy_npz_metadata_allow_pickle_false_v1','metadata_extracted_values_unindexed',methods)
            elif Path(path).suffix.lower()=='.zip':
                metadata_document(db,sid,zip_inventory(Path(path)),'zip_immediate_member_inventory_v1','inventoried_contents_unindexed',methods)
        for sid,path in codex: repair_jsonl_source(db,sid,positions,'revise_with_history')
        if db.execute('PRAGMA foreign_key_check').fetchall(): raise ValueError('Foreign-key violation introduced')
        db.commit()
    except Exception:
        db.rollback(); raise
    print('Committed bounded extraction additions; checking source and search integrity',flush=True)
    verify_repair(db,backup,methods,positions); db.close()

if __name__=='__main__': main()
