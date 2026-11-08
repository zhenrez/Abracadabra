import ast,hashlib,json,re,sqlite3,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables/host-closure-recovery-20261103'
OUT.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
seeds=['AGENTS.md','state/task.json','docs/HUMMBL_PLAN.md','src/server.ts','scripts/quarterback.py','scripts/verify_recovery.py','scripts/jev_tool.py','state/progress-audit.json','docs/PLUGIN_CAPABILITIES.md','docs/evidence/reactivation-local-jev-receipt.json','scripts/render_hierarchy_atlas.mjs','scripts/reconstruct_generational_constraints.py','state/reconstruction/hierarchy-atlas-combined.json','state/reconstruction/hierarchy-atlas.json','docs/evidence/hierarchy-ui-design-superjev.json','public/hierarchy-atlas.css','public/hierarchy-atlas-client.js','public/index.html','public/app.js','public/style.css','package.json','package-lock.json','tsconfig.json','state/work-queue.json','state/superjev-checkpoint.json','data/archive-manifest.json']
selected={};missing=[];edges=[];boundaries=[]
def resolve(p):
 p=p.resolve()
 if 'dist' in p.parts:
  parts=list(p.parts);parts[parts.index('dist')]='src';p=Path(*parts).with_suffix('.ts')
 if not p.exists() and p.suffix=='.js':p=p.with_suffix('.ts')
 return p
queue=[ROOT/s for s in seeds]
while queue:
 p=resolve(queue.pop(0))
 try:rel=p.relative_to(ROOT).as_posix()
 except ValueError:boundaries.append(str(p));continue
 if rel in selected:continue
 if p.is_dir():boundaries.append(rel+' (directory reference, not a missing file)');continue
 if not p.is_file():missing.append(rel);continue
 if any(x in rel.lower() for x in ['.codex/','codex-session','rollout-','data/raw/codex']):boundaries.append(rel);continue
 if p.suffix in ['.sqlite','.db']:boundaries.append(rel);continue
 b=p.read_bytes();selected[rel]=b
 if p.suffix not in ['.ts','.js','.mjs','.py','.ps1','.html']:continue
 t=b.decode('utf-8-sig')
 refs=set(re.findall(r'''["']((?:src|scripts|public|state|docs|data)/[A-Za-z0-9_./-]+\.(?:json|ts|js|mjs|py|ps1|css|html))["']''',t))
 for ref in refs:edges.append([rel,ref]);queue.append(ROOT/ref)
 for ref in re.findall(r'''(?:from\s*|import\s*\(|new URL\s*\()\s*["'](\.[^"']+)["']''',t):
  q=resolve(p.parent/ref);edges.append([rel,str(q)]);queue.append(q)
 if p.suffix=='.py':
  for node in ast.walk(ast.parse(t)):
   names=([node.module] if isinstance(node,ast.ImportFrom) and node.module else [x.name for x in node.names] if isinstance(node,ast.Import) else [])
   for name in names:
    q=p.parent/(name.replace('.','/')+'.py')
    if q.is_file():queue.append(q)
for p in ROOT.glob('tsconfig*.json'):selected[p.relative_to(ROOT).as_posix()]=p.read_bytes()
tree=ast.parse((ROOT/'scripts/reconstruct_generational_constraints.py').read_text('utf-8-sig'))
specs=next(ast.literal_eval(n.value) for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='source_specs' for t in n.targets))
db=sqlite3.connect((ROOT/'data/sunny.sqlite').as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row;db.execute('PRAGMA query_only=ON')
report={'scope':'Schema and selected metadata only; no message text or database export.','schema':{},'selection':[],'needed_columns':{'messages':['id','source_id','conversation_id','text','content_sha256','role','locator','create_time'],'sources':['id','path','sha256','original_path'],'conversations':['id','title']},'limitations':['Generator also reads and hashes complete original source files; row-only export is insufficient.','verify_recovery.py audits all database rows and source files and writes its report; not executed.','Absolute source paths require explicit relocation mapping in cloud; originals must remain preserved.']}
for table in report['needed_columns']:
 report['schema'][table]={'sql':db.execute('SELECT sql FROM sqlite_master WHERE type=? AND name=?',('table',table)).fetchone()[0],'columns':[dict(r) for r in db.execute('PRAGMA table_info('+table+')')]}
for name,mid,anchor in specs:
 r=db.execute('SELECT m.id,m.source_id,m.conversation_id,m.role,m.content_sha256,s.path,s.sha256 FROM messages m JOIN sources s ON s.id=m.source_id WHERE m.id=?',(mid,)).fetchone()
 report['selection'].append({'name':name,'message_id':mid,'metadata':dict(r) if r else None,'excluded_source':bool(r and any(x in r['path'].lower().replace('\\','/') for x in ['.codex/sessions','rollout-','data/raw/codex']))})
db.close()
selected['RECOVERY/DB-SELECTION.json']=(json.dumps(report,indent=2)+'\n').encode()
atlas=json.loads((ROOT/'state/reconstruction/hierarchy-atlas-combined.json').read_text('utf-8-sig'))
inputs=[]
for s in atlas.get('sources',[]):
 inputs.append({'id':s.get('id'),'path':s.get('path'),'declared_sha256':s.get('sha256'),'status':'Input reference only; previously transferred source corpus is not reread or duplicated here.'})
selected['RECOVERY/HTML-INPUT-LEDGER.json']=json.dumps(inputs,indent=2).encode()
boundaries.append('External installed SuperJev helper referenced by quarterback: not included; no external plugin code or runtime was launched.')
manifest={'scope':'Host source recursive literal local imports and explicitly named code/config references; dynamic paths and source corpus recorded as boundaries, not exhaustive closure.','files':[],'missing':sorted(set(missing)),'boundaries':sorted(set(boundaries)),'edges':edges,'redactions':[]}
url=re.compile(r'''https?://[^\s<>"']+''',re.I)
secret=re.compile(r'(?:[?&](?:sig|signature|token|access_token|X-Amz-Signature|X-Goog-Signature|se|sk)=)',re.I)
for rel,b in list(selected.items()):
 t=b.decode('utf-8-sig');matches=[m for m in url.finditer(t) if secret.search(m.group())]
 for m in reversed(matches):
  manifest['redactions'].append({'path':rel,'line':t.count('\n',0,m.start())+1,'start':m.start(),'end':m.end(),'kind':'signed URL'})
  t=t[:m.start()]+'[REDACTED SIGNED URL]'+t[m.end():]
 d=t.encode('utf-8') if matches else b
 # Stop rather than transmit a possible non-URL token.
 if re.search(r'\b(?:sk-proj-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|Bearer\s+[A-Za-z0-9_.-]{30,})',t):raise RuntimeError('Potential credential needs review: '+rel)
 selected[rel]=d;manifest['files'].append({'path':rel,'original_bytes':len(b),'original_sha256':sha(b),'transfer_bytes':len(d),'transfer_sha256':sha(d)})
selected['RECOVERY/MANIFEST.json']=json.dumps(manifest,indent=2).encode()
z=OUT/'SUNNY-host-closure-20261103.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as archive:
 for rel,b in sorted(selected.items()):archive.writestr(rel,b)
with zipfile.ZipFile(z) as archive:
 for f in manifest['files']:assert sha(archive.read(f['path']))==f['transfer_sha256']
assert z.stat().st_size<=8*1024*1024
(OUT/'DB-SELECTION.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(OUT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'archive':str(z),'bytes':z.stat().st_size,'sha256':sha(z.read_bytes()),'files':len(manifest['files']),'redactions':len(manifest['redactions']),'missing':manifest['missing'],'boundaries':manifest['boundaries'],'database_selection':report['selection']},indent=2))
