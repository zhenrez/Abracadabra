"""New receipts; never rewrites prior partial gate decisions."""
from pathlib import Path
import hashlib,json,subprocess,sys,ast,re
from closeout_fixtures import build
ROOT=Path(__file__).parent;OUT=ROOT/'closeout'
def main():
    checks=[]
    for name,cmd in [('all_tests',[sys.executable,'-B','-m','unittest','discover','-s',str(ROOT),'-p','test_*.py','-v']),
        ('original_six',[sys.executable,'-B','-m','unittest','discover','-s',str(ROOT/'frozen/sefer'),'-p','test_harmonic_verifier.py','-v'])]:
        p=subprocess.run(cmd,capture_output=True,text=True);(OUT/(name+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8')
        count=re.search(r'Ran (\d+) tests?',p.stdout+p.stderr)
        checks.append({'name':name,'command':cmd,'exit_code':p.returncode,'test_count':int(count.group(1)) if count else None})
        if p.returncode:raise RuntimeError(name+' failed')
    saved=json.loads((ROOT/'frozen/sefer/harmonic-demo.json').read_bytes())
    actual=json.loads(subprocess.check_output([sys.executable,'-B',str(ROOT/'frozen/sefer/harmonic_verifier.py')]))
    assert saved==actual
    assert actual['complete']['status']=='Valid' and actual['missing_m']['reconstruction_suggestion']=='m' and actual['expanded']['harmonic_checksum']['matched_slots']==29
    original=json.loads((ROOT/'source-manifest.json').read_text(encoding='utf-8'))
    project=ROOT.resolve().parents[1]
    assert all(hashlib.sha256((project/k).read_bytes()).hexdigest()==v for k,v in original['src_hashes'].items())
    for v in original['baseline'].values():assert hashlib.sha256((ROOT/v['path']).read_bytes()).hexdigest()==v['sha256']
    assert hashlib.sha256((ROOT/'frozen/source/matrix-message.txt').read_bytes()).hexdigest()==original['source']['sha256']
    for p in ROOT.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
    stores=build();(OUT/'historical-controls.json').write_text(json.dumps({k:json.loads(v.to_json()) for k,v in stores.items()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    supplied_path=OUT/'provided-source-manifest.json'
    supplied=json.loads(supplied_path.read_text(encoding='utf-8')) if supplied_path.exists() else None
    if supplied:
        for document in supplied['documents']:
            assert hashlib.sha256((OUT/document['preserved_path']).read_bytes()).hexdigest()==document['sha256']
    correction_path=OUT/'authority-correction.json'
    correction=json.loads(correction_path.read_text(encoding='utf-8')) if correction_path.exists() else None
    resolved=correction is not None and correction.get('duplicate_logs_are_current_conversation') is True
    receipt={'checks':checks,'current_tests':checks[0]['test_count'],'original_tests':checks[1]['test_count'],'full_demo_equal':True,'original_demo_checks':3,'frozen_integrity':'PASS',
      'authority_correction':correction,
      'historical_controls':list(stores),'historical_scope':'edition/publication representation, not historical reconstruction validation',
      'contract_changes':'none required by these four controls','g7_denial':'PASS in test_g7_denied and retained G0 tests',
      'provided_documents':supplied,
      'logs':{name:('REDUNDANT COPY OF CURRENT CONVERSATION; NO INDEPENDENT INPUT REQUIREMENT' if resolved else 'NOT RETRIEVED') for name in ('Pasted text(20261106-072010).txt','Pasted text (2)(20261106-072251).txt')},
      'search_scope':['Documents, Downloads, Desktop and .codex/attachments filename search','targeted current-session references','attachment text search for distinctive earlier work-state phrases'],
      'gates':{'G0':'PASSED' if resolved else 'PARTIAL','G1':'PASSED' if resolved else 'PARTIAL',**{f'G{i}':'LOCKED' for i in range(2,8)}},
      'functional_acceptance':{'G0_conservation_and_real_fixture_representation':'PASS','G1_original_and_adapter_regression':'PASS'},
      'remaining_dependency':None if resolved else 'Unresolved work-state source identity',
      'source_limits':['Earliest surviving manuscripts not retrieved','Lachish PDF download failed; inspected scholarly excerpt separately attributed','Both orientation procedures belong to modern annotation, not directly to the Hebrew commentary'],
      'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file()}}
    output=OUT/('certification-closeout.json' if resolved else 'certification-receipt.json')
    output.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('current_tests','original_tests','full_demo_equal','original_demo_checks','functional_acceptance','gates')},indent=2))
if __name__=='__main__':main()
