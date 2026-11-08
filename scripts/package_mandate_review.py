"""A separate Proofline integrity envelope for independently checked calculation records."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json,sys,uuid
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[1];out=root/'docs/evidence'
plugin=Path(r'C:\Users\Brend\.codex\plugins\cache\openai-curated-remote\proofline\2.0.2\skills\manage-evidence-decisions\scripts\proofline_package.py')
spec=importlib.util.spec_from_file_location('proofline_calculation_review',plugin);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
raw=(out/'mandate-independent-review.json').read_bytes();content=raw.decode('utf8');review=json.loads(content)
assert review['status']=='passed' and all(c['passed'] for c in review['checks'])
for name,expected in review['artifact_hashes'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==expected,name
uid=lambda x:str(uuid.uuid5(uuid.NAMESPACE_URL,x))
digest=lambda x:hashlib.sha256(x.encode()).hexdigest()
def hashed(kind,value):value['node_hash']=v.node_hash(kind,value);return value
sid=uid('SUNNY/mandate-independent-review');vid=uid(digest(content));parser='sunny-exact-review-span-v1'
source=hashed('source-version',{'workspace_id':uid(str(root)),'source_id':sid,'source_identity_sha256':digest('source:'+sid),'source_version_id':vid,'version_number':1,'content':content,'content_sha256':digest(content),'content_length':len(content),'parser_version':parser})
span={'source_node_hash':source['node_hash'],'source_id':sid,'source_version_id':vid,'start_offset':0,'end_offset':len(content),'start_line':1,'end_line':v.line_number(content,len(content)-1)}
chunk=hashed('chunk',{'id':uid(vid+'/chunk'),**span,'ordinal':0,'content':content,'content_sha256':digest(content)})
citation=hashed('citation',{'id':uid(vid+'/citation'),**span,'chunk_node_hashes':[chunk['node_hash']],'quote':content,'quote_sha256':digest(content)})
transform=hashed('transformation',{'method':'deterministic','parser_version':parser,'model_runs':[],'input_node_hashes':[source['node_hash'],chunk['node_hash'],citation['node_hash']]})
artifact=hashed('decision-artifact',{'id':uid('SUNNY/mandate/independent-calculation-review'),'kind':'constraint','title':'Keep executed calculation scope and source binding explicit','statement':'The recorded independent review passed nine scoped arithmetic/source checks and five focused prediction tests, with artifact hashes bound. It does not select a global orientation or establish blinded empirical success.','rationale':'This package verifies the exact review-record span and internal references. Confidence1 is literal record fidelity only; mathematical correctness depends on the scoped derivations and their independently checkable premises, not this hash envelope.','confidence':1.0,'valid_from':None,'valid_to':None,'transformation_node_hash':transform['node_hash'],'citation_node_hashes':[citation['node_hash']]})
now=datetime.now(timezone.utc).isoformat();status=hashed('review-state',{'artifact_node_hash':artifact['node_hash'],'status':'candidate','created_at':now,'updated_at':now})
package={'manifest':{'schema':v.SCHEMA,'created_at':now,'app_version':'sunny0.1.0','root_hash':v.envelope('package-root',{'artifact_node_hash':artifact['node_hash'],'review_node_hash':status['node_hash']})},'payload':{'source_version':source,'chunks':[chunk],'citations':[citation],'transformation':transform,'artifact':artifact,'review':status}}
(out/'mandate-derivation-proofline-package.json').write_text(json.dumps(package,indent=2),encoding='utf8')
result=v.verify(package);(out/'mandate-derivation-proofline-result.json').write_text(json.dumps(result,indent=2),encoding='utf8')
records=[]
claims=[('Scoped independent checks preserve source-native length/frequency reciprocals, normalization carries, the inverse-word counterexample and the twelve-candidate residue family.',['docs/evidence/mandate-independent-review.json']),('A scalar-only endpoint cannot left-invert both protected RL and LR histories; this follows conditionally from their equal scalar evaluations and unequal retained histories.',['state/reconstruction/tol-history-math.json','docs/evidence/mandate-independent-review.json']),('The native derivation retains a Jev group-membership error and its exact counterexample instead of treating model probability as mathematical proof.',['state/reconstruction/native-derivations.json','docs/evidence/native-derivations-jev-result.json'])]
for ix,(claim,refs) in enumerate(claims,101):records.append({'id':f'E-{ix:03d}','claim':claim,'provenance':'RESEARCH_SUPPORTED_INFERENCE','confidence':1.0,'evidence_strength':0,'status':'active','source_refs':refs,'scope':'Literal scoped calculation/review record; confidence is checked-record fidelity, not empirical probability. No human participant, historical attestation or generalization strength asserted.'})
(out/'mandate-derivation-mightshape-input.json').write_text(json.dumps(records,indent=2),encoding='utf8')
print(json.dumps(result))
