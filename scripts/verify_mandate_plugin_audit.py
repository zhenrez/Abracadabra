"""Final bounded audit artifact consistency check; no source or task mutation."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def load(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
report=load('docs/evidence/mandate-plugin-execution.json')
for name,meta in report['evidence_files'].items():assert sha(name)==meta['sha256'],name
review=load('docs/evidence/mandate-independent-review.json')
for name,expected in review['artifact_hashes'].items():assert sha(name)==expected,name
ledger=load('state/capabilities.json');before=load(ledger['prior_bytes_snapshot'])
assert sha(ledger['prior_bytes_snapshot'])==ledger['prior_bytes_sha256']
assert len(ledger['plugins'])==24 and len({p['name'] for p in ledger['plugins']})==24
old={p['name']:p for p in before['plugins']}
for p in ledger['plugins']:
 for key in ('historical_application','historical_boundary'):assert p.get(key)==old[p['name']].get(key)
 assert p['boundary'] and p['runtime_status'] and p['method_status']
for name in ['docs/evidence/mandate-mightshape-result.json','docs/evidence/mandate-derivation-mightshape-result.json']:assert load(name)['firewall']=='PASS'
for name in ['docs/evidence/mandate-proofline-verification.json','docs/evidence/mandate-derivation-proofline-result.json']:assert load(name)['valid']
assert load('docs/evidence/mandate-agentproof-blocked.json')['capture_started'] is False
assert load('docs/evidence/mandate-agentproof-existing-verification.json')['repository']['checked_file_count']==0
result={'status':'passed','checked_utc':datetime.now(timezone.utc).isoformat(),'evidence_files_hash_checked':len(report['evidence_files']),'review_artifact_hashes_checked':len(review['artifact_hashes']),'current_plugins':24,'historical_capability_fields_preserved':True,'project_complete':False,'extended_new_math_review':'Separate scope after new artifacts stabilize.'}
(ROOT/'docs/evidence/mandate-audit-final-verification.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result))
