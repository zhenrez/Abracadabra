"""T_split: typed expansion and parity, not an isomorphism of unequal sets.

Let P={2,3,4,11,17,22}. The tagged state domain is
S={(i,0):i in C22} union {(i,1):i in P}, so |S|=28.
Toggle is (i,b)->(i,b xor 1), restricted to P; other nodes are fixed.
Explicit enumeration of S is bijective with S, not with C22.
Historical inventories are separate emission tables with unmatched entries.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping
from vowel_drift import CARRIER

FRICATIVES=MappingProxyType({2:'v',3:'ɣ',4:'ð',11:'x',17:'f',22:'θ'})
UG_VALUES='ʔa b g x d h w z ħ tˤ j k ʃ l m ð n zˤ s ʕ p sˤ q r θ ɣ t ʔi ʔu s'.split()
AR_VALUES='ʔ/aː b t θ dʒ ħ x d ð r z s ʃ sˤ dˤ tˤ ðˤ ʕ ɣ f q k l m n h w/uː j/iː'.split()

@dataclass(frozen=True)
class State:
    source_index: int
    parity: int=0

class Script(ABC):
    def __init__(self,source:Mapping[int,str]):
        if dict(source)!=dict(CARRIER) or any(type(k) is not int for k in source):
            raise ValueError('Expected the exact indexed C22 carrier')
        self.source=MappingProxyType(dict(source))
    def validate(self,state):
        if type(state.source_index) is not int or state.source_index not in self.source:
            raise ValueError('Source index outside 1..22')
        if type(state.parity) is not int or state.parity not in (0,1):
            raise ValueError('Parity must be 0 or 1')
        if state.parity and state.source_index not in FRICATIVES:
            raise ValueError('Parity cannot overwrite a non-plosive node')
    def emit(self,state):
        self.validate(state)
        return FRICATIVES[state.source_index] if state.parity else self.source[state.source_index]
    @abstractmethod
    def transform(self): pass

class ParityScript(Script):
    def toggle(self,state):
        self.validate(state)
        return State(state.source_index,state.parity^1) if state.source_index in FRICATIVES else state
    def transform(self):
        return [dict(source_index=i,target_index=i,index_delta=0,operator='T_split/parity' if i in FRICATIVES else 'identity',
                     states=[dict(parity=b,phoneme=self.emit(State(i,b))) for b in ((0,1) if i in FRICATIVES else (0,))]) for i in self.source]

class ExpansionScript(Script):
    def transform(self):
        states=[State(i) for i in self.source]+[State(i,1) for i in FRICATIVES]
        return [dict(source_index=s.source_index,target_index=j,index_delta=j-s.source_index,
                     operator='T_split/explicit' if s.parity else 'identity',parity=s.parity,phoneme=self.emit(s))
                for j,s in enumerate(states,1)]

class InventoryScript(Script):
    def __init__(self,source,name,values):
        super().__init__(source); self.name=name; self.values=tuple(values)
    def transform(self):
        # Candidate relations may be many-to-one; never resolve ambiguity by index guessing.
        state_domain=[State(i) for i in self.source]+[State(i,1) for i in FRICATIVES]
        rows=[]
        for j,value in enumerate(self.values,1):
            matches=[s for s in state_domain if self.emit(s)==value]
            candidates=[dict(source_index=s.source_index,parity=s.parity,index_delta=j-s.source_index) for s in matches]
            rows.append(dict(target_index=j,phoneme=value,operator='T_split/emission' if matches else 'extension/unmatched',
                             source_index=matches[0].source_index if len(matches)==1 else None,
                             index_delta=j-matches[0].source_index if len(matches)==1 else None,
                             candidates=candidates,extension_id=f'{self.name}:{j}' if not matches else None))
        return rows

class DriftEngine:
    def __init__(self,source=CARRIER):
        self.parity=ParityScript(source); self.expansion=ExpansionScript(source)
        self.inventories={'ugaritic':InventoryScript(source,'ugaritic',UG_VALUES),
                          'arabic':InventoryScript(source,'arabic',AR_VALUES)}
    def transform(self,mode='parity',target=None):
        if mode=='parity':
            if target not in (None,'hebrew','syriac'):raise ValueError('Unsupported parity target')
            rows=self.parity.transform()
        elif mode=='expansion':
            if target is None:rows=self.expansion.transform()
            elif target in self.inventories:rows=self.inventories[target].transform()
            else:raise ValueError('Unknown expansion target')
        else:raise ValueError('mode must be parity or expansion')
        indices=[r['target_index'] for r in rows]
        if len(indices)!=len(set(indices)):raise ValueError('Target index collision')
        return dict(mode=mode,target=target,carrier_size=22,tagged_split_state_count=28,
                    target_columns=len(rows),rows=rows,
                    scope='Stipulated encoding of supplied readings; no historical chronology or phonological conditioning inferred')
    def inverse_candidates(self,target_index,target):
        rows=self.transform('expansion',target)['rows']
        if type(target_index) is not int or not 1<=target_index<=len(rows):raise ValueError('Target index out of bounds')
        return rows[target_index-1]['candidates']

if __name__=='__main__':
    import json
    engine=DriftEngine()
    print(json.dumps(dict(ugaritic=engine.transform('expansion','ugaritic'),
                         hebrew=engine.transform('parity','hebrew')),ensure_ascii=True,indent=2))
