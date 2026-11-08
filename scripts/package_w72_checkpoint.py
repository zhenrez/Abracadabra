"""Build a Proofline package for checkpoint text fidelity, not research truth."""
import copy
import importlib.util
import json
from pathlib import Path
import uuid
from datetime import datetime, timezone
import hashlib

root = Path(__file__).resolve().parents[1]
skill = Path('C:/Users/Brend/.codex/plugins/cache/openai-curated-remote/proofline/2.0.2/skills/manage-evidence-decisions')
spec = importlib.util.spec_from_file_location('proofline_package', skill/'scripts/proofline_package.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
p = copy.deepcopy(json.loads((skill/'references/fixtures/valid-minimal.json').read_text()) )
content = (root/'docs/reconstruction/W72_UPSTREAM_CHECKPOINT.md').read_text(encoding='utf-8')
quote = 'Ancient manuscript collation, Greek execution, independent historical coordinate mapping and held-out validation remain unfinished.'
start = content.index(quote)
end = start + len(quote)
source = p['payload']['source_version']
source_id = str(uuid.uuid5(uuid.NAMESPACE_URL, 'sunny:W72_UPSTREAM_CHECKPOINT'))
version_id = str(uuid.uuid5(uuid.NAMESPACE_URL, hashlib.sha256(content.encode()).hexdigest()))
source.update(source_id=source_id, source_version_id=version_id, source_identity_sha256=hashlib.sha256(f'source:{source_id}'.encode()).hexdigest(),content=content,content_length=len(content),content_sha256=hashlib.sha256(content.encode()).hexdigest())
source['node_hash'] = m.node_hash('source-version',source)
chunk = p['payload']['chunks'][0]
chunk.update(source_id=source_id,source_version_id=version_id,source_node_hash=source['node_hash'],content=content,content_sha256=source['content_sha256'],start_offset=0,end_offset=len(content),start_line=1,end_line=content.count('\n')+1,id=str(uuid.uuid5(uuid.NAMESPACE_URL,version_id+':chunk')))
chunk['end_line'] = m.line_number(content, len(content)-1)
chunk['node_hash'] = m.node_hash('chunk',chunk)
c = p['payload']['citations'][0]
c.update(source_id=source_id,source_version_id=version_id,source_node_hash=source['node_hash'],chunk_node_hashes=[chunk['node_hash']],quote=quote,quote_sha256=hashlib.sha256(quote.encode()).hexdigest(),start_offset=start,end_offset=end,start_line=content[:start].count('\n')+1,end_line=content[:end].count('\n')+1,id=str(uuid.uuid5(uuid.NAMESPACE_URL,version_id+':citation')))
c['node_hash'] = m.node_hash('citation',c)
t=p['payload']['transformation']
t.update(input_node_hashes=[source['node_hash'],chunk['node_hash'],c['node_hash']])
t['node_hash']=m.node_hash('transformation',t)
a=p['payload']['artifact']
a.update(id=str(uuid.uuid5(uuid.NAMESPACE_URL,version_id+':artifact')),title='W72 checkpoint limitation span',statement=quote,rationale='Confidence 1 means exact local span fidelity only; historical truth and completion are not assessed.',confidence=1.0,transformation_node_hash=t['node_hash'],citation_node_hashes=[c['node_hash']])
a['node_hash']=m.node_hash('decision-artifact',a)
r=p['payload']['review']
now=datetime.now(timezone.utc).isoformat()
r.update(artifact_node_hash=a['node_hash'],status='candidate',created_at=now,updated_at=now)
r['node_hash']=m.node_hash('review-state',r)
p['manifest'].update(created_at=now,app_version='sunny-w72-checkpoint-1',root_hash=m.envelope('package-root',{'artifact_node_hash':a['node_hash'],'review_node_hash':r['node_hash']}))
out=root/'state/research/w72-upstream/proofline-package.json'
out.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(str(out))
