"""Independent exact countermodels; no historical dates or sound licenses inferred."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, itertools, json
import sympy as S
from sympy.logic.inference import satisfiable

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent

def main():
    inputs = [
        'docs/reconstruction/symbol-sound-census/qames-topology-discrimination.json',
        'docs/reconstruction/symbol-sound-census/phyla-waves-assessment.json',
        'state/reconstruction/phonological-context-constraints.json',
        'state/delivery-2026-11-07/symbol-contact/root/howard-2026-qames.pdf',
        'state/delivery-2026-11-07/symbol-contact/root/howard-pages.json',
        'state/jev-receipts/000061-54b57b45fbcd.json',
    ]
    hashes = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs}
    # Abstract ordinal coordinates, not proposed historical dates or change durations.
    # All four emit identical terminal written marks. C and P have identical phones
    # at every time, although only C contains a transmission edge.
    histories = {
        'I_strict_inheritance': {'ancestor':1,'donorOnset':1,'recipientOnset':1,'contact':None,'terminalMarks':[1,1]},
        'C_directed_contact': {'ancestor':0,'donorOnset':2,'recipientOnset':4,'contact':3,'terminalMarks':[1,1]},
        'P_parallel_changes': {'ancestor':0,'donorOnset':2,'recipientOnset':4,'contact':None,'terminalMarks':[1,1]},
        'S_pure_scribal_normalization': {'ancestor':0,'donorOnset':None,'recipientOnset':None,'contact':None,'terminalMarks':[1,1]},
    }
    def phone(h, field, t):
        onset=h[field];return int(onset is not None and t>=onset)
    profiles = {name:{'ancestor':h['ancestor'], 'donorAt0through5':[phone(h,'donorOnset',t) for t in range(6)],
        'recipientAt0through5':[phone(h,'recipientOnset',t) for t in range(6)]} for name,h in histories.items()}
    assert profiles['C_directed_contact']==profiles['P_parallel_changes']
    assert len({tuple(h['terminalMarks']) for h in histories.values()})==1
    # Finite observation pool derived from the declared trajectories, not names
    # assigned to mechanism labels. Exhaust all subsets to find what they separate.
    observations={
        'ancestor_phone':{name:p['ancestor'] for name,p in profiles.items()},
        'recipient_phone_at_3':{name:p['recipientAt0through5'][3] for name,p in profiles.items()},
        'recipient_phone_at_5':{name:p['recipientAt0through5'][5] for name,p in profiles.items()},
        'terminal_written_marks':{name:tuple(histories[name]['terminalMarks']) for name in histories},
    }
    pairs={}
    for left,right in itertools.combinations(histories,2):
        discriminators=[o for o,v in observations.items() if v[left]!=v[right]]
        pairs[left+' versus '+right]={'inclusionMinimalSeparators':[[o] for o in discriminators],
            'noSeparatorInPool':not discriminators}
    assert pairs['C_directed_contact versus P_parallel_changes']['noSeparatorInPool']
    # Real-arithmetic SAT: the directed contact explanation requires an already
    # changed donor and transmission no later than recipient acquisition.
    d,k,r=S.symbols('donorOnset contact recipientOnset',real=True)
    core=S.And(d<k,k<=r)
    controls=[]
    for name,extras in [
        ('recipient_before_donor', [d>=4,r<=3]),
        ('recipient_before_earliest_contact', [k>=4,r<=3]),
    ]:
        full=satisfiable(S.And(core,*extras),use_lra_theory=True)
        proper=[satisfiable(S.And(core,x),use_lra_theory=True) is not False for x in extras]
        assert full is False and all(proper)
        controls.append({'id':name,'eventCore':[str(d<k),str(k<=r)],'additionalBounds':[str(x) for x in extras],
            'satisfiable':False,'eachIndividualBoundSatisfiable':proper,'additionalBoundSetIsInclusionMinimal':True})
    # Simultaneous donor/recipient observations cannot by themselves establish
    # donor direction: C and P above are an explicit all-time counterexample.
    result={
        'schema':'sunny.independent-history-discriminator-review.v1',
        'checkedAt':datetime.now(timezone.utc).isoformat(), 'status':'passed','exit_code':0,
        'inputHashes':hashes, 'jevDirection':'actual local receipt61; no new inference by reviewer',
        'guardUse':{'plugin':'Supermemory','operation':'search_memory','success':True,
            'conversationId':'01a1b80f-2cb4-76ab-95f2-655427aa87a8',
            'query':'SUNNY qames-topology-discrimination phyla waves PW-C1 PW-C3 inheritance contact contextual phonology; preserve transcription-to-phone uncertainty',
            'relevantDocument':'72MKv9qUA2zfLWcFptLisV',
            'scope':'Retrieved continuity, not mathematical/historical certification'},
        'coordinateScope':'Abstract witness/event order coordinates; no historical date assigned.',
        'finiteModels':histories,'phoneticProfiles':profiles,'observations':observations,
        'pairwiseDistinguishability':pairs,'exactRealArithmeticControls':controls,
        'checks':[
            'All four models produce identical terminal written marks.',
            'Contact and parallel histories have identical full phonetic trajectories.',
            'Pure scribal-only and changed-pronunciation models separate if a terminal phone is independently licensed.',
            'Both contact-excluding bound pairs are unsatisfiable and inclusion-minimal relative to the declared contact core.',
            'No tree-count enumeration repeated.'
        ],
        'sourceConditions':[
            'Q states refer to the same source-qualified lexeme, morphology, syllabic environment, historical vowel, reading/performance register and meaning of the feature.',
            'Greek or Latin written letters do not supply independently licensed historical phone observations here.',
            'No-loss/no-reversal, a unique innovation and no cross-tradition transfer are hypotheses, not source facts.',
            'S is a pure observation-channel explanation only. A hybrid of scribal normalization and real change remains possible.',
            'Earliest possible contact must be independently justified; failure to find a contact record does not establish a lower bound.',
            'Ruling out one directed contact episode does not rule out all contacts, reversed direction or a third-party donor.'
        ],
        'sourceFindings':[
            {'locator':'Howard234fn29','finding':'Babylonian vowel quality is assumed by the author; a minority unrounded interpretation remains reported.'},
            {'locator':'Howard235fn33','finding':'The local consonantal correspondence differs: T has v where B can retain w; a shared consonant-change event is not licensed.'},
            {'locator':'Howard236fn39','finding':'Separative differences caution against directly making Secunda the B/T ancestor; contact is offered as an alternative.'},
            {'locator':'Howard236main','finding':'The trajectory from limited morphological distribution to broad change remains missing; absence of presented evidence does not settle it.'},
            {'locator':'PW-C3','finding':'Manuscript spelling standardization is an observation-channel candidate and need not create a spoken ancestry edge.'}
        ],
        'historicalMechanismSelected':False,'originalPhonesRecovered':False,
        'unresolved':['Original witness collation','Independent transcription-to-phone calibration','Context-matched dated observations','Independently bounded transmission opportunities','Inheritance/contact/parallel hybrid models'],
    }
    (OUT/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'passed','exit_code':0,'checks':len(result['checks']),'models':4,'minimalUnsatisfiableAdditionalBoundPairs':2,'contactParallelAllTimePhoneEquivalent':True,'historicalMechanismSelected':False}))

if __name__=='__main__':main()
