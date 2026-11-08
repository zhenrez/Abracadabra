"""Conditional 3/7/12 slot validator, not a test of acoustic/historical truth.

Base domain has 3+7+12=22 slots. Tagged expansion has 3+2*7+12=29
states. There is a projection from expanded states to roots, not a bijection
between unequal domains. Category-preserving permutations alone leave
3!*7!*12! possibilities: counts do not identify a unique acoustic mapping.
"""
import json,math
import numpy as np
import networkx as nx
from scipy.spatial.distance import cdist

GROUPS={'Mothers':('ʔ','m','ʃ'),'Doubles':('b','g','d','k','p','r','t'),
        'Simples':('h','w','z','ħ','tˤ','j','l','n','s','ʕ','sˤ','q')}
ALIASES={'a':'ʔ','∫':'ʃ','ћ':'ħ','ℏ':'ħ','tˁ':'tˤ','sˁ':'sˤ','t^ʕ':'tˤ','s^ʕ':'sˤ'}
ALTERNATES={'v':'b','ɣ':'g','ð':'d','x':'k','f':'p','θ':'t'}

class HarmonicPhoneticVerifier:
    def __init__(self,mode='base',context=None):
        if mode not in ('base','expanded'):raise ValueError('mode must be base or expanded')
        self.mode=mode;self.context=context or {}
        self.slots={}
        for group,roots in GROUPS.items():
            for root in roots:
                for bit in ((0,1) if mode=='expanded' and group=='Doubles' else (0,)):
                    key=f'{root}:{bit}' if mode=='expanded' and group=='Doubles' else root
                    self.slots[key]=(group,root,bit)

    def candidates(self,token):
        if token in (None,'','?'):return set()
        if not isinstance(token,str):raise ValueError('Symbols must be strings or null')
        result=set()
        for part in token.split('/'):
            part=ALIASES.get(part,part)
            if part in self.slots:result.add(part)
            if self.mode=='expanded':
                if part in GROUPS['Doubles']:result.add(part+':0')
                if part in ALTERNATES:result.add(ALTERNATES[part]+':1')
            # User's shin/s mother alternative is deliberately ambiguous.
            if part=='s':result.add('ʃ')
        return {s for s in result if token not in self.context or self.slots[s][0]==self.context[token]}

    def validate(self,symbols):
        symbols=list(symbols);known=[(i,s) for i,s in enumerate(symbols) if s not in (None,'','?')]
        graph=nx.Graph();left=[('input',i) for i,s in known];right=[('slot',s) for s in self.slots]
        graph.add_nodes_from(left,bipartite=0);graph.add_nodes_from(right,bipartite=1)
        for i,s in known:
            for slot in sorted(self.candidates(s)):graph.add_edge(('input',i),('slot',slot))
        def match(g):return nx.algorithms.bipartite.maximum_matching(g,top_nodes=left)
        matching=match(graph);occupied={matching[n][1] for n in left if n in matching}
        matched=len(occupied);required=len(self.slots)
        feasible=matched==len(known)
        # A slot can be absent in a completion iff all known tokens still match
        # after deleting it. This retains ambiguity without choosing a winner.
        missing_candidates=[]
        if feasible and matched<required:
            for slot in self.slots:
                reduced=graph.copy();reduced.remove_node(('slot',slot))
                m=match(reduced)
                if sum(n in m for n in left)==len(left):missing_candidates.append(slot)
        distribution={g:[] for g in GROUPS}
        for slot in sorted(occupied):distribution[self.slots[slot][0]].append(slot)
        valid=feasible and len(symbols)==required and matched==required
        suggestion=missing_candidates[0] if feasible and required-matched==1 and len(missing_candidates)==1 else None
        issues=[]
        if len(symbols)!=required:issues.append('count differs from configured structure')
        if not feasible:issues.append('unknown symbol or competing occupancy; no injective assignment')
        if len(symbols)>29:issues.append('harmonic dissonance: user-defined count-limit flag only')
        if matched<required:issues.append('incomplete structural coverage')
        return dict(status='Valid' if valid else 'Invalid',validation_scope='stipulated structural model only',
          matrix_distribution=distribution,distribution_scope='one maximum matching; ambiguous assignments are not independently identified',
          harmonic_checksum=dict(current_sum=len(symbols),required_sum=required,matched_slots=matched),
          symmetry_gap=dict(unfilled_slots=required-matched,unassigned_known=len(known)-matched,
                            possible_missing_slots=missing_candidates),
          structural_distance=required-matched+len(known)-matched,
          harmonic_distance=None,reconstruction_suggestion=suggestion,
          suggestion_scope='Unique completion only within supplied slot model; not historical confirmation',
          input_candidates=[dict(index=i,symbol=s,slots=sorted(self.candidates(s))) for i,s in known],
          issues=issues,frequency_mapping_status='No tuning or phoneme-frequency map supplied')

    @staticmethod
    def harmonic_series(fundamental=110.0,count=16):
        if not np.isfinite(fundamental) or fundamental<=0 or type(count) is not int or count<1:raise ValueError('Positive fundamental/count required')
        return fundamental*np.arange(1,count+1,dtype=float)

    @staticmethod
    def frequency_distance(frequencies,reference):
        """Nearest absolute cents distance to explicitly supplied frequencies."""
        a=np.asarray(frequencies,dtype=float);b=np.asarray(reference,dtype=float)
        if a.ndim!=1 or b.ndim!=1 or not len(a) or not len(b) or not np.isfinite(a).all() or not np.isfinite(b).all() or np.any(a<=0) or np.any(b<=0):raise ValueError('Finite positive frequency arrays required')
        return cdist((1200*np.log2(a))[:,None],(1200*np.log2(b))[:,None],metric='cityblock').min(axis=1)

if __name__=='__main__':
    base=[r for roots in GROUPS.values() for r in roots];engine=HarmonicPhoneticVerifier()
    expanded=HarmonicPhoneticVerifier('expanded')
    examples=dict(complete=engine.validate(base),missing_m=engine.validate([r for r in base if r!='m']),
                  duplicate=engine.validate(base[:-1]+['b']),expanded=expanded.validate(list(expanded.slots)),
                  harmonic_series_hz=engine.harmonic_series().tolist(),
                  octave_distance_cents=engine.frequency_distance([220],[110]).tolist())
    print(json.dumps(examples,ensure_ascii=True,indent=2))
