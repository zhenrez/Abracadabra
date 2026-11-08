"""Independent LRA feasibility and rational witness checks of compiled TS adapter."""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime,timezone
import hashlib,itertools,json,random,subprocess,sys
import sympy as S
from sympy.logic.inference import satisfiable
DIR=Path(__file__).resolve().parent
ROOT=Path(__file__).resolve().parents[4]
def q(x):
    x=F(x);return {'numerator':str(x.numerator),'denominator':str(x.denominator)}
def w(lo=None,hi=None,lc=False,uc=False):
    return {'lower':None if lo is None else q(lo),'upper':None if hi is None else q(hi),'lowerClosed':lc,'upperClosed':uc}
def fraction(q):return F(int(q['numerator']),int(q['denominator']))
def constraints(x,window):
    out=[]
    for side,closed in [('lower','lowerClosed'),('upper','upperClosed')]:
        if window[side] is None:continue
        f=fraction(window[side]);value=S.Rational(f.numerator,f.denominator)
        out.append((x>=value if window[closed] else x>value) if side=='lower' else (x<=value if window[closed] else x<value))
    return out
def contains(window,value):
    if window is None:return False
    low=window['lower'];high=window['upper']
    return (low is None or value>fraction(low) or value==fraction(low) and window['lowerClosed']) and (high is None or value<fraction(high) or value==fraction(high) and window['upperClosed'])
def main():
    windows=[w(),w(0,0,True,True),w(0,0,False,True),w(1,-1,True,True),w(None,0,False,False),w(None,0,False,True),w(0,None,False,False),w(0,None,True,False)]
    windows += [w(-1,1,l,u) for l,u in itertools.product([False,True],repeat=2)]
    windows += [w(F(1,3),F(2,3),True,False),w(-10**40,-10**40+1,False,True)]
    cases=[]
    def add(d,k,r,s,label):cases.append({'id':label,'donor':d,'contact':k,'recipient':r,'strict':s})
    rng=random.Random(87431)
    for i in range(400):add(*(rng.choice(windows) for _ in range(3)),bool(i%2),'sample-'+str(i))
    for i,window in enumerate(windows):
        for axis in range(3):
            for strict in [False,True]:
                a=[w(),w(),w()];a[axis]=window;add(*a,strict,'axis-'+str(i)+'-'+str(axis)+'-'+strict.__str__())
    for strict in [False,True]:
        add(w(1,1,True,True),w(1,1,True,True),w(1,1,True,True),strict,'equal-'+str(strict))
        n=10**100
        add(w(),w(F(1,n+1),F(1,n),True,True),w(),strict,'large-derived-'+str(strict))
        add(w(F(-1,n)),w(F(-1,n),F(1,n),False,True),w(F(1,n)),strict,'small-rational-'+str(strict))
    (DIR/'adapter-cases.json').write_text(json.dumps(cases),encoding='utf8')
    node=subprocess.run(['node',str(DIR/'run_adapter_cases.mjs')],cwd=ROOT,capture_output=True,text=True)
    assert node.returncode==0,(node.stdout,node.stderr)
    actual=json.loads((DIR/'adapter-actual.json').read_text(encoding='utf8'));assert actual['start']==actual['finish'],'source changed during execution'
    d,k,r=S.symbols('d k r',real=True);failures=[];witnesses=0;projection=0
    for i,(case,row) in enumerate(zip(cases,actual['results'])):
        expr=S.And(*constraints(d,case['donor']),*constraints(k,case['contact']),*constraints(r,case['recipient']),d<k if case['strict'] else d<=k,k<=r)
        expected=satisfiable(expr,use_lra_theory=True) is not False
        if 'error' in row:
            failures.append({'id':case['id'],'issue':'throws on valid bounded rational input','error':row['error'],'expectedFeasible':expected});continue
        got=row['result']
        if got['feasible']!=expected:failures.append({'id':case['id'],'issue':'feasibility disagreement','expected':expected,'actual':got['feasible']});continue
        if got['feasible']:
            v=got['witness'];dv,kv,rv=(fraction(v[key]) for key in ['donorOnset','contact','recipientOnset'])
            valid=contains(case['donor'],dv) and contains(case['contact'],kv) and contains(case['recipient'],rv) and (dv<kv if case['strict'] else dv<=kv) and kv<=rv
            if not valid:failures.append({'id':case['id'],'issue':'invalid exact witness','witness':v})
            witnesses+=1
        elif got['witness'] is not None:failures.append({'id':case['id'],'issue':'infeasible case returned witness'})
        if i%7==0:
            for point in [F(-1),F(0),F(1,3),F(1,2),F(1)]:
                pp=S.Rational(point.numerator,point.denominator)
                possible=satisfiable(S.And(expr,S.Eq(k,pp)),use_lra_theory=True) is not False
                projected=contains(got['admissibleContact'],point)
                if possible!=projected:failures.append({'id':case['id'],'issue':'contact projection disagreement','point':str(point)})
                projection+=1
    result={'schema':'sunny.independent-ts-contact-adapter-review.v1','checkedAt':datetime.now(timezone.utc).isoformat(),'status':'passed' if not failures else 'failed',
        'exit_code':int(bool(failures)),'cases':len(cases),'independentExactWitnessChecks':witnesses,'independentProjectionMembershipChecks':projection,'failures':failures,
        'testedHashes':actual['start'],'sourceStable':True,'oracle':'SymPy exact real LRA of all input interval predicates and d<k<=r or d<=k<=r; not adapter intersection formula',
        'guardUse':'Actual Supermemory search_memory success for this review; retrieved continuity only',
        'boundary':'Arbitrary real event coordinates; no historical date, transcription-to-phone license or historical contact established.'}
    (DIR/'adapter-review.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result));return result['exit_code']
if __name__=='__main__':raise SystemExit(main())
