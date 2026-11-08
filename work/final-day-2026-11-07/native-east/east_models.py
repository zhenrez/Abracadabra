"""Source-bound native G3/G4 adapters. No cross-orientation outputs are read."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations, product
import ast, hashlib, json, sys

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[2]
sys.path.insert(0,str(PROJECT/'work/unit001'))
from contracts import NativeValidation,EncodedModel,CandidateSet,DescriptionLength,ReconstructionReceipt
from evidence import freeze,serialize

PROFILES=freeze(json.loads((ROOT/'source-profiles.json').read_text(encoding='utf-8')))
LEGACY_PATH=PROJECT/'work/four-orientations/native_models.py'
LEGACY_HASH='e9085c55d560ce92a5c7afd1e9ac20a7efcbdff0506ca4cf10de4245289da217'

def rational(value):
    if type(value) not in (str,int,Q):raise ValueError('Exact rational string/integer/Fraction required')
    try:result=Q(value)
    except (ValueError,ZeroDivisionError) as error:raise ValueError('Invalid rational') from error
    if result<=0:raise ValueError('Positive rational required')
    return result

def reuse_native_definitions():
    """Reuse pinned classes without executing the legacy module's Sefer imports."""
    raw=LEGACY_PATH.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=LEGACY_HASH:raise ValueError('Reviewed native definitions changed')
    tree=ast.parse(raw)
    selected=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ('Chinese','Indian','positive')]
    if len(selected)!=3:raise ValueError('Native reuse contract changed')
    namespace={'Q':Q,'combinations':combinations,'product':product}
    exec(compile(ast.Module(body=selected,type_ignores=[]),str(LEGACY_PATH),'exec'),namespace)
    return namespace['Chinese'](),namespace['Indian']()

LEGACY_CHINESE,LEGACY_INDIAN=reuse_native_definitions()

def receipt(namespace,solutions,domain,has_input,complete=False):
    count=len(solutions)
    identifiable='INSUFFICIENT_INPUT' if not has_input else 'NO_FEASIBLE_SOLUTION' if count==0 else 'UNIQUE_UNDER_MODEL' if count==1 else 'MULTIPLE_DISTINGUISHABLE'
    structural='NOT_EVALUATED' if not has_input else 'CONTRADICTION' if count==0 else 'VALID' if complete else 'INCOMPLETE'
    return ReconstructionReceipt('EVALUATED' if has_input else 'NOT_EVALUATED',
        'AMBIGUOUS_UNDERDETERMINED' if count>1 else 'UNSUPPORTED',
        {'status':structural,'native_constraints':'source profile plus exact native feasibility'},
        {'status':'NOT_EVALUATED','reason':'No registered coding comparison'},
        {'status':identifiable,'candidate_count':count},
        {'status':'NOT_VERIFIED','claim':'Historical reconstruction is not established by finite-model uniqueness'},
        CandidateSet(tuple(solutions),True,tuple(domain),'Distinguished by the full native state; no unproved equivalence quotient'),
        {'model':namespace,'cross_orientation_used':False})

class NativeAdapter:
    namespace=''
    profile_key=''
    def __init__(self):
        self.profile=PROFILES[self.profile_key]
        source_ids=self.profile.get('source_ids',(self.profile.get('source_id'),))
        self.sources=tuple(s for s in PROFILES['sources'] if s['id'] in source_ids)
        self.profile_hash=hashlib.sha256(serialize({'profile':self.profile,'sources':self.sources}).encode('utf-8')).hexdigest()
    def _encode(self,records):
        return EncodedModel(self.namespace,self.profile['profile_id'],self.profile_hash,tuple(records),(),(),
                            {'profile':self.profile,'sources':self.sources,'legacy_source_sha256':LEGACY_HASH})
    def validate_native(self,evidence):
        if not isinstance(evidence,EncodedModel):return NativeValidation('NOT_EVALUATED',('EncodedModel input required',))
        expected=self.encode(None)
        checks=(('model_namespace',evidence.model_namespace==self.namespace),('profile_id',evidence.profile_id==expected.profile_id),
                ('profile_hash',evidence.profile_hash==expected.profile_hash),('native_assignments',serialize(evidence.assignments)==serialize(expected.assignments)),
                ('source_profile',evidence.evidence_graph==expected.evidence_graph))
        return NativeValidation('VALID' if all(p for _,p in checks) else 'CONTRADICTION',checks)
    def describe(self,evidence,coding_scheme):
        return DescriptionLength('NOT_EVALUATED',None,'No declared executable coding scheme; no MDL score invented')

class ChineseModel(NativeAdapter):
    namespace='chinese:lushi-yinlv';profile_key='chinese'
    def act_length(self,value,operator):
        if operator not in ('D','U'):raise ValueError('Unknown native length operator')
        return LEGACY_CHINESE.act(rational(value),operator)
    def frequency_ratio(self,length):return 1/rational(length)
    def generation(self,count=12,reference_length=Q(1),register=0):
        if type(count) is not int or not 1<=count<=13:raise ValueError('Bounded generation count1..13 required')
        if type(register) is not int or not -64<=register<=64:raise ValueError('Bounded integer register required')
        reference=rational(reference_length)*Q(2)**register;relative=Q(1);rows=[];operator=None
        for i in range(count):
            length=reference*relative
            rows.append({'generation_index':i,'name':self.profile['generation_names'][i%12],
                'pitch_class':7*i%12,'length':length,'frequency':1/length,'operator':operator,
                'reference_length':reference,'register':register,'unwrapped_fifth_frequency':Q(3,2)**i/reference})
            operator='D' if relative*Q(2,3)>=Q(1,2) else 'U'
            relative=self.act_length(relative,operator)
        return tuple(rows)
    def contexts(self):return LEGACY_CHINESE.contexts()
    def modal_context(self,reference_index,role_rotation):
        if type(reference_index) is not int or type(role_rotation) is not int or (reference_index,role_rotation) not in self.contexts():raise ValueError('Invalid modal context')
        pitches=tuple((reference_index+i)%12 for i in (0,2,4,7,9));roles=LEGACY_CHINESE.functions
        return {'reference_index':reference_index,'pitch_classes':pitches,
                'role_assignments':tuple((roles[(i+role_rotation)%5],p) for i,p in enumerate(pitches)),
                'tuning_assignment_inferred':False}
    def encode(self,evidence=None):
        if evidence is not None:raise ValueError('Select a source profile explicitly; arbitrary inputs are reconstructed separately')
        return self._encode(tuple({**r,**{k:str(v) for k,v in r.items() if isinstance(v,Q)}} for r in self.generation()))
    def reconstruct(self,partial,constraints=None):
        if not isinstance(partial,dict):raise ValueError('Position-to-exact-length mapping required')
        if any(type(k) is not int or not 0<=k<12 for k in partial):raise ValueError('Invalid generation position')
        constraints=constraints or {}
        if set(constraints)-{'reference_lengths'}:raise ValueError('Unknown Chinese constraint')
        candidates=tuple(dict.fromkeys(rational(x) for x in constraints.get('reference_lengths',('1',))))
        if len(candidates)>128:raise ValueError('Finite candidate cap128 exceeded')
        solutions=[]
        for reference in candidates:
            rows=self.generation(reference_length=reference)
            if all(v is None or rational(v)==rows[k]['length'] for k,v in partial.items()):
                solutions.append({'reference_length':str(reference),'generation_lengths':tuple(str(r['length']) for r in rows)})
        return receipt(self.namespace,solutions,range(12),bool(partial),len(partial)==12 and all(v is not None for v in partial.values()))

class GramaModel(NativeAdapter):
    namespace='indian:grama-shruti';profile_key='grama'
    def allocations(self,grama):
        if grama not in ('shadja','madhyama'):raise ValueError('Unknown grama profile')
        return tuple(self.profile[grama])
    def frequency_profile(self):return None
    def murchanas(self,grama=None):
        if grama is not None:self.allocations(grama)
        notes=tuple(self.profile['note_order']);rows=[]
        for key in (grama,) if grama else ('shadja','madhyama'):
            allocation=self.allocations(key)
            for name,start in self.profile['murchanas'][key]:
                order=tuple((start+i)%7 for i in range(7))
                intervals=tuple(allocation[(index+1)%7] for index in order)
                rows.append({'grama':key,'name':name,'start_note':notes[start],
                    'note_order':tuple(notes[index] for index in order),'interval_units':intervals,
                    'total_units':sum(intervals),'frequency_ratios':None})
        return tuple(rows)
    def encode(self,evidence=None):
        if evidence is not None:raise ValueError('Explicit native source profile required')
        return self._encode(self.murchanas())
    def reconstruct(self,partial,constraints=None):
        if not isinstance(partial,dict):raise ValueError('Native partial fields required')
        fields={'grama','name','start_note','note_order','interval_units'}
        if set(partial)-fields or constraints:raise ValueError('Unknown grama constraint')
        solutions=[m for m in self.murchanas() if all(v is None or (tuple(v) if isinstance(v,(list,tuple)) else v)==m[k] for k,v in partial.items())]
        return receipt(self.namespace,solutions,tuple(sorted(fields)),bool(partial),'name' in partial and len(solutions)==1)

class MelakartaModel(NativeAdapter):
    namespace='indian:melakarta-modern-sampurna';profile_key='melakarta'
    def configurations(self):
        return tuple(sorted(LEGACY_INDIAN.configurations(),key=lambda s:(s[3],s[1],s[2],s[5],s[6])))
    def pair_madhyama(self,scale):
        if not isinstance(scale,(tuple,list)) or any(type(v) is not int for v in scale):raise ValueError('Integer symbolic positions required')
        try:return LEGACY_INDIAN.pair_madhyama(tuple(scale))
        except (TypeError,ValueError) as error:raise ValueError('Invalid melakarta configuration') from error
    def encode(self,evidence=None):
        if evidence is not None:raise ValueError('Explicit native source profile required')
        return self._encode(tuple({'mela_number':i+1,'positions':scale,'position_type':'symbolic_svarasthana','frequency_ratios':None} for i,scale in enumerate(self.configurations())))
    def reconstruct(self,partial,constraints=None):
        partial=tuple(partial)
        if not partial:return receipt(self.namespace,(),range(7),False)
        if len(partial)!=7 or any(v is not None and type(v) is not int for v in partial) or constraints:raise ValueError('Seven symbolic position slots required')
        solutions=[{'mela_number':i+1,'positions':scale} for i,scale in enumerate(self.configurations()) if all(v is None or v==scale[k] for k,v in enumerate(partial))]
        return receipt(self.namespace,solutions,range(7),True,all(v is not None for v in partial))
