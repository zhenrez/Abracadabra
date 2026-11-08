"""Finalize the already-returned bounded retrieval; no network operations."""
from pathlib import Path
import hashlib, importlib.util, json

ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
HELPER=Path('C:/Users/Brend/.codex/plugins/cache/created-by-me-remote/prumo-jev-research/0.1.1/skills/evidence-audit/scripts/evidence_ledger.py')
sha=lambda b:hashlib.sha256(b).hexdigest()

def write(name,obj):
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    raw=(OUT/'known-url-fetches.json').read_bytes()
    fetched=json.loads(raw.decode('utf-8-sig'))
    assert fetched['isError'] is False
    text=fetched['content'][0]['text']
    assert len(fetched['content'])==1
    (OUT/'fetched-content.txt').write_bytes(text.encode('utf-8'))
    spec=importlib.util.spec_from_file_location('shaked_audit',HELPER)
    audit=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    source=audit.init_source({'source_id':'shaked-two-URL-Exa-delivered-text','locator':str(OUT/'known-url-fetches.json')+'#/content/0/text','text':text})['source']
    records=[]
    for query in ['684.14','שומורו','213']:
        records.append(audit.locate({'source':source,'objective':{'objective_id':'SHAKED-'+query,'question':'Is the exact literal present in this delivered connector text?'},'quote':query})['evidence'])
    valid=audit.validate({'source':source,'records':records})
    assert valid['valid'] and valid['validated_records']==3
    write('source-snapshot.json',source)
    write('evidence-audit.json',{'records':records,'validation':valid,'helper_path':str(HELPER),'helper_sha256':sha(HELPER.read_bytes()),'boundary':'Literal search and snapshot consistency only; not_located applies to delivered text, not original article.'})
    result={
        'status':'BOUNDED_ACQUISITION_COMPLETE_TARGET_NOT_RETRIEVED',
        'target':{'author':'Shaul Shaked','publication_year':1995,'title':'Peace be Upon You, Exalted Angels: On Hekhalot, Liturgy and Incantation Bowls','journal':'Jewish Studies Quarterly','volume_issue':'2/3','page_range':'197-219','Molin_citation':'HLIB, 213; 684.14'},
        'direction':{'receipt':'state/jev-receipts/000062-5fcc72f3ccd7.json','selected':'molin_pausal_operation_and_source','new_Jev_inference_by_this_reader':False},
        'budget':{'primary_discovery_queries_used':2,'known_URLs_fetched':2,'fetch_calls':1,'retries':0,'additional_routes_after_budget':0},
        'fetched_URLs':['https://jstor.org/stable/40753131','https://www.academia.edu/38730945/Shaul_Shaked_Peace_Be_upon_You_Exalted_Angels_On_Hekhalot_Liturgy_and_Incantation_Bowls_Jewish_Studies_Quarterly_2_3_1995_197_219'],
        'delivered_layers':[
            'JSTOR-associated metadata, abstract-like opening paragraph and reference list; primary provenance of the opening block was not independently checked against a scan.',
            'Article-labelled Academia upload record with AI-marked abstract/key takeaways/FAQ and OCR-like bibliography fragments; no target page body.',
            'Bibliography rendering includes a fragment resembling a printed page219 header; it does not deliver page213 or define684.14.'
        ],
        'excluded_from_primary_witness_evidence':[
            'AcademiaAI abstract, key takeaways and FAQ.',
            'AI-summary mention of Bowl6/Moussaieff: correspondence to684.14 is not established.',
            'Connector indexing/enrichment metadata such as citation counts, topics and2016year.',
            'The2019upload date and2025last-update label as publication/specimen dates.'
        ],
        'index_year_discrepancy':{'JSTOR_associated_rendering_Published':'2016-01-01','Molin_bibliography_and_article_label_year':1995,'resolution':'Keep2016as conflicting indexing metadata; it does not supersede1995publication identification.'},
        'original_article_target_body_acquired':False,'printed_page213_acquired':False,'definition_of_684_14':'NOT RETRIEVED','confirmed_inventory_identity':None,'confirmed_collection_identity':None,'confirmed_specimen_date':None,'photograph_acquired':False,'original_PDF_bytes_acquired':False,'original_PDF_sha256':None,
        'preserved_prior_observation':'Molin primary-publication connector text givesשומורו andHLIB213;684.14. This new retrieval adds no independent edition/ink/date validation and does not alter that prior record.',
        'transport_file':'known-url-fetches.json','transport_bytes':len(raw),'transport_sha256':sha(raw),'text_JSON_pointer':'/content/0/text','text_file':'fetched-content.txt','text_sha256_utf8':sha(text.encode('utf-8')),'text_codepoints':len(text),
        'literal_checks':[{'literal':r['searched_quote'],'status':r['status']} for r in records],
        'actual_guard_execution':{'Supermemory_retrieval_saved':True,'Prumo_Evidence_Audit_records_validated':3,'Proofline_new_execution':False,'SuperJev_success_claimed':False},
        'next_exact_dependency':'Actual1995article printedp213 plus its notation/edition apparatus; verify whether684.14defines a bowl/inventory/line reference and inspect any photograph/dating statement actually supplied. Use authorized library/JSTOR access or an accessible author copy; no access bypass.',
        'scope_limits':'No claim that missing target text or photography is absent from original article. No chronology, precise-phoneme or ancestry/contact conclusion. No canonical/UI/global-memory edits.'
    }
    write('result.json',result)
    print(json.dumps({'status':result['status'],'audit_records_validated':3,'literal_checks':result['literal_checks'],'transport_sha256':result['transport_sha256'],'text_sha256_utf8':result['text_sha256_utf8'],'target_page_acquired':False},ensure_ascii=True,indent=2))

if __name__=='__main__':
    main()
