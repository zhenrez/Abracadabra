"""EU-001R domain-independent provenance contracts. No analytic model dependencies."""
from dataclasses import dataclass,fields
from enum import Enum
import base64,hashlib,json
from evidence import Immutable,primitive

class DataState(str,Enum):
    BLANK='BLANK';MISSING_CHARACTER='MISSING_CHARACTER';DAMAGED='DAMAGED';ILLEGIBLE='ILLEGIBLE'
    UNKNOWN_PHONETIC='UNKNOWN_PHONETIC';ATTESTED_SILENCE='ATTESTED_SILENCE';UNATTESTED='UNATTESTED'
    SOURCE_UNAVAILABLE='SOURCE_UNAVAILABLE';INFERRED='INFERRED';SUPERSEDED='SUPERSEDED';REJECTED='REJECTED';INAPPLICABLE='INAPPLICABLE'

@dataclass(frozen=True)
class SourceArtifact(Immutable):
    record_id:str;content_b64:str;content_hash:str;encoding:str;location:str;revision:str
    retrieval_context:object;license:str;permitted_use:str;acquisition:object
    lineage:tuple;supersedes:tuple;authority:str
    @classmethod
    def from_bytes(cls,record_id,raw,location,authority='USER_SUPPLIED_DATA',**metadata):
        return cls(record_id,base64.b64encode(raw).decode(),hashlib.sha256(raw).hexdigest(),'utf-8',location,
          metadata.get('revision',hashlib.sha256(raw).hexdigest()),metadata.get('retrieval_context',{}),
          metadata.get('license','UNVERIFIED'),metadata.get('permitted_use','local authorized engineering'),
          metadata.get('acquisition',{}),tuple(metadata.get('lineage',())),(),authority)
@dataclass(frozen=True)
class EvidenceObservation(Immutable):
    record_id:str;source_id:str;domain:str;value:object;locator:object
@dataclass(frozen=True)
class EvidenceClaim(Immutable):
    record_id:str;subject_id:str;property:str;value:object;status:str;evidence_refs:tuple
    competing_claims:tuple=();uncertainty:object=None
@dataclass(frozen=True)
class DerivationRecord(Immutable):
    record_id:str;input_refs:tuple;output_refs:tuple;method:str;version:str;parameters:object;agent:str
@dataclass(frozen=True)
class OperatorSpecification(Immutable):
    record_id:str;input_type:str;output_type:str;domain:str;codomain:str;parameters:object;preconditions:tuple
    rule:str;partial:bool;reversible:object;injective:object;invariants:tuple;validation_method:str;implementation_version:str;evidence_refs:tuple
@dataclass(frozen=True)
class TransformationClaim(Immutable):
    record_id:str;operator_ref:str;source_ref:str;target_ref:str;evidence_refs:tuple;status:str;uncertainty:object
@dataclass(frozen=True)
class DomainRecord(Immutable):
    record_id:str;domain:str;record_type:str;observation_refs:tuple;claim_refs:tuple;properties:object
@dataclass(frozen=True)
class ExperimentReceipt(Immutable):
    record_id:str;target:str;source_dependencies:tuple;source_family_exclusions:tuple;known_exposure:tuple
    model_version:str;permitted_data:object;prediction_lock:str;scoring:object;null_hypotheses:tuple
    negative_controls:tuple;abstention:bool;outcome:object;post_reveal_modifications:tuple;evaluation_group:str
    def __post_init__(self):
        super().__post_init__()
        if self.evaluation_group=='HISTORICAL_HOLDOUT' and (self.known_exposure or self.prediction_lock=='unsealed'):
            raise ValueError('Exposed or unsealed inputs cannot be certified historical holdouts')

RECORD_TYPES={c.__name__:c for c in (SourceArtifact,EvidenceObservation,EvidenceClaim,DerivationRecord,OperatorSpecification,TransformationClaim,DomainRecord,ExperimentReceipt)}

@dataclass(frozen=True)
class KernelStore(Immutable):
    records:tuple=()
    def validate(self):
        ids=[r.record_id for r in self.records]
        if len(ids)!=len(set(ids)):raise ValueError('Duplicate append-only record identity')
        index={r.record_id:r for r in self.records}
        def refs(values,kind=None):
            for value in values:
                if value not in index or kind is not None and not isinstance(index[value],kind):raise ValueError('Invalid typed evidence reference')
        for r in self.records:
            if type(r).__name__ not in RECORD_TYPES:raise ValueError('Unsupported record contract')
            if isinstance(r,SourceArtifact):
                raw=base64.b64decode(r.content_b64,validate=True)
                if hashlib.sha256(raw).hexdigest()!=r.content_hash:raise ValueError('Source digest mismatch')
                refs(r.lineage,SourceArtifact);refs(r.supersedes,SourceArtifact)
            elif isinstance(r,EvidenceObservation):refs((r.source_id,),SourceArtifact)
            elif isinstance(r,EvidenceClaim):refs((r.subject_id,));refs(r.evidence_refs);refs(r.competing_claims,EvidenceClaim)
            elif isinstance(r,DerivationRecord):refs(r.input_refs);refs(r.output_refs)
            elif isinstance(r,DomainRecord):refs(r.observation_refs,EvidenceObservation);refs(r.claim_refs,EvidenceClaim)
            elif isinstance(r,TransformationClaim):refs((r.operator_ref,),OperatorSpecification);refs((r.source_ref,r.target_ref));refs(r.evidence_refs)
            elif isinstance(r,OperatorSpecification):refs(r.evidence_refs)
            elif isinstance(r,ExperimentReceipt):refs(r.source_dependencies)
        return True
    def append(self,record):
        result=KernelStore(self.records+(record,));result.validate();return result
    def provenance(self,record_id):
        index={r.record_id:r for r in self.records};seen=set()
        if record_id not in index:raise ValueError('Unknown record')
        def visit(key):
            if key in seen:return
            seen.add(key);r=index[key]
            refs=[]
            if isinstance(r,DomainRecord):refs=list(r.observation_refs)+list(r.claim_refs)
            elif isinstance(r,EvidenceObservation):refs=[r.source_id]
            elif isinstance(r,EvidenceClaim):refs=list(r.evidence_refs)
            for value in refs:visit(value)
        visit(record_id);return tuple(sorted(seen))
    def to_json(self):return json.dumps([primitive(r) for r in self.records],ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
    @classmethod
    def from_json(cls,text):
        def decode(v):
            if isinstance(v,list):return tuple(decode(x) for x in v)
            if isinstance(v,dict):
                if '__enum__' in v:
                    if v['__enum__']!='DataState':raise ValueError('Unknown enum')
                    return DataState(v['value'])
                if '__type__' in v:
                    kind=RECORD_TYPES.get(v['__type__'])
                    if kind is None:raise ValueError('Unknown record type')
                    return kind(**{k:decode(x) for k,x in v.items() if k!='__type__'})
                return {k:decode(x) for k,x in v.items()}
            return v
        result=cls(tuple(decode(x) for x in json.loads(text)));result.validate();return result

@dataclass(frozen=True)
class OperatorRegistry(Immutable):
    definitions:tuple=()
    def register(self,spec):
        if not isinstance(spec,OperatorSpecification) or spec.record_id in [r.record_id for r in self.definitions]:raise ValueError('Duplicate or invalid definition')
        return OperatorRegistry(self.definitions+(spec,))
    def execute(self,*args):raise PermissionError('Definition registration does not authorize execution or search')

def migrate_matrix(graph):
    from evidence import validate_graph
    validate_graph(graph);source=SourceArtifact.from_bytes(graph.source.artifact_id,graph.source.raw_text.encode('utf-8'),graph.source.source_location,
        retrieval_context={'upstream_contract':'unit001.evidence','raw_reference':graph.source.raw_reference},acquisition=graph.source.acquisition)
    records=[source]
    for c in graph.cells:
        records.append(EvidenceObservation(c.cell_id,source.record_id,'linguistic_matrix',
            {'script_id':c.script_id,'script_label':c.script_label,'local_ordinal':c.ordinal,'glyph':c.glyph,'ipa':c.ipa,'english':c.english,
             'field_states':{n:DataState.BLANK if getattr(c,n)=='' else DataState.UNKNOWN_PHONETIC if n=='ipa' and c.ipa=='?' else None for n in ('glyph','ipa','english')}},c.coordinates))
    for w in graph.witnesses:
        records.append(DomainRecord(w.record_id,'phonetics_epigraphy','matrix_witness',(w.raw_cell_id,),(),
            {'glyph_representation':w.glyph_type.value,'phonetic_representation':w.phonetic_type.value,'unicode_scalars':w.unicode_scalars,'legacy_claim_refs':w.claim_refs}))
    for c in graph.claims:
        records.append(EvidenceClaim(c.claim_id,c.subject_id,c.property,c.value,c.epistemic_status.value,c.evidence_refs,c.competing_claims,c.uncertainty))
    records.append(DerivationRecord('derivation:matrix:migration',(source.record_id,),tuple(w.record_id for w in graph.witnesses),
        'lossless G0 adapter','EU-001R-v1',{'unicode_normalization':False},'host engineering adapter'))
    result=KernelStore(tuple(records));result.validate();return result

def schema_fixtures():
    """Synthetic contract examples only; none assert retrieval of historical objects."""
    examples={
      'T02':('epigraphy','damaged_sign',{'image_region':[1,2,30,40],'surface':'stone','state':DataState.DAMAGED,'sign_candidates':['A','B'],'reading_candidates':['x','y']}),
      'T03':('rabbinic','reading_layers',{'ketiv':'written-form','qere':'read-form','realization':DataState.UNATTESTED,'al_tikrei':'interpretation','dagesh':DataState.INAPPLICABLE}),
      'T04':('rabbinic','dual_classifications',{'letter_ids':['aleph','mem','shin'],'partitions':{'sefer':[3,7,12],'articulatory_classes':5},'recensions':['fixture-A','fixture-B'],'resh_realizations':['claim-A','claim-B'],'r:1':'tagged, not identified with either claim'}),
      'T05':('historical_language','adaptation_claim',{'source_sign':'A','target_sign':'B','relation':'PROPOSED_ADAPTATION','ordinal_alignment':False}),
      'T06':('music_mathematics','exact_quantities',{'ratio':{'numerator':2,'denominator':3,'unit':'string_length_ratio'},'alternative':{'numerator':4,'denominator':3},'engine':DataState.INAPPLICABLE}),
      'T07':('narrative','distinct_witnesses',{'witnesses':['Numbers 11','Sanhedrin 17a','Aristeas','Luke 10'],'counts_equated':False,'manuscript_dates':DataState.SOURCE_UNAVAILABLE}),
      'T08':('normative','rule',{'actor':'fixture actor','action':'fixture action','modality':'PROHIBITION','conditions':['c'],'exceptions':['e'],'authority':'synthetic authority','period':DataState.UNATTESTED}),
      'T09':('mathematics','orientation_candidates',{'namespace':'w72:fixture','candidates':['A','B'],'equivalence_class':['A','B'],'selected':None}),
      'T10':('diagrammatic','two_layouts',{'layouts':[{'image':'synthetic-A','nodes':[{'id':'a','label':'X','xy':[0,0]}],'edges':[]},{'image':'synthetic-B','nodes':[{'id':'b','label':'Y','xy':[1,2]}],'edges':[]}],'containment':[],'same_path_assignments':False}),
      'T11':('textual','orientation_procedures',{'source_text':'synthetic only','procedures':['straight','reverse middle row'],'index_convention':'explicit 1-based','chosen':None,'w72_alignment':None}),
      'T12':('morphology','root_pattern_candidates',{'form':'fixture-form','analyses':[{'root':'A','pattern':'P'},{'root':'B','pattern':'Q'}],'realizations':['reading-A','reading-B'],'error_channels':['damage','mishearing','redaction','unknown']})}
    result={}
    for key,(domain,kind,value) in examples.items():
        source=SourceArtifact.from_bytes(key+':source',json.dumps(value,default=str).encode(), 'synthetic:'+key,'SYNTHETIC_SCHEMA_FIXTURE',license='local fixture',permitted_use='schema testing only')
        obs=EvidenceObservation(key+':observation',source.record_id,domain,value,{'fixture':key})
        claim=EvidenceClaim(key+':claim',obs.record_id,'schema_example',value,'SYNTHETIC_SCHEMA_FIXTURE',(source.record_id,))
        record=DomainRecord(key+':domain',domain,kind,(obs.record_id,),(claim.record_id,),value)
        result[key]=KernelStore((source,obs,claim,record))
    return result
