"""Retain source-native alignment tables and exact version/turn witnesses."""
from pathlib import Path
import csv, hashlib, io, json, re, sqlite3
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'state'/'reconstruction'
def sha(text):return hashlib.sha256(text.encode('utf8')).hexdigest()
def cells(line):return [part.strip() for part in re.split(r'(?<!\\)\|',line.strip().strip('|'))]
def canonical(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'))
def main():
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'alignment-tables').mkdir(exist_ok=True)
    c=sqlite3.connect((ROOT/'data'/'sunny.sqlite').as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
    sources=[dict(row) for row in c.execute("SELECT * FROM sources WHERE kind='recovered_current_research' AND path LIKE '%.md'")]
    tables={}; errors=[]
    for source in sources:
        raw=Path(source['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=source['sha256']:raise ValueError('Alignment source bytes changed')
        text=raw.decode('utf-8-sig'); chunks=text.split('\n');lines=[line+'\n' for line in chunks[:-1]]+chunks[-1:]; offsets=[];cursor=0
        for line in lines:offsets.append(cursor);cursor+=len(line)
        turns=[]
        for message in c.execute('SELECT id,role,locator FROM messages WHERE source_id=?',(source['id'],)):
            bounds=re.fullmatch(r'lines:(\d+)-(\d+)',message['locator'] or '')
            if bounds:turns.append((int(bounds[1]),int(bounds[2]),message['id'],message['role']))
        for i in range(len(lines)-2):
            if '|' not in lines[i] or not re.fullmatch(r'\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*',lines[i+1].strip()):continue
            end=i+2
            while end<len(lines) and '|' in lines[end] and lines[end].strip():end+=1
            headers=cells(lines[i]);rows=[cells(line) for line in lines[i+2:end]]
            if not rows:continue
            body={'headers':headers,'rows':rows};digest=sha(canonical(body));quoted=''.join(lines[i:end])
            owners=[turn for turn in turns if turn[0]<=i+1<=turn[1]]
            owner=owners[0] if owners else None
            occurrence={'source_id':source['id'],'source_sha256':source['sha256'],'source_path':source['path'],'line_start':i+1,'line_end':end,'char_start':offsets[i],'char_end':offsets[i]+len(quoted),'position_basis':'UTF8-sig decoded Unicode code points and physical LF lines; raw source bytes retained','exact_quote':quoted,'quote_sha256':sha(quoted),'message_id':owner[2] if owner else None,'role':owner[3] if owner else 'source_document','locator':f'lines:{i+1}-{end}'}
            record=tables.setdefault(digest,{'id':'alignment-table-'+digest[:16],'content_sha256':digest,**body,'occurrences':[],'status':'retained_source_table_not_automatically_current_or_approved'})
            record['occurrences'].append(occurrence)
            if any(len(row)!=len(headers) for row in rows):record['parse_caution']='Some row widths differ; exact quoted source is authoritative, and no missing cell is inferred.'
    csv_records=[]
    for source in c.execute("SELECT * FROM sources WHERE kind='recovered_current_research' AND path LIKE '%.csv'"):
        source=dict(source);raw=Path(source['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=source['sha256']:raise ValueError('CSV source hash mismatch')
        text=raw.decode('utf-8-sig');rows=list(csv.reader(io.StringIO(text,newline='')))
        csv_records.append({'source_id':source['id'],'source_sha256':source['sha256'],'source_path':source['path'],'name':Path(source['path']).name,'headers':rows[0],'rows':rows[1:],'row_count':len(rows)-1,'status':'source_frame_retained; not a newly selected absolute orientation'})
    for digest,record in tables.items():(OUT/'alignment-tables'/(digest+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
    inventory={'schema':'sunny.reconstructed-alignment-register.v1','selection_receipt':'docs/evidence/reconstruction-alignment-superjev.json','source_transcripts':[{'id':s['id'],'path':s['path'],'sha256':s['sha256']} for s in sources],'distinct_markdown_tables':len(tables),'table_occurrences':sum(len(t['occurrences']) for t in tables.values()),'table_rows':sum(len(t['rows']) for t in tables.values()),'tables':[{'id':t['id'],'sha256':key,'headers':t['headers'],'row_count':len(t['rows']),'occurrences':[{k:v for k,v in o.items() if k!='exact_quote'} for o in t['occurrences']],'path':str(OUT/'alignment-tables'/(key+'.json'))} for key,t in tables.items()],'native_workbook_register':str(OUT/'tables.json'),'csv_frames':csv_records,'boundary':'A single replayable register of preserved native frames. Row-index equality is not an admitted cross-system join. Current corrections/supersessions are carried by the decisions and correspondences modules; older source tables remain inspectable. No table is silently given canonical authority.'}
    (OUT/'alignment.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in inventory.items() if k not in ('tables','source_transcripts','csv_frames')},indent=2))
if __name__=='__main__':main()
