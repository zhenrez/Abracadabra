"""Source-bound GEN/TIME/ADR and conditional class-carry reconstruction. No DB writes."""
from pathlib import Path
from fractions import Fraction
from itertools import combinations
from math import gcd
from functools import reduce
from datetime import datetime, timezone
import hashlib, json, sqlite3, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def normalize_octave(value):
    while value>=2:value/=2
    while value<1:value*=2
    return value
def main():
    selection=json.loads((ROOT/'docs/evidence/generational-hypotheses-superjev.json').read_text(encoding='utf-8-sig'))
    assert selection['answers']['hypotheses']['winner']=='joint_typed_constraints'
    c=sqlite3.connect('file:'+(ROOT/'data/sunny.sqlite').as_posix()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
    source_specs=[
        ('master_score','47d7a9f6cc9a98a17ff592a7c0062cfad491735ce1cc208c2d4583df5c41f03e',None),
        ('cainan_stage_witnesses','e5ab0e305e8ceb3a77ec964ab8948ae7970ff38bd6fc217fc26c3a035f0af35a','# SUN / SOL - Cainan:'),
        ('cainan_macro_transport','478d7777640329b833848daafd6825d3a03300b5f7e7943960d7fc02f8957aa8','# SUN / SOL - The rhythms interact'),
        ('generation_address_distinction','7d17a770e67579e27609f9ad54813118fd0644e422d225ed0949ed18f805dab3','# SUN / SOL - Cainan → Eldad'),
        ('age_year_time_limit','047bd2839c8b7373e7a761f42de29fc9a1dfcc3540c9eb3bc7df95995a3f2f03',None),
        ('two_turn_class_hunch','d39740a667f7d58443bcd8ba1784d40e8d8a83c9769c6725d57bb532c8fa1e50',None),
        ('sophia_boundary_aliases','733cd9c16b68b2df504f05d4fefb8a7df84c22c83ac9a4963e79a8626cfd2041',None),
        ('insertion_fifth_spiral','d281215afcf4aa5fc7ffaa0396dda5fa843359cd72d5ad1d523b392334ff114e',None),
    ]
    baseline=json.loads((ROOT/'state/reconstruction/coverage.json').read_text(encoding='utf-8'))
    linked={mid for m in baseline['reconstruction_module_references'].values() for mid in m['message_ids']}
    evidence=[]
    for name,mid,anchor in source_specs:
        r=c.execute('select m.*,s.path source_path,s.sha256 source_sha256,s.original_path,c.title from messages m join sources s on s.id=m.source_id join conversations c on c.id=m.conversation_id where m.id=?',(mid,)).fetchone()
        raw=Path(r['source_path']).read_bytes();assert sha(raw)==r['source_sha256']
        text=r['text'];assert sha(text.encode())==r['content_sha256']
        start=text.index(anchor) if anchor else 0
        end=len(text)
        if name=='insertion_fifth_spiral':end=text.index('SUN\'s musical evaluation',start)
        quote=text[start:end]
        evidence.append({'id':name,'message_id':mid,'message_role':r['role'],'source_role_detail':
            'User-supplied analytical passage; inner authorship not inferred from outer message role.' if name in ['master_score','insertion_fifth_spiral'] else
            'Direct user correction/hunch, with qualifiers retained.' if r['role']=='user' else 'Historical assistant-reported source result, not newly verified critical-edition evidence.',
            'source_id':r['source_id'],'source_path':r['source_path'],'original_path':r['original_path'],
            'source_sha256':r['source_sha256'],'message_content_sha256':r['content_sha256'],'locator':r['locator'],
            'native_create_time':r['create_time'],'display_date_text':text.splitlines()[0],
            'message_char_start':start,'message_char_end':end,'exact_quote':quote,'quote_sha256':sha(quote.encode()),
            'previous_module_message_reference':mid in linked,
            'coverage_boundary':'The selected exact span is reconstructed here; earlier message-ID contact is not evidence that this mathematics had been processed.'})
    # The previously reported chronological cases are data, not new historical adjudication.
    cases=[('MT',35,30,403,403,464,[35,30,373,30,61]),
           ('SP',135,130,303,303,404,[135,130,173,130,101]),
           ('Greek_430',135,130,430,330,460,[135,130,300,30,130]),
           ('Greek_400',135,130,400,330,460,[135,130,270,60,130]),
           ('Clementine_Latin',35,30,303,403,464,[35,30,273,130,61])]
    witness_runs=[];baseline_numbers=[];formula_numbers=[];reference_numbers=[];vector_labels=[]
    window=lambda d:[sum(d[:3]),sum(d[1:4]),sum(d[2:])]
    for name,a,b,uA,uB,DC,reference in cases:
        events=[('birth_A',0),('birth_B',a),('birth_C',a+b),('death_A',a+uA),('death_B',a+b+uB),('death_C',a+b+DC)]
        ordered=sorted(events,key=lambda e:e[1]);assert [x[0] for x in ordered]==[x[0] for x in events]
        event_durations=[ordered[i+1][1]-ordered[i][1] for i in range(5)]
        formula=[a,b,uA-b,b+uB-uA,DC-uB]
        assert event_durations==formula==reference and all(d>0 for d in formula)
        lifespans=window(formula);assert lifespans==[a+uA,b+uB,DC]
        # A common performance-clock rescaling preserves every stage ratio.
        for alpha,beta in [(Fraction(3,7),Fraction(11)),(Fraction(5,2),Fraction(-4))]:
            transformed=[alpha*t+beta for _,t in events]
            assert [transformed[i+1]-transformed[i] for i in range(5)]==[alpha*d for d in formula]
        witness_runs.append({'witness':name,'units':'witness-relative reported years','parameters':dict(zip(['a','b','uA','uB','D_C'],[a,b,uA,uB,DC])),
            'ordered_events':events,'durations':formula,'lifespans':lifespans,'stage_order':['solo_A','A+B','A+B+C','B+C','solo_C'],
            'pitch_roles':{'A':'R(C)=8f','B':'C=12f','C_voice':'L(C)=9f'},
            'model_condition':'Birth is entrance and death is exit only in this declared experiment; not the definition of audible sustain.'})
        baseline_numbers+=event_durations;formula_numbers+=formula;reference_numbers+=reference
        vector_labels += [name+':stage'+str(i+1) for i in range(5)]
    tempo_pairs=[]
    for x,y in combinations(witness_runs,2):
        scale=Fraction(y['durations'][0],x['durations'][0])
        mismatch=next((i for i,(a,b) in enumerate(zip(x['durations'],y['durations'])) if scale*a!=b),None)
        tempo_pairs.append({'from':x['witness'],'to':y['witness'],'uniform_positive_tempo_equivalent':mismatch is None,
            'scale_from_first_stage':str(scale),'first_incompatible_stage':None if mismatch is None else mismatch+1})
        assert mismatch is not None
    A=[[1,1,1,0,0],[0,1,1,1,0],[0,0,1,1,1]]
    null_basis=[[1,0,-1,1,0],[0,1,-1,0,1]]
    for v in null_basis:assert [sum(x*y for x,y in zip(row,v)) for row in A]==[0,0,0]
    mt=witness_runs[0]['durations'];counterexample=[x+y for x,y in zip(mt,null_basis[0])]
    assert window(mt)==window(counterexample) and mt!=counterexample
    mt_sp_delta=[y-x for x,y in zip(witness_runs[0]['durations'],witness_runs[1]['durations'])]
    assert mt_sp_delta==[100,100,-200,100,40]
    descendants=['Shelah','Eber','Peleg','Reu','Serug','Nahor','Terah']
    mt_sp_offsets=[100,200,300,400,500,600,650];sp_gr_offsets=[130]*7
    maximal_modulus=reduce(gcd,mt_sp_offsets+sp_gr_offsets);assert maximal_modulus==10
    common_moduli=[m for m in range(1,maximal_modulus+1) if all(v%m==0 for v in mt_sp_offsets+sp_gr_offsets)]
    assert common_moduli==[1,2,5,10]
    joint_selection=json.loads((ROOT/'docs/evidence/generational-joint-lattice-superjev.json').read_text(encoding='utf-8-sig'))
    assert joint_selection['answers']['joint_invariant_test']['winner']=='joint_lattice_character'
    joint_rows=[]
    for name,dt,dg in [('MT_to_SP',x,0) for x in mt_sp_offsets]+[('SP_to_Greek',x,1) for x in sp_gr_offsets]:
        change=(dt-130*dg)%50;assert change==0
        joint_rows.append({'witness_transform':name,'descendant':descendants[len(joint_rows)%7],
                           'delta_reported_years':dt,'delta_genealogical_index':dg,'delta_joint_phase_mod50':change})
    assert 650-6*100==50
    joint_phase=lambda t,g:(t-130*g)%50
    # Exact Smith certificate: U M V = diag(1,50), with unimodular U,V.
    M=[[50,130],[0,1]];U=[[0,1],[-1,180]];V=[[1,-1],[1,0]]
    mul=lambda A,B:[[sum(x*y for x,y in zip(row,col)) for col in zip(*B)] for row in A]
    assert mul(mul(U,M),V)==[[1,0],[0,50]]
    assert U[0][0]*U[1][1]-U[0][1]*U[1][0]==1
    assert V[0][0]*V[1][1]-V[0][1]*V[1][0]==1
    for a in range(-10,11):
        for b in range(-12,13):
            assert joint_phase(50*a+130*b,b)==0
    assert [joint_phase(r,0) for r in range(50)]==list(range(50))
    assert reduce(gcd,[100,200,300,400,500,600,651])==1
    assert (131-130)%50==1
    joint_periods=[n for n in range(1,61) if 7*n%12==0 and joint_phase(0,n)==0]
    assert joint_periods==[60]
    assert joint_phase(135,12)==joint_phase(265,13)==25
    assert joint_phase(399,14)==29
    kappa=Fraction(531441,524288)
    assert normalize_octave(Fraction(3,2)**12)==kappa
    assert normalize_octave(Fraction(3,2)**11)==Fraction(177147,131072)
    transport=[]
    for n in range(13):
        transport.append({'formal_insertions':n,'delta_generation':n,'delta_reported_years':130*n,
            'year_phase_mod10':130*n%10,'fifth_angular_phase_mod12':7*n%12,
            'exact_pitch_factor_before_octave_normalization':str(Fraction(3,2)**n),
            'octave_normalized_pitch_factor':str(normalize_octave(Fraction(3,2)**n))})
    assert transport[12]['year_phase_mod10']==transport[12]['fifth_angular_phase_mod12']==0
    class_carry=[]
    for k in range(9):
        h,parity=divmod(k,2);assert k==2*h+parity
        class_carry.append({'RL_circuits':k,'angle_degrees_if_common_angle':360*k,'720_class_counter':h,
            'circuit_parity_separate_unidentified_coordinate':parity,'acoustic_register_increment':k,
            'SUN_scalar_ratio':str(Fraction(1,2)**k)})
    result={'schema':'sunny.generational-temporal-constraint-reconstruction.v1','created_utc':datetime.now(timezone.utc).isoformat(),
        'decision_receipts':['docs/evidence/native-execution-expansion-superjev.json','docs/evidence/generational-hypotheses-superjev.json','docs/evidence/generational-joint-lattice-superjev.json'],
        'sources':evidence,'source_contact':{'messages':len(evidence),'newly_linked_message_ids':[e['message_id'] for e in evidence if not e['previous_module_message_reference']],
            'boundary':'New source linkage and exact selected mathematics, not exhaustive semantic certification of these entire messages.'},
        'retained_axes':['GEN','MEM','TIME','ADR','FUNC','TRN'],
        'constraints':[
            {'id':'GT-TIME-OVERLAP','status':'reproduced-and-extended-conditional','source_refs':['cainan_stage_witnesses','cainan_macro_transport','age_year_time_limit'],
             'premises':['Reported witness numbers retained without new external historical adjudication.','Declared birth-entrance/death-exit experiment; a common positive affine performance clock if a uniform tempo comparison is made.'],
             'formula':'d=(a,b,u_A-b,b+u_B-u_A,D_C-u_B)',
             'ordering_domain':'a>0,b>0,u_A>b,u_A<b+u_B,u_B<D_C; otherwise the assumed five-stage order must be recomputed, not forced.',
             'new_consequence':'The three lifespan measurements have a two-dimensional overlap ambiguity. Full master-score timing cannot be recovered from lifespans alone; two independent linear timing constraints are needed within the positive-real five-stage model.',
             'proof':'The 3x5 window matrix has rank3 and nullspace span{(1,0,-1,1,0),(0,1,-1,0,1)}. Positive small perturbations in either direction preserve all three lifespans but change entrances/overlaps. Given d1,d2 and the lifespans, d3=lA-d1-d2,d4=lB-lA+d1,d5=lC-lB+d2.',
             'matrix':A,'nullspace_basis':null_basis,'same_lifespans_counterexample':{'reported_MT':mt,'conditional_alternative_not_a_historical_witness':counterexample,'common_lifespans':window(mt)},
             'witness_executions':witness_runs,'uniform_tempo_pair_tests':tempo_pairs,'MT_to_SP_delta':mt_sp_delta,'MT_to_SP_lifespan_delta':[0,0,-60]},
            {'id':'GT-INSERTION-PHASE','status':'source-reproduced-and-new-derived-consequence','source_refs':['cainan_macro_transport','insertion_fifth_spiral'],
             'scope':'Shared Shelah-through-Terah sequence in the reported main readings; fixed Adam origin and declared fifth traversal.',
             'reported_time_offsets':{'descendants':descendants,'SP_minus_MT':mt_sp_offsets,'Greek_minus_SP':sp_gr_offsets},
             'insertion_transport':'J:(g,t,P)->(g+1,t+130,(3/2)P) before octave normalization; downstream relative birth intervals and relative pitch ratios are preserved.',
             'new_phase_consequence':{'largest_shared_positive_integer_year_modulus':maximal_modulus,'all_admissible_positive_integer_moduli':common_moduli,
               'proof':'Common phase requires m to divide every reported inter-witness time difference. Their greatest common divisor is10, so the permitted integer moduli are exactly the positive divisors of10. The earlier mod5 relation is valid but does not uniquely select a meter or Cainan membership.'},
             'new_joint_consequence':'Under formal composition of J, twelve insertions restore (year mod10, fifth angular address mod12) but retain +1560 reported years and octave-normalized pitch residual531441/524288. Thus that joint finite phase cannot replace the full chronology/residual/history state.',
             'formal_transport_execution':transport,'formal_composition_limit':'Only one Cainan insertion is source-reported. Iteration is an algebraic consequence of retaining the same transport, not a claim that twelve historical insertions occurred.',
             'scalar_connection':'3/2=R^{-1}; reverse traversal is explicit, not an unnoticed inversion of the descending SUN operator.',
             'selection_limit':'These predicates distinguish transformations but do not elect a witness without independent source-defined boundary requirements.'},
            {'id':'GT-JOINT-TIME-GEN','status':'new-source-derived-joint-invariant-executed','source_refs':['cainan_macro_transport','insertion_fifth_spiral'],
             'premises':['Shared Shelah-through-Terah main witness readings only.','Integer reported years and genealogical indices; common Arpachshad time origin and Adam-at-zero generation convention fixed across witnesses.','The retained fifth-traversal adapter is used only where explicitly stated.'],
             'shift_lattice':{'basis_columns':M,'proof':'All MT→SP shifts are integer multiples of(50,0), and (50,0)=(650,0)-6(100,0) belongs to their integer span. The SP→Greek shift is(130,1). Thus the exact generated integer lattice H has the stated basis. Negative coefficients concern a representational lattice, not causal backwards generation.',
                'smith_certificate':{'U':U,'V':V,'U_M_V':[[1,0],[0,50]],'determinant':50,'quotient':'Z²/H is isomorphic to Z50'}},
             'primitive_joint_character':'I(t,g)=t-130g mod50 = t+20g mod50',
             'kernel_proof':'I(t,g)=0 iff t-130g=50k for some integerk, iff (t,g)=k(50,0)+g(130,1) lies inH. The map is ontoZ50 because I(1,0)=1. Therefore it exactly classifies the lattice cosets.',
             'maximality_with_time_coefficient_one':'For t+b g modm to annihilate every actual shift, the zero-generation shifts force m to divide50 and the insertion forces b=-130 modm. The largest such positive integerm is50, with b=20.',
             'actual_source_row_checks':joint_rows,
             'strict_refinement_of_pure_time':{'identity':'I mod10 = t mod10','counterexample_to_sufficiency_of_pure_time':{'states':[[0,0],[10,0]],'same_pure_time_mod10':0,'different_joint_mod50':[0,10]},'interpretation':'The joint invariant retains a factor of five beyond the common pure-time projection; this does not select a historical calendar or musical meter.'},
             'not_constant_along_genealogical_dynamics':{'source_counterexample':'SP Eber→Peleg has delta(t,g)=(134,1), changingI by4 modulo50. With the retained origin, Shelah,Eber,Peleg haveI=25,25,29.','reason':'This is invariance across the specified witness representations, not a conservation law along every ancestral edge.'},
             'conditional_music_address_consequence':{'premise':'Hold t modulo50 fixed, and use the declared fifth angular address p=7g modulo12.','derivation':'I depends on g modulo5, because20 has additive order5 modulo50. Pitch address depends on g modulo12. A generator shift preserving both must be divisible by5and12, hence60. The exact finite check finds60as the first positive return.','period':60,'boundary':'A representation-sufficiency result for these observables, not a new universal60generation class or a claim that time stays fixed during actual descent. Actual coupled insertion transports preserveI while changing time.'},
             'gauge_limit':'Changing common time or generation origin shifts allI values by one common constant. Independent per-witness origin changes require an explicit gauge alignment before numericalI values are comparable.',
             'falsifiers':['A new included zero-generation witness shift not divisible by50 changes the lattice index.','A source insertion vector other than(130,1) changes the joint coefficient or lattice.','A different declared generation convention, witness reading or origin requires recomputation.','A nonlinear year-to-performance adapter is outside this integer-year quotient.'],
             'executed_adverse_controls':[{'altered_input':'Replace final MT→SP shift650 by651, keeping other listed shifts.','result':'The zero-generation time gcd becomes1, so the claimed Z50 quotient no longer survives.'},{'altered_input':'Replace insertion(130,1) by(131,1).','result':'The original I changes by1 modulo50, so it fails the altered source vector; a recomputed coefficient would be required.'}],
             'independent_solver':'docs/evidence/generational-joint-wolfram-check.json','historical_witness_elected':False},
            {'id':'GT-GEN-ADR','status':'reproduced-conditional-exclusion','source_refs':['generation_address_distinction','master_score'],
             'witness_values':[{'entity':'Ephraim','expanded_GEN':24,'shorter_GEN':23,'camp_ADR':7},{'entity':'Manasseh','expanded_GEN':24,'shorter_GEN':23,'camp_ADR':8},{'entity':'Benjamin','expanded_GEN':23,'shorter_GEN':22,'camp_ADR':9}],
             'proof':'A deterministic map of GEN alone must give Ephraim and Manasseh the same output. Fixed camp ADR gives7 and8, and the declared fifth traversal gives different pitch classes. Hence no GEN-only map can preserve both distinctions. Their shared institutional standing is not their biological depth.',
             'excluded_joint_assumptions':['GEN alone fixes personal musical pitch/address','Distinct fixed Numbers2 tribal addresses must remain distinct under the declared address/pitch adapter'],
             'named_identity_branches':{'Benjamin_Ephraim':'Two distinct tribal positions cannot be one local W72 binary fiber if tribe fixes p; no rejection of the tradition itself.','Zebulun_siblings':'Same tribal p is compatible in principle; tau/beta assignment is still not supplied.','Levite_Amram':'Outside ordinary outer-camp carrier unless a separate registered map is supplied.'},
             'temporal_limit':'Eldad/Medad activities and quail-related contribution have source event order but no corresponding numerical birth/duration data. Do not transfer the Cainan5year offsets or treat prophecy presentation order as three measured beats.'},
            {'id':'GT-720-REGISTER','status':'new-conditional-compatibility-constraint','source_refs':['two_turn_class_hunch','sophia_boundary_aliases','master_score'],
             'premises':['User-proposed two360degree turns per class lift retained with its original exploratory qualification.','For this compatibility test only: same angular wheel for retained R5/L7 steps,30degrees per address step; one RL circuit is360degrees.','SUN RL=O halves the scalar center and increments descent-positive acoustic grade by1.'],
             'proof':'After k RL circuits, angle=360k and acoustic grade increment=k. A720degree class counter h=floor(k/2) leaves parity epsilon=k mod2. Thus acoustic grade increment=2h+epsilon. At720degrees h=1 but acoustic grade increment=2 and C_new/C_old=1/4.',
             'consequence':'A720degree class lift cannot silently be identified with a single acoustic O-halving under the shared-angle premises. Keep class and register separate, or supply a different explicit bridge/angle convention.',
             'minimal_state_requirement':'If a rule distinguishes alternating whole-turn returns, phase modulo360 alone is insufficient; preserve at least return parity or integer winding. This does not identify parity with W72 beta.',
             'execution':class_carry,'retained_sophia_alias_rule':'12 at the boundary, midnight0, and operator13 can be distinct roles of one transition. An alias does not create a thirteenth equal Shem sector.',
             'unknowns':['Which angular variable the source720class condition actually measures','Whether the class lift is SUN acoustic O, another operation, or a composite','Any lawful radius, height, rebound or fourth-axis realization'],
             'physics_status':'Explicit model-premise compatibility theorem; no physical proof of a two-turn universe.'}],
        'verification':{'source_files_hash_verified':len({e['source_id'] for e in evidence}),'exact_message_spans':len(evidence),
            'witness_event_sort_and_closed_formula_agree':5,'uniform_tempo_pair_failures':len(tempo_pairs),'formal_insertion_cases':13,'class_carry_cases':9,
            'joint_witness_shift_checks':14,'joint_lattice_smith_index':50,
            'independent_wolfram':['docs/evidence/generational-wolfram-check.json','docs/evidence/generational-joint-wolfram-check.json']},
        'unresolved':['Historical critical-edition verification of the reported numerical witnesses','An admitted year/cycle-to-performance-clock adapter','Source-defined class/generation/register bridge and actual720variable','Full GEN/MEM/TIME/ADR/FUNC/TRN constraint integration beyond these passages','Independent blind predictions after adequate MissionI reconstruction'],
        'database_mutation':False,'canonical_orientation_selected':False,'blind_prediction':False}
    save(ROOT/'state/reconstruction/generational-constraints.json',result)
    save(ROOT/'docs/evidence/generational-numerical-vectors.json',{'baseline':baseline_numbers,'candidate':formula_numbers,'reference':reference_numbers})
    save(ROOT/'docs/evidence/generational-numerical-protocol.json',{'baseline':'Exact event-sort durations','candidate':'Closed five-stage formula','reference':'Already exposed assistant-reported witness table; not a blind reference','ordered_vector_labels':vector_labels,'units':'Witness-relative reported years in each explicitly indexed case','scope':'25 explicitly ordered stage entries from five source cases; comparison only checks arithmetic agreement, not historical truth or mathematical completeness','cost_basis':'Not measured; no efficiency claim'})
    c.close()
    body='''# Executed generation, time and class-lift constraints

The recovered master score keeps GEN, MEM, TIME, ADR, FUNC and TRN distinct. This unit executes their connections rather than giving them a common arbitrary coordinate.

The Cainan chronology supplies a usable transport: relative to the reported Samaritan reading, the Greek insertion moves each shared Shelah–Terah descendant one generation and130years forward. Under the declared fifth traversal it also moves pitch by3/2, preserving downstream relative timing and pitch intervals. This is inverse-R traversal, not the descending SUN R operation.

A newly derived pure-time constraint strengthens the earlier mod-5 observation: all reported inter-witness birth-time differences have greatest common divisor 10. The common positive integer-year moduli are exactly 1, 2, 5 and 10. This arithmetic does not select a musical meter or Cainan's membership. If the insertion is formally composed twelve times, the year-mod-10 and nominal pitch addresses both return, but 1,560 years and a 531441/524288 pitch residual remain. Only one insertion is source-reported; iteration is an algebraic consequence.

Combining TIME and GEN retains more information. The actual witness-shift vectors generate the integer lattice with basis (50,0) and (130,1). Its determinant is 50 and its Smith form is diag(1,50). The joint character I(t,g)=t−130g mod 50, equivalently t+20g mod 50, has exactly this lattice as its kernel. All fourteen reported Shelah–Terah witness shifts preserve I. It retains an extra factor of five beyond pure time mod 10, and 50 is the largest modulus with coefficient one on time that annihilates these actual shifts. No historical witness or calendar wins by agreeing with a constraint derived from all of them.

This is a constraint across witness representations. It is not constant along every genealogical step: the reported Samaritan Eber→Peleg interval (134 years, one generation) changes I by 4. Changing the common origin shifts all I values together; independent witness origins need explicit alignment. Adverse controls replacing 650 by 651 or the insertion by (131,1) break the original invariant as predicted.

One conditional musical consequence follows: at fixed time mod 50, I depends on generation mod 5 while the declared fifth address depends on generation mod 12. Preserving both requires generation mod 60. This is a representation requirement for these observables, not an invented universal class count; actual genealogy does not keep time fixed.

The five-stage birth-entrance/death-exit experiment was reproduced by sorting events and by its closed formula across five numerical witness readings. All ten witness pairs fail uniform tempo equivalence. The later age/year correction remains in force: lifetime is not audible sustain by definition, and no year-to-beat conversion has been adopted.

The overlap reconstruction gives another new constraint. Three voice lifespans constrain five stage durations through a rank-three window matrix, leaving two timing freedoms. Two independent linear timing conditions are still needed to recover the complete passage. The JSON supplies exact nullspace directions and a positive-duration counterexample with unchanged lifespans but changed overlap. MT-to-SP redistributes the inner passage by (+100,−200,+100), preserving the middle voice's 433 years without preserving the entire three-voice texture.

The connected genealogy supplies a hard address restriction: Ephraim and Manasseh share biological GEN 24 in the expanded reading but occupy camp addresses 7 and 8. A deterministic GEN-only pitch/address map cannot preserve both. Benjamin belongs to GEN 23 while occupying camp sector 9. Institutional standing, blessing precedence and biological depth remain separate. Eldad/Medad identity branches retain their different address obligations; no numerical Cainan rhythm is transferred to their undated activity.

The 720° class proposal also yields a precise conditional restriction. If its turns use the same angular wheel as R5/L7, one RL circuit is 360° and halves the scalar center. Two circuits are 720° and quarter it. Writing h for completed 720° class cycles and epsilon for remaining circuit parity gives acoustic register increment=2h+epsilon. A single class lift cannot simultaneously mean one acoustic halving under those premises. Preserve the counters separately or derive a different bridge. Parity is not identified with W72 beta; 720° remains a stated model premise, with the user's original qualification retained.

Sophia 12/midnight 0/operator 13 is retained as a boundary-role proposal. It does not create a thirteenth equal sector or equate succession with genealogy. Radius, height, rebound and the fourth-axis law remain unassigned.

Actual Jev selected these joint constraints; exact source spans, arithmetic executions, assumptions and alternative branches are in state/reconstruction/generational-constraints.json. Independent Wolfram verifies the window rank/nullspace, greatest common divisor and class carry. Prumo verifies source coordinates, and Numerical Research Kit checks the two duration computations against the exposed table. Those guards do not certify external historical truth, a complete SUNNY reconstruction or blind predictive success.
'''
    (ROOT/'docs/reconstruction/GENERATIONAL_CONSTRAINTS.md').write_text(body,encoding='utf-8')
    print(json.dumps({'constraints':len(result['constraints']),'source_spans':len(evidence),'new_message_links':len(result['source_contact']['newly_linked_message_ids']),'witness_cases':5,'tempo_failures':len(tempo_pairs),'max_shared_modulus':maximal_modulus,'overlap_kernel_dimension':2,'class_carry_cases':len(class_carry)}))
if __name__=='__main__':main()
