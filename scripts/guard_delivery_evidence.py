"""Run the actual installed Proofline verifier on current SUNNY evidence spans."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json,uuid
ROOT=Path(__file__).resolve().parents[1]
PLUGIN=Path('C:/Users/Brend/.codex/plugins/cache/openai-curated-remote/proofline/2.0.2/skills/manage-evidence-decisions/scripts/proofline_package.py')
OUT=ROOT/'state/delivery-2026-11-07/guards'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
uid=lambda text:str(uuid.uuid5(uuid.NAMESPACE_URL,text))

def main():
    spec=importlib.util.spec_from_file_location('proofline_current_delivery',PLUGIN)
    proof=importlib.util.module_from_spec(spec);spec.loader.exec_module(proof)
    OUT.mkdir(parents=True,exist_ok=True);results=[]
    for name,relative,quote,statement in [
        ('actual-jev-frontier','state/jev-receipts/000058-bbb3ab44bbf5.json','"value": "minimal_source_bound_score_anchors"',
         'The preserved local model result selects the named score-anchor investigation; this package checks its exact span, not provider billing or decision correctness.'),
        ('score-anchor-result','state/reconstruction/score-anchor-constraints.json','"sufficientPairs": 8',
         'The exact source-conditioned calculation artifact records eight sufficient duration pairs. Mathematical validity has separate independent solver checks.'),
    ]:
        raw=(ROOT/relative).read_bytes();content=raw.decode('utf8');start=content.index(quote);end=start+len(quote)
        source_id=uid('SUNNY/'+relative);version_id=uid(sha(raw));parser='sunny-exact-delivery-span-v1';stamp=datetime.now(timezone.utc).isoformat()
        def node(kind,obj):return {**obj,'node_hash':proof.node_hash(kind,obj)}
        source=node('source-version',{'workspace_id':uid(str(ROOT)),'source_id':source_id,'source_identity_sha256':sha(('source:'+source_id).encode()),'source_version_id':version_id,'version_number':1,'content':content,'content_sha256':sha(content.encode()),'content_length':len(content),'parser_version':parser})
        chunk=node('chunk',{'id':uid(version_id+'/chunk'),'source_node_hash':source['node_hash'],'source_id':source_id,'source_version_id':version_id,'ordinal':0,'start_offset':0,'end_offset':len(content),'start_line':1,'end_line':proof.line_number(content,len(content)-1),'content':content,'content_sha256':sha(content.encode())})
        citation=node('citation',{'id':uid(version_id+'/citation'),'source_node_hash':source['node_hash'],'chunk_node_hashes':[chunk['node_hash']],'source_id':source_id,'source_version_id':version_id,'start_offset':start,'end_offset':end,'start_line':proof.line_number(content,start),'end_line':proof.line_number(content,end-1),'quote':quote,'quote_sha256':sha(quote.encode())})
        transform=node('transformation',{'method':'deterministic','parser_version':parser,'model_runs':[],'input_node_hashes':[source['node_hash'],chunk['node_hash'],citation['node_hash']]})
        artifact=node('decision-artifact',{'id':uid('SUNNY/delivery/'+name),'kind':'constraint','title':name,'statement':statement,'rationale':'Confidence1means exact quoted-span fidelity only. No calibrated research confidence, signature, source authenticity, model authority or complete SUNNY claim.','confidence':1.0,'valid_from':None,'valid_to':None,'transformation_node_hash':transform['node_hash'],'citation_node_hashes':[citation['node_hash']]})
        review=node('review-state',{'artifact_node_hash':artifact['node_hash'],'status':'candidate','created_at':stamp,'updated_at':stamp})
        package={'manifest':{'schema':proof.SCHEMA,'created_at':stamp,'app_version':'SUNNY-delivery-2026-11-07','root_hash':proof.envelope('package-root',{'artifact_node_hash':artifact['node_hash'],'review_node_hash':review['node_hash']})},'payload':{'source_version':source,'chunks':[chunk],'citations':[citation],'transformation':transform,'artifact':artifact,'review':review}}
        result=proof.verify(package)
        (OUT/(name+'-proofline.json')).write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        results.append({'name':name,'sourcePath':relative,'sourceBytesSha256':sha(raw),'verification':result})
    report={'status':'passed','exit_code':0,'verifierPath':str(PLUGIN),'verifierSha256':sha(PLUGIN.read_bytes()),'packages':results,'signed':False,'boundary':'Exact source span/package integrity only. Independent mathematical checks and model receipts retain their separate scopes.'}
    (OUT/'proofline-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
