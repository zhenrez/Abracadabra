"""Fresh, bounded input-fidelity guards; old project guardrail outputs stay intact."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json,sys,uuid
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'/'evidence'
PROOFLINE=Path(r'C:\Users\Brend\.codex\plugins\cache\openai-curated-remote\proofline\2.0.2\skills\manage-evidence-decisions\scripts\proofline_package.py')
def digest(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()
def main():
 manifest_path=OUT/'mandate-input-preservation.json';raw=manifest_path.read_bytes();manifest=json.loads(raw)
 checks=[]
 for row in manifest['inputs']+[manifest['authority_snapshot']]:
  a=Path(row['original']);b=Path(row['snapshot']);ah=hashlib.sha256(a.read_bytes()).hexdigest();bh=hashlib.sha256(b.read_bytes()).hexdigest()
  checks.append({'original':str(a),'snapshot':str(b),'original_sha256':ah,'snapshot_sha256':bh,'matches_manifest_and_each_other':ah==bh==row['sha256']==row['snapshot_sha256']})
 assert all(row['matches_manifest_and_each_other'] for row in checks)
 assert manifest['authority']['source_role']=='parent_agent_attestation_of_latest_direct_user_turn'
 assert 'byte identity to the inline turn is not asserted' in manifest['authority']['limitation']
 source_count=len(manifest['inputs']);unique_count=len({row['sha256'] for row in manifest['inputs']})
 assert (source_count,unique_count)==(5,3)
 spec=importlib.util.spec_from_file_location('proofline_mandate',PROOFLINE);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
 content=raw.decode('utf-8-sig');uid=lambda name:str(uuid.uuid5(uuid.NAMESPACE_URL,name))
 def hashed(kind,obj):obj['node_hash']=v.node_hash(kind,obj);return obj
 sid=uid('SUNNY/mandate-preservation-manifest');vid=uid(digest(content));parser='sunny-exact-manifest-span-v1'
 source=hashed('source-version',{'workspace_id':uid(str(ROOT)),'source_id':sid,'source_identity_sha256':digest('source:'+sid),'source_version_id':vid,'version_number':1,'content':content,'content_sha256':digest(content),'content_length':len(content),'parser_version':parser})
 chunk=hashed('chunk',{'id':uid(vid+'/chunk'),'source_node_hash':source['node_hash'],'source_id':sid,'source_version_id':vid,'ordinal':0,'start_offset':0,'end_offset':len(content),'start_line':1,'end_line':v.line_number(content,len(content)-1),'content':content,'content_sha256':digest(content)})
 # Quote the manifest, not a reconstructed inline message. It includes the explicit
 # attestation/byte-identity limit and all five original/snapshot occurrences.
 cite=hashed('citation',{'id':uid(vid+'/citation'),'source_node_hash':source['node_hash'],'chunk_node_hashes':[chunk['node_hash']],'source_id':sid,'source_version_id':vid,'start_offset':0,'end_offset':len(content),'start_line':1,'end_line':v.line_number(content,len(content)-1),'quote':content,'quote_sha256':digest(content)})
 transform=hashed('transformation',{'method':'deterministic','parser_version':parser,'model_runs':[],'input_node_hashes':[source['node_hash'],chunk['node_hash'],cite['node_hash']]})
 artifact=hashed('decision-artifact',{'id':uid('SUNNY/mandate/preservation-fidelity'),'kind':'constraint','title':'Preserve every supplied input occurrence and qualify inline authority','statement':'Five named attachment occurrences currently exist and match their snapshots, with three unique contents. Current inline authority is represented by a parent attestation, not independently captured inline bytes.','rationale':'Fresh byte comparisons are in mandate-input-guard-checks.json. The numeric confidence1 is exact local manifest-span fidelity only, not historical/mathematical truth, absence of earlier deletion, native-inline identity, or research confidence. The package remains a review candidate.','confidence':1.0,'valid_from':None,'valid_to':None,'transformation_node_hash':transform['node_hash'],'citation_node_hashes':[cite['node_hash']]})
 now=datetime.now(timezone.utc).isoformat();review=hashed('review-state',{'artifact_node_hash':artifact['node_hash'],'status':'candidate','created_at':now,'updated_at':now})
 package={'manifest':{'schema':v.SCHEMA,'created_at':now,'app_version':'sunny0.1.0','root_hash':v.envelope('package-root',{'artifact_node_hash':artifact['node_hash'],'review_node_hash':review['node_hash']})},'payload':{'source_version':source,'chunks':[chunk],'citations':[cite],'transformation':transform,'artifact':artifact,'review':review}}
 (OUT/'mandate-input-proofline-package.json').write_text(json.dumps(package,ensure_ascii=False,indent=2),encoding='utf-8')
 result=v.verify(package)
 (OUT/'mandate-input-guard-checks.json').write_text(json.dumps({'checked_utc':now,'status':'passed','attachment_occurrences':source_count,'unique_attachment_contents':unique_count,'checks':checks,'proofline':result,'scope':'Current byte/span integrity and attestation-role preservation, not universal math or proof no input was ever lost.'},indent=2),encoding='utf-8')
 records=[]
 for ix,claim,refs in [
  (1,'Five supplied attachment occurrences currently match their saved byte snapshots; three distinct content hashes remain separate from occurrence count.',['docs/evidence/mandate-input-preservation.json','docs/evidence/mandate-input-guard-checks.json']),
  (2,'The current authority record is explicitly a parent-agent attestation; native inline byte identity is not asserted.',['data/raw/mandate-inputs/current-authority-attestation-2026-10-31.json']),
  (3,'The earlier AgentProof scope records two failed child commands and zero changed-file commitments; that capture is not a passing mathematical check.',['docs/evidence/agentproof-sunny-scope.json'])]:
  records.append({'id':f'E-{ix:03d}','claim':claim,'provenance':'RESEARCH_SUPPORTED_INFERENCE','confidence':1.0,'evidence_strength':0,'status':'active','source_refs':refs,'scope':'Literal engineering-record/fidelity observation only. Confidence1 is an exact checked-record statement, not domain plausibility or a learned weight; strength0 makes no real-world population claim.'})
 (OUT/'mandate-mightshape-input.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
 print(json.dumps({'status':'passed','attachment_occurrences':source_count,'unique_contents':unique_count,'file_comparisons':len(checks),'proofline':result},indent=2))
if __name__=='__main__':main()
