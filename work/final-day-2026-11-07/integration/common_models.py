"""Common native API wrapper; no cross-orientation correspondence is created."""
from pathlib import Path
from dataclasses import fields
from collections.abc import Mapping
import hashlib,inspect,json,sys

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
PROJECT=BASE.parents[1]
for path in (PROJECT/'work/unit001',BASE):
    if str(path) not in sys.path:sys.path.insert(0,str(path))
from contracts import EncodedModel,NativeValidation,DescriptionLength
from evidence import serialize
import baseline

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

class CommonOrientation:
    """Preserve native validation and make encode(evidence,profile) uniform.

    This adapter never passes one orientation's results to another. The only
    admitted profile is the actual profile already configured by its native model.
    """
    def __init__(self,native,default_profile_id=None):
        self.native=native
        self.native_module=sys.modules[type(native).__module__]
        configured=getattr(native,'profile',None)
        if isinstance(configured,Mapping) and 'profile_id' in configured:
            self.kind='COMMON';actual=configured['profile_id']
        elif hasattr(native,'core_sha256') and getattr(native,'namespace','').startswith('western:'):
            self.kind='WESTERN';actual=native.namespace
        else:raise ValueError('No supported, explicit native profile contract')
        if default_profile_id is not None and default_profile_id!=actual:
            raise ValueError('Default profile differs from the admitted native profile')
        self.default_profile_id=actual
        self.namespace=native.namespace
    def _select(self,profile):
        if profile is not None and profile!=self.default_profile_id:
            raise ValueError('Unadmitted source profile')
    def encode(self,evidence=None,profile=None):
        self._select(profile)
        native=self.native.encode(evidence)
        if isinstance(native,EncodedModel):
            if native.profile_id!=self.default_profile_id:raise ValueError('Native profile identity changed')
            return native
        if self.kind!='WESTERN':raise ValueError('Unsupported native encoding')
        payload=json.loads(self.native_module.canonical_json(native.observations))
        profile_path=Path(self.native_module.__file__).parent/'source-profiles.json'
        binding={'native_kind':'WESTERN','raw_evidence':native.raw_evidence,
                 'evidence_sha256':native.evidence_sha256,'core_sha256':native.core_sha256,
                 'kind':native.kind,'mode':native.mode,'native_program_sha256':sha(self.native_module.__file__),
                 'profile_catalog_sha256':sha(profile_path)}
        profile_hash=hashlib.sha256(serialize({'profile_id':self.default_profile_id,
            'core_sha256':native.core_sha256,'profile_catalog_sha256':binding['profile_catalog_sha256']}).encode('utf-8')).hexdigest()
        return EncodedModel(self.namespace,self.default_profile_id,profile_hash,tuple(payload),(),(),binding)
    def validate_native(self,evidence):
        if evidence is None:return NativeValidation('NOT_EVALUATED',('No common native input supplied',))
        if not isinstance(evidence,EncodedModel):return NativeValidation('INVALID',('Common EncodedModel required',))
        try:
            self._select(evidence.profile_id)
            if self.kind=='WESTERN':
                raw=json.loads(evidence.evidence_graph['raw_evidence'])
                expected=self.encode(raw,evidence.profile_id)
                native=self.native.encode(raw)
            else:
                expected=self.encode(None,evidence.profile_id);native=evidence
            if serialize(evidence)!=serialize(expected):raise ValueError('Common encoding differs from complete native/source binding')
            return self.native.validate_native(native)
        except (ValueError,TypeError,KeyError,AttributeError) as error:
            return NativeValidation('INVALID',(str(error),))
    def reconstruct(self,partial,constraints=None):
        return self.native.reconstruct(partial,constraints)
    def to_json(self,encoded):
        if self.validate_native(encoded).status!='VALID':raise ValueError('Invalid common encoding')
        return serialize(encoded)
    def from_json(self,text):
        payload=json.loads(text)
        required={f.name for f in fields(EncodedModel)}
        if not isinstance(payload,dict) or payload.get('__type__')!='EncodedModel' or set(payload)-{'__type__'}!=required:
            raise ValueError('Common encoding schema required')
        result=EncodedModel(**{k:v for k,v in payload.items() if k!='__type__'})
        if self.validate_native(result).status!='VALID':raise ValueError('Serialized source binding invalid')
        return result
    def _program_files(self):
        module=self.native_module
        paths=[Path(module.__file__)]
        for name in ('CORE_PATH','LEGACY_PATH'):
            value=getattr(module,name,None)
            if value is not None:paths.append(Path(value))
        profile=Path(module.__file__).parent/'source-profiles.json'
        if profile.exists():paths.append(profile)
        return tuple(dict.fromkeys(paths))
    def description_measurement(self,evidence):
        if self.validate_native(evidence).status!='VALID':raise ValueError('Valid common native encoding required for measurement')
        # All native assignment fields and sequence order survive the prefix code.
        # The evidence graph is explicitly given side information, not silently costed at zero.
        pairs=tuple((self.namespace+':assignment',serialize(record)) for record in evidence.assignments)
        coded=baseline.encode_literal(pairs)
        if baseline.decode(coded['bits'])!=pairs:raise ValueError('Native assignment code failed exact recovery')
        programs=self._program_files();program_bytes=sum(p.stat().st_size for p in programs)
        adapter_bytes=Path(__file__).stat().st_size
        model_bits=8*program_bytes+coded['model_bits']
        adapter_bits=8*adapter_bytes
        total=model_bits+adapter_bits+coded['data_bits']
        return {'scheme':'lossless-typed-v1','payload_scheme':coded['scheme'],
            'conditional_on':'Preserved source evidence graph, profile selection, shared result contracts and this declared codec implementation',
            'assignment_records':len(pairs),'roundtrip':'EXACT','model_bits':model_bits,'adapter_bits':adapter_bits,
            'data_given_model_bits':coded['data_bits'],'conditional_total_bits':total,
            'native_program_and_profile_bytes':program_bytes,'adapter_program_bytes':adapter_bytes,
            'native_program_files':{str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in programs},
            'adapter_sha256':sha(__file__),'shared_codec_program_bytes':Path(inspect.getfile(baseline)).stat().st_size,
            'shared_codec_sha256':sha(inspect.getfile(baseline)),
            'given_evidence_graph_utf8_bytes':len(serialize(evidence.evidence_graph).encode('utf-8')),
            'historical_comparison':'NOT_EVALUATED',
            'interpretation':'Reproducible conditional representation code; not an optimized generative MDL, held-out advantage or historical identification'}
    def describe(self,evidence=None,coding_scheme=None):
        if coding_scheme!='lossless-typed-v1':
            return DescriptionLength('NOT_EVALUATED',None,'An explicit supported coding scheme is required')
        if evidence is None:return DescriptionLength('NOT_EVALUATED',None,'No encoded evidence supplied')
        measured=self.description_measurement(evidence)
        return DescriptionLength('MEASURED_CONDITIONAL_CODE',measured['conditional_total_bits'],
            json.dumps(measured,ensure_ascii=False,sort_keys=True,separators=(',',':')))
