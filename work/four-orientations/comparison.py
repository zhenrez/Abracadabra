"""Typed operator preservation and survivor semantics; no automatic promotion."""
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class Map:
    name:str
    domain:str
    codomain:str
    kind:str
    function:Callable

def preservation(samples,source_operator,target_operator,adapter_before,adapter_after):
    s,t,a,b=source_operator,target_operator,adapter_before,adapter_after
    if not (s.domain==a.domain and s.codomain==b.domain and a.codomain==t.domain and b.codomain==t.codomain):
        raise ValueError('Noncomposable typed diagram')
    allowed={'identity','order','function','generation','realization'}
    if any(m.kind not in allowed for m in (s,t,a,b)):raise ValueError('Unsupported transformation kind')
    if s.kind!=t.kind:raise ValueError('Operator relation kinds differ; supply a separately justified bridge')
    samples=tuple(samples)
    if not samples:raise ValueError('Nonempty evidence domain required')
    residuals=[]
    for x in samples:
        left=b.function(s.function(x));right=t.function(a.function(x))
        if left!=right:residuals.append(dict(input=str(x),source_path=str(left),target_path=str(right)))
    return dict(status='preserved_on_test_domain' if not residuals else 'falsified_on_test_domain',
                tested=len(samples),residuals=residuals,historical_equivalence=False)

def reconstruct(candidates,finite_domain_complete=False,independent_evidence=False):
    """Candidates are externally filtered survivors, never created by slot count."""
    candidates=tuple(candidates)
    if not candidates:return dict(status='falsified' if finite_domain_complete else 'unsupported',survivors=[])
    determined=len(candidates)==1 and finite_domain_complete and independent_evidence
    return dict(status='determined' if determined else 'ambiguous',survivors=list(candidates),
                scope='declared candidate family only',cross_orientation_permission=determined)
