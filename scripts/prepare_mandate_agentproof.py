"""Copy the actual focused calculation unit into a separate, hash-bound Git scope."""
from pathlib import Path
import hashlib,json

root=Path(__file__).resolve().parents[1]
scope=root/'work'/'mandate-agentproof-2026-10-31'
if scope.exists():raise SystemExit('New capture scope already exists; do not replace it.')
files=['src/prediction.ts','src/law.ts','dist/prediction.js','dist/law.js','tests/prediction.test.mjs','state/native-comparison.json','package.json']
rows=[]
for name in files:
 source=root/name
 if not source.is_file() or source.is_symlink():raise SystemExit('Actual calculation input missing or symlinked: '+name)
 data=source.read_bytes();dest=scope/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 rows.append({'source':str(source),'snapshot':str(dest),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
control=scope/'.agentproof';control.mkdir()
request={'action':'capture','model':'gpt-6.1-sol','sandbox':'read-only','prompt':'This isolated local repository is an authorized, hash-bound copy of the actual SUNNY calculation unit. Parent coordination uses SuperJev and Proofline/MightShape guardrails. Run only the focused Node test file tests/prediction.test.mjs with node --test and report the pass/fail counts; do not start services, browsers, additional agents, network research, or persistent processes. Do not modify any file or read private configuration. Stop after this bounded calculation check.'}
(control/'request.json').write_text(json.dumps(request,indent=2),encoding='utf-8')
manifest={'schema':'sunny.agentproof-actual-snapshot.v1','scope':str(scope),'substantive_choice':'docs/evidence/mandate-continuity-guard-superjev.json','files':rows,'limit':'Focused actual calculation snapshot, not the complete SUNNY repository or current chat. Original sources and previous receipts are unchanged.'}
(root/'docs/evidence/mandate-agentproof-snapshot.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'scope':str(scope),'file_count':len(rows),'bytes':sum(r['bytes'] for r in rows)}))
