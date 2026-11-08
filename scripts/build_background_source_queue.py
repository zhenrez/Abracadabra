"""Read-only historical intake; immutable full-message projections, finite queue.

Lexical eligibility is not semantic processing. Source originals and roles stay
distinct; only duplicate processing is consolidated, never occurrence evidence.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sqlite3
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'state/background';RAW=ROOT/'data/raw/background-projections'
PROFILES={
 'bridge':dict(query='"Completed Harmony" OR Fludd OR Kepler OR monochord OR "TOL adapter"',hypotheses=[dict(id='explicit-bridge-operation',statement='This passage explicitly specifies whether or how Completed Harmony, Kepler/Fludd monochord logic, or a Tree-of-Life adapter is used, withheld, or compared in its stated musical experiment.'),dict(id='native-carrier-relation',statement='This passage explicitly relates distinct Western and Chinese musical constructions at a named comparison or adapter level, while retaining their source-native distinctions.')]),
 'calendar':dict(query='calendar OR epoch OR timekeeping OR "unbroken" OR "calendar reform"',hypotheses=[dict(id='declared-time-frame',statement='This passage specifies a named calendar, epoch, reference event, timekeeping institution, or reform rule within its own proposed historical timing model.'),dict(id='calendar-counterfactual',statement='This passage explicitly defines or tests an unbroken institutional calendar or a counterfactual combination of selected calendar reforms, rather than merely mentioning dates.')]),
 'glyph':dict(query='"Paleo Hebrew" OR Aramaic OR phonetic OR phonetics OR "letter order" OR glyph',hypotheses=[dict(id='explicit-sound-symbol-map',statement='This passage specifies a literal sound-to-symbol correspondence, phonetic value, or ordered alphabet mapping for a named language or writing system.'),dict(id='glyph-sound-distinction',statement='This passage explicitly distinguishes a written glyph or letter-order transformation from the sounds or phonetic realization assigned to it.')])}
KINDS=('supplied_archive_member','nested_library','recovered_current_research')
EXCLUDED_TITLE=re.compile(r'Articulate SUNNY Specification|SUNNY(?: |$)|plugin|Codex |validation|hook',re.I)
sha=lambda x:hashlib.sha256(x).hexdigest()
def file_sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()
def immutable(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_bytes()!=raw:raise ValueError('immutable projection collision: '+str(path))
    else:
        with path.open('xb') as out:out.write(raw)
def encode(x):return json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False).encode('utf-8')

def build(queue_jobs=0,quiet=False):
    BASE.mkdir(parents=True,exist_ok=True);RAW.mkdir(parents=True,exist_ok=True)
    connection=sqlite3.connect('file:'+str(ROOT/'data/sunny.sqlite')+'?mode=ro',uri=True);connection.row_factory=sqlite3.Row
    connection.execute('pragma query_only=ON')
    groups={};profile_counts={};exclusions=Counter();source_cache={}
    for track,profile in PROFILES.items():
        rows=connection.execute("SELECT DISTINCT m.id,m.native_id,m.conversation_id,m.role,m.text,m.content_sha256,m.source_id,m.locator,m.create_time,m.branch_status,c.title,s.path source_path,s.original_path,s.sha256 source_sha256,s.kind source_kind FROM search_index f JOIN messages m ON m.id=f.id JOIN conversations c ON c.id=m.conversation_id JOIN sources s ON s.id=m.source_id WHERE search_index MATCH ? AND m.role IN ('user','assistant')",(profile['query'],)).fetchall()
        profile_counts[track]={'matched_message_occurrences':len(rows),'eligible_occurrences':0}
        for row in rows:
            item=dict(row)
            if item['source_kind'] not in KINDS:
                exclusions['not_historical_native_source_kind']+=1;continue
            if EXCLUDED_TITLE.search(item['title'] or ''):
                exclusions['current_assignment_or_software_title']+=1;continue
            text=item.pop('text');digest=sha(text.encode('utf-8'))
            if digest!=item['content_sha256']:
                exclusions['stored_content_hash_mismatch']+=1;continue
            profile_counts[track]['eligible_occurrences']+=1
            key=(digest,item['role'])
            if key not in groups:groups[key]={'content_sha256':digest,'source_role':item['role'],'text':text,'tracks':set(),'occurrences':{}}
            group=groups[key];group['tracks'].add(track);group['occurrences'][item['id']]=item
    # Expand duplicate occurrence provenance over the entire registered message
    # table, including duplicates outside the selected historical intake.
    digests=sorted({key[0] for key in groups})
    for offset in range(0,len(digests),400):
        batch=digests[offset:offset+400]
        rows=connection.execute("SELECT m.id,m.native_id,m.conversation_id,m.role,m.content_sha256,m.source_id,m.locator,m.create_time,m.branch_status,c.title,s.path source_path,s.original_path,s.sha256 source_sha256,s.kind source_kind FROM messages m JOIN conversations c ON c.id=m.conversation_id JOIN sources s ON s.id=m.source_id WHERE m.content_sha256 IN ("+','.join('?' for _ in batch)+")",batch).fetchall()
        for row in rows:
            item=dict(row);key=(item['content_sha256'],item['role'])
            if key in groups:groups[key]['occurrences'][item['id']]=item
    # All reads are now materialized. Close before validation/projection writes
    # so an integrity exception cannot leave a source connection open.
    connection.close()
    contacts=set()
    coverage=json.loads((ROOT/'state/reconstruction/coverage.json').read_text(encoding='utf-8-sig'))
    for value in coverage.get('reconstruction_module_references',{}).values():contacts.update(value.get('message_ids',[]))
    for result_path in (BASE/'main/runs').glob('*/result.json'):
        result=json.loads(result_path.read_text(encoding='utf-8-sig'))
        for record in result.get('source_records',[]):
            if record['source'].get('message_id'):contacts.add(record['source']['message_id'])
    records=[]
    for (digest,role),group in sorted(groups.items()):
        text=group.pop('text');occurrences=sorted(group.pop('occurrences').values(),key=lambda x:x['id'])
        content=text.encode('utf-8');projection=RAW/digest/'text.txt';immutable(projection,content)
        for occurrence in occurrences:
            p=Path(occurrence['source_path'])
            key=(str(p),occurrence['source_sha256'])
            if key not in source_cache:
                actual=file_sha(p) if p.is_file() else None
                source_cache[key]={'path_exists':p.is_file(),'actual_sha256':actual,'matches_recorded_source_hash':actual==occurrence['source_sha256']}
            occurrence['original_source_integrity']=source_cache[key]
        occurrence_manifest={'schema':'sunny.background-source-occurrences.v1','content_sha256':digest,'projection_path':projection.relative_to(ROOT).as_posix(),'projection_semantics':'Exact UTF-8 encoding of stored full message text; not native export bytes or proof of historical truth.','source_role':role,'occurrences':occurrences}
        manifest_bytes=encode(occurrence_manifest);manifest_path=projection.parent/('occurrences-'+sha(manifest_bytes)+'.json');immutable(manifest_path,manifest_bytes)
        statuses=[]
        if len(text)>16000:statuses.append('pending_oversized_full_message_no_truncation')
        if not any(o['original_source_integrity']['matches_recorded_source_hash'] for o in occurrences):statuses.append('pending_original_source_integrity')
        if not text.strip():statuses.append('pending_empty_text')
        if any(o['id'] in contacts for o in occurrences):statuses.append('prior_exact_module_or_background_contact_semantic_status_unknown')
        record={**group,'tracks':sorted(group['tracks']),'characters':len(text),'bytes':len(content),'projection_path':projection.relative_to(ROOT).as_posix(),'occurrence_manifest':manifest_path.relative_to(ROOT).as_posix(),'occurrence_count':len(occurrences),'status':';'.join(statuses) if statuses else 'eligible_unprocessed'}
        records.append(record)
    eligible=[r for r in records if r['status']=='eligible_unprocessed']
    selected=[];seen=set()
    for queued_path in (BASE/'main/queue').glob('*.json'):
        queued=json.loads(queued_path.read_text(encoding='utf-8-sig'))
        for source in queued.get('sources',[]):
            if source.get('path','').startswith('data/raw/background-projections/'):
                seen.add((source['sha256'],source['source_role']))
    # Round-robin allocation is a transparent operational coverage bound,
    # not evidence weight, confidence score, or selection of a true model.
    for index in range(len(eligible)):
        for track in PROFILES:
            candidates=[r for r in eligible if track in r['tracks'] and (r['content_sha256'],r['source_role']) not in seen]
            if not candidates:continue
            record=candidates[0];seen.add((record['content_sha256'],record['source_role']));selected.append((track,record))
            if len(selected)>=queue_jobs:break
        if len(selected)>=queue_jobs:break
    queued=[]
    if queue_jobs:
        queue=BASE/'main/queue';queue.mkdir(parents=True,exist_ok=True)
        for track,record in selected[:queue_jobs]:
            text=(ROOT/record['projection_path']).read_text(encoding='utf-8')
            manifest=json.loads((ROOT/record['occurrence_manifest']).read_text(encoding='utf-8'))
            primary=next(o for o in manifest['occurrences'] if o['original_source_integrity']['matches_recorded_source_hash'])
            job_id='historical-'+track+'-'+record['source_role']+'-'+record['content_sha256'][:16]
            source=dict(path=record['projection_path'],sha256=record['content_sha256'],start_line=1,end_line=len(text.splitlines()),source_role=record['source_role'],source_id=primary['source_id'],message_id=primary['id'],timestamp=primary['create_time'],timestamp_precision='stored message metadata; literal display date retained in full text',origin=primary,all_duplicate_occurrences_manifest=record['occurrence_manifest'])
            job=dict(schema='sunny.background-job.v1',id=job_id,kind='source_forensics',track=track,sources=[source],hypotheses=PROFILES[track]['hypotheses'],compare_sources=False,bounds=dict(max_source_characters=16000,max_sources=1),review_boundary='Historical source candidate classification only; assistant content is not user approval; projection bytes are not native source bytes or historical truth.')
            path=queue/(job_id+'.json');immutable(path,encode(job));queued.append({'id':job_id,'track':track,'path':path.relative_to(ROOT).as_posix(),'role':record['source_role'],'characters':record['characters']})
    result=dict(schema='sunny.background-source-backlog.v1',built_utc=datetime.now(timezone.utc).isoformat(),source_database='data/sunny.sqlite',database_access='read-only + query_only',profiles=profile_counts,eligible_source_kinds=KINDS,excluded_record_reasons=dict(exclusions),unique_text_role_groups=len(records),message_occurrences=sum(r['occurrence_count'] for r in records),unique_text_hashes=len({r['content_sha256'] for r in records}),eligible_bounded_groups=len(eligible),pending_status_counts=dict(Counter(r['status'] for r in records if r['status']!='eligible_unprocessed')),queue_limit=queue_jobs,queued_jobs=queued,records=records,limits=['Lexical eligibility does not prove semantic relevance, processing or completeness.','Current local Codex/tool/hook/task records excluded from this finite native-source intake; exclusion is not loss or absence from full SUNNY scope.','Oversized full messages are preserved and pending; no silent truncation.','Identical text with different roles remains separately processable; all duplicate occurrence metadata retained.','No source age is treated as truth; deterministic processing order is hash order within balanced tracks.'])
    raw=encode(result);snapshot=BASE/'backlog-builds'/('backlog-'+sha(raw)+'.json');immutable(snapshot,raw)
    (BASE/'source-backlog.json').write_bytes(raw)
    if not quiet:print(json.dumps({k:v for k,v in result.items() if k not in ('records','queued_jobs')},ensure_ascii=False))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--queue-jobs',type=int,default=0);args=parser.parse_args()
    if not 0<=args.queue_jobs<=128:parser.error('initial finite queue cap is 128 jobs')
    build(args.queue_jobs)
