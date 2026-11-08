"""Exact, source-bound native bridge words; no model vote substitutes for arithmetic."""
from __future__ import annotations
import argparse,hashlib,json,math,platform,sys
from datetime import datetime,timezone
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(raw):return hashlib.sha256(raw).hexdigest()
def ratio(x):return {'numerator':x.numerator,'denominator':x.denominator,'exact':str(x)}
def valuation(x,p):
    a=x.numerator;b=x.denominator;n=0
    while a%p==0:a//=p;n+=1
    while b%p==0:b//=p;n-=1
    return n
def normalize_frequency(x):
    if x<=0:raise ValueError('positive frequency ratio required')
    original=x;k=0
    while x<1:x*=2;k+=1
    while x>=2:x/=2;k-=1
    assert x==original*F(2)**k and 1<=x<2
    return x,k
def word_path(ops,start=F(1)):
    values=[ratio(start)];x=start
    for name,factor in ops:x*=factor;values.append({'operator':name,**ratio(x)})
    return values
def compute():
    binding_path=ROOT/'docs/evidence/native-derivations-source-bindings.json'
    bindings=json.loads(binding_path.read_text(encoding='utf8'));source_checks=[]
    for source in bindings['sources']:
        p=ROOT/source['path'];raw=p.read_bytes();assert digest(raw)==source['sha256'],source['id']
        text=raw.decode('utf-8-sig')
        for quote in source.get('quotes',[]):assert quote['quote'] in text and digest(quote['quote'].encode('utf8'))==quote['quote_sha256']
        source_checks.append({'source_id':source['id'],'sha256':source['sha256'],'quotes_checked':len(source.get('quotes',[]))})
    R_L=F(2,3);L_L=F(3,4);O_L=F(1,2);D_L=F(2,3);U_L=F(4,3)
    D_f=1/D_L;U_f=1/U_L;E=F(16,15);K=F(81,80);q=D_f
    assert R_L*L_L==L_L*R_L==O_L and D_L==R_L and U_L==1/L_L
    limma=E/K;reverse,k_reverse=normalize_frequency(q**-5);forward,k_forward=normalize_frequency(q**7)
    cycle=forward/reverse;required_bridge=E/forward
    inverse_word=D_f**-2*U_f**-3
    assert limma==F(256,243)==reverse==inverse_word
    assert forward==F(2187,2048) and cycle==F(3**12,2**19)==F(531441,524288)
    assert K*reverse==E and K*forward==E*cycle
    assert required_bridge==F(32768,32805)==K/cycle
    assert (-5)%12==7%12 and reverse!=forward
    # A nonnegative word has nu_3(D_f^m U_f^n 2^z)=m+n>=0.
    # The target has nu_3=-5; octave factors have nu_3=0. This is a proof,
    # not extrapolation from a finite search. Integer group exponents solve uniquely.
    assert valuation(D_f,3)==valuation(U_f,3)==1 and valuation(limma,3)==-5
    assert (-2)+(-3)==-5 and -(-2)-2*(-3)==8
    witness_checks=0
    for m in range(13):
        for n in range(13):
            for z in range(-20,21):
                assert D_f**m*U_f**n*F(2)**z!=limma;witness_checks+=1
    # Every permutation of two inverse D and three inverse U steps has the same
    # evaluated endpoint, but its ordered intermediate states need not coincide.
    from itertools import permutations
    ordered=[]
    for names in sorted(set(permutations(('D_f^-1','D_f^-1','U_f^-1','U_f^-1','U_f^-1')))):
        factors={'D_f^-1':1/D_f,'U_f^-1':1/U_f}
        path=word_path([(name,factors[name]) for name in names]);assert F(path[-1]['numerator'],path[-1]['denominator'])==limma
        ordered.append({'word':list(names),'path':path})
    assert len(ordered)==10
    normalized_paths=[]
    for row in ordered:
        normalized_paths.append([str(normalize_frequency(F(v['numerator'],v['denominator']))[0]) for v in row['path']])
    assert all(path==normalized_paths[0] for path in normalized_paths)
    from itertools import combinations
    sample_sets=[]
    for size in range(5):
        for positions in combinations((1,2,3,4),size):
            signatures=[tuple(row['path'][p]['exact'] for p in positions) for row in ordered]
            sample_sets.append({'positions':list(positions),'distinct_histories':len(set(signatures))})
    distinguishing=[x for x in sample_sets if x['distinct_histories']==10]
    assert min(len(x['positions']) for x in distinguishing)==4
    adjacent_witnesses=[]
    for omitted in (1,2,3,4):
        pair=None
        for i,left in enumerate(ordered):
            for right in ordered[i+1:]:
                equal_elsewhere=all(left['path'][p]['exact']==right['path'][p]['exact'] for p in (1,2,3,4) if p!=omitted)
                if equal_elsewhere and left['path'][omitted]['exact']!=right['path'][omitted]['exact']:
                    pair={'omitted_position':omitted,'left_word':left['word'],'right_word':right['word'],'left_value':left['path'][omitted],'right_value':right['path'][omitted]};break
            if pair:break
        assert pair;adjacent_witnesses.append(pair)
    # The TOL archive explicitly preserves words before its evaluation quotient.
    # R/L below is a source-defined instance, not an invented definition of an
    # otherwise unretrieved named A/B adapter.
    tol_RL=word_path([('R_L',R_L),('L_L',L_L)]);tol_LR=word_path([('L_L',L_L),('R_L',R_L)])
    assert tol_RL[-1]['exact']==tol_LR[-1]['exact']=='1/2' and tol_RL[1]['exact']!=tol_LR[1]['exact']
    # Source FK lift (a,m)*(b,n)=(ab,m+n), Phi(a,m)=a*2^-m.
    def compose(a,b):return (a[0]*b[0],a[1]+b[1])
    def realize(a):return a[0]*F(2)**(-a[1])
    fk_out=(E,0);fk_return=(1/E,1);fk=compose(fk_out,fk_return)
    assert fk==(F(1),1) and realize(fk)==F(1,2)
    # Treating the return as the actual inverse would erase the registered loop.
    actual_inverse=(1/E,0);erased=compose(fk_out,actual_inverse)
    assert erased==(F(1),0) and realize(erased)==1
    predictions=json.loads((ROOT/'docs/evidence/native-derivations-jev-result.json').read_text(encoding='utf-8-sig'))
    verdicts={'group_membership':True,'forward_semigroup':False,'same_normalized_ratio':False,'residual_hypothesis':True}
    comparison=[{'question':key,'jev_predicted':predictions['answers'][key]['value'],'exact_result':value,'agrees':predictions['answers'][key]['value']==value} for key,value in verdicts.items()]
    return {'schema':'sunny.native-derivations.v1','computed_utc':datetime.now(timezone.utc).isoformat(),'status':'exact_assertions_passed','source_bindings':bindings,'source_checks':source_checks,
      'conventions':{'carrier':'Positive ideal pipe-length and frequency ratios; separate reciprocal actions.','units':'Ratios are dimensionless; a dimensional length or frequency requires its positive reference. No age-to-beat conversion.','frequency_normalization':'N(x)=x*2^k in[1,2); integer k retained. In the source Phi(a,m)=a*2^-m convention, m=-k.','word_composition':'Paths list operations in execution order; evaluated positive scalar multipliers commute, source path history does not disappear.','source_specific_FK_lift':'Phi and loop registration are retained bridge-specific hypotheses; not a newly established universal law.'},
      'native_operations':{'SUN_length':{'R':ratio(R_L),'L':ratio(L_L),'O':ratio(O_L),'inverses':{'R^-1':ratio(1/R_L),'L^-1':ratio(1/L_L),'O^-1':ratio(1/O_L)}},'Chinese_length':{'D_L':ratio(D_L),'U_L':ratio(U_L),'ordered_D_then_U':word_path([('D_L',D_L),('U_L',U_L)])},'Chinese_frequency':{'D_f':ratio(D_f),'U_f':ratio(U_f),'ordered_D_then_U':word_path([('D_f',D_f),('U_f',U_f)])},'bridge_frequency':{'E_Earth':ratio(E),'K_syntonic':ratio(K)}},
      'connected_discriminator':{'target_E_over_K':ratio(limma),'reverse_five':{'exact':ratio(reverse),'unreduced':ratio(q**-5),'normalization_k':k_reverse,'source_register_m':-k_reverse},'forward_seven':{'exact':ratio(forward),'unreduced':ratio(q**7),'normalization_k':k_forward,'source_register_m':-k_forward},'shared_fifth_cycle_index_mod12':7,'forward_over_reverse_residual':ratio(cycle),'old_bridge_on_forward7':ratio(K*forward),'required_bridge_on_forward7':ratio(required_bridge),'required_bridge_over_old_bridge':ratio(required_bridge/K),'residual_cents':1200*math.log2(float(cycle)),'residual_cents_status':'binary64 descriptive value; exact ratio is authoritative; external Wolfram30digit result saved separately.','discriminating_observable':'Directed generation word together with register carries or a measured/source-specified residual. Mod12 address alone does not decide these exact realizations.','consequence':'Retaining the81/80 bridge and exact16/15 Earth target forces the reverse-five algebraic realization or an explicitly retained inverse-cycle correction on the forward-seven realization. The two words are not exact substitutes merely because their finite index matches.','not_claimed':'No unique global orientation; no claim that arbitrary inverse-generator words were the historical Chinese procedure.'},
      'forward_semigroup_obstruction':{'exact_proof':'For nonnegative m,n and integer z, nu_3(D_f^m U_f^n 2^z)=m+n>=0, while nu_3(E/K)=-5. Thus no forward semigroup word plus octave shifts equals E/K.','group_solution':{'D_f_exponent':-2,'U_f_exponent':-3,'witness':ratio(inverse_word)},'finite_sanity_bounds':{'m':[0,12],'n':[0,12],'z':[-20,20],'cases_checked':witness_checks},'proof_scope':'Universal nonnegative-word obstruction follows from the exact valuation argument, not the finite sanity loop.'},
      'history_observables':{'inverse_word_permutations':ordered,'evaluated_endpoint':ratio(limma),'all_octave_normalized_pitch_paths_identical':True,'common_normalized_pitch_path':normalized_paths[0],'fixed_intermediate_sample_sets':sample_sets,'minimum_raw_or_register_sample_count':4,'minimality_witnesses':adjacent_witnesses,'scope':'The declared10-word algebraic budget with two inverseD and three inverseU steps. This is not an independently frozen historical Chinese path population.','consequence':'Every normalized pitch sample can agree while actual operator/register history differs. Register carries, absolute octave or direct operation labels are necessary to distinguish these histories; pitch-class sampling alone is insufficient.','source_TOL_RL_path':tol_RL,'source_TOL_LR_path':tol_LR,'named_TOL_ABBA_status':'Literal separately named A/B adapter definitions not yet recovered in this run. R/L is the explicit source-defined example of history versus evaluation; no matrices or nonlinear maps invented.'},
      'FK_registered_loop':{'outbound':{'ratio':ratio(E),'grade':0},'return':{'ratio':ratio(1/E),'grade':1},'composition':{'ratio':ratio(fk[0]),'grade':fk[1],'realization':ratio(realize(fk))},'if_return_is_actual_inverse':{'ratio':ratio(erased[0]),'grade':erased[1],'realization':ratio(realize(erased))},'consequence':'Local ratio cancellation alone does not produce the octave lift. The distinct return-channel/grade registration is load-bearing and remains source-conditional.'},
      'jev_hypothesis_checks':comparison,'jev_math_errors_retained':[x for x in comparison if not x['agrees']],
      'novelty':{'kind':'New connected derivation computed in this run from already exposed source constants.','not_independent_blind':True,'global_mathematical_novelty_claimed':False,'source_novelty_audit':'docs/evidence/native-derivations-novelty.json'},
      'software':{'python':platform.python_version(),'arithmetic':'fractions.Fraction and integer valuations','randomness':'none'},'independent_verification':'docs/evidence/native-derivations-wolfram-result.json'}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'state/reconstruction/native-derivations.json');args=parser.parse_args()
    out=compute();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'status':out['status'],'output':str(args.output),'source_files_checked':len(out['source_checks']),'E_over_K':out['connected_discriminator']['target_E_over_K'],'forward7':out['connected_discriminator']['forward_seven']['exact'],'cycle_residual':out['connected_discriminator']['forward_over_reverse_residual'],'required_forward_bridge':out['connected_discriminator']['required_bridge_on_forward7'],'jev_errors_retained':out['jev_math_errors_retained']},ensure_ascii=True,indent=2))
if __name__=='__main__':main()
