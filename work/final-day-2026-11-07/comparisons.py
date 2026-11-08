"""Exact typed mathematical controls; historical reconstruction remains guarded."""
from dataclasses import dataclass
from fractions import Fraction as Q

def exact(value):
    if type(value) not in (int,str,Q):raise ValueError('Exact rational required; floats and Booleans are rejected')
    try:result=Q(value)
    except (ValueError,ZeroDivisionError) as error:raise ValueError('Invalid rational') from error
    if result<=0 or max(result.numerator.bit_length(),result.denominator.bit_length())>16384:
        raise ValueError('Positive bounded rational required')
    return result

@dataclass(frozen=True)
class ScalarOperator:
    name:str;quantity_type:str;factor:object
    def __post_init__(self):
        if not self.name or self.quantity_type not in ('length_ratio','frequency_ratio'):raise ValueError('Explicit typed scalar operator required')
        object.__setattr__(self,'factor',exact(self.factor))
    def apply(self,value):return exact(value)*self.factor
@dataclass(frozen=True)
class QuantityAdapter:
    source_type:str;target_type:str;kind:str;scale:object
    def __post_init__(self):
        if self.kind not in ('identity','reciprocal'):raise ValueError('Unregistered mathematical adapter kind')
        if self.kind=='identity' and self.source_type!=self.target_type:raise ValueError('Identity adapter cannot change quantity types')
        if self.kind=='reciprocal' and {self.source_type,self.target_type}!={'length_ratio','frequency_ratio'}:
            raise ValueError('Reciprocal conversion requires explicit length/frequency types')
        if self.source_type not in ('length_ratio','frequency_ratio') or self.target_type not in ('length_ratio','frequency_ratio'):
            raise ValueError('Unknown adapter quantity type')
        object.__setattr__(self,'scale',exact(self.scale))
    def apply(self,value):
        value=exact(value);return self.scale*value if self.kind=='identity' else self.scale/value

def commutation(source,target,adapter,inputs):
    if source.quantity_type!=adapter.source_type or target.quantity_type!=adapter.target_type:
        raise ValueError('Operator/adapter diagram is not composable')
    inputs=tuple(exact(v) for v in inputs)
    if not inputs or len(inputs)>1024:raise ValueError('Declared finite control inputs1..1024required')
    cases=[]
    for value in inputs:
        left=adapter.apply(source.apply(value));right=target.apply(adapter.apply(value))
        cases.append({'input':str(value),'source_then_adapter':str(left),'adapter_then_target':str(right),'residual':str(left-right)})
    coefficient=adapter.scale*(source.factor-target.factor) if adapter.kind=='identity' else adapter.scale*(1/source.factor-target.factor)
    preserved=coefficient==0
    if preserved!=all(row['residual']=='0' for row in cases):raise AssertionError('Finite and symbolic controls disagree')
    return {'status':'PRESERVED_UNDER_DECLARED_ADAPTER' if preserved else 'COUNTEREXAMPLE','cases':tuple(cases),
        'tolerance':{'kind':'EXACT_RATIONAL','value':'0'},'uniform_residual_coefficient':str(coefficient),
        'uniform_argument':'residual=c*x on positive rationals' if adapter.kind=='identity' else 'residual=c/x on positive rationals',
        'source_operator':source.name,'target_operator':target.name,
        'adapter':{'kind':adapter.kind,'scale':str(adapter.scale),'source_type':adapter.source_type,'target_type':adapter.target_type},
        'source_evidence_role':'DECLARED_MATHEMATICAL_CONTROL','historical_support':'NOT_VERIFIED',
        'historical_holdout':False,'model_preference':'NOT_EVALUATED'}

def adapter_candidates(source,target,candidates,inputs):
    candidates=tuple(candidates);inputs=tuple(inputs)
    if len(candidates)>128:raise ValueError('Declared candidate family exceeds128')
    if any(not isinstance(candidate,QuantityAdapter) for candidate in candidates) or len(set(candidates))!=len(candidates):
        raise ValueError('Unique typed adapter definitions required')
    outcomes=tuple(commutation(source,target,a,inputs) for a in candidates)
    survivors=tuple(r for r in outcomes if r['status']=='PRESERVED_UNDER_DECLARED_ADAPTER')
    return {'survivors':survivors,'evaluations':outcomes,'candidate_family_exhausted':True,
        'identifiability':'NO_FEASIBLE_SOLUTION' if not survivors else 'UNIQUE_UNDER_DECLARED_FINITE_MODEL' if len(survivors)==1 else 'MULTIPLE_DISTINGUISHABLE',
        'historical_support':'NOT_VERIFIED','equivalence':'No quotient of differing scale/register parameters has been asserted'}

def historical_reconstruct(value):
    raise PermissionError('Historical G7 remains locked pending independently validated source-specific adapters and holdout evidence')
