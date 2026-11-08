"""Deterministic, stipulated vowel drift; not a historical derivation or transliterator."""
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Iterable

CARRIER = MappingProxyType(dict(enumerate(
    ('ʔ','b','g','d','h','w','z','ħ','tˤ','j','k','l','m','n','s','ʕ','p','sˤ','q','r','ʃ','t'),1)))
LARYNGEALS = frozenset(('ʔ','h','ħ','ʕ'))

@dataclass(frozen=True)
class Correspondence:
    phoneme: str
    glyph: str
    target_index: int

@dataclass(frozen=True)
class Target:
    name: str
    mappings: Mapping[int, Correspondence]

    def __post_init__(self):
        copied=dict(self.mappings)
        for index,value in copied.items():
            if type(index) is not int or index not in CARRIER:
                raise ValueError('Invalid carrier index')
            if not isinstance(value,Correspondence) or not value.phoneme or not value.glyph:
                raise ValueError('Complete correspondence required')
            if type(value.target_index) is not int or value.target_index<1:
                raise ValueError('Invalid target index')
        object.__setattr__(self,'mappings',MappingProxyType(copied))

GREEK=Target('greek',{
    1:Correspondence('a','Α',1),5:Correspondence('e','Ε',5),
    8:Correspondence('ɛː','Η',7),16:Correspondence('o','Ο',15),
    10:Correspondence('i','Ι',9)})
LATIN=Target('latin',{
    1:Correspondence('a','A',1),5:Correspondence('e','E',5),
    8:Correspondence('h','H',8),16:Correspondence('o','O',14),
    10:Correspondence('i','I',9)})

class VowelDriftOperator:
    def __init__(self,targets=(GREEK,LATIN)):
        values=tuple(targets)
        if len({t.name for t in values})!=len(values):
            raise ValueError('Duplicate target name')
        self._targets=MappingProxyType({t.name:t for t in values})

    def apply_vowel_drift(self,carrier_index:int,target_language:str,*,
                          include_glide:bool=False,missing:str='identity')->str:
        """Return IPA. Strict core changes laryngeals only; /j/→/i/ is opt-in.

        missing='identity' preserves an unmapped laryngeal; 'error' rejects it.
        Non-laryngeal consonants always pass through, except the optional glide.
        """
        if type(carrier_index) is not int or carrier_index not in CARRIER:
            raise ValueError('Carrier index must be an integer from 1 through 22')
        if target_language not in self._targets:
            raise ValueError('Unknown target language: '+str(target_language))
        if missing not in ('identity','error'):
            raise ValueError('missing must be identity or error')
        source=CARRIER[carrier_index]
        if source not in LARYNGEALS and not (include_glide and source=='j'):
            return source
        mapping=self._targets[target_language].mappings.get(carrier_index)
        if mapping is not None: return mapping.phoneme
        if missing=='error': raise ValueError('No target mapping for '+source)
        return source

    def transform(self,indices:Iterable[int],target_language:str,**options)->list[str]:
        return [self.apply_vowel_drift(i,target_language,**options) for i in indices]

    @staticmethod
    def rotate_phase(vector:tuple[float,float])->tuple[float,float]:
        """Abstract R90(x,y)=(-y,x). No acoustic coordinates are inferred."""
        x,y=vector
        return -y,x

def apply_vowel_drift(carrier_index,target_language):
    return VowelDriftOperator().apply_vowel_drift(carrier_index,target_language)

if __name__=='__main__':
    import json
    operator=VowelDriftOperator()
    sample=[1,2,5,8,10,16,22]
    print(json.dumps(dict(indices=sample,source=[CARRIER[i] for i in sample],
        greek=operator.transform(sample,'greek'),latin=operator.transform(sample,'latin'),
        greek_with_glide=operator.transform(sample,'greek',include_glide=True),
        latin_with_glide=operator.transform(sample,'latin',include_glide=True)),ensure_ascii=True,indent=2))
