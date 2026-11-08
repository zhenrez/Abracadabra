"""Freeze a scoped14-question scholarly baseline; preserve gaps and prior exposure."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'state/delivery-2026-11-07/pausal-operations'

def main():
    bank=ROOT/'state/research/reactivation/symbols/p0a-14-baseline.json'
    original=json.loads(bank.read_text(encoding='utf8'))
    answers=[
        ('bounded','Molin2020 supplies comparative pausal/contextual reconstructions; DeCaen/Dresher2020 discuss prosodic domains and pausal forms. Relational functional-dependency theory supplies the mathematical consistency criterion.','Original source editions and whole scholarly literature remain incompletely covered.'),
        ('bounded','Historical Semitic phonology, biblical reading traditions, prosody/cantillation, manuscript transmission and relational/functional mathematics.','The fields do not by themselves establish a musical or geometric adapter.'),
        ('bounded','Pausal/contextual form; qames/ṣere; vocalic shewa; matres lectionis; stress; intonational/phonological phrase; functional dependency; information-losing projection.','Similar terms across traditions do not establish identical operations.'),
        ('bounded','Context-conditioned phonological relations and prosodic-domain models; exact finite relation and functional-dependency tests.','The intended complete SUNNY geometry and original-sound map are not derived by these methods.'),
        ('partial','The acquired2020 primary edited volume and its source bibliographies provide a bounded entry point; inherited14-question baseline retained.','No exhaustive cross-tradition survey has been completed.'),
        ('partial','Inspected: Molin; DeCaen/Dresher; BerkeleyCS186 mathematical definitions. Shaked1995 and Naveh/Shaked1985 are cited-edition targets, not yet collated originals.','Field-wide canonical status is not inferred from these references.'),
        ('bounded','Context/lexeme/historical-vowel distinctions; tradition/witness differences; prosodic-domain versus accent-label rules; orthographic versus phonetic interpretation.','No single additional argument or historical explanation selected by source repetition or model preference.'),
        ('conditional','Within the admitted comparative pairs, a deterministic map from surface[a]andpausealone has incompatible outputs. Source-proposed same-accent counterexamples oppose an accent-only pause decoder.','These conditional counterexamples do not falsify a richer original-symbol system or establish ancient sounds.'),
        ('open','Original ink, cited edition locators, specimen dating, transcription-to-phone licensing, source-specific grammar and applicability to new words remain unresolved.','A unique global alignment and universal phonological rule remain open.'),
        ('bounded','Exa versioned primary-volume rendering, exactMolinspans, independent source-review ledgers, actual local Jev62 receipt.','Connector text is not byte-identical original PDF or independently observed inscription.'),
        ('partial','Molin compares bowl quotations with later Babylonian manuscript reconstructions and Tiberian written comparanda; DeCaen/Dresher analyze Tiberian prosody.','Do not silently transfer Tiberian accent/domain rules into unpointed Babylonian bowls.'),
        ('partial','Received spelling, reconstructed pronunciation, notation and grammar have different histories; pausal and contextual are source-defined roles, not measured silence.','Historical terminology and original phonological categories need source-specific recovery.'),
        ('bounded','Same-input/different-output conflicts are also studied as failures of functional dependency and as failure of an operation to descend through a quotient.','This structural reuse is not a new general theorem or a cross-domain historical identity.'),
        ('open','No negative search establishes absence of prior art. Source acquisition and searches are recorded separately in the shaked/prosody directories.','The complete scholarly and controlled heterodox census remains unfinished.')
    ]
    questions=[{**{k:q[k] for k in ['id','question']},'status':a[0],'answer':a[1],'gap':a[2]}
        for q,a in zip(original['questions'],answers)]
    assert len(questions)==14
    result={'schema':'sunny.pausal-operations-p0a-baseline.v1','frozenAt':datetime.now(timezone.utc).isoformat(),
        'questionBank':str(bank.relative_to(ROOT)).replace('\\','/'),'questionBankSha256':hashlib.sha256(bank.read_bytes()).hexdigest(),
        'scope':'Bounded current scholarly-method/source census; not complete original SUNNY research coverage.',
        'exposure':['Molin primary publication connector text already inspected','DeCaen/Dresher chapter current source review','BerkeleyCS186 functional-dependency definitions inspected'],
        'questions':questions,'heterodoxPhase':{'tenQuestionTriage':'not completed for this extension','M1throughM12':'not completed for this extension',
            'newHeterodoxSourceExposure':False,'boundary':'No completed First&3/4 Order census is claimed.'},
        'newGeneralTheoremClaimed':False,'fullMissionComplete':False}
    OUT.mkdir(parents=True,exist_ok=True);p=OUT/'p0a-baseline.json'
    if p.exists():
        old=p.read_bytes();history=OUT/'history';history.mkdir(exist_ok=True)
        saved=history/('p0a-'+hashlib.sha256(old).hexdigest()+'.json')
        if saved.exists():assert saved.read_bytes()==old
        else:saved.write_bytes(old)
    p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'bounded_baseline_frozen','exit_code':0,'questions':14,'fullCensusComplete':False}))

if __name__=='__main__':main()
