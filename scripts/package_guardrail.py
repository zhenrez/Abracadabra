"""Build the actual SUNNY source-integrity package selected by Jev receipt 000004."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json,uuid
ROOT=Path(__file__).resolve().parents[1]
verifier=Path(r'C:\Users\Brend\.codex\plugins\cache\openai-curated-remote\proofline\2.0.2\skills\manage-evidence-decisions\scripts\proofline_package.py')
spec=importlib.util.spec_from_file_location('proofline_package',verifier); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
content=(ROOT/'state'/'latest-user-correction.txt').read_text(encoding='utf8')
sha=lambda x:hashlib.sha256(x.encode('utf8')).hexdigest()
uid=lambda value:str(uuid.uuid5(uuid.NAMESPACE_URL,value))
source_id=uid('SUNNY/direct-user-correction'); version_id=uid(sha(content)); parser='sunny-exact-user-span-v1'
def hashed(kind,obj): obj['node_hash']=module.node_hash(kind,obj); return obj
source=hashed('source-version',{'workspace_id':uid(str(ROOT)),'source_id':source_id,'source_identity_sha256':sha('source:'+source_id),'source_version_id':version_id,'version_number':1,'content':content,'content_sha256':sha(content),'content_length':len(content),'parser_version':parser})
chunk=hashed('chunk',{'id':uid(version_id+'/chunk0'),'source_node_hash':source['node_hash'],'source_id':source_id,'source_version_id':version_id,'ordinal':0,'start_offset':0,'end_offset':len(content),'start_line':1,'end_line':module.line_number(content,len(content)-1),'content':content,'content_sha256':sha(content)})
quote='use jev for absolutely everything, every possible decision absolutely MUST be dictated by jev'; start=content.index(quote); end=start+len(quote)
citation=hashed('citation',{'id':uid(version_id+'/citation'),'source_node_hash':source['node_hash'],'chunk_node_hashes':[chunk['node_hash']],'source_id':source_id,'source_version_id':version_id,'start_offset':start,'end_offset':end,'start_line':module.line_number(content,start),'end_line':module.line_number(content,end-1),'quote':quote,'quote_sha256':sha(quote)})
transformation=hashed('transformation',{'method':'deterministic','parser_version':parser,'model_runs':[],'input_node_hashes':[source['node_hash'],chunk['node_hash'],citation['node_hash']]})
artifact=hashed('decision-artifact',{'id':uid('SUNNY/engineering/live-jev-required'),'kind':'constraint','title':'Direct user requirement: actual Jev decision gates','statement':'The user requires actual Jev to dictate SUNNY decisions.','rationale':'Exact extraction of the located direct user instruction; Jev selected packaging scope in receipt000004-e9e767cab464. confidence1 denotes exact source-span fidelity only, not Jev accuracy, research truth, account completeness or ontology validity. Research confidence remains UNKNOWN outside this package.','confidence':1.0,'valid_from':None,'valid_to':None,'transformation_node_hash':transformation['node_hash'],'citation_node_hashes':[citation['node_hash']]})
now=datetime.now(timezone.utc).isoformat()
review=hashed('review-state',{'artifact_node_hash':artifact['node_hash'],'status':'candidate','created_at':now,'updated_at':now})
package={'manifest':{'schema':module.SCHEMA,'created_at':now,'app_version':'sunny0.1.0','root_hash':module.envelope('package-root',{'artifact_node_hash':artifact['node_hash'],'review_node_hash':review['node_hash']})},'payload':{'source_version':source,'chunks':[chunk],'citations':[citation],'transformation':transformation,'artifact':artifact,'review':review}}
result=module.verify(package)
out=ROOT/'docs'/'evidence'/'proofline-sunny-decision.json'; out.write_text(json.dumps(package,ensure_ascii=False,indent=2),encoding='utf8')
(out.with_name('proofline-sunny-scope.json')).write_text(json.dumps({'source':str(ROOT/'state'/'latest-user-correction.txt'),'source_bytes_sha256':hashlib.sha256((ROOT/'state'/'latest-user-correction.txt').read_bytes()).hexdigest(),'decision_receipt':'state/jev-receipts/000004-e9e767cab464.json','confidence_semantics':'exact deterministic source-span fidelity only','research_confidence':None,'signed':False,'authentication':'No independent signer or trusted timestamp','verification':result},indent=2),encoding='utf8')
print(json.dumps({'package':str(out),'verification':result},indent=2))
