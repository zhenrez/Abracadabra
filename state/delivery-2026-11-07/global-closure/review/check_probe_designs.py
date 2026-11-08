"""Independent direct-address oracle for every two-word phase probe pair."""
from pathlib import Path
from datetime import datetime,timezone
from math import gcd
import hashlib,itertools,json
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent

def main():
    path=ROOT/'state/delivery-2026-11-07/global-closure/phase-probe-designs.json';raw=path.read_bytes();record=json.loads(raw)
    candidates=list(itertools.product(range(6),[1,5]));words=list(itertools.product(range(12),repeat=2))
    # Walk R then L as actual translations rather than importing the proposed
    # q coefficient/determinant implementation.
    def observe(word,candidate):
        r,l=word;b,s=candidate;p=q=0
        for _ in range(r):p=(p+5)%12;q=(q+b)%6
        for _ in range(l):p=(p+7)%12;q=(q+s-b)%6
        return q
    vectors={w:tuple(observe(w,c) for c in candidates) for w in words}
    sufficient=[];insufficient=[];mismatches=[];failures=[]
    for a,b in itertools.combinations(words,2):
        signatures=[(vectors[a][i],vectors[b][i]) for i in range(12)]
        direct=len(set(signatures))==12
        criterion=gcd(a[0]-a[1],b[0]-b[1],6)==1 and (a[0]*b[1]-b[0]*a[1])%3!=0
        if direct!=criterion:mismatches.append([a,b,direct,criterion])
        (sufficient if direct else insufficient).append((a,b))
    assert len(sufficient)+len(insufficient)==10296 and not mismatches
    assert len(sufficient)==record['counts']['minimalSufficientPairs']==4608
    assert len(insufficient)==record['counts']['insufficientPairs']==5688
    assert all(len(set(v))<12 for v in vectors.values())
    # Canonical pair IDs normalize the independently generated pairs.
    expected={frozenset(('R'+str(a[0])+'L'+str(a[1]),'R'+str(b[0])+'L'+str(b[1]))) for a,b in sufficient}
    supplied=record['sufficientPairs']
    def pair_ids(row):
        if isinstance(row,list):return frozenset(row)
        for key in ['probes','wordIds','probeIds','ids','words','pair']:
            if key in row:return frozenset(row[key])
        if 'left' in row and 'right' in row:return frozenset((row['left'],row['right']))
        if 'first' in row and 'second' in row:return frozenset((row['first'],row['second']))
        raise AssertionError('Unrecognized source pair representation: '+repr(row)[:300])
    assert {pair_ids(row) for row in supplied}==expected
    # Two distinct failures show why neither conjunct can be omitted.
    gcdOnly=[(a,b) for a,b in itertools.combinations(words,2) if gcd(a[0]-a[1],b[0]-b[1],6)==1 and (a[0]*b[1]-b[0]*a[1])%3==0]
    determinantOnly=[(a,b) for a,b in itertools.combinations(words,2) if gcd(a[0]-a[1],b[0]-b[1],6)!=1 and (a[0]*b[1]-b[0]*a[1])%3!=0]
    def collision(pair):
        a,b=pair;seen={}
        for i,c in enumerate(candidates):
            signature=(vectors[a][i],vectors[b][i])
            if signature in seen:return {'words':pair,'candidates':[seen[signature],c],'sameObservedPhases':signature}
            seen[signature]=c
        raise AssertionError('Expected collision')
    controls={'gcdConjunctAlone':collision(gcdOnly[0]),'determinantConjunctAlone':collision(determinantOnly[0])}
    result={'schema':'sunny.independent-phase-probe-design-review.v1','checkedAt':datetime.now(timezone.utc).isoformat(),'status':'passed','exit_code':0,
        'inputSha256':hashlib.sha256(raw).hexdigest(),'inputPath':str(path.relative_to(ROOT)).replace('\\','/'),
        'wordOccurrences':144,'candidateCompletions':12,'pairsChecked':10296,'sufficientPairs':4608,'insufficientPairs':5688,'criterionMismatches':0,
        'entirePublishedSufficientPairSetMatches':True,'singleProbeCanIdentifyAll12':False,'minimumFixedLabelPhaseProbes':2,
        'oracle':'Independent direct iteration of R=(5,b), L=(7,s-b) on the72address carrier, followed by equality partitions of the12candidate signatures.',
        'necessaryConjunctCounterexamples':controls,
        'boundary':'Fixed source/observation phase labels and origin, same optional transitive family only. No actual historical phase observation, unique historical orientation, unrestricted family elimination or full-corpus novelty claim.',
        'priorArt':'Orbit result already explicit in the recovered sourceatlas4.2; arbitrary two-word sufficient-pair classification is a new bounded execution refinement here, with complete-corpus novelty unestablished.'}
    (OUT/'probe-design-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
