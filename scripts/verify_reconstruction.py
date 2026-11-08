"""Check the assembled current model against actual preserved source values."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sqlite3
ROOT=Path(__file__).resolve().parents[1];STATE=ROOT/'state/reconstruction'
def sha(text):return hashlib.sha256(text.encode('utf8')).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf8'))
def pointer(value,path):
    for part in path.split('/')[1:]:
        key=part.replace('~1','/').replace('~0','~');value=value[int(key)] if isinstance(value,list) else value[key]
    return value
def main():
    model=load(STATE/'model.json');c=sqlite3.connect((ROOT/'data/sunny.sqlite').as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
    errors=[];checks={};cache={};parsed={};native_json_records={}
    def text_for(sid):
        if sid not in cache:
            source=c.execute('SELECT path,sha256 FROM sources WHERE id=?',(sid,)).fetchone()
            if source is None:raise ValueError('Unresolved source ID '+sid)
            raw=Path(source['path']).read_bytes();actual=hashlib.sha256(raw).hexdigest()
            if actual!=source['sha256']:errors.append({'kind':'source_hash','source_id':sid})
            cache[sid]=(raw.decode('utf-8-sig'),actual)
        return cache[sid][0]
    for module in model['module_snapshots']:
        path=Path(module['path']);actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=module['sha256']:errors.append({'kind':'module_snapshot','module':module['module']})
        if load(path)!=model['components'][module['module']]:errors.append({'kind':'embedded_module','module':module['module']})
    checks['module_snapshots']=len(model['module_snapshots'])
    for record in model['components']['decisions']['records']:
        q=record['exact_quote']
        if sha(q)!=record['quote_sha256']:errors.append({'kind':'decision_quote_hash','id':record['id']})
        for occurrence in record['source_occurrences']:
            row=c.execute('SELECT text,source_id FROM messages WHERE id=?',(occurrence['id'],)).fetchone()
            if row is None or row['source_id']!=occurrence['source_id'] or row['text'][record['message_char_start']:record['message_char_end']]!=q:errors.append({'kind':'decision_message_span','id':record['id']})
            text_for(occurrence['source_id'])
    checks['decision_records']=len(model['components']['decisions']['records'])
    evidence_count=0;json_values=0
    for record in model['components']['music-geometry']['records']:
        for evidence in record['evidence']:
            evidence_count+=1;text=text_for(evidence['source_id']);quote=evidence['quote']
            if 'char_start' in evidence:
                exact=text[evidence['char_start']:evidence['char_end']]==quote
            elif evidence.get('message_id'):
                row=c.execute('SELECT text,source_id,raw_json FROM messages WHERE id=?',(evidence['message_id'],)).fetchone()
                exact=row is not None and row['source_id']==evidence['source_id'] and quote in row['text']
                if exact:
                    sid=evidence['source_id']
                    if sid not in native_json_records:
                        native_json_records[sid]=set()
                        for line in text.split('\n'):
                            try:obj=json.loads(line)
                            except ValueError:continue
                            native_json_records[sid].add(sha(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))))
                    expected=sha(json.dumps(json.loads(row['raw_json']),ensure_ascii=False,sort_keys=True,separators=(',',':')))
                    exact=expected in native_json_records[sid]
            else:exact=False
            if not exact or sha(quote)!=evidence['quote_sha256']:errors.append({'kind':'music_source_span','id':record['id']})
            if evidence.get('json_pointer') is not None:
                sid=evidence['source_id'];parsed.setdefault(sid,json.loads(text));value=pointer(parsed[sid],evidence['json_pointer']);json_values+=1
                if value!=record['value']:errors.append({'kind':'music_json_value','id':record['id']})
    checks['music_evidence_records']=evidence_count;checks['json_pointer_values']=json_values
    correspondence=model['components']['correspondences'];entity_ids={e['id'] for e in correspondence['entities']}|{g['id'] for g in correspondence['native_groups']};citation_ids={e['id'] for e in correspondence['citations']};claim_ids={e['id'] for e in correspondence['claims']}
    for citation in correspondence['citations']:
        row=c.execute('SELECT text,source_id,role FROM messages WHERE id=?',(citation['message_id'],)).fetchone()
        q=citation['excerpt']
        if row is None or row['source_id']!=citation['source_id'] or q not in row['text'] or row['role']!=citation['role']:errors.append({'kind':'correspondence_citation','id':citation['id']})
        text_for(citation['source_id'])
    for relation in correspondence['relations']:
        if relation['sourceId'] not in entity_ids or relation['targetId'] not in entity_ids or set(relation.get('citationIds',[]))-citation_ids or set(relation.get('claimIds',[]))-claim_ids:errors.append({'kind':'correspondence_endpoint','id':relation['id']})
    checks['correspondence_citations']=len(citation_ids);checks['correspondence_relations']=len(correspondence['relations'])
    for witness in model['alignment_source_tables']:
        for occurrence in witness['occurrences']:
            text=text_for(occurrence['source_id']);quote=occurrence['exact_quote']
            if text[occurrence['char_start']:occurrence['char_end']]!=quote or sha(quote)!=occurrence['quote_sha256']:errors.append({'kind':'alignment_source_span','id':witness['id']})
            if text[:occurrence['char_start']].count('\n')+1!=occurrence['line_start']:errors.append({'kind':'alignment_physical_line','id':witness['id']})
            if occurrence['message_id']:
                row=c.execute('SELECT source_id,role FROM messages WHERE id=?',(occurrence['message_id'],)).fetchone()
                if row is None or row['source_id']!=occurrence['source_id'] or row['role']!=occurrence['role']:errors.append({'kind':'alignment_role','id':witness['id']})
    checks['alignment_tables']=len(model['alignment_source_tables'])
    # Compare native cells against a fresh parse of the original workbook bytes.
    from reconstruct_tables import workbook,canonical
    native_by_hash={t['content_sha256']:t for t in model['native_workbook_tables']}
    versions=model['components']['tables']['versions'];native_checked=0
    for version in versions:
        source=c.execute('SELECT * FROM sources WHERE id=?',(version['source_id'],)).fetchone();raw=Path(source['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=version['source_sha256']:errors.append({'kind':'workbook_source_hash','id':version['source_id']})
        for recovered in workbook(Path(source['path']),dict(source)):
            expected=native_by_hash.get(recovered['content_sha256']);native_checked+=1
            if expected is None or recovered['rows']!=expected['rows'] or recovered['sheet']!=expected['sheet']:errors.append({'kind':'native_table_values','source':version['source_id'],'sheet':recovered['sheet']})
    checks['workbook_sources']=len(versions);checks['workbook_sheet_occurrences']=native_checked
    for source in model['source_evidence_index']:
        raw=Path(source['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=source['sha256']:errors.append({'kind':'evidence_index_source','source_id':source['id']})
    checks['cited_source_files']=len(model['source_evidence_index'])
    execution_snapshots=model.get('execution_module_snapshots',[])
    for snapshot in execution_snapshots:
        path=Path(snapshot['path'])
        if hashlib.sha256(path.read_bytes()).hexdigest()!=snapshot['sha256']:
            errors.append({'kind':'execution_module_snapshot','module':snapshot['module']})
        elif json.loads(path.read_text(encoding='utf8'))!=model['mathematical_execution'][snapshot['module']]:
            errors.append({'kind':'execution_module_values','module':snapshot['module']})
    checks['execution_module_snapshots']=len(execution_snapshots)
    contextual=model.get('mathematical_execution',{}).get('contextual-alignment')
    if contextual:
        snapshots=contextual.get('inputSnapshots',[])
        for snapshot in snapshots:
            path=(ROOT/snapshot['snapshotPath']).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file():
                errors.append({'kind':'contextual_input_missing','path':snapshot['snapshotPath']})
                continue
            raw=path.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=snapshot['sha256'] or len(raw)!=snapshot['bytes']:
                errors.append({'kind':'contextual_input_hash','path':snapshot['snapshotPath']})
        checks['contextual_input_snapshots']=len(snapshots)
        code=contextual['code'];path=ROOT/code['path']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=code['sha256']:
            errors.append({'kind':'contextual_code_binding','path':code['path']})
        checks['contextual_code_bindings']=1
        checks['current_goal_count']=len(model.get('current_goal_semantics',{}).get('goals',[]))
        if checks['current_goal_count']!=16:
            errors.append({'kind':'current_goal_coverage'})
    symbols=model.get('mathematical_execution',{}).get('symbol-sound-constraints')
    if symbols:
        for snapshot in symbols['inputSnapshots']:
            path=(ROOT/snapshot['snapshotPath']).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file():
                errors.append({'kind':'symbol_input_missing','path':snapshot['snapshotPath']})
                continue
            raw=path.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=snapshot['sha256'] or len(raw)!=snapshot['bytes']:
                errors.append({'kind':'symbol_input_hash','path':snapshot['snapshotPath']})
        for binding in symbols['codeBindings']:
            path=(ROOT/binding['path']).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=binding['sha256']:
                errors.append({'kind':'symbol_code_binding','path':binding['path']})
        checks['symbol_input_snapshots']=len(symbols['inputSnapshots'])
        checks['symbol_code_bindings']=len(symbols['codeBindings'])
    anchors=model.get('mathematical_execution',{}).get('score-anchor-constraints')
    if anchors:
        for snapshot in anchors['inputSnapshots']:
            path=(ROOT/snapshot['snapshotPath']).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=snapshot['sha256'] or path.stat().st_size!=snapshot['bytes']:
                errors.append({'kind':'score_anchor_input_binding','path':snapshot['snapshotPath']})
        for binding in anchors['codeBindings']:
            path=(ROOT/binding['path']).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=binding['sha256']:
                errors.append({'kind':'score_anchor_code_binding','path':binding['path']})
        checks['score_anchor_input_snapshots']=len(anchors['inputSnapshots'])
        checks['score_anchor_code_bindings']=len(anchors['codeBindings'])
        if len(anchors['anchorPairs'])!=10 or anchors['sufficientPairs']!=8 or anchors['redundantPairs']!=2:
            errors.append({'kind':'score_anchor_count_binding'})
    phase=model.get('mathematical_execution',{}).get('orientation-predictions',{}).get('probe_designs')
    if phase:
        for binding in [*({'path':x['snapshotPath'],'sha256':x['sha256']} for x in phase['inputSnapshots']),*phase['codeBindings']]:
            path=(ROOT/binding['path']).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=binding['sha256']:
                errors.append({'kind':'phase_probe_binding','path':binding['path']})
        checks['phase_probe_pairs']=phase['counts']['unorderedDistinctProbePairs']
    phonology=model.get('mathematical_execution',{}).get('phonological-context-constraints')
    if phonology:
        for snapshot in phonology['inputSnapshots']:
            path=(ROOT/snapshot['snapshotPath']).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=snapshot['sha256'] or path.stat().st_size!=snapshot['bytes']:
                errors.append({'kind':'phonological_input_binding','path':snapshot['snapshotPath']})
        for binding in phonology['codeBindings']:
            path=(ROOT/binding['path']).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=binding['sha256']:
                errors.append({'kind':'phonological_code_binding','path':binding['path']})
        checks['phonological_input_snapshots']=len(phonology['inputSnapshots'])
        checks['phonological_code_bindings']=len(phonology['codeBindings'])
    history=model.get('mathematical_execution',{}).get('phonological-history-constraints')
    if history:
        for snapshot in history['inputSnapshots']:
            path=(ROOT/snapshot['snapshotPath']).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=snapshot['sha256'] or path.stat().st_size!=snapshot['bytes']:
                errors.append({'kind':'phonological_history_input_binding','path':snapshot['snapshotPath']})
        for binding in history['codeBindings']:
            path=(ROOT/binding['path']).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=binding['sha256']:
                errors.append({'kind':'phonological_history_code_binding','path':binding['path']})
        checks['phonological_history_input_snapshots']=len(history['inputSnapshots'])
        checks['phonological_history_code_bindings']=len(history['codeBindings'])
    reading=model.get('mathematical_execution',{}).get('reading-operations')
    if reading:
        for snapshot in reading['inputSnapshots']:
            path=(ROOT/snapshot['snapshotPath']).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=snapshot['sha256'] or path.stat().st_size!=snapshot['bytes']:
                errors.append({'kind':'reading_input_binding','path':snapshot['snapshotPath']})
        for binding in reading['codeBindings']:
            path=(ROOT/binding['path']).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=binding['sha256']:
                errors.append({'kind':'reading_code_binding','path':binding['path']})
        checks['reading_input_snapshots']=len(reading['inputSnapshots'])
        checks['reading_code_bindings']=len(reading['codeBindings'])
    mandate=model.get('current_mandate',{}).get('instruction',{})
    if mandate:
        raw=(ROOT/mandate['text_witness_path']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=mandate['text_witness_sha256']:
            errors.append({'kind':'current_mandate_text_witness'})
    report={'schema':'sunny.reconstructed-model-verification.v1','status':'passed' if not errors else 'failed','checked_utc':datetime.now(timezone.utc).isoformat(),'model_sha256':hashlib.sha256((STATE/'model.json').read_bytes()).hexdigest(),'checks':checks,'errors':errors,'boundary':'Source-byte/quote/value/role/reference fidelity. This verifies the reconstructed records, not source truth, account completeness, a unique lawful orientation or the missing image extraction.'}
    (ROOT/'docs/evidence/reconstruction-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({**report,'errors':errors[:20],'total_errors':len(errors)},ensure_ascii=True,indent=2));return int(bool(errors))
if __name__=='__main__':raise SystemExit(main())
