"""Execute the installed evidence guard and finite genealogy integrity checks."""
from pathlib import Path
import copy,hashlib,json,subprocess,sys
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
GUARD=Path('C:/Users/Brend/.codex/plugins/cache/created-by-me-remote/prumo-jev-research/0.1.1/skills/evidence-audit/scripts/evidence_ledger.py')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def guard(operation,payload,expect_success=True):
    run=subprocess.run([sys.executable,'-X','utf8','-B',str(GUARD),operation],input=json.dumps(payload,ensure_ascii=False),encoding='utf-8',capture_output=True)
    data=json.loads(run.stdout)
    assert (run.returncode==0)==expect_success,(operation,run.returncode,data)
    return data
def main():
    source_path=BASE/'genesis-primary-regions.json';raw=source_path.read_bytes();text=raw.decode('utf-8')
    source=guard('init-source',{'source_id':'genesis-primary-regions','locator':str(source_path.relative_to(ROOT)).replace('\\','/'),'text':text})['source']
    comparison=json.loads((BASE/'genesis-witness-comparison.json').read_text(encoding='utf-8'))
    records=[]
    for claim in comparison['ageAtBegettingClaims']:
        if claim['family'] not in ['MT','SP']:continue
        quote=json.dumps(claim['sourceRegion']['literalSourceText'],ensure_ascii=False)
        match=guard('locate',{'source':source,'objective':{'objective_id':claim['id'],'question':'Verify exact captured transcription string, not its numeric interpretation or ancient truth.'},'quote':quote})
        records.append(match['evidence'])
    validated=guard('validate',{'source':source,'records':records})
    tampered=copy.deepcopy(records[0]);tampered['passages'][0]['text']+='x'
    rejection=guard('validate',{'source':source,'evidence':tampered},False)
    model_path=ROOT/'state/reconstruction/biblical-genealogies.json';model=json.loads(model_path.read_text(encoding='utf-8'))
    ids={e['id'] for e in model['entities']};relations={e['id']:e for e in model['relationships']}
    assert len(ids)==len(model['entities']) and len(relations)==len(model['relationships'])
    assert all(e['source'] in ids and e['target'] in ids for e in relations.values())
    assert len(model['receivedSourcePlacements'])==15
    master=json.loads((ROOT/'state/reconstruction/master-score.json').read_text(encoding='utf-8'))
    lookup={p['id']:p for v in master['program']['views'] if v['id'].startswith('chronology:') for p in v['participants']}
    for row in model['receivedSourcePlacements']:
        source_row=lookup[row['sourceParticipantId']]
        assert row['onset']==source_row['onset'] and row['duration']==source_row['duration']
        assert row['GEN']==source_row['coordinates']['GEN'] and row['TIME']==source_row['coordinates']['TIME']
    assert {c['family']:c['namedEntries'] for c in model['receivedNativeLineageChains']}=={'MT':33,'SP':25,'Greek':34}
    for chain in model['receivedNativeLineageChains']:
        assert len(set(chain['nodeIds']))==len(chain['nodeIds'])
        assert [(relations[k]['source'],relations[k]['target']) for k in chain['relationshipIds']]==list(zip(chain['nodeIds'],chain['nodeIds'][1:]))
        if chain['family']=='SP':assert all(r.startswith('Gen.') for k in chain['relationshipIds'] for r in relations[k]['verseRefs'])
    assert model['counts']['originalEditionParentageAssertionsAdmitted']==49
    assert model['counts']['ancientInkIndependentlyInspectedAssertions']==0
    assert comparison['GreekSource']['apparatusGen11_13']['reportedVariants']==[{'siglum':'E','years':330},{'siglum':'D','years':130}]
    for item in comparison['GreekSource']['sourceBindings']:assert sha(BASE/item['path'])==item['sha256']
    assert sha(BASE/comparison['MTsource']['path'])==comparison['MTsource']['sha256']
    for item in comparison['SPsource']['sourceBindings']:assert sha(BASE/item['path'])==item['sha256']
    package={'source':source,'records':records,'validation':validated,'tamperRejection':rejection}
    (BASE/'genesis-evidence-audit.json').write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report={'status':'passed','outputSha256':sha(model_path),'installedGuard':str(GUARD),'installedGuardSha256':sha(GUARD),'literalTranscriptionStringsVerified':len(records),'tamperedPassageRejected':True,'sourceSnapshotSha256':source['sha256_utf8'],'allIdsUnique':True,'allRelationEndpointsAddressed':True,'all15ClockPlacementsEqualMaster':True,'conditionalChainsAcyclicAndOrdered':True,'SPSourceReferencesStayInGenesis':True,'allGreekImageAndPdfHashesMatch':True,'MTandSPTranscriptionHashesMatch':True,'apparatusCorrectionRetained':True,'factualSupport':'not assessed by mechanical guard','scope':'Finite evidence fidelity and structural checks; numeric interpretations and semantic claims remain separately declared. No full Bible primary collation or historical orientation certified.'}
    (BASE/'independent-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
