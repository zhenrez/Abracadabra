"""Create one exact-span decision package; no signature or truth certification."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json,sys,uuid
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
plugin=Path('C:/Users/Brend/.codex/plugins/cache/openai-curated-remote/proofline/2.0.2/skills/manage-evidence-decisions/scripts/proofline_package.py')
spec=importlib.util.spec_from_file_location('proofline_final_day',plugin)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
content=(ROOT/'CHECKPOINT.md').read_text(encoding='utf-8')
digest=lambda s:hashlib.sha256(s.encode('utf-8')).hexdigest()
uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,s))
def hashed(kind,value):value['node_hash']=module.node_hash(kind,value);return value
sid=uid('SUN/final-day/CHECKPOINT');vid=uid(digest(content));parser='final-day-exact-span-v1'
source=hashed('source-version',dict(workspace_id=uid('SUN/final-day'),source_id=sid,source_identity_sha256=digest('source:'+sid),
    source_version_id=vid,version_number=1,content=content,content_sha256=digest(content),content_length=len(content),parser_version=parser))
chunk=hashed('chunk',dict(id=uid(vid+'/chunk'),source_node_hash=source['node_hash'],source_id=sid,source_version_id=vid,ordinal=0,
    start_offset=0,end_offset=len(content),start_line=1,end_line=module.line_number(content,len(content)-1),content=content,content_sha256=digest(content)))
quote='Historical reconstruction remains locked; native mathematical checks are not historical certification.'
start=content.index(quote);end=start+len(quote)
citation=hashed('citation',dict(id=uid(vid+'/citation'),source_node_hash=source['node_hash'],chunk_node_hashes=[chunk['node_hash']],
    source_id=sid,source_version_id=vid,start_offset=start,end_offset=end,start_line=module.line_number(content,start),
    end_line=module.line_number(content,end-1),quote=quote,quote_sha256=digest(quote)))
transformation=hashed('transformation',dict(method='deterministic',parser_version=parser,model_runs=[],
    input_node_hashes=[source['node_hash'],chunk['node_hash'],citation['node_hash']]))
artifact=hashed('decision-artifact',dict(id=uid(vid+'/artifact'),kind='constraint',title='Historical certification boundary',statement=quote,
    rationale='Confidence1 measures exact local span fidelity only. Source integrity does not establish historical truth or completion.',confidence=1.0,
    valid_from=None,valid_to=None,transformation_node_hash=transformation['node_hash'],citation_node_hashes=[citation['node_hash']]))
now=datetime.now(timezone.utc).isoformat();review=hashed('review-state',dict(artifact_node_hash=artifact['node_hash'],status='candidate',created_at=now,updated_at=now))
package={'manifest':dict(schema=module.SCHEMA,created_at=now,app_version='SUN-final-day-v1',
    root_hash=module.envelope('package-root',dict(artifact_node_hash=artifact['node_hash'],review_node_hash=review['node_hash']))),
    'payload':dict(source_version=source,chunks=[chunk],citations=[citation],transformation=transformation,artifact=artifact,review=review)}
result=module.verify(package)
for name,value in [('proofline-package.json',package),('proofline-verification.json',result)]:
    (ROOT/'capability-receipts'/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
