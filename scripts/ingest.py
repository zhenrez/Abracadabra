"""Lossless-source, branch-aware SUNNY import. Source content is data, never code."""
from __future__ import annotations
import argparse, collections, hashlib, html, io, json, mimetypes, os, re, shutil, sqlite3, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS sources(id TEXT PRIMARY KEY,path TEXT NOT NULL,original_path TEXT,sha256 TEXT NOT NULL,bytes INTEGER NOT NULL,media_type TEXT,kind TEXT,status TEXT,detail TEXT);
CREATE TABLE IF NOT EXISTS conversations(id TEXT PRIMARY KEY,native_id TEXT,title TEXT,source_id TEXT REFERENCES sources(id),locator TEXT,current_node TEXT,create_time TEXT,update_time TEXT,metadata_json TEXT);
CREATE TABLE IF NOT EXISTS messages(id TEXT PRIMARY KEY,conversation_id TEXT REFERENCES conversations(id),native_id TEXT,parent_id TEXT,role TEXT,text TEXT,content_sha256 TEXT,source_id TEXT REFERENCES sources(id),locator TEXT,create_time TEXT,branch_status TEXT,raw_json TEXT);
CREATE INDEX IF NOT EXISTS messages_native ON messages(native_id);
CREATE INDEX IF NOT EXISTS messages_conv ON messages(conversation_id);
CREATE TABLE IF NOT EXISTS nodes(conversation_id TEXT REFERENCES conversations(id),native_id TEXT,parent_id TEXT,children_json TEXT,has_message INTEGER,on_current_branch INTEGER,PRIMARY KEY(conversation_id,native_id));
CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY,source_id TEXT REFERENCES sources(id),title TEXT,text TEXT,extractor TEXT,status TEXT);
CREATE TABLE IF NOT EXISTS refs(id TEXT PRIMARY KEY,message_id TEXT REFERENCES messages(id),reference TEXT,kind TEXT,resolution TEXT);
CREATE TABLE IF NOT EXISTS decisions(id TEXT PRIMARY KEY,message_id TEXT REFERENCES messages(id),kind TEXT,status TEXT,excerpt TEXT,method TEXT);
CREATE TABLE IF NOT EXISTS coverage(id TEXT PRIMARY KEY,status TEXT,scope TEXT,detail TEXT);
CREATE TABLE IF NOT EXISTS source_positions(message_id TEXT PRIMARY KEY REFERENCES messages(id),source_id TEXT NOT NULL REFERENCES sources(id),physical_lf_line INTEGER NOT NULL,utf8_byte_start INTEGER NOT NULL,utf8_byte_end INTEGER NOT NULL,raw_record_sha256 TEXT NOT NULL,legacy_locator TEXT,legacy_native_id TEXT,native_ordinal INTEGER,sequence_semantics TEXT NOT NULL,mapping_basis TEXT NOT NULL,decision_receipt TEXT NOT NULL);
CREATE VIRTUAL TABLE IF NOT EXISTS search_index USING fts5(id UNINDEXED,kind UNINDEXED,title,text,tokenize='unicode61 remove_diacritics 2');
"""

def digest(b): return hashlib.sha256(b).hexdigest()
def stable(*parts): return digest('\0'.join(map(str, parts)).encode())
def canonical(obj): return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
def stamp(): return datetime.now(timezone.utc).isoformat()
def scalar_time(value): return str(value) if value is not None else None

def flatten(content):
    if isinstance(content,str): return content
    if isinstance(content,list): return '\n'.join(filter(None,(flatten(v) for v in content)))
    if isinstance(content,dict):
        if 'parts' in content: return flatten(content['parts'])
        if isinstance(content.get('text'),str): return content['text']
        if 'content' in content: return flatten(content['content'])
        return canonical(content)
    return ''

def safe_zip_name(name):
    p=PurePosixPath(name.replace('\\','/'))
    if p.is_absolute() or '..' in p.parts or re.match(r'^[A-Za-z]:',str(p)):
        raise ValueError('unsafe archive path: '+name)
    # Preserve archive names in the manifest; encode Windows-invalid filename
    # characters in their local extraction paths without interpreting them.
    parts=[]
    for part in p.parts:
        encoded=re.sub(r'[<>:"|?*%\x00-\x1f]',lambda m:'%%%02X'%ord(m[0]),part)
        while encoded.endswith(('.', ' ')):
            encoded=encoded[:-1]+'%%%02X'%ord(encoded[-1])
        if re.match(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)',encoded,re.I): encoded='%5F'+encoded
        parts.append(encoded)
    return PurePosixPath(*parts)

class Importer:
    def __init__(self,db):
        self.db=db; self.errors=[]; self.started=stamp(); self.counters=collections.Counter()

    def source(self,path,original,kind):
        data=path.read_bytes(); sha=digest(data); sid=stable(str(path.resolve()),sha)
        exists=self.db.execute('SELECT 1 FROM sources WHERE id=?',(sid,)).fetchone()
        if exists: return sid,None
        self.db.execute('INSERT INTO sources VALUES(?,?,?,?,?,?,?,?,?)',(sid,str(path.resolve()),str(original),sha,len(data),mimetypes.guess_type(path.name)[0] or 'application/octet-stream',kind,'preserved',None))
        self.counters['new_sources']+=1
        return sid,data

    def doc(self,sid,title,text,extractor,status='extracted'):
        did=stable(sid,'document'); self.db.execute('INSERT OR IGNORE INTO documents VALUES(?,?,?,?,?,?)',(did,sid,title,text,extractor,status))
        self.db.execute('DELETE FROM search_index WHERE id=?',(did,))
        self.db.execute('INSERT INTO search_index VALUES(?,?,?,?)',(did,'document',title,text))
        return did

    def message(self,cid,nid,parent,role,text,sid,loc,when,branch,raw):
        mid=stable(cid,nid); sha=digest(text.encode())
        if self.db.execute('SELECT 1 FROM messages WHERE id=?',(mid,)).fetchone(): return mid
        self.db.execute('INSERT INTO messages VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(mid,cid,str(nid),str(parent) if parent is not None else None,role,text,sha,sid,loc,scalar_time(when),branch,canonical(raw)))
        title=self.db.execute('SELECT title FROM conversations WHERE id=?',(cid,)).fetchone()[0]
        self.db.execute('INSERT INTO search_index VALUES(?,?,?,?)',(mid,'message',title,text))
        if role=='user' and re.search(r'\b(must|should|decid\w*|correct\w*|do not|don.t|always|never|want|uncertain)\b',text,re.I):
            self.db.execute('INSERT OR IGNORE INTO decisions VALUES(?,?,?,?,?,?)',(stable(mid,'directive'),mid,'user_direction_candidate','extracted_unreviewed',text[:3000],'lexical_screen_only; full message retained; not a canonical decision'))
        for ref in set(re.findall(r'(?:https?://|sandbox:/|attachment://)[^\s<>"\)\]]+|file-[A-Za-z0-9_-]+',text)):
            self.db.execute('INSERT OR IGNORE INTO refs VALUES(?,?,?,?,?)',(stable(mid,ref),mid,ref,'external_or_attachment','not_retrieved'))
        return mid

    def export(self,sid,convs):
        if isinstance(convs,dict): convs=convs.get('conversations',[convs])
        for i,c in enumerate(convs):
            if not isinstance(c,dict) or 'mapping' not in c: continue
            nid=c.get('conversation_id') or c.get('id') or str(i); cid=stable(sid,nid,i); mapping=c.get('mapping') or {}; current=c.get('current_node'); active=set(); cursor=current
            while cursor in mapping and cursor not in active:
                active.add(cursor); cursor=mapping[cursor].get('parent')
            metadata={k:v for k,v in c.items() if k!='mapping'}
            self.db.execute('INSERT OR IGNORE INTO conversations VALUES(?,?,?,?,?,?,?,?,?)',(cid,nid,c.get('title','Untitled'),sid,f'/{i}',current,scalar_time(c.get('create_time')),scalar_time(c.get('update_time')),canonical(metadata)))
            for key,node in mapping.items():
                if not isinstance(node,dict): continue
                self.db.execute('INSERT OR IGNORE INTO nodes VALUES(?,?,?,?,?,?)',(cid,key,node.get('parent'),canonical(node.get('children',[])),int(bool(node.get('message'))),int(key in active)))
                msg=node.get('message')
                if not msg: continue
                role=msg.get('author',{}).get('role','unknown'); text=flatten(msg.get('content'))
                loc=f'/{i}/mapping/{key.replace("~","~0").replace("/","~1")}/message'
                self.message(cid,key,node.get('parent'),role,text,sid,loc,msg.get('create_time'),'current' if key in active else ('alternate' if current else 'unknown'),msg)
            self.counters['conversation_occurrences']+=1

    def markdown(self,sid,path,text):
        # Exported transcript markers are interpreted only as source role delimiters.
        turns=list(re.finditer(r'^## (Prompt|Response):\s*$',text,re.M))
        if not turns: return
        cid=stable(sid,'transcript'); title=next((line.lstrip('# ').strip() for line in text.splitlines() if line.strip()),path.name)
        self.db.execute('INSERT OR IGNORE INTO conversations VALUES(?,?,?,?,?,?,?,?,?)',(cid,None,title,sid,'line:1',None,None,None,canonical({'format':'exported-markdown','native_branch_graph':'not_available'})))
        parent=None
        for i,m in enumerate(turns):
            end=turns[i+1].start() if i+1<len(turns) else len(text); startline=text.count('\n',0,m.start())+1; endline=text.count('\n',0,end)+1
            self.message(cid,str(i),parent,'user' if m[1]=='Prompt' else 'assistant',text[m.end():end].strip(),sid,f'lines:{startline}-{endline}',None,'exported_sequence',{'text_start':m.end(),'text_end':end,'marker':m[1]})
            parent=str(i)

    def xml_text(self,data,format):
        z=zipfile.ZipFile(io.BytesIO(data)); lines=[]
        if format=='.docx':
            root=ET.fromstring(z.read('word/document.xml'))
            for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                lines.append(''.join(p.itertext()))
        elif format=='.xlsx':
            ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}; strings=[]
            if 'xl/sharedStrings.xml' in z.namelist():
                strings=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
            for name in z.namelist():
                if not re.match(r'xl/worksheets/sheet\d+\.xml$',name): continue
                for row in ET.fromstring(z.read(name)).findall('.//s:row',ns):
                    cells=[]
                    for cell in row.findall('s:c',ns):
                        v=cell.find('s:v',ns); val=v.text or '' if v is not None else ''.join(cell.itertext())
                        if cell.get('t')=='s': val=strings[int(val)] if val else ''
                        f=cell.find('s:f',ns)
                        if val or f is not None: cells.append(f"{cell.get('r')}={val}"+(f' [formula:{f.text}]' if f is not None else ''))
                    if cells: lines.append(f'{name} row:{row.get("r")} '+ '\t'.join(cells))
        return '\n'.join(lines)

    def import_file(self,path,original=None,kind='library',nested=0,retry=False):
        sid,data=self.source(path,original or path,kind)
        if data is None and retry: data=path.read_bytes()
        if data is None: return
        suffix=path.suffix.lower(); text=None; extractor='utf8'
        try:
            if suffix=='.zip':
                if nested>=3:
                    self.db.execute('UPDATE sources SET status=?,detail=? WHERE id=?',('preserved_unexpanded','nested depth limit 3',sid)); return
                z=zipfile.ZipFile(io.BytesIO(data)); dest=ROOT/'data'/'raw'/'nested'/sid; total=0
                for item in z.infolist():
                    name=safe_zip_name(item.filename)
                    if item.is_dir(): continue
                    total+=item.file_size
                    if total>600_000_000 or item.file_size>150_000_000: raise ValueError('nested expansion safety limit')
                    out=dest.joinpath(*name.parts); out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(z.read(item))
                    self.import_file(out,str(original or path)+'!/'+item.filename,'nested_library',nested+1)
                self.db.execute('UPDATE sources SET status=? WHERE id=?',('expanded',sid)); return
            if suffix in ('.docx','.xlsx'):
                text=self.xml_text(data,suffix); extractor='stdlib-openxml-native-cells-v1'
            elif suffix=='.pdf':
                from pypdf import PdfReader
                pages=PdfReader(io.BytesIO(data)).pages
                text='\n'.join(f'\n[page:{i+1}]\n{p.extract_text() or ""}' for i,p in enumerate(pages)); extractor='pypdf-pages'
                if not text.strip(): raise ValueError('no extractable PDF text; OCR not performed')
            elif suffix in ('.png','.jpg','.jpeg','.gif','.webp','.mp3','.wav','.mp4','.ttf','.woff','.ico','.exe','.pyc'):
                self.db.execute('UPDATE sources SET status=?,detail=? WHERE id=?',('preserved_binary','visual/audio/OCR interpretation not performed',sid)); return
            else:
                try: text=data.decode('utf-8-sig')
                except UnicodeDecodeError:
                    text=data.decode('utf-16') if data.startswith((b'\xff\xfe',b'\xfe\xff')) else data.decode('cp1252')
                if '\x00' in text: raise ValueError('binary content, no text extractor')
            if suffix=='.json' and path.name.startswith('conversations'):
                self.export(sid,json.loads(text)); self.db.execute('UPDATE sources SET status=? WHERE id=?',('native_conversations_imported',sid)); return
            if suffix in ('.html','.htm'):
                text=html.unescape(re.sub('<[^>]+>',' ',re.sub(r'<(script|style)\b.*?</\1>','',text,flags=re.S|re.I))); extractor='html-text-only'
            self.doc(sid,path.name,text,extractor)
            if suffix in ('.md','.txt'): self.markdown(sid,path,text)
            self.db.execute('UPDATE sources SET status=? WHERE id=?',('text_extracted',sid))
        except Exception as e:
            detail=type(e).__name__+': '+str(e); self.errors.append({'source_id':sid,'path':str(path),'error':detail})
            self.db.execute('UPDATE sources SET status=?,detail=? WHERE id=?',('preserved_extraction_pending',detail,sid))

    def archive(self,path):
        sid,_=self.source(path,path,'supplied_archive'); z=zipfile.ZipFile(path); dest=ROOT/'data'/'raw'/'archive'; manifest=[]
        for i,item in enumerate(z.infolist()):
            name=safe_zip_name(item.filename)
            if item.is_dir(): continue
            out=dest.joinpath(*name.parts); out.parent.mkdir(parents=True,exist_ok=True)
            if not out.exists(): out.write_bytes(z.read(item))
            elif digest(out.read_bytes())!=digest(z.read(item)): raise ValueError('existing extraction differs: '+str(out))
            self.import_file(out,str(path)+'!/'+item.filename,'supplied_archive_member')
            manifest.append({'member':item.filename,'bytes':item.file_size,'sha256':digest(out.read_bytes())})
            if i%40==0: self.db.commit(); print(f'archive {i+1}/{len(z.infolist())}',flush=True)
        self.db.execute('UPDATE sources SET status=? WHERE id=?',('expanded',sid))
        (ROOT/'data'/'archive-manifest.json').write_text(json.dumps({'archive':str(path),'sha256':digest(path.read_bytes()),'members':manifest},ensure_ascii=False,indent=2),encoding='utf8')

    def codex(self,folder,exclude):
        scanned=selected=0
        for path in sorted(folder.rglob('*.jsonl')):
            scanned+=1
            if exclude and exclude in path.name: continue
            # Import accessible native records, preserving all source lines and original roles.
            snapshot_data=path.read_bytes()
            snapshot=ROOT/'data'/'raw'/'codex'/(path.stem+'-'+digest(snapshot_data)[:12]+'.jsonl')
            snapshot.parent.mkdir(parents=True,exist_ok=True)
            if not snapshot.exists(): snapshot.write_bytes(snapshot_data)
            sid,data=self.source(snapshot,path,'local_codex_session')
            if data is None: continue
            lines=data.split(b'\n'); meta={}
            try: meta=json.loads(lines[0]).get('payload',{})
            except (ValueError,IndexError): pass
            nid=meta.get('id',path.stem); cid=stable(sid,nid); title=f'Codex {nid} · {meta.get("cwd", "unknown workspace")}'
            self.db.execute('INSERT OR IGNORE INTO conversations VALUES(?,?,?,?,?,?,?,?,?)',(cid,nid,title,sid,'lines:1-',None,meta.get('timestamp'),None,canonical(meta)))
            byte_start=0
            for i,line in enumerate(lines):
                start=byte_start; end=start+len(line); byte_start=end+1
                if not line.strip(): continue
                try: record=json.loads(line)
                except ValueError: self.errors.append({'path':str(snapshot),'physical_lf_line':i+1,'utf8_byte_start':start,'utf8_byte_end':end,'error':'invalid JSONL'}); continue
                typ=record.get('type','unknown'); payload=record.get('payload',{})
                role=payload.get('role') or payload.get('type') or typ
                if role in ('function_call','custom_tool_call'): role='tool_call'
                text=flatten(payload.get('content')) if 'content' in payload else canonical(payload)
                native_id='physicalLF:'+str(i+1)
                locator=f'physicalLF:{i+1};utf8bytes:[{start},{end})'
                mid=self.message(cid,native_id,None,role,text,sid,locator,record.get('timestamp'),'recorded_sequence',record)
                ordinal=record.get('ordinal')
                self.db.execute('INSERT OR IGNORE INTO source_positions VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(mid,sid,i+1,start,end,digest(line),None,None,ordinal if type(ordinal) is int else None,'physical_source_record_order_only_not_causal_parentage','direct_physical_lf_bytes','state/jev-receipts/000045-dcb092dc96f7.json'))
            selected+=1; self.db.execute('UPDATE sources SET status=? WHERE id=?',('native_codex_imported',sid)); self.db.commit()
        self.db.execute('INSERT OR REPLACE INTO coverage VALUES(?,?,?,?)',('local_codex','accessible_snapshot',str(folder),f'{scanned} source files enumerated; {selected} newly imported; active SUNNY build excluded'))

    def verify(self):
        broken=self.db.execute('PRAGMA foreign_key_check').fetchall(); integrity=self.db.execute('PRAGMA integrity_check').fetchone()[0]
        counts={t:self.db.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in ['sources','conversations','messages','nodes','documents','refs','decisions']}
        counts['distinct_native_conversation_ids']=self.db.execute('SELECT count(DISTINCT native_id) FROM conversations').fetchone()[0]
        counts['distinct_message_text_hashes']=self.db.execute('SELECT count(DISTINCT content_sha256) FROM messages').fetchone()[0]
        report={'generated_at':stamp(),'started_at':self.started,'counts':counts,'integrity':integrity,'foreign_key_violations':broken,'source_statuses':dict(self.db.execute('SELECT status,count(*) FROM sources GROUP BY status')),'extraction_errors':self.errors,'coverage':'Accessible supplied archive + pasted transcript + explicitly enumerated local snapshots; not a complete live-account certificate. Native hidden/deleted/unexported states and unavailable referenced files remain unknown.','decision_semantics':'Lexically extracted directions are candidates, not canonically adjudicated decisions.','duplicate_semantics':'Counts are source occurrences; matching native IDs/content hashes are indexed, never silently merged across accounts.','narrative_review':'Machine extraction/search completed; semantic review and Jev reconstruction remain separate work.'}
        (ROOT/'data'/'recovery-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8'); print(json.dumps(report,ensure_ascii=True,indent=2),flush=True)
        return report

def main():
    p=argparse.ArgumentParser(); p.add_argument('--archive',type=Path); p.add_argument('--attachment',type=Path); p.add_argument('--codex',type=Path); p.add_argument('--exclude-session',default='01a18f6a-af21-78c1-83e2-02117c13aa7a'); p.add_argument('--db',type=Path,default=ROOT/'data'/'sunny.sqlite'); p.add_argument('--extra',type=Path,action='append',default=[]); p.add_argument('--retry-pending',action='store_true'); args=p.parse_args()
    args.db.parent.mkdir(parents=True,exist_ok=True); db=sqlite3.connect(args.db); db.executescript(SCHEMA); imp=Importer(db)
    if args.retry_pending:
        pending=db.execute("SELECT id,path,original_path,kind FROM sources WHERE status='preserved_extraction_pending'").fetchall()
        for sid,path,original,kind in pending:
            imp.import_file(Path(path),original,kind,retry=True)
    if args.archive: imp.archive(args.archive)
    if args.attachment: imp.import_file(args.attachment,kind='supplied_specification_transcript')
    for path in args.extra: imp.import_file(path,kind='recovered_prior_artifact')
    if args.codex: imp.codex(args.codex,args.exclude_session)
    db.execute('INSERT OR REPLACE INTO coverage VALUES(?,?,?,?)',('live_account','not_available','ChatGPT live account','No live conversation search/read capability is exposed. Export coverage cannot prove live-account completeness.'))
    db.commit(); imp.verify(); db.close()

if __name__=='__main__': main()
