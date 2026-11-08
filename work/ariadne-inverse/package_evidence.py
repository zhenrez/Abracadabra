"""Bind an exact local limitation span using installed Proofline primitives."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json,sys,uuid
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
plugin=Path('C:/Users/Brend/.codex/plugins/cache/openai-curated-remote/proofline/2.0.2/skills/manage-evidence-decisions/scripts/proofline_package.py')
spec=importlib.util.spec_from_file_location('proofline_package',plugin)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
content=(ROOT/'README.md').read_text(encoding='utf-8')
sha=lambda s:hashlib.sha256(s.encode('utf-8')).hexdigest()
uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,s))
def hashed(kind,obj):obj['node_hash']=m.node_hash(kind,obj);return obj
sid=uid('SUN/ARIADNE/inverse-prototype/README');vid=uid(sha(content));parser='ariadne-exact-span-v1'
source=hashed('source-version',dict(workspace_id=uid('SUN/ARIADNE'),source_id=sid,source_identity_sha256=sha('source:'+sid),source_version_id=vid,version_number=1,content=content,content_sha256=sha(content),content_length=len(content),parser_version=parser))
chunk=hashed('chunk',dict(id=uid(vid+'/chunk'),source_node_hash=source['node_hash'],source_id=sid,source_version_id=vid,ordinal=0,start_offset=0,end_offset=len(content),start_line=1,end_line=m.line_number(content,len(content)-1),content=content,content_sha256=sha(content)))
quote='No joint MDL search, learned historical transition system, independent historical holdout or acoustic validation ran.'
start=content.index(quote);end=start+len(quote)
citation=hashed('citation',dict(id=uid(vid+'/citation'),source_node_hash=source['node_hash'],chunk_node_hashes=[chunk['node_hash']],source_id=sid,source_version_id=vid,start_offset=start,end_offset=end,start_line=m.line_number(content,start),end_line=m.line_number(content,end-1),quote=quote,quote_sha256=sha(quote)))
transformation=hashed('transformation',dict(method='deterministic',parser_version=parser,model_runs=[],input_node_hashes=[source['node_hash'],chunk['node_hash'],citation['node_hash']]))
artifact=hashed('decision-artifact',dict(id=uid(vid+'/artifact'),kind='constraint',title='ARIADNE inverse prototype evidence boundary',statement=quote,rationale='Confidence 1 denotes exact local span fidelity only; not scientific truth, independent review or model approval.',confidence=1.0,valid_from=None,valid_to=None,transformation_node_hash=transformation['node_hash'],citation_node_hashes=[citation['node_hash']]))
now=datetime.now(timezone.utc).isoformat()
review=hashed('review-state',dict(artifact_node_hash=artifact['node_hash'],status='candidate',created_at=now,updated_at=now))
package=dict(manifest=dict(schema=m.SCHEMA,created_at=now,app_version='ariadne-prototype1',root_hash=m.envelope('package-root',dict(artifact_node_hash=artifact['node_hash'],review_node_hash=review['node_hash']))),payload=dict(source_version=source,chunks=[chunk],citations=[citation],transformation=transformation,artifact=artifact,review=review))
result=m.verify(package)
(ROOT/'proofline-package.json').write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
