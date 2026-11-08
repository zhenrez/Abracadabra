"""Small shared contracts; downstream orientations have no implementations here."""
from dataclasses import dataclass
from typing import Protocol
import json
from evidence import Immutable

@dataclass(frozen=True)
class NativeValidation(Immutable):
    status:str;checks:tuple;receipt:object=None
@dataclass(frozen=True)
class EncodedModel(Immutable):
    model_namespace:str;profile_id:str;profile_hash:str;assignments:tuple;unassigned_records:tuple;unmatched_values:tuple
    evidence_graph:object=None
@dataclass(frozen=True)
class CandidateSet(Immutable):
    solutions:tuple;complete:bool;domain:tuple;equivalence:str='Assignments are distinguished by input position and canonical slot'
@dataclass(frozen=True)
class DescriptionLength(Immutable):
    status:str;bits:object;reason:str
@dataclass(frozen=True)
class ReconstructionReceipt(Immutable):
    execution:str;outcome:str;structural:object;model_preference:object;identifiability:object;historical:object;candidates:CandidateSet;premises:object
class OrientationModel(Protocol):
    def validate_native(self,evidence)->NativeValidation:...
    def encode(self,evidence,profile)->EncodedModel:...
    def reconstruct(self,partial,constraints=None)->ReconstructionReceipt:...
    def describe(self,evidence,coding_scheme)->DescriptionLength:...
class CrossOrientationAdapter(Protocol):
    source_model:str;target_model:str;domain:object;codomain:object
    proposed_mapping:object;operator_correspondence:object;evaluation_inputs:object
    tolerance:object;commutation_result:object;evidence_dependencies:object
class CrossOrientationRegistry:
    """Unit001 has no unlock API, runtime config or environment bypass."""
    __slots__=()
    @property
    def adapters(self):return ()
    def register(self,adapter):raise PermissionError('G7 LOCKED: registration unauthorized in Unit001')
    def evaluate(self,*args,**kwargs):raise PermissionError('G7 LOCKED: cross-model evaluation unauthorized')
    def to_json(self):return '{"adapters":[],"g7":false}'
    @classmethod
    def from_json(cls,text):
        if json.loads(text)!={'adapters':[],'g7':False}:raise PermissionError('Locked runtime rejects populated or unlocked configuration')
        return cls()
