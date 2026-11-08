"""G0 source conservation. No musical orientation is imported by this module."""
from dataclasses import dataclass,fields,is_dataclass
from enum import Enum
from types import MappingProxyType
from collections.abc import Mapping
import hashlib,json

class PhoneticType(str,Enum):
    PHONEME_VALUE='PHONEME_VALUE';LETTER_NAME='LETTER_NAME';SYLLABOGRAM='SYLLABOGRAM';VOWEL_SIGN='VOWEL_SIGN';UNKNOWN_VALUE='UNKNOWN_VALUE';SILENT_PLACEHOLDER='SILENT_PLACEHOLDER'
class GlyphType(str,Enum):
    ATTESTED_EPIGRAPHIC_TRANSCRIPTION='ATTESTED_EPIGRAPHIC_TRANSCRIPTION';UNICODE_STANDARD_CHAR='UNICODE_STANDARD_CHAR';UNICODE_PROXY_FOR_UNENCODED='UNICODE_PROXY_FOR_UNENCODED';UNRESOLVED_REPRESENTATION='UNRESOLVED_REPRESENTATION'
class Epistemic(str,Enum):
    USER_SUPPLIED_DATA='USER_SUPPLIED_DATA';ATTESTED_SOURCE='ATTESTED_SOURCE';STIPULATED_BASELINE='STIPULATED_BASELINE';SCHOLARLY_RECONSTRUCTION='SCHOLARLY_RECONSTRUCTION';HYPOTHESIZED_ALIGNMENT='HYPOTHESIZED_ALIGNMENT';INFERRED='INFERRED';UNRESOLVED='UNRESOLVED';SUPERSEDED='SUPERSEDED'

def freeze(value):
    if isinstance(value,Mapping):return MappingProxyType({k:freeze(v) for k,v in value.items()})
    if isinstance(value,(list,tuple)):return tuple(freeze(x) for x in value)
    if isinstance(value,set):raise TypeError('Unordered sets are not serializable evidence')
    return value
class Immutable:
    def __post_init__(self):
        for f in fields(self):object.__setattr__(self,f.name,freeze(getattr(self,f.name)))
def sha(raw):return hashlib.sha256(raw).hexdigest()

@dataclass(frozen=True)
class SourceArtifact(Immutable):
    artifact_id:str;source_location:str;source_kind:str;byte_hash:str;encoding:str;raw_text:str
    raw_reference:str;acquisition:Mapping;authority:Epistemic;original_version:str;supersedes:tuple=()
@dataclass(frozen=True)
class ParsedGrid(Immutable):
    header:tuple;rows:tuple;line_endings:tuple;script_labels:tuple
@dataclass(frozen=True)
class RawCell(Immutable):
    cell_id:str;artifact_id:str;script_id:str;script_label:str;ordinal:int
    glyph:str;ipa:str;english:str;blank_fields:tuple;coordinates:Mapping
@dataclass(frozen=True)
class WitnessRecord(Immutable):
    record_id:str;artifact_id:str;script_id:str;script_label:str;local_ordinal:int;raw_cell_id:str
    raw_supplied_glyph:str;raw_supplied_ipa:str;raw_supplied_english_approx:str
    glyph_type:GlyphType;phonetic_type:PhoneticType;unicode_scalars:tuple;claim_refs:tuple;attestation_refs:tuple=()
@dataclass(frozen=True)
class Claim(Immutable):
    claim_id:str;subject_id:str;property:str;value:object;epistemic_status:Epistemic
    evidence_refs:tuple;source_locator:object;uncertainty:str;competing_claims:tuple=();dating_refs:tuple=()
@dataclass(frozen=True)
class DatedAttestation(Immutable):
    attestation_id:str;subject_id:str;date_kind:str;earliest:object;latest:object
    evidence_refs:tuple=();chronology:str='astronomical integer years: 1 CE=1, 1 BCE=0, 2 BCE=-1'
    def __post_init__(self):
        super().__post_init__()
        if self.date_kind not in ('inscription','manuscript_copy','script_origin','scholarly_reconstruction'):raise ValueError('Unknown date kind')
        if any(v is not None and type(v) is not int for v in (self.earliest,self.latest)):raise ValueError('Integer years or unresolved bounds required')
        if self.earliest is not None and self.latest is not None and self.earliest>self.latest:raise ValueError('Reversed chronology')
@dataclass(frozen=True)
class GenealogyEdge(Immutable):
    edge_id:str;source_record_id:str;target_record_id:str;relation_type:str;epistemic_status:Epistemic
    evidence_claims:tuple;competing_hypotheses:tuple;provenance:Mapping;chronological_constraints:tuple=()
@dataclass(frozen=True)
class DerivedFeature(Immutable):
    feature_id:str;source_records:tuple;feature_type:str;value:object;method:str;method_version:str;error_representation:object;evidence_refs:tuple=()
@dataclass(frozen=True)
class EvidenceGraph(Immutable):
    source:SourceArtifact;grid:ParsedGrid;cells:tuple;witnesses:tuple;claims:tuple
    attestations:tuple=();genealogy:tuple=();alignments:tuple=();features:tuple=()

TYPES={c.__name__:c for c in (SourceArtifact,ParsedGrid,RawCell,WitnessRecord,Claim,DatedAttestation,GenealogyEdge,DerivedFeature,EvidenceGraph)}
ENUMS={c.__name__:c for c in (PhoneticType,GlyphType,Epistemic)}
def primitive(value):
    if isinstance(value,Enum):return {'__enum__':type(value).__name__,'value':value.value}
    if is_dataclass(value):return {'__type__':type(value).__name__,**{f.name:primitive(getattr(value,f.name)) for f in fields(value)}}
    if isinstance(value,Mapping):return {k:primitive(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [primitive(v) for v in value]
    return value
def serialize(value):return json.dumps(primitive(value),ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def deserialize(text):
    def decode(v):
        if isinstance(v,list):return tuple(decode(x) for x in v)
        if not isinstance(v,dict):return v
        if '__enum__' in v:return ENUMS[v['__enum__']](v['value'])
        if '__type__' in v:
            if v['__type__'] not in TYPES:raise ValueError('Unknown record type')
            return TYPES[v['__type__']](**{k:decode(x) for k,x in v.items() if k!='__type__'})
        return {k:decode(x) for k,x in v.items()}
    result=decode(json.loads(text))
    if isinstance(result,EvidenceGraph):validate_graph(result)
    return result

def parse_grid(text):
    rows=[];endings=[]
    for line in text.splitlines(keepends=True):
        end='\r\n' if line.endswith('\r\n') else '\n' if line.endswith('\n') else '\r' if line.endswith('\r') else ''
        body=line[:-len(end)] if end else line
        rows.append(tuple(body.split('\t')));endings.append(end)
    if not rows or rows[0]!=tuple(['Alphabet']+[str(i) for i in range(1,37)]):raise ValueError('Exact 36-column header required')
    if (len(rows)-1)%3 or any(len(r)!=37 for r in rows):raise ValueError('Three full rows per script required; no padding/truncation')
    labels=[]
    for i in range(1,len(rows),3):
        if rows[i+1][0]!='IPA' or rows[i+2][0]!='English sound' or not rows[i][0]:raise ValueError('Source row roles invalid')
        labels.append(rows[i][0])
    if len(set(labels))!=len(labels):raise ValueError('Duplicate script label')
    return ParsedGrid(rows[0],tuple(rows),tuple(endings),tuple(labels))

def roundtrip_source(graph):
    return ''.join('\t'.join(row)+ending for row,ending in zip(graph.grid.rows,graph.grid.line_endings)).encode(graph.source.encoding)

def phonetic_type(label,ordinal,value):
    if value=='?' or value=='':return PhoneticType.UNKNOWN_VALUE
    if label=='English':return PhoneticType.LETTER_NAME
    if label=='Old Persian':return PhoneticType.VOWEL_SIGN if ordinal<=3 else PhoneticType.SYLLABOGRAM
    return PhoneticType.PHONEME_VALUE

def import_matrix(raw,location,acquisition=None):
    text=raw.decode('utf-8');digest=sha(raw);artifact='source:'+digest;grid=parse_grid(text)
    source=SourceArtifact(artifact,location,'USER_SUPPLIED_COMPARATIVE_DATASET',digest,'utf-8',text,
                          'sha256:'+digest,acquisition or {},Epistemic.USER_SUPPLIED_DATA,digest)
    offsets=[];pos=0
    for row,ending in zip(grid.rows,grid.line_endings):
        offsets.append(pos);pos+=len('\t'.join(row))+len(ending)
    cells=[];witnesses=[];claims=[]
    for script_number,label in enumerate(grid.script_labels):
        script_id=artifact+':script:'+str(script_number+1);row_index=1+3*script_number
        for ordinal in range(1,37):
            vals={};coords={}
            for offset,name in enumerate(('glyph','ipa','english')):
                row=grid.rows[row_index+offset];value=row[ordinal]
                start=offsets[row_index+offset]+sum(len(x)+1 for x in row[:ordinal]);end=start+len(value)
                vals[name]=value;coords[name]={'row':row_index+offset+1,'column':ordinal+1,'start':start,'end':end,
                    'byte_start':len(text[:start].encode('utf-8')),'byte_end':len(text[:end].encode('utf-8'))}
            cell_id=script_id+':ordinal:'+str(ordinal)
            cell=RawCell(cell_id,artifact,script_id,label,ordinal,vals['glyph'],vals['ipa'],vals['english'],
                         tuple(n for n,v in vals.items() if v==''),coords);cells.append(cell)
            if not cell.glyph:continue
            rid=cell_id+':witness'
            gt=GlyphType.UNICODE_PROXY_FOR_UNENCODED if label in ('Proto-Sinaitic (proxy)','Paleo-Hebrew') else GlyphType.UNICODE_STANDARD_CHAR
            pt=phonetic_type(label,ordinal,cell.ipa)
            supplied=Claim(rid+':supplied',rid,'supplied_representation',vals,Epistemic.USER_SUPPLIED_DATA,(artifact,cell_id),coords,
                           'Comparative table only; historical pronunciation/date/authentic glyph form not independently verified')
            classification=Claim(rid+':classification',rid,'representation_classification',dict(phonetic=pt.value,glyph=gt.value),Epistemic.INFERRED,
                                (supplied.claim_id,),coords,'Importer typing; syllabic/alternative values preserved literally; no inferred sound realization')
            claims.extend((supplied,classification))
            witnesses.append(WitnessRecord(rid,artifact,script_id,label,ordinal,cell_id,cell.glyph,cell.ipa,cell.english,
                                           gt,pt,tuple(map(ord,cell.glyph)),(supplied.claim_id,classification.claim_id)))
    graph=EvidenceGraph(source,grid,tuple(cells),tuple(witnesses),tuple(claims));validate_graph(graph);return graph

def validate_graph(g):
    if not isinstance(g,EvidenceGraph):raise ValueError('EvidenceGraph required')
    raw=g.source.raw_text.encode(g.source.encoding)
    if sha(raw)!=g.source.byte_hash or roundtrip_source(g)!=raw:raise ValueError('Source digest or roundtrip mismatch')
    if g.grid!=parse_grid(g.source.raw_text):raise ValueError('Grid differs from source')
    ids=[g.source.artifact_id]+[c.cell_id for c in g.cells]+[w.record_id for w in g.witnesses]+[c.claim_id for c in g.claims]+[a.attestation_id for a in g.attestations]+[e.edge_id for e in g.genealogy]+[e.edge_id for e in g.alignments]+[f.feature_id for f in g.features]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate record ID')
    allowed=set(ids);cellmap={c.cell_id:c for c in g.cells};witnessmap={w.record_id:w for w in g.witnesses};claimmap={c.claim_id:c for c in g.claims};attest={a.attestation_id for a in g.attestations}
    def refs(values,domain=allowed):
        if any(x not in domain for x in values):raise ValueError('Invalid foreign-key reference')
    positions=set()
    for c in g.cells:
        if c.artifact_id!=g.source.artifact_id or not 1<=c.ordinal<=36:raise ValueError('Cell source/ordinal invalid')
        key=(c.artifact_id,c.script_id,c.ordinal)
        if key in positions:raise ValueError('Duplicate grid occupancy')
        positions.add(key)
        for name in ('glyph','ipa','english'):
            coordinate=c.coordinates[name];value=getattr(c,name)
            if g.source.raw_text[coordinate['start']:coordinate['end']]!=value:raise ValueError('Value/source span mismatch')
            if raw[coordinate['byte_start']:coordinate['byte_end']].decode('utf-8')!=value:raise ValueError('UTF-8 span mismatch')
            if g.grid.rows[coordinate['row']-1][coordinate['column']-1]!=value:raise ValueError('Grid coordinate mismatch')
        if c.blank_fields!=tuple(n for n in ('glyph','ipa','english') if getattr(c,n)==''):raise ValueError('Blank flag mismatch')
    occupied=set()
    for w in g.witnesses:
        refs((w.raw_cell_id,),cellmap);c=cellmap[w.raw_cell_id];key=(w.artifact_id,w.script_id,w.local_ordinal)
        if key in occupied:raise ValueError('Duplicate position occupancy')
        occupied.add(key)
        if not c.glyph or key!=(c.artifact_id,c.script_id,c.ordinal) or w.script_label!=c.script_label:raise ValueError('Witness address mismatch')
        if (w.raw_supplied_glyph,w.raw_supplied_ipa,w.raw_supplied_english_approx)!=(c.glyph,c.ipa,c.english):raise ValueError('Witness value mismatch')
        if w.unicode_scalars!=tuple(map(ord,c.glyph)):raise ValueError('Unicode altered')
        if not isinstance(w.glyph_type,GlyphType) or not isinstance(w.phonetic_type,PhoneticType):raise ValueError('Invalid enum')
        refs(w.claim_refs,claimmap);refs(w.attestation_refs,attest)
        if w.phonetic_type==PhoneticType.SILENT_PLACEHOLDER and not any(claimmap[x].property=='attested_silence' and claimmap[x].epistemic_status==Epistemic.ATTESTED_SOURCE for x in w.claim_refs):raise ValueError('Silence needs attested claim')
    if len(occupied)!=sum(bool(c.glyph) for c in g.cells):raise ValueError('Populated cell not represented exactly once')
    for c in g.claims:
        refs((c.subject_id,));refs(c.evidence_refs);refs(c.competing_claims,claimmap);refs(c.dating_refs,attest)
        if not isinstance(c.epistemic_status,Epistemic):raise ValueError('Invalid epistemic status')
    for a in g.attestations:refs((a.subject_id,));refs(a.evidence_refs)
    relations={'DIRECT_BORROWING','DOCUMENTED_DESCENT','GRAPHICAL_ADAPTATION','SOUND_VALUE_REASSIGNMENT','ACROPHONIC_ADAPTATION','PARALLEL_DEVELOPMENT','PROPOSED_SIMILARITY','UNRESOLVED_RELATIONSHIP'}
    for e in g.genealogy+g.alignments:
        refs((e.source_record_id,e.target_record_id),witnessmap);refs(e.evidence_claims,claimmap);refs(e.competing_hypotheses)
        if e.relation_type not in relations or not e.evidence_claims:raise ValueError('Relationship requires typed evidence')
    for f in g.features:
        refs(f.source_records,witnessmap);refs(f.evidence_refs)
        if not f.source_records or not f.method or not f.method_version:raise ValueError('Feature provenance missing')
    return True

def verify_g0_conservation(g):
    validate_graph(g)
    raw=g.source.raw_text;parsed=parse_grid(raw)
    checks=[
      ('15 script groups',len(parsed.script_labels)==15),
      ('source order',g.grid.script_labels==tuple(r[0] for r in parsed.rows[1::3])),
      ('original labels',all(c.script_label in parsed.script_labels for c in g.cells)),
      ('36 addressable slots each',len(g.cells)==540 and all(sorted(c.ordinal for c in g.cells if c.script_label==label)==list(range(1,37)) for label in parsed.script_labels)),
      ('381 populated source positions',len(g.witnesses)==sum(bool(v) for row in parsed.rows[1::3] for v in row[1:])==381),
      ('159 explicit empty positions',sum(c.glyph=='' for c in g.cells)==159),
      ('all three fields preserved',all((w.raw_supplied_glyph,w.raw_supplied_ipa,w.raw_supplied_english_approx)==(c.glyph,c.ipa,c.english) for w in g.witnesses for c in (next(x for x in g.cells if x.cell_id==w.raw_cell_id),))),
      ('Unicode scalar fidelity',all(w.unicode_scalars==tuple(map(ord,w.raw_supplied_glyph)) for w in g.witnesses)),
      ('proxy classification',all(w.glyph_type==GlyphType.UNICODE_PROXY_FOR_UNENCODED for w in g.witnesses if w.script_label=='Proto-Sinaitic (proxy)')),
      ('no ordinal alignment inferred',not g.alignments),
      ('heterogeneous Old Persian',{w.phonetic_type for w in g.witnesses if w.script_label=='Old Persian'}=={PhoneticType.VOWEL_SIGN,PhoneticType.SYLLABOGRAM}),
      ('question marks remain unknown',all(w.phonetic_type==PhoneticType.UNKNOWN_VALUE for w in g.witnesses if w.raw_supplied_ipa=='?')),
      ('alternatives retained',all(w.raw_supplied_ipa==next(c.ipa for c in g.cells if c.cell_id==w.raw_cell_id) for w in g.witnesses if '/' in w.raw_supplied_ipa)),
      ('genealogy external',all('ancestor' not in f.name for f in fields(WitnessRecord))),
      ('raw and inferred claims separate',{c.epistemic_status for c in g.claims}=={Epistemic.USER_SUPPLIED_DATA,Epistemic.INFERRED}),
      ('no invented attestations',not g.attestations),
      ('reference integrity',validate_graph(g)),
      ('unique witness primary keys',len({(w.artifact_id,w.script_id,w.local_ordinal) for w in g.witnesses})==len(g.witnesses)),
      ('nested immutable maps',all(isinstance(c.coordinates,MappingProxyType) and all(isinstance(v,MappingProxyType) for v in c.coordinates.values()) for c in g.cells)),
      ('exact source roundtrip',roundtrip_source(g)==raw.encode('utf-8'))]
    return dict(status='PASSED' if all(v for _,v in checks) else 'FAILED',invariants=[dict(id=i+1,name=n,status='PASS' if v else 'FAIL') for i,(n,v) in enumerate(checks)])
