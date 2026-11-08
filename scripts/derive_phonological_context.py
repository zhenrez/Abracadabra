"""Source-conditioned phonetic context and relative-chronology constraints, not original sound recovery."""
from pathlib import Path
from itertools import permutations
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'state/delivery-2026-11-07/symbol-contact/root'
sha=lambda raw:hashlib.sha256(raw).hexdigest()

def main():
    extraction=json.loads((FOLDER/'howard-pages.json').read_text(encoding='utf8'))
    pdf=FOLDER/'howard-2026-qames.pdf'
    assert sha(pdf.read_bytes())==extraction['sourceSha256']
    pages={p['printedPage']:p for p in extraction['pages']}
    compact=lambda s:''.join(s.split())
    forms=[('Ps18:39','εμωσημ',2,True),('Ps18:43','ουεσοκημ',4,True),
        ('Ps18:36','θεσοδηνι',3,True),('Ps89:39','ὀυαθθεμας',7,False),
        ('Ps89:47','θεβαρ',3,False),('Ps35:22','ελθαρακ',5,False)]
    rows=[]
    for locus,form,index,suffix in forms:
        text=pages[233]['text'];assert form in text,(locus,form)
        observed='O-grade' if form[index] in 'οω' else 'A-grade' if form[index]=='α' else None
        assert observed==('O-grade' if suffix else 'A-grade')
        rows.append({'locus':locus,'publishedGreekForm':form,'themeIndexZeroBased':index,
            'publishedThemeLetter':form[index],'transcriptionGrade':observed,'pronominalSuffix':suffix,
            'readingLayer':'Howard reported edition reading; not independently collated manuscript ink',
            'source':{'printedPage':233,'pdfPageOneBased':5,'textStart':text.index(form),'textEnd':text.index(form)+len(form)}})
    assert 'θεσαδηνι' in pages[233]['text']
    variants=[{'editionReport':'Yuditsky / Carrera Companioni2022p190 as cited by Howard','theme':'ο'},
        {'editionReport':'Sperber1938p159 as cited by Howard','theme':'α'},
        {'editionReport':'Mercati unread theme vowel as reported by Howard','theme':None}]
    cases=[]
    for variant in variants:
        grades=[r['transcriptionGrade'] for r in rows]
        grades[2]='O-grade' if variant['theme']=='ο' else 'A-grade' if variant['theme']=='α' else None
        failures=[r['locus'] for r,g in zip(rows,grades) if g is not None and g!=('O-grade' if r['pronominalSuffix'] else 'A-grade')]
        cases.append({'reading':variant,'transcriptionGrades':grades,'checkedContexts':sum(g is not None for g in grades),
            'simpleSuffixConditionConflicts':failures,'scope':'Compatibility of this explicit transcription-grade rule only; no broad phonological or morphological account eliminated'})
    events=['L_local_pre_waw_rounding','V_w_to_v','G_general_syllable_shift']
    edges=[(events[0],events[1]),(events[0],events[2])]
    extensions=[list(order) for order in permutations(events) if all(order.index(a)<order.index(b) for a,b in edges)]
    assert len(extensions)==2
    assert any(o.index(events[2])>o.index(events[1]) for o in extensions)
    assert any(o.index(events[2])<o.index(events[1]) for o in extensions)
    result={'schema':'sunny.phonological-context-constraints.v1','jevReceipt':'state/jev-receipts/000060-a1b30f75db7d.json',
        'source':{'author':'Jonathan Howard','doi':'10.1017/S0041977X25100992','onlineDate':'2025-12-22','issueDate':'2026',
            'url':'https://doi.org/10.1017/S0041977X25100992','pdfSha256':extraction['sourceSha256'],'license':'CC BY-NC-SA4.0'},
        'sourceCases':rows,'disputedThemeVowel':{'locus':'Ps18:36','variants':variants,'locator':'printed233footnote25',
            'primaryCollationPending':True},'conditionalExecutions':cases,
        'retainedExplanations':[{'id':'syllable_conditioned_rounding','source':'Howard2026pp232–237','status':'source-proposed; conditional'},
            {'id':'morphological_stem_or_analogy','source':'Alternative scholarship discussed by Howardpp231–233','status':'retained competing explanation; not eliminated by the same grade pattern'}],
        'provisionalComparisonArguments':['source-qualified sign','historical vowel class','syllable environment','morphology','stress/pause','tradition and source date','edition reading'],
        'typeBoundary':'These arguments are required by this source comparison; they are not asserted complete or irreducible universal types.',
        'chronology':{'source':'Howardp235 critiques transfer of a local assimilation date to the broader shift; Kantor2023pp78–79 retains the earlier argument.',
            'events':events,'conditionalPrecedenceEdges':edges,'allStrictLinearExtensions':extensions,
            'newConsequence':'L<V and L<G do not entail G<V. An upper bound on V does not supply an upper bound on G without an additional bridge premise.',
            'proof':'Both listed total orders satisfy every supplied edge, but they place G on opposite sides of V. One is a countermodel to each purported forced order.',
            'missingPremise':'An independently justified relation between local assimilation and the broader shift sufficient to transfer the claimed date bound.',
            'scope':'Conditional relative chronology of phonological processes; no ancient calendar date or institutional rectification selected'},
        'coarseFeatureBoundary':'The old five-tradition binary example remains preserved within its assumptions. Contextual/lexical diffusion and disputed forms require explicit refinement before transferring its topology counts to historical genealogy.',
        'independence':'Howard reassesses earlier editions and arguments; this is not an independent newly discovered manuscript. Six published forms are not six independent historical witnesses.',
        'open':['Independent collation of Ps18:36 theme vowel','Original chronology/contact witnesses','Licensing Greek transcription grade to a historical phone','Discrimination of phonological and morphological explanations'],
        'originalSoundRecovered':False,'historicalGenealogySelected':False,'blindPrediction':False,'fullMissionComplete':False}
    snapshots=[]
    for source in [pdf,FOLDER/'howard-pages.json',ROOT/'state/jev-receipts/000060-a1b30f75db7d.json']:
        raw=source.read_bytes();digest=sha(raw);target=ROOT/'data/raw/reconstruction-integrations'/digest/source.name
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():assert target.read_bytes()==raw
        else:target.write_bytes(raw)
        snapshots.append({'sourcePath':str(source.relative_to(ROOT)).replace('\\','/'),'snapshotPath':str(target.relative_to(ROOT)).replace('\\','/'),'sha256':digest,'bytes':len(raw)})
    result['inputSnapshots']=snapshots
    result['codeBindings']=[{'path':relative,'sha256':sha((ROOT/relative).read_bytes())}
        for relative in ['scripts/derive_phonological_context.py','tests/phonological_context_independent.py']]
    raw=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    (FOLDER/'context-constraints.json').write_text(raw,encoding='utf8')
    (ROOT/'state/reconstruction/phonological-context-constraints.json').write_text(raw,encoding='utf8')
    print(json.dumps({'status':'passed','exit_code':0,'publishedForms':len(rows),'explicitReadingBranches':len(cases),'chronologicalExtensions':len(extensions),'originalSoundRecovered':False,'sourceGradeIsNotPhone':True}))

if __name__=='__main__':main()
