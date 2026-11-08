import hashlib,json,pathlib,subprocess,sys
root=pathlib.Path('.')
base=root/'state/delivery-2026-11-07/pausal-operations/prosody'
source_path=root/'state/delivery-2026-11-07/history-discriminator/exa-loc-fetch.json'
original_bytes=source_path.read_bytes()
t=json.loads(original_bytes.decode('utf-8-sig'))['content'][0]['text']
(base/'source-rendering.utf8.txt').write_bytes(t.encode('utf-8'))
lines=t.splitlines(keepends=True)
starts=[0]
for line in lines: starts.append(starts[-1]+len(line))
def span(a,b):
    lo,hi=starts[a-1],starts[b]
    selected=t[lo:hi]
    return {'source_lines_one_based':[a,b],'source_offsets_codepoints_half_open':[lo,hi],'source_offsets_utf16_half_open':[len(t[:lo].encode('utf-16-le'))//2,len(t[:hi].encode('utf-16-le'))//2],'region_sha256_utf8':hashlib.sha256(selected.encode('utf-8')).hexdigest(),'coordinate_target':'source-rendering.utf8.txt; Exa tool text rendering, not PDF byte coordinates'}
regions=[
('P1','accent_not_sufficient',7243,7253,'Authors endorse prior fixing of pausal forms and deny prediction from written accents alone.'),
('P2','native_hierarchy',7298,7338,'Source contrasts I and P with ranked TH disjunctives; equates minimal phrase MP with P, not I.'),
('P3','minimal_phrase_operations',7342,7344,'MP is the domain of spirantization, external gemination/dehiq and rhythmic stress retraction/nesiga; Judg1:8 contrasts initial b within/across MP.'),
('P4','division_simplification',7377,7381,'Source-proposed division splits MPs in prominent higher domains; simplification merges MPs and changes realized disjunctive to conjunctive in subordinate domains, with system-specific conditions.'),
('P5','same_zaqef_different_form',7448,7479,'Gen43:25 heard before direct-object ki is contextual/P; Judg2:17 heard before adjunct ki is pausal/I. Both have D1zaqef. I assignment also depends on non-syntactic factors.'),
('P6','morphological_operations',7485,7534,'Table10 supplies multiple vowel/stress alternation types and historical proposals; pause need not shift stress in one direction. Table glyph/transcription order is damaged in this rendering.'),
('P7','same_form_different_rank',7615,7650,'Pausal and-he-slaughtered is analyzed as initial word-sentence/I in Lev8:19(D0atnah),8:23(D1salselet),8:15(D2revia). Lev9 contextual forms have overt objects.'),
('P8','candidate_filter_and_exceptions',7651,7689,'Apparent pausal morphology can be plural rather than singular; some claimed I contexts are questionable; fixed pausal idioms and genuine reading clashes remain possible.'),
('P9','deuteronomy_conjunctive',7691,7761,'Deut5:14 daughter remains pausal on Cmunah; authors explain via left-branching list,D3depth saturation,simplification. They explicitly do not call the reconstructed transformation inevitable under their conservative cliticization assumption.'),
('P10','grouping_changes',7762,7794,'Different number of listed animal items changes grouping of servants between Deut5:14 and Exod20:10; proposed grouping-by-twos/threes account avoids requiring a social-history explanation.'),
('P11','poetic_conjunctive_and_lexical_limit',7795,7838,'Ps3:9 blessing is pausal with conjunctivemunah before selah; obligatory revia-mugras simplification proposed. Ps32:4 contextual summer before selah blocks universal before-selah pause; wordclass sensitivity is offered as another explanation.'),
('P12','historical_conclusion_limits',7840,7889,'Authors infer vocalization predates accent melody but do not exclude distinct-reading scenarios; accent mismatch alone cannot decide the history.')]
evidence=[{'id':i,'topic':topic,'assessment':'SOURCE_PROPOSED_ANALYSIS','summary':summary,**span(a,b)} for i,topic,a,b,summary in regions]
(base/'chapter-main-text.utf8.txt').write_bytes(t[starts[7204]:starts[7890]].encode('utf-8'))
quotes=[('Q1','cannot be predicted from the accents.',7249,7250),('Q2','not entirely determined',7473,7474),('Q3','virtual disjunctives',7803,7808)]
helper=pathlib.Path('C:/Users/Brend/.codex/plugins/cache/created-by-me-remote/prumo-jev-research/0.1.1/skills/evidence-audit/scripts/evidence_ledger.py')
plugin_checks={'tool':'installed Prumo+JevResearch evidence_ledger.py','execution':[]}
try:
    p=subprocess.run([sys.executable,str(helper),'init-source'],input=json.dumps({'source_id':'DECAEN-DRESHER2020-EXA-RENDERING','locator':'https://tile.loc.gov/storage-services/master/gdc/gdcebookspublic/20/19/39/45/70/2019394570/2019394570.pdf ; content[0].text rendering','text':t},ensure_ascii=False),text=True,encoding='utf-8',capture_output=True,timeout=25)
    init=json.loads(p.stdout)
    (base/'plugin-source.json').write_text(json.dumps(init,ensure_ascii=False,indent=2),encoding='utf-8')
    source=init['source']
    records=[]
    for qid,quote,a,b in quotes:
        scope=span(a,b)['source_offsets_utf16_half_open']
        request={'source':source,'objective':{'objective_id':qid,'question':'Verify exact wording in inspected chapter source range.'},'quote':quote,'search_ranges_utf16':[scope]}
        p=subprocess.run([sys.executable,str(helper),'locate'],input=json.dumps(request,ensure_ascii=False),text=True,encoding='utf-8',capture_output=True,timeout=25)
        out=json.loads(p.stdout)
        (base/(qid+'-locate.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
        plugin_checks['execution'].append({'operation':'locate','quote_id':qid,'exit_code':p.returncode,'result_keys':list(out)})
        records.append(out['evidence'])
    p=subprocess.run([sys.executable,str(helper),'validate'],input=json.dumps({'source':source,'records':records},ensure_ascii=False),text=True,encoding='utf-8',capture_output=True,timeout=25)
    out=json.loads(p.stdout)
    (base/'plugin-validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    plugin_checks['execution'].append({'operation':'validate','exit_code':p.returncode,'result':out})
except Exception as ex:
    plugin_checks['error']={'type':type(ex).__name__,'message':str(ex)}
rows=[
{'id':'ZAQEF-1','locus':'Gen43:25','lexeme':'hear','form':'contextual','written_accent':'D1zaqef','source_proposed_domain':'P','conditioning':'verb before direct-object clause headed by ki=that','evidence_id':'P5'},
{'id':'ZAQEF-2','locus':'Judg2:17','lexeme':'hear','form':'pausal','written_accent':'D1zaqef','source_proposed_domain':'I','conditioning':'verb before adjunct clause headed by ki=but','evidence_id':'P5'},
{'id':'LEV-1','locus':'Lev8:19','lexeme':'and he slaughtered','form':'pausal','written_accent':'D0atnah','source_proposed_domain':'I','conditioning':'initial word-sentence; first half-verse ends here','evidence_id':'P7'},
{'id':'LEV-2','locus':'Lev8:23','lexeme':'and he slaughtered','form':'pausal','written_accent':'D1salselet','source_proposed_domain':'I','conditioning':'additional verse material demotes accent rank under continuous dichotomy','evidence_id':'P7'},
{'id':'LEV-3','locus':'Lev8:15','lexeme':'and he slaughtered','form':'pausal','written_accent':'D2revia','source_proposed_domain':'I','conditioning':'further verse material demotes accent rank again','evidence_id':'P7'},
{'id':'LEV-CONTEXT','locus':['Lev9:8','Lev9:12','Lev9:18'],'lexeme':'and he slaughtered','form':'contextual','written_accent':'not independently transcribed in this ledger','source_proposed_domain':'does not end I','conditioning':'verb takes overt object; not an independent word-sentence','evidence_id':'P7'},
{'id':'DEUT-CONJ','locus':'Deut5:14','lexeme':'your daughter','form':'pausal','written_accent':'Cmunah','source_proposed_domain':'I before simplification','conditioning':'list grouping and subordinateD3 transformation; reconstruction not asserted inevitable','evidence_id':'P9'},
{'id':'PS-CONJ','locus':'Ps3:9','lexeme':'your blessing','form':'pausal','written_accent':'Cmunah','source_proposed_domain':'I','conditioning':'before selah; writtenC explained by obligatory poetic revia-mugras transformation','evidence_id':'P11'},
{'id':'PS-SELAH-COUNTER','locus':'Ps32:4','lexeme':'summer','form':'contextual','written_accent':'not independently transcribed in this ledger','source_proposed_domain':'unresolved alternative analysis','conditioning':'before selah; either no I required or morphology-specific susceptibility differs','evidence_id':'P11'}]
for row in rows: row['status']='PUBLISHED_SOURCE_ANALYSIS; NOT_NEW_MANUSCRIPT_COLLATION'
result={'schema':'sunny.pausal_prosody.prior_art.v1','status':'BOUNDED_SOURCE_REUSE_COMPLETE; GLOBAL_RESEARCH_OPEN','source':{'authors':['Vincent DeCaen','B.ElanDresher'],'chapter':'Pausal Forms and Prosodic Structure in Tiberian Hebrew','year':2020,'start_printed_page':331,'inspected_sections':['1','2','3','4.1','4.2','5'],'container':'Studies in Semitic Vocalisation and Reading Traditions','container_doi':'10.11647/OBP.0207','rendering_url':'https://tile.loc.gov/storage-services/master/gdc/gdcebookspublic/20/19/39/45/70/2019394570/2019394570.pdf','acquisition':'already acquired Exa content[0].text','original_json_sha256':hashlib.sha256(original_bytes).hexdigest(),'rendering_sha256_utf8':hashlib.sha256(t.encode('utf-8')).hexdigest(),'chapter_main_text_sha256_utf8':hashlib.sha256((base/'chapter-main-text.utf8.txt').read_bytes()).hexdigest(),'original_pdf_hash':None,'images_and_tree_figures_inspected':False,'rendering_limit':'Hebrew order, table IPA and tree figures partly damaged/absent; no corrected glyphs or exact tree geometry fabricated'},'actual_plugin_use':{'supermemory':'search_memory succeeded this phase; general continuity only','conversation_id':'01a1b7ef-ccb2-7de9-9308-cf4ce4c46128','evidence_guard':plugin_checks,'jev':{'receipt':'state/jev-receipts/000062-5fcc72f3ccd7.json','model':'AgentJev-0.6B','checkpoint':'agentjev-v1','selected':'molin_pausal_operation_and_source','top_probability':0.40687549114227295,'margin':0.09827455878257751,'new_inference_in_this_subtask':False}},'evidence':evidence,'native_domains':{'W':'prosodic word including clitic group','P_or_MP':'minimal/phonological phrase; domain for spirantization,dehiq,nesiga','I':'intonational phrase; source-proposed pausal-form domain, not separately encoded by TH accent ranks','V':'verse taken as given in source analysis','TH_accents':'relative hierarchyD0-D3 with conjunctives; distinct prose and poetic transformation conditions'},'source_native_operations':[{'operation':'cliticization','condition':'maqqef joins grammatical words to one prosodic word; native evidence required','evidence_id':'P2'},{'operation':'division','condition':'MP split in prominent upper prosodic positions; slower reading','evidence_id':'P4'},{'operation':'simplification','condition':'MPs merged and disjunctive realized as conjunctive under native rank/adjacency constraints; prose and poetic systems differ','evidence_id':'P4'},{'operation':'contextual_pausal_alternation','condition':'form-class-dependent vowel/stress correspondence at proposedI edge; no universal stress-direction or qames transform','evidence_id':'P6'}],'counterexamples':rows,'operator_inputs_required':['source tradition','specific witness','lexical and morphological form-class','written accent with full verse hierarchy','prosodic-word/clitic grouping','candidateI/P segmentation','syntax/semantic relation','rhythmic/list context','exception status'],'prior_art_fit':{'P0-A':'Reuse published native domains, transformations and explicit counterexamples before designing a new mapping; this is applicable primary-source prior art for context-sensitive operations. It is not completion of the full P0-A fourteen-question program.','strong_falsified_shortcut':'pausal form determined by accent label alone','retained_competitor':'genuine historical reading clashes or scribal lapses are not excluded by authors','unresolved_native_items':['minor pause excluded by chapter','full token-level lexical/morphological census not run','hypothesized latentI/P boundaries are analyses, not measured natural intonation','independent manuscripts/figures not collated']},'transfer_limits':['Tiberian accent conditions are not automatically conditions in Babylonian bowl transmission.','Molin proposed pausal/contextual readings can be represented as separate candidate forms, but the bowl context needs independently supported native prosodic evidence.','Written waw pattern alone does not establish anI boundary or license a Tiberian vowel/stress operation.','Do not infer inherited sound change/contact/acoustics from accent mismatch; no ancient Hz/duration recovered.','Do not read table10 IPA as clean original glyph data: this extraction contains damaged ordering.'],'canonical_or_ui_edits':False}
(base/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'result_written':True,'evidence_regions':len(evidence),'counterexample_rows':len(rows),'plugin_checks':plugin_checks,'source_hash':result['source']['rendering_sha256_utf8']},ensure_ascii=False,indent=2))
