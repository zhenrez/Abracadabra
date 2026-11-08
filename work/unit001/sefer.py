"""G1 adapter. Only the frozen Sefer implementation and G0 records are dependencies."""
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
import hashlib,importlib.util,itertools,json
from evidence import Immutable,PhoneticType,validate_graph,serialize
from contracts import NativeValidation,EncodedModel,CandidateSet,DescriptionLength,ReconstructionReceipt

ROOT=Path(__file__).resolve().parent
NAMES=('aleph','bet','gimel','dalet','he','waw','zayin','het','tet','yod','kaf','lamed','mem','nun','samekh','ayin','pe','tsadi','qof','resh','shin','taw')
ALIASES=('ʔ','b','g','d','h','w','z','ħ','tˤ','j','k','l','m','n','s','ʕ','p','sˤ','q','r','ʃ','t')
SLOT_ALIASES=MappingProxyType({'sefer:letter:'+n:a for n,a in zip(NAMES,ALIASES)})
@dataclass(frozen=True)
class Profile(Immutable):
    profile_id:str;script_label:str;baseline_hash:str

class SeferModel:
    namespace='sefer:stipulated-legacy-3-7-12'
    def __init__(self):
        path=ROOT/'frozen/sefer/harmonic_verifier.py'
        manifest=json.loads((ROOT/'source-manifest.json').read_text(encoding='utf-8'))
        self.baseline_hash=hashlib.sha256(path.read_bytes()).hexdigest()
        if self.baseline_hash!=manifest['baseline']['harmonic_verifier.py']['sha256']:raise ValueError('Frozen baseline integrity failure')
        spec=importlib.util.spec_from_file_location('unit001_frozen_sefer',path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.legacy_module=module
        self.categories=MappingProxyType({slot:next(g for g,values in module.GROUPS.items() if alias in values) for slot,alias in SLOT_ALIASES.items()})

    def legacy(self,symbols,mode='base',context=None):
        return self.legacy_module.HarmonicPhoneticVerifier(mode,context).validate(symbols)

    def state_inventory(self,mode='base'):
        if mode not in ('base','expanded'):raise ValueError('Invalid mode')
        result={}
        for slot,alias in SLOT_ALIASES.items():
            double=self.categories[slot]=='Doubles'
            for bit in ((0,1) if mode=='expanded' and double else (0,)):
                key=slot+':state:'+str(bit) if mode=='expanded' and double else slot
                result[key]=MappingProxyType(dict(letter_id=slot,category=self.categories[slot],state=bit,
                    legacy_label=alias+':'+str(bit) if mode=='expanded' and double else alias,
                    phonetic_realization=alias if bit==0 else None,
                    epistemic_status='STIPULATED_BASELINE',alternate_phonetic_attestation='NOT_VERIFIED' if bit else None))
        return MappingProxyType(result)

    def slot_candidates(self,token,mode='base'):
        states=self.state_inventory(mode)
        if token in (None,'','?'):return tuple(states)
        if token in states:return (token,)
        if mode=='expanded' and token in SLOT_ALIASES:
            state=token+':state:0'
            return (state,) if state in states else (token,)
        labels=self.legacy_module.HarmonicPhoneticVerifier(mode).candidates(token)
        return tuple(sorted(key for key,value in states.items() if value['legacy_label'] in labels))

    def encode(self,evidence,profile):
        validate_graph(evidence)
        if not isinstance(profile,Profile) or profile.baseline_hash!=self.baseline_hash:raise ValueError('Explicit source-qualified profile required')
        records=[w for w in evidence.witnesses if w.script_label==profile.script_label]
        if not records:raise ValueError('Selected script has no evidence')
        assignments=[];unassigned=[];unmatched=[]
        for w in records:
            if w.phonetic_type!=PhoneticType.PHONEME_VALUE:
                unassigned.append(w.record_id);unmatched.append(dict(record_id=w.record_id,value=w.raw_supplied_ipa,reason=w.phonetic_type.value));continue
            candidates=self.slot_candidates(w.raw_supplied_ipa)
            assignments.append(dict(record_id=w.record_id,raw_cell_id=w.raw_cell_id,claim_refs=w.claim_refs,
                raw_ipa=w.raw_supplied_ipa,candidates=candidates,profile_id=profile.profile_id,
                assignment_status='STIPULATED_BASELINE_PROJECTION',historical_support='NOT_VERIFIED'))
            if not candidates:unmatched.append(dict(record_id=w.record_id,value=w.raw_supplied_ipa,reason='No slot candidate'))
        return EncodedModel(self.namespace,profile.profile_id,self.baseline_hash,tuple(assignments),tuple(unassigned),tuple(unmatched),evidence)

    def reconstruct(self,partial,constraints=None,mode='base',class_constraints=None):
        tokens=list(partial);states=self.state_inventory(mode);domain=tuple(states)
        constraints=constraints or {};class_constraints=class_constraints or {}
        for key in tuple(constraints)+tuple(class_constraints):
            if type(key) is not int or not 0<=key<len(tokens):raise ValueError('Constraint input index out of bounds')
        choices=[]
        for i,token in enumerate(tokens):
            candidates=set(self.slot_candidates(token,mode))
            if i in constraints:candidates&=set(constraints[i])
            if i in class_constraints:candidates={c for c in candidates if states[c]['category']==class_constraints[i]}
            choices.append(tuple(sorted(candidates)))
        solutions=[]
        if tokens and len(tokens)<=len(domain):
            order=sorted(range(len(tokens)),key=lambda i:(len(choices[i]),i))
            assignment=[None]*len(tokens)
            def visit(depth,used):
                if depth==len(order):
                    solutions.append(dict(assignments=tuple(assignment),unfilled=tuple(s for s in domain if s not in used)))
                    if len(solutions)>100000:raise RuntimeError('Candidate bound exceeded; no identifiability verdict issued')
                    return
                i=order[depth]
                for candidate in choices[i]:
                    if candidate not in used:
                        assignment[i]=candidate;visit(depth+1,used|{candidate})
            visit(0,set())
        solutions.sort(key=lambda s:s['assignments'])
        if not tokens:
            execution='NOT_EVALUATED';structural='NOT_EVALUATED';ident='INSUFFICIENT_INPUT';outcome='NOT_EVALUATED'
        elif not solutions:
            execution='EVALUATED';structural='CONTRADICTION';ident='NO_FEASIBLE_SOLUTION';outcome='UNSUPPORTED'
        else:
            execution='EVALUATED';structural='VALID' if len(tokens)==len(domain) else 'INCOMPLETE'
            ident='UNIQUE_UNDER_MODEL' if len(solutions)==1 else 'MULTIPLE_DISTINGUISHABLE'
            outcome='AMBIGUOUS_UNDERDETERMINED'
        conflict=[]
        if tokens and not solutions:
            conflict=[dict(input_index=i,token=token,admissible_slots=choices[i]) for i,token in enumerate(tokens)]
        return ReconstructionReceipt(execution,outcome,
            dict(status=structural,required=len(domain),input_count=len(tokens),constraints=dict(exclusive_occupancy=True,category_constraints=class_constraints),conflicts=conflict),
            dict(status='NOT_EVALUATED',reason='G6 locked; no coding scheme or model comparison'),
            dict(status=ident,solution_count=len(solutions),within_model_only=True),
            dict(status='NOT_VERIFIED',claim='This particular reconstruction is not historically confirmed by structural uniqueness'),
            CandidateSet(tuple(solutions),True,domain),
            dict(namespace=self.namespace,baseline_hash=self.baseline_hash,input_tokens=tokens,candidates=choices,mode=mode,
                 slot_constraints=constraints,class_constraints=class_constraints,cross_orientation_used=False))

    def validate_native(self,evidence):
        if not isinstance(evidence,EncodedModel) or not evidence.assignments:
            return NativeValidation('NOT_EVALUATED',('No selected Sefer evidence assignments',))
        if evidence.model_namespace!=self.namespace or evidence.profile_hash!=self.baseline_hash:raise ValueError('Foreign or unbound model input')
        if evidence.evidence_graph is None:raise ValueError('Native assignments require their immutable G0 evidence graph')
        validate_graph(evidence.evidence_graph)
        records={w.record_id:w for w in evidence.evidence_graph.witnesses}
        seen=set();seen_cells=set()
        for assignment in evidence.assignments:
            record_id=assignment['record_id'];cell_id=assignment['raw_cell_id']
            if record_id in seen or cell_id in seen_cells:raise ValueError('Duplicate assignment evidence identity')
            seen.add(record_id);seen_cells.add(cell_id)
            witness=records.get(record_id)
            if witness is None or witness.phonetic_type!=PhoneticType.PHONEME_VALUE:raise ValueError('Assignment is not a phonemic source witness')
            if not assignment['claim_refs'] or tuple(assignment['claim_refs'])!=witness.claim_refs:raise ValueError('Assignment claim binding differs from source witness')
            if cell_id!=witness.raw_cell_id or assignment['raw_ipa']!=witness.raw_supplied_ipa:raise ValueError('Assignment observation differs from source witness')
            if assignment['profile_id']!=evidence.profile_id:raise ValueError('Assignment belongs to a different profile')
        tokens=[a['raw_ipa'] for a in evidence.assignments]
        constrained={i:tuple(a['candidates']) for i,a in enumerate(evidence.assignments)}
        for i,t in enumerate(tokens):
            if not set(constrained[i])<=set(self.slot_candidates(t)):raise ValueError('Encoding contains ungrounded candidate')
        receipt=self.reconstruct(tokens,constraints=constrained)
        return NativeValidation(receipt.structural['status'],('Actual candidate membership','Exclusive occupancy','Class membership','State count'),receipt)

    def describe(self,evidence,coding_scheme):
        return DescriptionLength('NOT_EVALUATED',None,'G6 locked; no measured description length or historical preference')

    def pair_counts(self):
        letters=tuple(SLOT_ALIASES)
        return dict(base=len(letters),expanded=len(self.state_inventory('expanded')),
            undirected=len(tuple(itertools.combinations(letters,2))),
            directed_distinct=len(tuple(itertools.permutations(letters,2))),ordered_with_self=len(tuple(itertools.product(letters,repeat=2))))

    def possibility_graph(self,directed=False):
        import networkx as nx
        graph=nx.DiGraph() if directed else nx.Graph();graph.add_nodes_from(SLOT_ALIASES)
        graph.add_edges_from(itertools.permutations(SLOT_ALIASES,2) if directed else itertools.combinations(SLOT_ALIASES,2))
        graph.graph.update(namespace=self.namespace,evidence_status='COMBINATORIAL_POSSIBILITY_SPACE_NOT_ATTESTED_RELATIONS')
        return graph
