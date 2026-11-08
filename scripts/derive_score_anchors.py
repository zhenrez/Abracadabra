"""Exact, source-conditioned score observability; no historical sound/calendar selection."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'state/delivery-2026-11-07/mathematics'
A=[[1,1,1,0,0],[0,1,1,1,0],[0,0,1,1,1]]
LABELS=['solo A','A+B','A+B+C','B+C','solo C']

def rref(matrix):
    rows=[[Q(x) for x in row] for row in matrix]
    if not rows:return rows,[]
    pivot=0;pivots=[]
    for col in range(len(rows[0])):
        nonzero=next((i for i in range(pivot,len(rows)) if rows[i][col]),None)
        if nonzero is None:continue
        rows[pivot],rows[nonzero]=rows[nonzero],rows[pivot]
        scale=rows[pivot][col];rows[pivot]=[x/scale for x in rows[pivot]]
        for i in range(len(rows)):
            if i==pivot:continue
            scale=rows[i][col]
            rows[i]=[x-scale*y for x,y in zip(rows[i],rows[pivot])]
        pivots.append(col);pivot+=1
        if pivot==len(rows):break
    return rows,pivots

def solve(coefficients,values):
    if not coefficients or len(coefficients)!=len(values):raise ValueError('Aligned equations required')
    n=len(coefficients[0])
    if any(len(row)!=n for row in coefficients):raise ValueError('Unaligned variable coordinates')
    rows,pivots=rref([list(a)+[b] for a,b in zip(coefficients,values)])
    if n in pivots:return {'consistent':False,'rank':len(pivots)-1}
    free=[j for j in range(n) if j not in pivots]
    particular=[Q(0)]*n
    for i,col in enumerate(pivots):particular[col]=rows[i][-1]
    basis=[]
    for f in free:
        vector=[Q(0)]*n;vector[f]=Q(1)
        for i,col in enumerate(pivots):vector[col]=-rows[i][f]
        basis.append(vector)
    return {'consistent':True,'rank':len(pivots),'dimension':len(free),'particular':particular,'nullspace':basis}

def dot(a,b):return sum((Q(x)*Q(y) for x,y in zip(a,b)),Q(0))
def unit(index,n=5):return [int(j==index) for j in range(n)]
def identifiable(solution,target):
    if not solution['consistent']:return {'status':'inconsistent'}
    if any(dot(target,v) for v in solution['nullspace']):return {'status':'underdetermined'}
    return {'status':'determined','value':dot(target,solution['particular'])}

def minimal_conflicts(coefficients,values,names):
    result=[]
    for size in range(1,len(names)+1):
        for subset in combinations(range(len(names)),size):
            if any(set(x).issubset(subset) for x in result):continue
            if not solve([coefficients[i] for i in subset],[values[i] for i in subset])['consistent']:result.append(subset)
    return [[names[i] for i in subset] for subset in result]

def multiply(a,b):return [[dot(row,col) for col in zip(*b)] for row in a]
def vector(matrix,x):return [dot(row,x) for row in matrix]
def encode(value):
    if isinstance(value,Q):return str(value)
    if isinstance(value,dict):return {k:encode(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [encode(v) for v in value]
    return value

def main():
    source=ROOT/'state/reconstruction/generational-constraints.json'
    model=json.loads(source.read_text(encoding='utf-8-sig'))
    case=next(c for c in model['constraints'] if c['id']=='GT-TIME-OVERLAP')
    assert case['matrix']==A
    nullspace=solve(A,[0,0,0])['nullspace']
    assert len(nullspace)==2
    pairs=[];replays=[]
    # d -> cumulative event-offset coordinates z=T*d. D is the exact inverse.
    T=[[int(j<=i) for j in range(5)] for i in range(5)]
    inverse=[[int(i==j)-int(i==j+1) for j in range(5)] for i in range(5)]
    assert multiply(T,inverse)==[unit(i) for i in range(5)]
    for pair in combinations(range(5),2):
        restrictions=[[v[i] for v in nullspace] for i in pair]
        determinant=restrictions[0][0]*restrictions[1][1]-restrictions[0][1]*restrictions[1][0]
        pairs.append({'stageIndices':[i+1 for i in pair],'labels':[LABELS[i] for i in pair],
            'restrictionOnTimingFreedoms':restrictions,'determinant':determinant,'sufficient':determinant!=0})
        for witness in case['witness_executions']:
            values=witness['lifespans']+[witness['durations'][i] for i in pair]
            coefficients=A+[unit(i) for i in pair]
            result=solve(coefficients,values)
            assert result['consistent'] and result['dimension']==(0 if determinant else 1)
            if determinant:
                assert result['particular']==[Q(x) for x in witness['durations']]
                transformed=solve(multiply(coefficients,inverse),values)
                assert transformed['dimension']==0 and vector(inverse,transformed['particular'])==result['particular']
            replays.append({'witness':witness['witness'],'anchors':[i+1 for i in pair],
                'remainingTimingFreedoms':result['dimension'],'exactReconstruction':bool(determinant),
                'basisChangedReplay':bool(determinant),'sourceExposure':'already exposed; not a blind prediction'})
    assert len([p for p in pairs if p['sufficient']])==8
    assert [p['stageIndices'] for p in pairs if not p['sufficient']]==[[1,4],[2,5]]
    mt=next(w for w in case['witness_executions'] if w['witness']=='MT')
    singles=[]
    for i in range(5):
        result=solve(A+[unit(i)],mt['lifespans']+[mt['durations'][i]])
        singles.append({'anchorStage':i+1,'anchorValue':mt['durations'][i],
            'remainingTimingFreedoms':result['dimension'],
            'stagePredictions':[{'stage':j+1,**identifiable(result,unit(j))} for j in range(5)]})
    bad_coefficients=A+[unit(0),unit(3)];bad_values=mt['lifespans']+[35,31]
    conflict=minimal_conflicts(bad_coefficients,bad_values,['lifespan_A','lifespan_B','lifespan_C','d1=35','d4=31'])
    assert conflict==[['lifespan_A','lifespan_B','d1=35','d4=31']]
    # A unique algebraic solution can violate the retained event-order domain.
    positive_control=solve(A+[unit(0),unit(1)],mt['lifespans']+[1,30])
    assert positive_control['dimension']==0 and positive_control['particular'][3]==-4
    OUT.mkdir(parents=True,exist_ok=True)
    result={'schema':'sunny.score-anchor-observability.v1','source':{'path':str(source.relative_to(ROOT)).replace('\\','/'),
        'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'constraint':'GT-TIME-OVERLAP','sourceSpans':case['source_refs']},
        'jevReceipt':'state/jev-receipts/000058-bbb3ab44bbf5.json',
        'domain':{'equations':'A*d=l; five ordered positive stages in the declared birth-entrance/death-exit experiment',
            'units':'Witness-relative reported years; no year-to-beat conversion',
            'scope':'Exact linear relations in this source-conditioned domain, not a complete universal ontology or original sound recovery'},
        'matrix':A,'retainedNullspaceBasis':nullspace,'minimumAdditionalIndependentObservations':2,
        'anchorPairs':pairs,'sufficientPairs':8,'redundantPairs':2,'witnessReplays':replays,
        'singleAnchorPredictions':singles,
        'symbolicConsequences':{'d4':'lB-lA+d1','d5':'lC-lB+d2','d3':'lA-d1-d2',
            'positiveDomain':'d1>max(0,lA-lB), d2>max(0,lB-lC), d1+d2<lA',
            'MT_positiveDomain':'d1>5, d2>0, d1+d2<438'},
        'contradictionControl':{'status':'synthetic deliberately incompatible anchors; not an observed witness error',
            'anchorValues':{'d1':35,'d4':31},'minimalConflicts':conflict,'irrelevantToThisConflict':['lifespan_C'],
            'requiredIdentity':'d4-d1=lB-lA=-5; the two supplied anchors instead give -4'},
        'orderControl':{'anchors':{'d1':1,'d2':30},'uniqueAlgebraicSolution':positive_control['particular'],
            'positiveOrderedStageModelAdmissible':False,'consequence':'Recompute event order or reject these anchors in the fixed ordering; do not report a negative duration as a physical performance'},
        'representationChange':{'from':'ordered stage durations d','to':'cumulative event offsets z=T*d',
            'matrix':T,'inverse':inverse,'equationTransform':'A -> A*T^-1; every anchor covector transforms the same way',
            'proof':'For invertible T the solution sets correspond bijectively. A target is fixed exactly when its covector annihilates every null vector; this criterion is unchanged by simultaneous inverse transformation.',
            'checkedReplays':40,'transferBoundary':'Nonlinear, unit-changing, temporal-origin or source-witness identifications require their own adapters'},
        'priorArt':[{'title':'Gilbert Strang, Six Great Theorems / Linear Algebra in a Nutshell','url':'https://math.mit.edu/~gs/linearalgebra/ila5/linearalgebra5_6Great.pdf',
            'reuse':'Row-space/nullspace duality supplies the identifiability criterion; this is reused mathematics, not a claimed new theorem'},
            {'title':'SymPy matrices documentation','url':'https://docs.sympy.org/latest/modules/matrices/matrices.html',
            'reuse':'Exact Gauss-Jordan solution/nullspace methods; independent verification may use the installed library'}],
        'derivation':['A*(d-dprime)=0 for the difference of two score realizations, so every ambiguity lies in ker(A).',
            'A target c*d is unique iff c annihilates ker(A). Extra anchor rows resolve all ambiguity iff their restrictions to ker(A) have full rank2.',
            'Stage1and4 restrictions are equal; Stage2and5 restrictions are equal. Their paired determinants vanish. All other pairs have determinant+1or-1.',
            'Hence eight of the ten supplied duration pairs reconstruct every stage; the other two leave one degree of freedom.',
            'Strict positivity is an additional domain constraint, checked after algebraic consistency; no integer-year prior is imposed.'],
        'newInferenceScope':'A concrete extension of the retained overlap ambiguity: the exact measurement pairs and their surviving consequences. Not a novel general linear-algebra method.',
        'historicalOrientationSelected':False,'blindPrediction':False,'fullMissionComplete':False}
    snapshots=[]
    for relative,role in [('state/reconstruction/generational-constraints.json','retained source-conditioned calculation'),
                          ('state/jev-receipts/000058-bbb3ab44bbf5.json','actual model-directed investigation choice')]:
        original=ROOT/relative;raw=original.read_bytes();sha=hashlib.sha256(raw).hexdigest()
        target=ROOT/'data/raw/reconstruction-integrations'/sha/original.name
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():assert target.read_bytes()==raw
        else:target.write_bytes(raw)
        snapshots.append({'sourcePath':relative,'snapshotPath':str(target.relative_to(ROOT)).replace('\\','/'),
            'sha256':sha,'bytes':len(raw),'role':role})
    result['inputSnapshots']=snapshots
    result['codeBindings']=[{'path':relative,'sha256':hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()}
        for relative in ['scripts/derive_score_anchors.py','tests/score_anchors_independent.py']]
    encoded=encode(result)
    (OUT/'score-anchors.json').write_text(json.dumps(encoded,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (ROOT/'state/reconstruction/score-anchor-constraints.json').write_text(json.dumps(encoded,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    request={'state':{'arithmetic_expression':'1*0-0*1','declaredInterpretation':'Determinant of the restrictions for duration anchors d1,d4 on the retained two-dimensional timing kernel; zero means this pair is redundant'},
        'questions':{'determinant':{'type':'choice','instructions':'Which option equals the exact supplied determinant?',
            'criteria':{'rank_deficient':'0','independent_positive':'1','independent_negative':'-1'}}},'solvers':['arithmetic_exact']}
    (OUT/'prumo-anchor-request.json').write_text(json.dumps(request,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'passed','exit_code':0,'anchorPairs':10,'sufficientPairs':8,'redundantPairs':2,'witnessReplays':50,'basisChangedReplays':40,'minimalConflicts':conflict,'sourceQualified':True,'historicalOrientationSelected':False}))

if __name__=='__main__':main()
