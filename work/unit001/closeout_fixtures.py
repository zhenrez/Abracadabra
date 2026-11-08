"""Four source-identified architecture controls, with no reconstruction selection."""
from pathlib import Path
import json,re,hashlib
from kernel import SourceArtifact,EvidenceObservation,EvidenceClaim,DomainRecord,KernelStore
ROOT=Path(__file__).parent/'closeout'
def source(key):
    meta=next(x for x in json.loads((ROOT/'source-manifest.json').read_text(encoding='utf-8')) if x['id']==key)
    raw=(ROOT/meta['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=meta['sha256']:raise ValueError('Pinned source changed')
    return SourceArtifact.from_bytes('closeout:source:'+key,raw,meta['url'],meta['authority'],
        revision=meta['sha256'],retrieval_context={'english_version':meta['english_version'],'hebrew_version':meta['hebrew_version'],
        'age_scope':meta['age_scope']},license=meta['license'],acquisition={'capture':meta['capture'],'retrieved_utc':meta['retrieved_utc']})
def build():
    result={};sources=[source(k) for k in ('Sefer_Yetzirah.1','Sefer_Yetzirah_Gra_Version.1')]
    observations=[]
    for s in sources:
        d=json.loads(__import__('base64').b64decode(s.content_b64))
        observations.append(EvidenceObservation(s.record_id+':he',s.record_id,'textual',{'he':d['he'],'english':d['text'],
            'hebrew_edition':d['heVersionTitle'],'english_edition':d['versionTitle']},{'ref':d['ref'],'fields':['he','text']}))
    domain=DomainRecord('control:recensions','textual','recension_comparison',tuple(o.record_id for o in observations),(),
        {'recensions':['Sefer Yetzirah','Sefer Yetzirah Gra Version'],'independent_manuscripts_verified':False,
         'shared_hebrew_edition':'Warsaw 1884','earliest_manuscript_status':'NOT ESTABLISHED','phonetic_assignment_selected':None})
    result['recensions']=KernelStore(tuple(sources+observations+[domain]))
    s=source('Ruth.3.3');d=json.loads(__import__('base64').b64decode(s.content_b64));he=d['he']
    written=re.findall(r'class="mam-kq-k">\((.*?)\)</span>',he)
    read=re.findall(r'class="mam-kq-q">\[(.*?)\]</span>',he)
    if len(written)!=2 or len(read)!=2:raise ValueError('Source reading markup changed')
    o=EvidenceObservation('control:qere:obs',s.record_id,'rabbinic',{'raw_hebrew_html':he},{'ref':'Ruth 3:3','field':'he'})
    r=DomainRecord('control:qere','rabbinic','written_versus_read',(o.record_id,),(),{'pairs':[dict(written=k,read=q) for k,q in zip(written,read)],
      'phonetic_realization':None,'hermeneutic_interpretation':None,'edition':d['heVersionTitle'],'ancient_manuscript_claim':False})
    result['qere_ketiv']=KernelStore((s,o,r))
    p=ROOT/'Lachish-inspected-excerpt.txt';s=SourceArtifact.from_bytes('control:epigraphy:source',p.read_bytes(),
      'https://doi.org/10.52486/01.00008.2','HOST_TRANSCRIPTION_OF_INSPECTED_PRIMARY_SCHOLARLY_SOURCE',
      retrieval_context={'locator':'printed p47, before Table1','original_pdf_bytes':'NOT_RETRIEVED; direct capture is HTML error','quote_vs_paraphrase':'explicitly labeled in captured excerpt'},license='UNVERIFIED')
    o=EvidenceObservation('control:epigraphy:obs',s.record_id,'epigraphy',{'artifact':'Basket B736, Locus C283','surface':'ostracon',
       'following_numeral_state':'too faded for reliable reading','artifact_photograph':None},{'publication_pages':[44,47]})
    ids=['control:epigraphy:c13','control:epigraphy:c14','control:epigraphy:c16']
    claims=[EvidenceClaim(cid,o.record_id,'candidate_total',number,'SCHOLARLY_RECONSTRUCTION',(s.record_id,),tuple(x for x in ids if x!=cid),
             {'explanation':'authors prefer following 6; 3 or 4 also possible','selected':False}) for cid,number in zip(ids,[13,14,16])]
    result['epigraphy']=KernelStore((s,o,*claims))
    s=source('Ibn_Ezra_on_Exodus.14.19.1');d=json.loads(__import__('base64').b64decode(s.content_b64));text=d['text']
    marker='<sup class="footnote-marker">74</sup>'
    if marker not in text:raise ValueError('Footnote source locator changed')
    start=text.index(marker);depth=0;end=None
    for tag in re.finditer(r'<(/?)i\b[^>]*>',text[start:]):
        depth+=-1 if tag.group(1) else 1
        if depth==0:
            end=start+tag.end();break
    if end is None:raise ValueError('Unclosed source footnote')
    footnote=text[start:end]
    if 'invert verse 20' not in footnote:raise ValueError('Orientation evidence absent')
    o=EvidenceObservation('control:orientation:obs',s.record_id,'textual',{'hebrew_commentary':d['he'],'english_annotated_text':text,
       'footnote74':footnote},{'ref':d['ref'],'field':'text','start':start,'end':end})
    r=DomainRecord('control:orientation','textual','competing_orientation_descriptions',(o.record_id,),(),
      {'procedures':['three verses in original order','middle verse reversed'],
       'attribution':'modern translation footnote 74; no direct attribution of both procedures to Ibn Ezra',
       'translation_edition':d['versionTitle'],'hebrew_edition':d['heVersionTitle'],'selected':None,'w72_alignment':None,
       'evidence_verdict':'attested in this annotation, not an independently established medieval transmission claim'})
    result['orientations']=KernelStore((s,o,r))
    for store in result.values():store.validate()
    return result
if __name__=='__main__':
    data=build();(ROOT/'historical-controls.json').write_text(json.dumps({k:json.loads(v.to_json()) for k,v in data.items()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS: four source-identified controls serialized')
