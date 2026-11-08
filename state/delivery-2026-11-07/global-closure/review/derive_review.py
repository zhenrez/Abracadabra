"""Independent group-action certificate and targeted sixteen-module source audit."""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime,timezone
import hashlib,itertools,json,re
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ptr(obj,path):
    for part in path.strip('/').split('/'):
        part=part.replace('~1','/').replace('~0','~')
        obj=obj[int(part)] if isinstance(obj,list) else obj[part]
    return obj
def values(obj,path=''):
    if isinstance(obj,dict):
        for k,v in obj.items():yield from values(v,path+'/'+k.replace('~','~0').replace('/','~1'))
    elif isinstance(obj,list):
        for i,v in enumerate(obj):yield from values(v,path+'/'+str(i))
    else:yield path,obj

def main():
    modelPath=ROOT/'state/reconstruction/model.json';modelRaw=modelPath.read_bytes();m=json.loads(modelRaw.decode('utf-8-sig'));modules=m['mathematical_execution']
    names=['coverage','native-derivations','orientation-predictions','tol-history-math','native-execution','generational-constraints','algebraic-extension','derived-laws','master-score','hierarchy-atlas-combined','contextual-alignment','symbol-sound-constraints','score-anchor-constraints','phonological-context-constraints','phonological-history-constraints','reading-operations']
    assert all(name in modules for name in names)
    selections={
        'coverage':(['/semantic_coverage','/count_contract'],'coverage-accounting','Inventory/contact is not a source-authenticated phase map or semantic completion.'),
        'native-derivations':(['/conventions','/connected_discriminator','/FK_registered_loop'],'source-conditioned-derived','Exact ratios/register/carries and distinct return grade survive; no map from these quantities to W72q is supplied.'),
        'orientation-predictions':(['/family','/proofs/0/premises','/proofs/1','/outstanding'],'conditional-fixed-coordinate-input','The existing prediction contract explicitly fixes coordinate labels and origin. Removing that contract is a changed comparison, not a source-proved license.'),
        'tol-history-math':(['/recovered/adapter','/partial_adapter_obligations','/unretrieved_literal_AB_BA'],'partial-source-adapter-and-open-definition','Registered source addresses/path/provenance must survive. Literal A/B operators and domains remain unretrieved; arbitrary shear cannot be substituted.'),
        'native-execution':(['/registry/4/executionScope','/registry/5/nativeInstanceRequirements','/novelty/nonClaims'],'source-native-finite-operator','Unspecified cyclic origins/orbits are retained, without identifying them with the W72q coordinate.'),
        'generational-constraints':(['/retained_axes','/constraints/1/scope','/constraints/2/gauge_limit','/constraints/4/minimal_state_requirement','/unresolved'],'source-frame-conditional','Adam/time origins and circuit parity are frame-qualified; return parity is explicitly not W72beta. No q-anchor transfer is supplied.'),
        'algebraic-extension':(['/scope','/discriminators/1'],'derived-exact-pitch-distinction','Exact prime-exponent/root/cycle residual distinguishes pitches; a shared finite dial is conditional and supplies no W72 orientation.'),
        'derived-laws':(['/law_proposals/4/assumptions','/law_proposals/5/assumptions','/law_proposals/12/assumptions','/unknowns'],'conditional-law-register','Fixed-phase premises and missing independent observations remain explicit; no unconditional promotion to physical equivalence.'),
        'master-score':(['/universalCompletion','/program/views/0/condition','/program/views/1/participants/0/coordinates','/readingExtension/boundary'],'source-clock-and-role-qualified','Reported-year/GEN/ADR contexts and untimed phonetic annotations are distinct; no global q licensing follows.'),
        'hierarchy-atlas-combined':(['/globalOrientationSelected','/proposedExternalJoins','/unresolved/5','/unresolved/9'],'native-identity-and-open-cross-domain-joins','Stable source identities and typed joins are retained. Musical chain/address recurrence does not erase exact residual; no phase-label identification is admitted here.'),
        'contextual-alignment':(['/nativeMathematicalRegister','/transformationRegister/modalInverse','/transformationRegister/allRitualConditions/relative_standard_concordance'],'conditional-modern-pitchclass-adapter','Gong/role offsets and relative standard names are declared Z12 pitch-class conventions, with free common alpha. T leaves p fixed; this does not constrain q without another bridge.'),
        'symbol-sound-constraints':(['/presenceProjection','/observationBoundary','/sourceCondition'],'source-phonological-hypothesis','Two contextual mark grammars share a presence projection; not a W72q measurement or musical sound assignment.'),
        'score-anchor-constraints':(['/representationChange','/domain/scope'],'derived-linear-coordinate-law','Simultaneous transformation of equations and anchor covectors preserves deductions; non-unit/frame changes need separate adapters. This does not license a source phase shear.'),
        'phonological-context-constraints':(['/typeBoundary','/coarseFeatureBoundary','/originalSoundRecovered'],'source-context-conditional','Context, historical process and comparative grade remain explicit; no W72 address-to-phone assignment.'),
        'phonological-history-constraints':(['/currentHistoricalBoundsAdmitted','/operator','/historicalMechanismSelected'],'conditional-event-order','Contact order uses its own real event windows; zero actual historical bounds admitted and no W72phase bridge.'),
        'reading-operations':(['/conditions','/scoreAnnotationBoundary','/historicalOperatorSelected'],'source-reading-conditional','Molin notation, lexical/grammatical alternatives and unknown acoustics are retained; no sacred-original sound or phase coupling is established.'),
    }
    audit=[];keywordIndex={};pattern=re.compile(r'\bphase\b|\bchirality\b|\bshear\b|\borigin\b|\bmetric\b|\bresidual\b|\bbeta\b|\bternary\b|AB/BA|Completed Harmony|TOL',re.I)
    for name in names:
        path=ROOT/'state/reconstruction'/f'{name}.json';moduleRaw=path.read_bytes();unit=json.loads(moduleRaw.decode('utf-8-sig'))
        paths,classification,finding=selections[name]
        # Root may append the new probe certificate while reviewing. Bind the
        # actual module bytes and confirm every reviewed old constraint survives.
        assert all(ptr(unit,p)==ptr(modules[name],p) for p in paths),name
        refs=[{'path':str(path.relative_to(ROOT)).replace('\\','/'),'pointer':p,'value':ptr(unit,p)} for p in paths]
        audit.append({'module':name,'sha256':hashlib.sha256(moduleRaw).hexdigest(),'matchesModelSnapshotAtReview':unit==modules[name],'reviewedConstraintsMatchModelSnapshot':True,'classification':classification,'finding':finding,'references':refs,
            'scope':'Targeted semantic review of the listed definitions/constraints; all scalar leaves mechanically indexed separately. Not exhaustive historical source reconstruction.'})
        keywordIndex[name]=[{'pointer':p,'value':v} for p,v in values(unit) if pattern.search(p) or isinstance(v,str) and pattern.search(v)]
    # Independent brute-force action over every carrier element.
    carrier=list(itertools.product(range(12),range(6)));group=list(itertools.product([1,5],range(6)));family=list(itertools.product(range(6),[1,5]))
    def T(g,x):u,v=g;p,q=x;return p,(u*q+v*p)%6
    def add(x,y):return (x[0]+y[0])%12,(x[1]+y[1])%6
    def act(g,c):u,v=g;b,s=c;return (u*b-v)%6,u*s%6
    def compose(g,h):u,v=g;a,b=h;return u*a%6,(u*b+v)%6
    for g in group:
        assert len({T(g,x) for x in carrier})==72
        for x in carrier:
            for y in carrier:assert T(g,add(x,y))==add(T(g,x),T(g,y))
        for h in group:
            assert compose(g,h) in group
            for x in carrier:assert T(g,T(h,x))==T(compose(g,h),x)
        for b,s in family:
            b2,s2=act(g,(b,s))
            for x in carrier:
                assert T(g,add(x,(5,b)))==add(T(g,x),(5,b2))
                assert T(g,add(x,(7,(s-b)%6)))==add(T(g,x),(7,(s2-b2)%6))
    def orbitPartition(subgroup):
        unseen=set(family);orbits=[]
        while unseen:
            c=min(unseen);orb={act(g,c) for g in subgroup};orbits.append(sorted(orb));unseen-=orb
        return orbits
    groups={
        'p_only':group,
        'p_and_beta':[(u,v) for u,v in group if all(T((u,v),x)[1]%2==x[1]%2 for x in carrier)],
        'p_and_tau':[(u,v) for u,v in group if all(T((u,v),x)[1]%3==x[1]%3 for x in carrier)],
        'p_beta_tau':[(u,v) for u,v in group if all(T((u,v),x)[1]==x[1] for x in carrier)],
        'p_and_origin':[(u,v) for u,v in group if T((u,v),(0,0))==(0,0)],
        'p_no_shear':[(u,v) for u,v in group if v==0],
    }
    partitions={label:{'group':gs,'orbits':orbitPartition(gs)} for label,gs in groups.items()}
    assert [len(partitions[k]['orbits']) for k in ['p_only','p_and_beta','p_and_tau','p_beta_tau']]==[1,2,6,12]
    assert len(partitions['p_and_origin']['group'])==12
    stabilizers=[{'candidate':c,'elements':[g for g in group if act(g,c)==c]} for c in family]
    assert all(len(s['elements'])==1 for s in stabilizers)
    # Scalar descriptors are path-dependent but independent of the optional phase completion.
    scalarCounterexamples=[]
    for c in family:
        b,s=c;scalarCounterexamples.append({'candidate':c,'Raddress':[5,b],'Oaddress':[0,s],'Rscalar':'2/3','Oscalar':'1/2',
            'R12Address':[0,0],'R12Scalar':str(F(2,3)**12),'octaveCompensatedR12':str(2**7*F(2,3)**12)})
    assert len({x['R12Scalar'] for x in scalarCounterexamples})==1
    for r,l in itertools.product(range(12),repeat=2):
        scalar=F(2,3)**r*F(3,4)**l
        assert all(F(2)**(r-2*l)*F(3)**(l-r)==scalar for _ in family)
    atlas=ROOT/'data/raw/recovered/f07f6e78ad08c09559939d044f382c5fb15a88ca56d10f2a6f5d060475e908fb/SUN_SOL_Orientation_Atlas.md'
    source=atlas.read_text(encoding='utf-8-sig')
    snippets=[
        'Their classification depends on the labels retained.',
        'The original phase-contract attachment cited by a recovered assistant passage was also not retrieved.',
        'A coordinate relabeling that moves every label with it is a gauge change;',
        'Selecting one of the twelve transitive completions requires a purpose for phase transport and independent evidence about its labels.',
    ]
    refs=[]
    for snippet in snippets:
        start=source.index(snippet);end=source.find('\n',start)
        refs.append({'path':str(atlas.relative_to(ROOT)).replace('\\','/'),'sha256':sha(atlas),'startCodePoint':start,'endCodePointExclusive':end,'lineOneBased':source.count('\n',0,start)+1,'quote':source[start:end]})
    result={'schema':'sunny.independent-global-closure-review.v1','checkedAt':datetime.now(timezone.utc).isoformat(),'status':'passed','exit_code':0,
        'modelSha256AtRead':hashlib.sha256(modelRaw).hexdigest(),'moduleBindingScope':'Actual module bytes at review; original selected constraints are checked against the model snapshot. A concurrent appended probe certificate may await model reassembly.','jevReceipt':'state/jev-receipts/000063-298ff24c136a.json','modulesReviewed':audit,'moduleCount':16,
        'sourcePriorArt':refs,'priorArtFinding':'The p-preserving equivalence and beta/tau refinements are explicit in the recovered October18orientationatlas §4.2. This certificate reproduces/refines that result; no new symmetry-discovery claim.',
        'groupLaw':'(u,v)∘(a,b)=(ua,ub+v)mod6','candidateAction':'(b,s)→(ub-v,us)mod6','carrierElements':72,'groupOrder':12,
        'partitions':partitions,'stabilizers':stabilizers,'scalarCounterexamples':scalarCounterexamples,
        'concreteCounterexamples':[
            {'case':'Origin alone does not anchor the phase convention','transform':[1,1],'originBefore':[0,0],'originAfter':[0,0],'pointBefore':[1,0],'pointAfter':[1,1]},
            {'case':'Conjugacy is not fixed-operator commutation','candidateBefore':[0,1],'transform':[1,5],'candidateAfter':[1,1],'RphaseBefore':0,'RphaseAfter':1,'sameScalar':'2/3'},
            {'case':'Scalar/registered path residual supplies no absolute phase anchor','differentOphases':[1,5],'sameOscalar':'1/2','allCompletionsR12Residual':'524288/531441'},
            {'case':'A fixed product metric would forbid a shear, but no such global metric is supplied here','hypotheticalMetric':'squared sum of shortest cyclic unit-coordinate distances','transform':[1,1],'fromOriginPoint':[1,0],'distanceSquaredBefore':1,'distanceSquaredAfter':2,'sourceLicense':'not asserted'},
        ],
        'minimumMissingBridge':'Independent source-qualified semantic phase measurements sufficient to instantiate q(R) and q(O), OR an explicitly source-licensed equivalence contract transporting every phase label/observation/adapter covariantly. A bare origin or scalar residual is insufficient.',
        'limits':['This is one optional transitive12family, not allSUNNYconfigurations.','The separate phase-preserving profile remains retained.','All16modules reviewed at the displayed source-qualified definitions; whole-corpus semantics and inaccessible sources remain open.','No fixed historical/display labels may be silently moved.','TOLAB/BA operational definitions remain unretrieved.'],
        'guardUse':{'plugin':'Supermemory','operation':'search_memory','success':True,'conversationId':'01a1b80f-2cb4-76ab-95f2-655427aa87a8','scope':'Retrieved continuity, not mathematical or historical certification.'},
        'historicalOrientationSelected':False,'fullGeometryReconstructed':False}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'module-keyword-index.json').write_text(json.dumps({'scope':'Mechanical discovery index; not a semantic reconstruction claim.','modules':keywordIndex},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (OUT/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'passed','exit_code':0,'modulesReviewed':16,'groupOrder':12,'orbitCount':1,'allStabilizerOrders':1,'betaTauOrbitCounts':[2,6,12],'originAloneLeaves12':True,'priorArtAlreadyStatesEquivalence':True,'scalarResidualSuppliesNoAbsolutePhaseAnchor':True}))
if __name__=='__main__':main()
