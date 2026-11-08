"""Use the installed Proofline/MightShape contracts on this actual scoped packet."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib, importlib.util, json, subprocess, sys, uuid
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
PLUGIN=Path('C:/Users/Brend/.codex/plugins/cache/openai-curated-remote/proofline/2.0.2/skills/manage-evidence-decisions/scripts/proofline_package.py')
MIGHT=Path('C:/Users/Brend/.codex/plugins/cache/openai-curated-remote/mightshape/1.0.1/skills/mightshape/scripts/check_evidence.py')
spec=importlib.util.spec_from_file_location('western_proofline',PLUGIN)
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
def digest(x):return hashlib.sha256(x.encode()).hexdigest()
def uid(x):return str(uuid.uuid5(uuid.NAMESPACE_URL,x))
def hashed(kind,x):x['node_hash']=v.node_hash(kind,x);return x
def write(name,x):(ROOT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding='utf8')
content=(ROOT/'verification-02.json').read_text(encoding='utf8')
review=json.loads(content)
assert review['status']=='passed'
for name,expected in review['packet_hashes'].items():
 assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
sid=uid('SUNNY/western/method-packet-review');vid=uid(digest(content));parser='sunny-western-exact-review-span-v1'
source=hashed('source-version',{'workspace_id':uid(str(ROOT.parents[3])),'source_id':sid,'source_identity_sha256':digest('source:'+sid),'source_version_id':vid,'version_number':1,'content':content,'content_sha256':digest(content),'content_length':len(content),'parser_version':parser})
span={'source_node_hash':source['node_hash'],'source_id':sid,'source_version_id':vid,'start_offset':0,'end_offset':len(content),'start_line':1,'end_line':v.line_number(content,len(content)-1)}
chunk=hashed('chunk',{'id':uid(vid+'/chunk'),**span,'ordinal':0,'content':content,'content_sha256':digest(content)})
citation=hashed('citation',{'id':uid(vid+'/citation'),**span,'chunk_node_hashes':[chunk['node_hash']],'quote':content,'quote_sha256':digest(content)})
transform=hashed('transformation',{'method':'deterministic','parser_version':parser,'model_runs':[],'input_node_hashes':[source['node_hash'],chunk['node_hash'],citation['node_hash']]})
artifact=hashed('decision-artifact',{'id':uid('SUNNY/western/method-packet/decision'),'kind':'constraint','title':'Keep source-conditioned reading and actual measurement scope separate','statement':'The Western packet records13passing scoped source/hash, exact parameter and instrument/receipt checks, with all audio measurements still unperformed. Preserve the native musical dimensions, source discrepancies and historical transfer gaps.','rationale':'Exact local review-record/span fidelity only. Confidence1 is not a historical, phonetic or mathematical truth probability; original source authenticity and full research completeness are outside this unsigned candidate package.','confidence':1.0,'valid_from':None,'valid_to':None,'transformation_node_hash':transform['node_hash'],'citation_node_hashes':[citation['node_hash']]})
now=datetime.now(timezone.utc).isoformat()
status=hashed('review-state',{'artifact_node_hash':artifact['node_hash'],'status':'candidate','created_at':now,'updated_at':now})
package={'manifest':{'schema':v.SCHEMA,'created_at':now,'app_version':'sunny-western-reactivation2','root_hash':v.envelope('package-root',{'artifact_node_hash':artifact['node_hash'],'review_node_hash':status['node_hash']})},'payload':{'source_version':source,'chunks':[chunk],'citations':[citation],'transformation':transform,'artifact':artifact,'review':status}}
write('proofline-package-02.json',package)
claims=[
 ('An official method tutorial has source-preserved count, endpoint and duplicate-time discrepancies; its conceptual method is retained while verbatim reproduction is deferred.',['method-audit.json','sources/praat_bada.html']),
 ('A context/subtradition-qualified Genesis1.1 Alef target and publisher-labelled modern reading pair are bound; no audio was decoded or measured.',['operational-constraint.json','paired-reading-access.json']),
 ('A corpus-specific glottal-event observation rubric transfers only conditionally; incomplete, prosodic, nonmarked and indeterminate alternatives remain.',['operational-constraint.json','source-register-02.json']),
 ('The14-question Western scholarly subregister accounts for7bounded,6partial and1open fields; it does not establish domain completion or a blind result.',['p0a-14-western.json','verification-02.json'])
]
records=[{'id':f'E-{i:03d}','claim':claim,'provenance':'RESEARCH_SUPPORTED_INFERENCE','confidence':1.0,'evidence_strength':0,'status':'active','source_refs':refs,'scope':'Literal packet-record fidelity only. These schema-required values do not weight sources or estimate scientific confidence. No direct participants or empirical generalization claimed.'} for i,(claim,refs) in enumerate(claims,501)]
write('mightshape-input-02.json',records)
results={}
for name,args in [
 ('proofline-result-02.json',[sys.executable,'-B',str(PLUGIN),'verify',str(ROOT/'proofline-package-02.json')]),
 ('mightshape-result-02.json',[sys.executable,'-B',str(MIGHT),str(ROOT/'mightshape-input-02.json')])
]:
 done=subprocess.run(args,capture_output=True,encoding='utf8',timeout=25)
 try:result=json.loads(done.stdout)
 except json.JSONDecodeError:result={'stdout':done.stdout,'stderr':done.stderr}
 write(name,{'exit_code':done.returncode,'result':result})
 results[name]={'exit_code':done.returncode,'result':result}
print(json.dumps(results,ensure_ascii=True))
if any(x['exit_code'] for x in results.values()):raise SystemExit(1)
