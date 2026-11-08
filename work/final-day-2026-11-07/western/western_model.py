"""Western native orientation contract, reusing the preserved exact Unit002 core.

Pythagorean tuning is an explicit mathematical profile. Modern mode labels do
not certify ancient or medieval usage; historical witness profiles stay distinct.
"""
from dataclasses import dataclass, fields, is_dataclass
from fractions import Fraction
from pathlib import Path
from collections.abc import Mapping
import hashlib
import importlib.util
import json
import sys

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[2]
UNIT001=PROJECT/'work/unit001'
if str(UNIT001) not in sys.path:sys.path.insert(0,str(UNIT001))
from contracts import NativeValidation, DescriptionLength, CandidateSet, ReconstructionReceipt

CORE_PATH=PROJECT/'work/unit002/western.py'
spec=importlib.util.spec_from_file_location('sun_preserved_western_core',CORE_PATH)
_core=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=_core
spec.loader.exec_module(_core)
Interval=_core.Interval
Pitch=_core.Pitch


def exact(value):
    if isinstance(value,Mapping) and set(value)=={'numerator','denominator'}:
        if any(type(x) is not int for x in value.values()):raise ValueError('Integer rational components required')
        try:return Fraction(value['numerator'],value['denominator'])
        except ZeroDivisionError as error:raise ValueError('Zero rational denominator') from error
    if type(value) not in (int,str,Fraction):raise ValueError('Exact integer, rational string or Fraction required')
    try:return Fraction(value)
    except (ValueError,ZeroDivisionError) as error:raise ValueError('Invalid rational quantity') from error


def canonical_json(value):
    def encode(v):
        if isinstance(v,Fraction):return {'numerator':v.numerator,'denominator':v.denominator}
        if is_dataclass(v):return {f.name:encode(getattr(v,f.name)) for f in fields(v)}
        if isinstance(v,Mapping):return {k:encode(x) for k,x in v.items()}
        if isinstance(v,(list,tuple)):return [encode(x) for x in v]
        return v
    return json.dumps(encode(value),ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)


def source_profiles():
    return json.loads((ROOT/'source-profiles.json').read_text(encoding='utf-8'))['profiles']


@dataclass(frozen=True)
class WesternObservation:
    record_id:str
    ratio:Fraction
    onset:Fraction
    duration:Fraction
    voice:str
    source_ref:str
    def __post_init__(self):
        for name in ('ratio','onset','duration'):object.__setattr__(self,name,exact(getattr(self,name)))
        if self.ratio<=0 or self.onset<0 or self.duration<=0:raise ValueError('Invalid positive pitch/duration or negative onset')
        if any(not isinstance(v,str) or not v for v in (self.record_id,self.voice,self.source_ref)):
            raise ValueError('Explicit event identity, voice and source reference required')
    @property
    def register(self):return Pitch(self.ratio).register
    @property
    def pitch_class(self):return Pitch(self.ratio).pitch_class


@dataclass(frozen=True)
class WesternEncoding:
    namespace:str
    kind:str
    mode:object
    observations:tuple
    raw_evidence:str
    evidence_sha256:str
    core_sha256:str


class WesternOrientation:
    namespace='western:pythagorean-major:v1'
    def __init__(self):
        self.core=_core.WesternModel()
        self.core_sha256=hashlib.sha256(CORE_PATH.read_bytes()).hexdigest()
    def encode(self,evidence):
        if not isinstance(evidence,dict):raise ValueError('Explicit Western evidence mapping required')
        if evidence.get('profile_id',self.namespace)!=self.namespace:raise ValueError('Unknown or unadmitted tuning profile')
        kind=evidence.get('kind','performance')
        mode=evidence.get('mode')
        if kind not in ('scale','performance'):raise ValueError('Unknown Western input kind')
        if mode is not None and mode not in self.core.MODE_NAMES:raise ValueError('Unknown configured mode')
        source=evidence.get('source_ref')
        if not source or not isinstance(source,str):raise ValueError('Source reference required')
        observations=tuple(WesternObservation(x['record_id'],x['ratio'],x.get('onset','0'),x.get('duration','1'),
                            x.get('voice','v1'),x.get('source_ref',source)) for x in evidence.get('observations',()))
        raw=canonical_json(evidence)
        return WesternEncoding(self.namespace,kind,mode,observations,raw,
                               hashlib.sha256(raw.encode('utf-8')).hexdigest(),self.core_sha256)
    def validate_native(self,evidence):
        if evidence is None:return NativeValidation('NOT_EVALUATED',('No native evidence supplied',))
        try:
            encoded=evidence if isinstance(evidence,WesternEncoding) else self.encode(evidence)
            rebuilt=self.encode(json.loads(encoded.raw_evidence))
            if rebuilt!=encoded:raise ValueError('Encoding differs from its source binding')
            values=encoded.observations
            if not values:return NativeValidation('NOT_EVALUATED',('No observations supplied',))
            if len({x.record_id for x in values})!=len(values):raise ValueError('Duplicate event identity')
            checks=['actual source and implementation binding','unique observed event identities','positive exact quantities',
                    'separate exact pitch class and register','explicit native tuning profile']
            if encoded.kind=='scale':
                if encoded.mode is None or len(values)!=7:raise ValueError('Seven ordered degrees and an explicit mode required')
                expected=self.core.mode(encoded.mode)['ratios'];tonic=values[0].ratio
                if tuple(x.ratio/tonic for x in values)!=expected:raise ValueError('Scale observations violate configured exact mode')
                checks.append('all supplied scale degrees match configured native mode')
            return NativeValidation('VALID',tuple(checks))
        except (ValueError,TypeError,KeyError,AttributeError) as error:
            return NativeValidation('INVALID',(str(error),))
    def reconstruct(self,partial,constraints=None):
        if not isinstance(partial,dict):raise ValueError('Partial Western assignment mapping required')
        constraints=constraints or {}
        if set(constraints)-{'mode'}:raise ValueError('Unsupported native constraint')
        ratios=tuple(partial.get('ratios',()))
        if ratios and len(ratios)!=7:raise ValueError('Seven degree positions required')
        tonic=exact(partial.get('tonic','1'))
        if tonic<=0:raise ValueError('Positive specified tonic required')
        names=(constraints['mode'],) if 'mode' in constraints else self.core.MODE_NAMES
        if any(name not in self.core.MODE_NAMES for name in names):raise ValueError('Unknown mode constraint')
        known=tuple(None if r is None else exact(r) for r in ratios)
        solutions=[]
        for name in names:
            predicted=tuple(r*tonic for r in self.core.mode(name)['ratios'])
            if known and all(r is None or r==predicted[i] for i,r in enumerate(known)):
                solutions.append({'mode':name,'ratios':tuple(map(str,predicted))})
        if not ratios or all(r is None for r in ratios):
            status='NOT_EVALUATED';identity='INSUFFICIENT_INPUT';outcome='UNSUPPORTED'
        elif not solutions:status='CONTRADICTION';identity='NO_FEASIBLE_SOLUTION';outcome='UNSUPPORTED'
        else:
            status='INCOMPLETE' if None in ratios else 'VALID'
            identity='UNIQUE_UNDER_MODEL' if len(solutions)==1 else 'MULTIPLE_DISTINGUISHABLE'
            outcome='AMBIGUOUS_UNDERDETERMINED' if len(solutions)!=1 else 'UNSUPPORTED'
        candidates=CandidateSet(tuple(solutions),True,tuple(names),'Mode names and exact degree assignments remain distinguishable')
        return ReconstructionReceipt('NOT_EVALUATED' if status=='NOT_EVALUATED' else 'EVALUATED',outcome,
            {'status':status,'known_positions':sum(r is not None for r in known),'required':7},
            {'status':'NOT_EVALUATED','reason':'No evaluated coding scheme'},
            {'status':identity,'candidate_count':len(solutions)},
            {'status':'NOT_VERIFIED','reason':'Native completion does not establish a historical reconstruction'},
            candidates,{'tonic':str(tonic),'mode_constraint':constraints.get('mode'),'namespace':self.namespace,
                        'finite_domain_exhausted':True,'cross_orientation_used':False})
    def describe(self,evidence=None,coding_scheme=None):
        return DescriptionLength('NOT_EVALUATED',None,'No independently evaluated coding scheme or historical baseline supplied')
    def transform_events(self,encoding,interval,time_factor=Fraction(1)):
        if self.validate_native(encoding).status!='VALID':raise ValueError('Valid source-bound encoding required')
        factor=exact(time_factor)
        if factor<=0:raise ValueError('Positive rhythm multiplier required')
        return tuple(WesternObservation(o.record_id,o.ratio*interval.ratio,o.onset*factor,o.duration*factor,o.voice,o.source_ref)
                     for o in encoding.observations)
    def tetrachord(self):
        steps=(Fraction(9,8),Fraction(9,8),Fraction(256,243))
        return {'steps':steps,'span':steps[0]*steps[1]*steps[2],
                'status':'PROFILE_SPECIFIC_DERIVATION','source_ref':'plato:timaeus:35b-36b',
                'scope':'One tone-tone-limma division; not every ancient Greek genus or tuning'}
    def length_action(self,length,operator):
        ratios={'fifth':Fraction(2,3),'fourth':Fraction(3,4),'octave':Fraction(1,2)}
        value=exact(length)
        if value<=0 or operator not in ratios:raise ValueError('Positive length and known native interval required')
        return value*ratios[operator]
