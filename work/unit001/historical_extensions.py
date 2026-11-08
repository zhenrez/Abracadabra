"""A source-specific historical control; no Sefer state or cross-model assignment."""
from pathlib import Path
import hashlib,json
from kernel import SourceArtifact,EvidenceObservation,EvidenceClaim,DomainRecord,KernelStore

ROOT=Path(__file__).resolve().parent/'list-completion/resh-source'

def build_resh():
    meta=json.loads((ROOT/'source-manifest.json').read_text(encoding='utf-8'))
    raw=(ROOT/'loc-web-extraction.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=meta['files']['loc-web-extraction.json']:
        raise ValueError('Historical extraction changed')
    source=SourceArtifact.from_bytes(meta['source_id'],raw,meta['url'],meta['source_kind'],
        revision=meta['files']['loc-web-extraction.json'],license=meta['license'],
        retrieval_context={'edition':meta['author_editor_translator']+' '+meta['published'],
          'underlying_work':meta['underlying_work'],'underlying_author':meta['underlying_author'],
          'underlying_author_period':meta['underlying_author_period'],
          'earliest_surviving_manuscript':meta['earliest_surviving_manuscript'],
          'limitations':meta['limitations'],'artifact_bytes_downloaded':False},
        acquisition={'retrieved_utc':meta['retrieved_utc'],'attempts':meta['attempts']})
    observations=[];claims=[]
    captured_text=json.loads(raw)
    if not isinstance(captured_text,str):raise ValueError('Expected exact captured web extraction text')
    for item in meta['claims']:
        observation=EvidenceObservation(item['id']+':observation',source.record_id,'historical_phonetics',
            {'raw_extraction':captured_text},
            {'section_and_page':item['locator'],'capture':'loc-web-extraction.json','value_scope':'entire exact web extraction'})
        claim=EvidenceClaim(item['id']+':claim',observation.record_id,'source_described_Resh_grade',item,
            'SOURCE_SPECIFIC_TRANSLATED_TESTIMONY',(source.record_id,),
            uncertainty={'ipa':'NOT_ESTABLISHED','independent_manuscript_confirmation':False,
              'relationship_to_tagged_state':'NOT_ASSIGNED','description_origin':'host summary of translated source'},source_locator=observation.locator)
        observations.append(observation);claims.append(claim)
    control=DomainRecord('control:resh:historical','historical_phonetics','contextual_Resh_claims',
        tuple(o.record_id for o in observations),tuple(c.record_id for c in claims),
        {'letter_identity':'Hebrew Resh','source_family':meta['underlying_work'],
         'independent_manuscripts_verified':False,'earliest_surviving_manuscript':meta['earliest_surviving_manuscript'],
         'sefer_r1_mapping':None,'manuscript_image_collated':False})
    result=KernelStore((source,*observations,*claims,control));result.validate();return result
