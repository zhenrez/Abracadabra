from pathlib import Path
import importlib.util,sys,hashlib,json,uuid,datetime,xml.etree.ElementTree as ET
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
WORKSPACE=ROOT.parents[3]
PLUGIN=Path('C:/Users/Brend/.codex/plugins/cache/openai-curated-remote/proofline/2.0.2/skills/manage-evidence-decisions/scripts/proofline_package.py')
spec=importlib.util.spec_from_file_location('symbols_proofline',PLUGIN);proof=importlib.util.module_from_spec(spec);spec.loader.exec_module(proof)
sha=lambda s:hashlib.sha256(s.encode('utf-8')).hexdigest()
uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,s))
def package(path,quote,statement,label,start_from=0):
 content=path.read_text(encoding='utf-8-sig');start=content.index(quote,start_from);end=start+len(quote);sid=uid(str(path));vid=uid(sha(content));parser='sunny-symbol-source-span-v1'
 def hashed(kind,obj):obj['node_hash']=proof.node_hash(kind,obj);return obj
 source=hashed('source-version',dict(workspace_id=uid(str(WORKSPACE)),source_id=sid,source_identity_sha256=sha('source:'+sid),source_version_id=vid,version_number=1,content=content,content_sha256=sha(content),content_length=len(content),parser_version=parser))
 chunk=hashed('chunk',dict(id=uid(vid+'/chunk'),source_node_hash=source['node_hash'],source_id=sid,source_version_id=vid,ordinal=0,start_offset=0,end_offset=len(content),start_line=1,end_line=proof.line_number(content,len(content)-1),content=content,content_sha256=sha(content)))
 citation=hashed('citation',dict(id=uid(vid+'/quote/'+str(start)),source_node_hash=source['node_hash'],chunk_node_hashes=[chunk['node_hash']],source_id=sid,source_version_id=vid,start_offset=start,end_offset=end,start_line=proof.line_number(content,start),end_line=proof.line_number(content,end-1),quote=quote,quote_sha256=sha(quote)))
 transform=hashed('transformation',dict(method='deterministic',parser_version=parser,model_runs=[],input_node_hashes=[source['node_hash'],chunk['node_hash'],citation['node_hash']]))
 artifact=hashed('decision-artifact',dict(id=uid('sunny/symbols/'+label),kind='constraint',title=label,statement=statement,rationale='Exact source-span fidelity only. Confidence1 is deterministic fidelity, not historical or phonetic certainty. Source is an edition or digitized text; no original glyph reading or waveform is certified.',confidence=1.0,valid_from=None,valid_to=None,transformation_node_hash=transform['node_hash'],citation_node_hashes=[citation['node_hash']]))
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();review=hashed('review-state',dict(artifact_node_hash=artifact['node_hash'],status='candidate',created_at=now,updated_at=now))
 data=dict(manifest=dict(schema=proof.SCHEMA,created_at=now,app_version='sunny-symbols-v1',root_hash=proof.envelope('package-root',dict(artifact_node_hash=artifact['node_hash'],review_node_hash=review['node_hash']))),payload=dict(source_version=source,chunks=[chunk],citations=[citation],transformation=transform,artifact=artifact,review=review))
 result=proof.verify(data);dest=ROOT/(label+'-proofline-package.json');dest.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');return dict(label=label,package=dest.name,source=str(path.relative_to(ROOT)),source_bytes_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),exact_span=[start,end],verification=result)
results=[]
results.append(package(ROOT/'sources/elephantine_A3_7_tei.xml','>עבר</rs>כי','The museum TEI contains resh in its normalized recto servant token.','A3-7-TEI-resh'))
results.append(package(ROOT/'sources/cal_A3_7.html','עבדכי','CAL contains dalet in its normalized servant token.','A3-7-CAL-dalet'))
text=(ROOT/'sources/cowley1923-text.txt').read_text(encoding='utf-8-sig');start=text.index('No.  39.')
results.append(package(ROOT/'sources/cowley1923-text.txt','is  no  date.','Cowley39 explicitly reports that the letter has no date; a later approximate composition estimate is distinct.','Cowley39-undated',start))
baseline=json.loads((ROOT/'p0a-14-baseline.json').read_text(encoding='utf-8'));mission=json.loads((WORKSPACE/'state/mission.json').read_text(encoding='utf-8-sig'))
exact=[(q['id'],q['question']) for q in mission['prior_art_research']['p0_a_questions']];observed=[(q['id'],q['question']) for q in baseline['questions']];assert exact==observed
hashes=[]
for file in ['source-fetch-manifest.json','source-fetch-extra-manifest.json','cal-fetch-manifest.json']:
 for r in json.loads((ROOT/file).read_text(encoding='utf-8')):
  if r.get('status')=='retrieved':
   actual=hashlib.sha256((ROOT/r['local_path']).read_bytes()).hexdigest();assert actual==r['sha256'];hashes.append(dict(id=r['id'],sha256=actual,matches=True))
facsimile=json.loads((ROOT/'sachau-facsimile-receipt.json').read_text(encoding='utf-8'));assert hashlib.sha256((ROOT/facsimile['original_local_path']).read_bytes()).hexdigest()==facsimile['member_sha256']
out=dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='passed',proofline_runtime_sha256=hashlib.sha256(PLUGIN.read_bytes()).hexdigest(),packages=results,source_hash_checks=hashes,original_facsimile_hash_matches=True,p0a_exact14_questions_match=True,scope='Source integrity, actual Proofline package verification and exact questionnaire fidelity; no independent palaeographic/phonetic/historical verdict.',protected_path_access='Installed plugin was read/executed; bytecode writes disabled. No plugin cache, credentials, user durable memory or shared task files were changed.')
(ROOT/'packet-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'status':out['status'],'proofline_packages':len(results),'source_hashes_checked':len(hashes),'p0a_exact14_questions_match':True},indent=2))
