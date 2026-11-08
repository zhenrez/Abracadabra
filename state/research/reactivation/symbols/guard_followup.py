from pathlib import Path
import importlib.util,sys,hashlib,json,uuid,datetime,pdfplumber
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
PLUGIN=Path('C:/Users/Brend/.codex/plugins/cache/openai-curated-remote/proofline/2.0.2/skills/manage-evidence-decisions/scripts/proofline_package.py')
spec=importlib.util.spec_from_file_location('symbols_followup_proofline',PLUGIN);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
digest=lambda s:hashlib.sha256(s.encode('utf-8')).hexdigest()
uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,s))
def make_package(path,quote,label,statement,start_from=0):
 content=path.read_text(encoding='utf-8-sig');start=content.index(quote,start_from);end=start+len(quote);sid=uid(str(path));vid=uid(digest(content));parser='sunny-symbol-source-span-v2'
 def hashed(kind,obj):obj['node_hash']=v.node_hash(kind,obj);return obj
 source=hashed('source-version',dict(workspace_id=uid(str(ROOT.parents[3])),source_id=sid,source_identity_sha256=digest('source:'+sid),source_version_id=vid,version_number=1,content=content,content_sha256=digest(content),content_length=len(content),parser_version=parser))
 chunk=hashed('chunk',dict(id=uid(vid+'/chunk'),source_node_hash=source['node_hash'],source_id=sid,source_version_id=vid,ordinal=0,start_offset=0,end_offset=len(content),start_line=1,end_line=v.line_number(content,len(content)-1),content=content,content_sha256=digest(content)))
 citation=hashed('citation',dict(id=uid(vid+'/'+label),source_node_hash=source['node_hash'],chunk_node_hashes=[chunk['node_hash']],source_id=sid,source_version_id=vid,start_offset=start,end_offset=end,start_line=v.line_number(content,start),end_line=v.line_number(content,end-1),quote=quote,quote_sha256=digest(quote)))
 transform=hashed('transformation',dict(method='deterministic',parser_version=parser,model_runs=[],input_node_hashes=[source['node_hash'],chunk['node_hash'],citation['node_hash']]))
 artifact=hashed('decision-artifact',dict(id=uid('sunny/symbols/'+label),kind='constraint',title=label,statement=statement,rationale='Exact text-span fidelity to the identified source/extraction only. Confidence1 is not historical or phonetic confidence. Photographs and original printed pages remain separate graphic evidence; interpretive alternatives remain open.',confidence=1.0,valid_from=None,valid_to=None,transformation_node_hash=transform['node_hash'],citation_node_hashes=[citation['node_hash']]))
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();review=hashed('review-state',dict(artifact_node_hash=artifact['node_hash'],status='candidate',created_at=now,updated_at=now))
 package=dict(manifest=dict(schema=v.SCHEMA,created_at=now,app_version='sunny-symbols-followup-v1',root_hash=v.envelope('package-root',dict(artifact_node_hash=artifact['node_hash'],review_node_hash=review['node_hash']))),payload=dict(source_version=source,chunks=[chunk],citations=[citation],transformation=transform,artifact=artifact,review=review))
 result=v.verify(package);(ROOT/(label+'-proofline-package.json')).write_text(json.dumps(package,ensure_ascii=False,indent=2),encoding='utf-8');return dict(label=label,source=str(path.relative_to(ROOT)),span=[start,end],verification=result)
pdfpath=ROOT/'sources/khan2020.pdf';original_sha=hashlib.sha256(pdfpath.read_bytes()).hexdigest();assert original_sha=='bcab644037f62795041c3c6e6e37f1c1eb28f29d147b6d2c4409fd6bc3c0da24'
saved=json.loads((ROOT/'sources/khan-alef-operation-pages.json').read_text(encoding='utf-8'));pdf=pdfplumber.open(pdfpath)
for p in saved:assert p['text']==pdf.pages[p['pdf_page']-1].extract_text()
content='Original PDF SHA256: '+original_sha+'\n'+'\n'.join('Printed page '+str(p['printed_page'])+'; PDF page '+str(p['pdf_page'])+'\n'+p['text'] for p in saved)
extracted=ROOT/'sources/khan-alef-operation-extract.txt';extracted.write_text(content,encoding='utf-8')
cowley=ROOT/'sources/cowley1923-text.txt';start=cowley.read_text(encoding='utf-8').index('No.  39.')
results=[make_package(cowley,'was  not  a  slave.','Cowley39-polite-address','Cowley interprets the servant expression as polite address rather than literal slavery.',start),make_package(extracted,'equivalent to a mappiq','Khan-alef-competing-reading','Khan reports the consonantal-only/mappiq interpretation as a competing reading.'),make_package(extracted,'BL Or 2552 fol. 51r, 1','Khan-alef-manuscript-locus','Khan identifies the Arabic-script manuscript locus used in the gemination argument.'),make_package(extracted,'for a longer duration.','Khan-alef-articulation-duration','Khan allows longer laryngeal articulation; this phrase supplies no fixed numeric duration or frequency.')]
newhashes=[]
for receiptfile in ['cowley39-printed-page-receipt.json','sachau-facsimile-receipt.json']:
 r=json.loads((ROOT/receiptfile).read_text(encoding='utf-8'));actual=hashlib.sha256((ROOT/r['original_local_path']).read_bytes()).hexdigest();assert actual==r['member_sha256'];newhashes.append({'receipt':receiptfile,'member_sha256':actual,'matches':True})
sheet=json.loads((ROOT/'collation-sheet.json').read_text(encoding='utf-8'));from PIL import Image
base=Image.open(ROOT/sheet['base']['reading_image'])
for region in sheet['regions']:
 crop=Image.open(ROOT/region['file']);assert crop.size==base.crop(tuple(region['box'])).size;assert crop.tobytes()==base.crop(tuple(region['box'])).tobytes()
out={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'passed','actual_proofline_packages':results,'original_source_hash_checks':newhashes,'pdf_extraction_pages_exact':len(saved),'pdf_sha256':original_sha,'crop_pixel_bindings_exact':len(sheet['regions']),'scope':'Actual Proofline exact-span checks, source byte hashes and exact reading-crop pixels. No independent glyph identity, historical pronunciation, empirical duration result or global musical proof.'}
(ROOT/'followup-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'status':'passed','proofline_packages':len(results),'pdf_pages':len(saved),'crop_regions':len(sheet['regions'])},indent=2))
