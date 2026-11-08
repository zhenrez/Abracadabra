"""Verify the supplied Exa text transport without network or PDF/ink claims."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib.util, json, re, uuid

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
TRANSPORT = ROOT / 'state/delivery-2026-11-07/history-discriminator/exa-loc-fetch.json'
LEDGER = Path('C:/Users/Brend/.codex/plugins/cache/created-by-me-remote/prumo-jev-research/0.1.1/skills/evidence-audit/scripts/evidence_ledger.py')
PROOF = Path('C:/Users/Brend/.codex/plugins/cache/openai-curated-remote/proofline/2.0.2/skills/manage-evidence-decisions/scripts/proofline_package.py')
URL = 'https://tile.loc.gov/storage-services/master/gdc/gdcebookspublic/20/19/39/45/70/2019394570/2019394570.pdf'
sha = lambda b: hashlib.sha256(b).hexdigest()
uid = lambda s: str(uuid.uuid5(uuid.NAMESPACE_URL, s))

def write(name, obj):
    (OUT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    raw = TRANSPORT.read_bytes()
    transport = json.loads(raw.decode('utf-8-sig'))
    assert transport['isError'] is False
    assert len(transport['content']) == 1 and transport['content'][0]['type'] == 'text'
    text = transport['content'][0]['text']
    text_raw = text.encode('utf-8')
    (OUT/'connector-content-text.txt').write_bytes(text_raw)
    chapter_start = text.index('BIBLICAL QUOTATIONS IN THE')
    chapter_end = text.index('PHONOLOGICAL ADAPTATION AND THE', chapter_start)
    chapter = text[chapter_start:chapter_end]
    spelling = 'שומורו'
    spelling_start = text.index(spelling, chapter_start, chapter_end)
    assert [spelling_start, spelling_start+len(spelling)] == [274601,274607]
    row_start = text.rfind('\n', 0, spelling_start)+1
    row_end = text.index('\n', spelling_start)
    row = text[row_start:row_end]
    bhs_raw = row.split(' BHS)')[0]
    bhs_letters = ''.join(c for c in bhs_raw if '\u05d0' <= c <= '\u05ea')
    assert bhs_letters == 'שמרו'
    secondary = 'שומרו'
    forms = {'published_connector_reading': spelling, 'earlier_secondary_discovery_lead': secondary, 'BHS_comparator_letters_normalized_from_fragmented_row': bhs_letters}
    counts = {k:{'text':v,'waw_count':v.count('ו'),'waw_codepoint_indices_zero_based':[i for i,c in enumerate(v) if c=='ו']} for k,v in forms.items()}
    assert [counts[k]['waw_count'] for k in forms] == [3,2,1]
    additions = [i for i,c in enumerate(spelling) if c=='ו' and spelling[:i]+spelling[i+1:] == secondary]
    assert spelling[0]+spelling[2]+spelling[4]+spelling[5] == bhs_letters
    assert spelling[1] == spelling[3] == 'ו'
    target_indices = [1,3]
    assert ''.join(c for i,c in enumerate(spelling) if i not in target_indices) == bhs_letters
    assert text.count('שומורו',chapter_start,chapter_end) == 1
    assert chapter.count('684.14') == 1
    bibliography_start = text.index('(HLIB) Shaked, Shaul. 1995.',chapter_start)
    bibliography_end = text.index('Yeivin Yisrael.',bibliography_start)
    intro_end = text.index('©',chapter_start)
    method_start = text.index('focus on orthographic features',chapter_start)
    method_end = text.index('9 That is,',method_start)
    pause_start = text.index('2.4. Evidence for the Prominence of Orality',chapter_start)
    pause_end = text.index('Similarly, the following form',pause_start)
    note_start = text.index('overview and evaluation of the existing research',pause_end)
    note_end = text.index('48 Yeivin',note_start)
    regions = [
        ('chapter_intro_and_general_dates',chapter_start,intro_end),
        ('method_and_assumptions',method_start,method_end),
        ('num_9_23_row',row_start,row_end),
        ('num_9_23_spelling',spelling_start,spelling_start+len(spelling)),
        ('pausal_and_phonetic_interpretation',pause_start,pause_end),
        ('footnote_46_continuation_and_47',note_start,note_end),
        ('HLIB_bibliography',bibliography_start,bibliography_end),
    ]
    audit = module('bowl_evidence_ledger',LEDGER)
    source = audit.init_source({'source_id':'molin-2020-LOC-Exa-content0', 'locator':str(TRANSPORT)+'#/content/0/text; upstream='+URL, 'text':text})['source']
    passages=[]
    records=[]
    for name,start,end in regions:
        span=[len(text[:start].encode('utf-16-le'))//2,len(text[:end].encode('utf-16-le'))//2]
        quote=text[start:end]
        result=audit.locate({'source':source,'objective':{'objective_id':'BOWL-TEXT-'+name,'question':'Does this exact selected source passage occur in the saved connector text?'},'quote':quote,'source_offsets_utf16':span})
        records.append(result['evidence'])
        passages.append({'id':name,'codepoint_span_half_open':[start,end],'utf16_span_half_open':span,'utf8_byte_span_half_open':[len(text[:start].encode('utf-8')),len(text[:end].encode('utf-8'))], 'original_text_lines_one_based':[text.count('\n',0,start)+1,text.count('\n',0,end-1)+1], 'text':quote,'sha256_utf8':sha(quote.encode('utf-8'))})
    verification=audit.validate({'source':source,'records':records})
    write('source-snapshot.json',source)
    write('evidence-passages.json',{'source_sha256_utf8':sha(text_raw),'passages':passages,'evidence_records':records})
    write('evidence-audit-validation.json',verification)
    record={
        'status':'PRIMARY_PUBLICATION_TEXT_ACQUIRED_AND_SPAN_VERIFIED',
        'source_layer':'Exa connector text rendering of LOC-hosted original publication, not original PDF bytes or independently inspected ink',
        'upstream_url':URL,
        'transport_path':str(TRANSPORT),'transport_sha256':sha(raw),'transport_bytes':len(raw),
        'text_json_pointer':'/content/0/text','text_sha256_utf8':sha(text_raw),'text_utf8_bytes':len(text_raw),'text_codepoints':len(text),'text_utf16_code_units':len(text.encode('utf-16-le'))//2,
        'normalization_applied_to_source_text':'none','source_pdf_sha256':None,'pdf_render_inspected':False,
        'chapter_codepoint_span_half_open':[chapter_start,chapter_end],
        'target_spelling_span': [spelling_start,spelling_start+len(spelling)],'raw_num_9_23_row':row,
        'BHS_raw_extracted_segment':bhs_raw,'BHS_normalization_rule':'retain only U+05D0..U+05EA Hebrew letters, dropping extraction spaces/combining signs; retain raw source separately',
        'counts':counts,
        'two_additions_relative_to_BHS':{'inserted_character':'ו','indices_in_published_reading_zero_based':target_indices,'after_base_letters':['ש','מ'],'final_waw_retained_from_BHS':True},
        'HLIB':{'author':'Shaul Shaked','year':1995,'title':'Peace be Upon You, Exalted Angels: On Hekhalot Liturgy and Incantation Bowls','journal':'Jewish Studies Quarterly','volume_issue':'2/3','pages':'197-219','citation_as_editorially_reordered_from_connector_row':'HLIB, 213; 684.14','page_213_verified_as_cited':True,'meaning_of_684_14':'UNRESOLVED: Molin chapter text supplies the locator but does not explicitly define its components; likely edition/bowl and line must be checked against the edition, not asserted as verified'},
        'published_inference':{'pausal_IPA_literal':'[ʃɔːˈmɔːruː]','contextual_IPA_literal':'[ʃɔːmaˈruː]','scope':'Molin interprets the two qames-corresponding vowel letters as a pausal reading and evidence for oral/liturgical transmission; these are published reconstructions, not acoustic observations.', 'footnote_46':'Refers to use of waw parallel to Tiberian qames in Hebrew and Aramaic bowls; overview/evaluation in Juusola1999 and Molin2017 pp17-22.', 'footnote_47':'Yeivin1985 p427; [a] denotes shewa.'},
        'dating':'Chapter reports positive evidence for bowl production in sixth/seventh centuries and proposes possible earlier beginning; no independently established date for this cited specimen acquired.',
        'source_page_mapping':'Target section identified by chapter and subsection; printed pp163-164 are the known citation target, but original PDF pagination/render was not independently checked.',
        'definition_search_scope':{'chapter_codepoint_span':[chapter_start,chapter_end],'684_14_occurrences':chapter.count('684.14'),'HLIB_occurrences':chapter.count('HLIB'),'explicit_numbering_definition_located':False},
        'guard_execution':{'evidence_audit_helper':str(LEDGER),'evidence_audit_helper_sha256':sha(LEDGER.read_bytes()),'validated_records':verification['validated_records'],'new_network_requests':0,'new_jev_inference':False},
        'remaining_discriminator':'Verify the edition locator and original letter readings/date, then test whether the qames-corresponding use belongs to broader chronology/phonology rather than a context-specific pausal, vernacular, or writing convention. This text alone cannot choose inheritance over contact/parallel change.'
    }
    write('primary-text-record.json',record)
    proof_result={'status':'UNAVAILABLE','reason':'Installed verifier not found','signed':False}
    if PROOF.exists():
        proof=module('bowl_proofline',PROOF)
        source_id=uid('SUNNY/LOC-Exa-content0');version_id=uid(sha(text_raw));parser='sunny-connector-exact-span-v1';stamp=datetime.now(timezone.utc).isoformat()
        def node(kind,obj):return {**obj,'node_hash':proof.node_hash(kind,obj)}
        src=node('source-version',{'workspace_id':uid(str(ROOT)),'source_id':source_id,'source_identity_sha256':sha(('source:'+source_id).encode()),'source_version_id':version_id,'version_number':1,'content':text,'content_sha256':sha(text_raw),'content_length':len(text),'parser_version':parser})
        chunk=node('chunk',{'id':uid(version_id+'/chunk'),'source_node_hash':src['node_hash'],'source_id':source_id,'source_version_id':version_id,'ordinal':0,'start_offset':0,'end_offset':len(text),'start_line':1,'end_line':proof.line_number(text,len(text)-1),'content':text,'content_sha256':sha(text_raw)})
        citation=node('citation',{'id':uid(version_id+'/citation'),'source_node_hash':src['node_hash'],'chunk_node_hashes':[chunk['node_hash']],'source_id':source_id,'source_version_id':version_id,'start_offset':spelling_start,'end_offset':spelling_start+len(spelling),'start_line':proof.line_number(text,spelling_start),'end_line':proof.line_number(text,spelling_start+len(spelling)-1),'quote':spelling,'quote_sha256':sha(spelling.encode('utf-8'))})
        transform=node('transformation',{'method':'deterministic','parser_version':parser,'model_runs':[],'input_node_hashes':[src['node_hash'],chunk['node_hash'],citation['node_hash']]})
        artifact=node('decision-artifact',{'id':uid('SUNNY/bowl/connector-readout'),'kind':'constraint','title':'Molin Num9:23 connector text spelling','statement':'The supplied primary-publication connector text contains the quoted spelling at the recorded span. This checks text fidelity, not original PDF/ink, ancient sound, date or historical truth.','rationale':'Confidence1means exact quoted-span fidelity only; no calibrated research confidence, signature or source authenticity claim.','confidence':1.0,'valid_from':None,'valid_to':None,'transformation_node_hash':transform['node_hash'],'citation_node_hashes':[citation['node_hash']]})
        review=node('review-state',{'artifact_node_hash':artifact['node_hash'],'status':'candidate','created_at':stamp,'updated_at':stamp})
        package={'manifest':{'schema':proof.SCHEMA,'created_at':stamp,'app_version':'SUNNY-bowl-primary-text-2026-11-07','root_hash':proof.envelope('package-root',{'artifact_node_hash':artifact['node_hash'],'review_node_hash':review['node_hash']})},'payload':{'source_version':src,'chunks':[chunk],'citations':[citation],'transformation':transform,'artifact':artifact,'review':review}}
        verified=proof.verify(package)
        write('proofline-package.json',package)
        proof_result={'status':'EXECUTED','verification':verified,'verifier_path':str(PROOF),'verifier_sha256':sha(PROOF.read_bytes()),'signed':False,'scope':'Exact connector-text span/package integrity; no PDF/ink, pronunciation or historical truth.'}
    write('proofline-validation.json',proof_result)
    assert verification['valid'] is True and verification['validated_records']==7
    summary={'status':'passed','text_sha256_utf8':sha(text_raw),'transport_sha256':sha(raw),'spelling_span':[spelling_start,spelling_start+len(spelling)],'waw_counts':[3,2,1],'evidence_records_validated':verification['validated_records'],'proofline':proof_result,'original_pdf_inspected':False,'edition_locator_expansion_verified':False}
    write('verification-summary.json',summary)
    print(json.dumps(summary,ensure_ascii=True,indent=2))

if __name__=='__main__':
    main()
