import json,re,hashlib,zipfile
from functools import lru_cache
from pathlib import Path
R=Path(__file__).resolve().parents[1]
out=R/'deliverables/score-hierarchy-review-20261103'
out.mkdir(exist_ok=True)
seeds=['AGENTS.md', 'CONTINUE.md', 'PLAN.md', 'state/task.json', 'state/mission.json', 'state/reactivation.json', 'docs/reconstruction/SUNNY_GOALS.md', 'docs/HUMMBL_PLAN.md', 'package.json', 'package-lock.json', 'tsconfig.json', 'state/background/main/model-budget.json', 'state/processes/jev-8149.json', 'docs/reconstruction/MASTER_SCORE.md', 'docs/reconstruction/GENERATIONAL_CONSTRAINTS.md', 'docs/reconstruction/ALGEBRAIC_EXTENSION.md', 'docs/reconstruction/HIERARCHY_SOURCE_REGISTER.md', 'state/reconstruction/master-score.json', 'state/reconstruction/generational-constraints.json', 'state/reconstruction/algebraic-extension.json', 'state/reconstruction/hierarchy-atlas-combined.json', 'state/reconstruction/hierarchy-atlas.json', 'state/reconstruction/musical-hierarchies.json', 'state/reconstruction/angelic-hierarchy-supplement.json', 'deliverables/SUNNY_Hierarchy_Atlas.html', 'docs/evidence/hierarchy-independent-review.json', 'docs/evidence/hierarchy-ui-final-verification.json', 'scripts/combine_hierarchy_atlas.mjs', 'scripts/reconstruct_master_score.mjs', 'scripts/reconstruct_generational_constraints.py', 'scripts/reconstruct_algebraic_extension.mjs', 'src/score.ts', 'src/hierarchy.ts', 'src/algebraic-scalar.ts', 'tests/score.test.mjs', 'tests/hierarchy.test.mjs', 'tests/algebraic-scalar.test.mjs', 'state/research/reactivation/western/checkpoint-01.json', 'state/research/reactivation/symbols/checkpoint-02.json']
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
 if not p.is_file() and p.suffix=='.js':
  p=Path(str(p).replace('/dist/','/src/').replace('\\dist\\','\\src\\')).with_suffix('.ts')
 return p if p.is_file() and p.suffix.lower() not in ['.sqlite','.db','.exe','.dll'] else None
while queue:
 rel,why,depth=queue.pop(0)
 p=R/rel
 if rel in seen:continue
 if rel.startswith('data/raw/codex/') or '/rollout-' in rel:missing.append({'path':rel,'reason':'excluded native log copy'});continue
 if not p.is_file():missing.append({'path':rel,'from':why});continue
 if (p.stat().st_size>25000000 and rel!='deliverables/SUNNY_Hierarchy_Atlas.html') or p.suffix.lower() in ['.zip','.7z']:
  missing.append({'path':rel,'from':why,'reason':'oversized or archive dependency; bounded transfer retains reference, not silently missing'});continue
 raw=p.read_bytes();seen[rel]={'path':rel,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'from':why}
 # Raw witnesses are terminal; do not recursively import their historical instructions or archives.
 if depth>=2 or rel in ['CONTINUE.md','PLAN.md','AGENTS.md','state/reactivation.json','state/reconstruction/coverage.json','docs/evidence/hierarchy-independent-review.json','docs/evidence/hierarchy-ui-final-verification.json','state/task.json','state/mission.json','docs/HUMMBL_PLAN.md','docs/PLUGIN_CAPABILITIES.md','work/jev-resume-20261102/HANDOFF.md','state/reconstruction/hierarchy-inputs.json'] or rel.startswith('data/') or p.suffix.lower() not in ['.json','.md','.py','.ts','.mjs']:continue
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
attachment=Path('C:/Users/Brend/.codex/attachments/9e8a9e86-cd7d-4923-8da0-1ead7954ca88/Pasted text.txt')
attachment_bytes=attachment.read_bytes() if attachment.is_file() else None
manifest={'scope':'Bounded depth-two explicit path dependency slice; raw witnesses terminal. Not exhaustive account census or proof of semantic acceptance. Missing/unresolved dynamic references remain visible in included scripts.','files':list(seen.values()),'missing':missing}
(out/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
archive=R/'deliverables/SUNNY-score-hierarchy-review-20261103.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for rel,row in seen.items():
  b=(R/rel).read_bytes()
  if hashlib.sha256(b).hexdigest()!=row['sha256']:raise RuntimeError('Source changed '+rel)
  z.writestr(rel,b)
 z.write(out/'MANIFEST.json','MANIFEST.json')
 if attachment_bytes is not None:z.writestr('known-attachment/Pasted text.txt',attachment_bytes)
 z.writestr('ATTACHMENT-MANIFEST.json',json.dumps({'original_path':str(attachment),'bytes':len(attachment_bytes) if attachment_bytes else None,'sha256':hashlib.sha256(attachment_bytes).hexdigest() if attachment_bytes else None}))
print(json.dumps({'path':str(archive),'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':len(seen),'missing':missing}))

