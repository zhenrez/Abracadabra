"""Independent source-role and finite-function counterexample for Molin examples7/8."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,itertools,json,re,unicodedata
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent

def main():
    path=ROOT/'state/delivery-2026-11-07/history-discriminator/exa-loc-fetch.json'
    raw=path.read_bytes();text=json.loads(raw)['content'][0]['text']
    receipt=ROOT/'state/jev-receipts/000062-5fcc72f3ccd7.json'
    def span(value):
        start=text.index(value)
        return {'text':value,'startCodePoint':start,'endCodePointExclusive':start+len(value)}
    words=[
        {'example':7,'word':'שומורו','normalizedBhsComparator':'שמרו','reference':'Num9:23','citation':'HLIB213;684.14',
         'pausal':'ʃɔːˈmɔːruː','contextual':'ʃɔːmaˈruː','contextualMedialNucleus':'a','pausalMedialNucleus':'ɔː','comparativeFootnote':'47;Yeivin1985p427'},
        {'example':8,'word':'תוכילו','normalizedBhsComparator':'תאכלו','reference':'Lev26:29','citation':'AMB176;9.9',
         'pausal':'toːˈχeːluː','contextual':'toːχaˈluː','contextualMedialNucleus':'a','pausalMedialNucleus':'eː','comparativeFootnote':'48;Yeivin1985p585'},
    ]
    ipa=[]
    for row in words:
        row['wordSpan']=span(row['word']);row['ipaSpans']={key:span(row[key]) for key in ['pausal','contextual']}
        for role in ['contextual','pausal']:
            value=row[role];stress=value.index('ˈ');nuclei=[(i,c) for i,c in enumerate(value) if c in 'aɔuoe']
            stressIndex=1+sum(i<stress for i,_ in nuclei)
            assert len(nuclei)==3
            assert stressIndex==(3 if role=='contextual' else 2)
            ipa.append({'example':row['example'],'role':role,'ipa':value,'stressSyllableOneBased':stressIndex,'syllableNuclei':[c for _,c in nuclei],
                'lengthMarkCount':value.count('ː'),'notationNotMeasuredDuration':True})
    # Source extraction keeps the BHS string's exact mark order; only the declared
    # consonant comparator is normalized, not its damaged vowel/RTL representation.
    exampleLines={}
    for number in [7,8]:
        line=next(line for line in text.splitlines() if line.endswith('('+str(number)+') '))
        before=line.split(' BHS)')[0]
        bare=''.join(c for c in unicodedata.normalize('NFD',before) if '\u05d0'<=c<='\u05ea')
        assert bare==words[number-7]['normalizedBhsComparator']
        exampleLines[str(number)]={'rawLine':line,'normalizedConsonantsOnly':bare,'vocalizationNormalizationClaimed':False}
    assert words[0]['word'].count('ו')==3 and words[0]['normalizedBhsComparator'].count('ו')==1
    assert 'χ' in words[1]['pausal'] and ord('χ')==0x03c7
    assert '47 Yeivin (1985, 427). Again, [a] here indicates shewa.' in text
    assert '48 Yeivin (1985, 585).' in text
    # All deterministic functions on the two exposed (a,pauseFlag) inputs, into
    # the observed output alphabet, fail the two paused targets simultaneously.
    outputs=['a','ɔː','eː'];functions=list(itertools.product(outputs,repeat=2))
    survivors=[f for f in functions if f[0]=='a' and f[1]=='ɔː' and f[1]=='eː']
    assert not survivors
    stateFunctions=[]
    for z7,z8 in itertools.product([0,1],repeat=2):
        if z7==z8:continue
        f={(z7,True):'ɔː',(z8,True):'eː',(z7,False):'a',(z8,False):'a'}
        stateFunctions.append({'stateByExample':{'7':z7,'8':z8},'rows':[{'additionalState':z,'pause':p,'output':v} for (z,p),v in sorted(f.items())]})
    assert len(stateFunctions)==2
    result={
        'schema':'sunny.independent-pausal-operation-review.v1','checkedAt':datetime.now(timezone.utc).isoformat(),'status':'passed','exit_code':0,
        'inputHashes':{'state/delivery-2026-11-07/history-discriminator/exa-loc-fetch.json':hashlib.sha256(raw).hexdigest(),
            'state/jev-receipts/000062-5fcc72f3ccd7.json':hashlib.sha256(receipt.read_bytes()).hexdigest()},
        'sourceLayer':'Exa retrieved text of original Molin publication; not PDF-page collation, original bowl ink or an ancient recording.',
        'sourceUrl':'https://tile.loc.gov/storage-services/master/gdc/gdcebookspublic/20/19/39/45/70/2019394570/2019394570.pdf',
        'sectionSpan':span('2.4. Evidence for the Prominence of Orality'), 'wordCases':words,'exactExampleLines':exampleLines,'ipaAnalysis':ipa,
        'primarySourceCitations':{
            'HLIB':span('(HLIB) Shaked, Shaul. 1995.'),
            'AMB':span('(AMB) Naveh, Joseph and Shaul Shaked. 1985.'),
            'Yeivin47':span('47 Yeivin (1985, 427). Again, [a] here indicates shewa.'),
            'Yeivin48':span('48 Yeivin (1985, 585).')},
        'counterexample':{'assumption':'Both exposed examples belong to a shared deterministic operator family whose only inputs are current medial nucleus and pauseFlag.',
            'inputsEqual':[['a',True],['a',True]],'requiredOutputs':['ɔː','eː'],'functionsEnumerated':len(functions),'functionsSatisfyingBoth':len(survivors),
            'minimumDistinctAdditionalStates':2,'twoStateRealizationsUpToLabelSwap':stateFunctions,
            'scope':'Necessity of some distinguishing state under the assumption, not proof of a particular historical sound rule.'},
        'retainedParameterCandidates':['Lexeme/root or learned lexical association','Consonantal/segmental environment','Morphological or inflectional class','Historical vowel derivation','Witness/reading tradition or performance register','Operator-family selection'],
        'roles':{'bowlSpellings':'Published forms attributed to the cited bowl evidence.',
            'BhsComparators':'Received biblical comparators; no claim that BHS reproduces the bowl vowels.',
            'PausalIpa':'Author conditional historical pronunciation interpretation.',
            'ContextualIpa':'Corresponding Babylonian-manuscript comparandum, not a contextual token on the same bowl.',
            'Stress':'Stress location inferred within the printed three-nucleus IPA strings; no measured onset time.',
            'Length':'IPA length notation only, without milliseconds, waveform, frequency, pitch or a forced2:1ratio.'},
        'guardUse':{'plugin':'Supermemory','operation':'search_memory','success':True,'conversationId':'01a1b80f-2cb4-76ab-95f2-655427aa87a8','scope':'Continuity retrieval; not source certification.'},
        'checks':['Exact4IPAstrings and2wordspans found','Both BHSconsonantcomparators recovered without vowel reconstruction','Both stresses shift syllable3to2 onebased','9unaryfunctions yield0solutions','Atleast2additionalstates suffice without selecting their identity','Contextual comparanda and phonetic/duration limits retained'],
        'originalPhonesRecovered':False,'specificHistoricalOperatorSelected':False,
        'unverified':['Bowl ink and specimen chronology','Expansion of684.14 and9.9beyond printed citation','Manuscript originals underlying Yeivin comparisons','Acoustic durations/waveforms','Which distinguishing state the historical operation used']}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'passed','exit_code':0,'checks':len(result['checks']),'ipaStrings':4,'wordCases':2,'unaryFunctions':9,'survivors':0,'minimumAdditionalStateCardinality':2},ensure_ascii=False))
if __name__=='__main__':main()
