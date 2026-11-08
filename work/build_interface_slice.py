import json,re,hashlib,zipfile
from functools import lru_cache
from pathlib import Path
R=Path(__file__).resolve().parents[1]
out=R/'deliverables/interface-slice-20261102'
out.mkdir(exist_ok=True)
seeds=['state/mission.json','state/task.json','docs/HUMMBL_PLAN.md','docs/PLUGIN_CAPABILITIES.md','work/jev-resume-20261102/HANDOFF.md','state/jev-receipts/000055-7e888363daa7.json','state/jev-receipts/000056-45128d97853d.json']
for n in ['NATIVE_EXECUTION','NATIVE_DERIVATIONS','MUSIC_GEOMETRY','MUSICAL_HIERARCHIES']:seeds.append('docs/reconstruction/'+n+'.md')
for n in ['native-execution','native-derivations','music-geometry','musical-hierarchies']:seeds.append('state/reconstruction/'+n+'.json')
seeds+=['scripts/reconstruct_native_execution.mjs','scripts/reconstruct_native_derivations.py','scripts/reconstruct_musical_hierarchies.py','src/native-operators.ts','tests/native-operators.test.mjs','docs/evidence/native-derivations-source-bindings.json','state/reconstruction/hierarchy-inputs.json']
m=json.loads((R/'state/mission.json').read_text(encoding='utf-8-sig'))
seeds+=['src/law.ts','tests/musical-hierarchies.test.mjs','docs/evidence/musical-hierarchy-primary-retrieval.json']
seeds += [x['path'] for x in m['prior_art_research']['references']]
seen={};missing=[];queue=[(p,'seed',0) for p in seeds]
def strings(x):
 if isinstance(x,str):yield x
 elif isinstance(x,list):
  for y in x:yield from strings(y)
 elif isinstance(x,dict):
  for k,v in x.items():
   yield k
   yield from strings(v)
@lru_cache(maxsize=20000)
def candidate(s,base):
 s=s.replace('\\','/').split('#')[0]
 if not s.startswith(('data/','state/','src/','tests/','scripts/','docs/','work/','../','./',str(R).replace('\\','/')+'/')):return None
 if '.codex/' in s or 'sessions/' in s:return None
 p=Path(s)
 if not p.is_absolute():p=(R/s) if s.startswith(('data/','state/','src/','tests/','scripts/','docs/','work/')) else base/s
 try:p=p.resolve();p.relative_to(R)
 except:return None
 return p if p.is_file() and p.suffix.lower() not in ['.sqlite','.db','.exe','.dll'] else None
while queue:
 rel,why,depth=queue.pop(0)
 p=R/rel
 if rel in seen:continue
 if not p.is_file():missing.append({'path':rel,'from':why});continue
 if p.stat().st_size>25000000 or p.suffix.lower() in ['.zip','.7z']:
  missing.append({'path':rel,'from':why,'reason':'oversized or archive dependency; bounded transfer retains reference, not silently missing'});continue
 raw=p.read_bytes();seen[rel]={'path':rel,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'from':why}
 # Raw witnesses are terminal; do not recursively import their historical instructions or archives.
 if depth>=2 or rel in ['state/task.json','state/mission.json','docs/HUMMBL_PLAN.md','docs/PLUGIN_CAPABILITIES.md','work/jev-resume-20261102/HANDOFF.md','state/reconstruction/hierarchy-inputs.json'] or rel.startswith('data/') or p.suffix.lower() not in ['.json','.md','.py','.ts','.mjs']:continue
 text=raw.decode('utf-8-sig',errors='replace');values=[]
 if p.suffix=='.json':
  try:values=list(strings(json.loads(text)))
  except:pass
 values += re.findall(r'[`\"\']([^`\"\'\n]+)[`\"\']',text)
 values += re.findall(r'\]\(([^)]+)\)',text)
 for s in values:
  if len(s)>1000:continue
  c=candidate(s,p.parent)
  if c:
   cr=c.relative_to(R).as_posix()
   if cr.startswith(('data/','state/reconstruction/','docs/evidence/','src/','tests/','scripts/')):queue.append((cr,rel,depth+1))
manifest={'scope':'Bounded depth-two explicit path dependency slice; raw witnesses terminal. Not exhaustive account census or proof of semantic acceptance. Missing/unresolved dynamic references remain visible in included scripts.','files':list(seen.values()),'missing':missing}
(out/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
archive=R/'deliverables/SUNNY-interface-dependencies-20261102.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for rel,row in seen.items():
  b=(R/rel).read_bytes()
  if hashlib.sha256(b).hexdigest()!=row['sha256']:raise RuntimeError('Source changed '+rel)
  z.writestr(rel,b)
 z.write(out/'MANIFEST.json','MANIFEST.json')
print(json.dumps({'path':str(archive),'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':len(seen),'missing':missing}))

