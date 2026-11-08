"""EU-001R bounded verification and reproducible handoff generation."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys,re
from evidence import import_matrix,verify_g0_conservation,serialize
from kernel import migrate_matrix,schema_fixtures
from sefer import SeferModel,SLOT_ALIASES,Profile
ROOT=Path(__file__).parent;PROJECT=ROOT.resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    checks=[]
    for name,cmd in [('unit_tests',[sys.executable,'-B','-m','unittest','discover','-s',str(ROOT),'-p','test_*.py','-v']),
                     ('original_six',[sys.executable,'-B','-m','unittest','discover','-s',str(ROOT/'frozen/sefer'),'-p','test_harmonic_verifier.py','-v'])]:
        p=subprocess.run(cmd,capture_output=True,text=True)
        (ROOT/(name+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8')
        count=re.search(r'Ran (\d+) tests?',p.stdout+p.stderr)
        checks.append(dict(name=name,command=cmd,exit_code=p.returncode,test_count=int(count.group(1)) if count else None))
        if p.returncode:raise RuntimeError(name+' failed')
    baseline=json.loads((ROOT/'source-manifest.json').read_text(encoding='utf-8'))
    frozen_ok=all(sha(ROOT/v['path'])==v['sha256'] for v in list(baseline['baseline'].values())+list(baseline['earlier_derived'].values())+list(baseline['context'].values()))
    src_ok=all(sha(PROJECT/p)==h for p,h in baseline['src_hashes'].items())
    old_ok=all(sha(PROJECT/p)==h for p,h in baseline['existing_work_hashes'].items())
    assert frozen_ok and src_ok and old_ok
    graph=import_matrix((ROOT/'frozen/source/matrix-message.txt').read_bytes(),baseline['source']['locator'],{'acquired_utc':baseline['acquired_utc'],'event_line':baseline['source']['line']})
    g0=verify_g0_conservation(graph);store=migrate_matrix(graph)
    (ROOT/'normalized-evidence.json').write_text(serialize(graph)+'\n',encoding='utf-8')
    (ROOT/'kernel-evidence.json').write_text(store.to_json()+'\n',encoding='utf-8')
    (ROOT/'schema-fixtures.json').write_text(json.dumps({k:json.loads(v.to_json()) for k,v in schema_fixtures().items()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    model=SeferModel();saved=json.loads((ROOT/'frozen/sefer/harmonic-demo.json').read_bytes())
    fresh=json.loads(subprocess.check_output([sys.executable,'-B',str(ROOT/'frozen/sefer/harmonic_verifier.py')]))
    assert saved==fresh
    base=[x for xs in model.legacy_module.GROUPS.values() for x in xs]
    cases={'complete':(base,'base'),'missing_m':([x for x in base if x!='m'],'base'),'duplicate':(base[:-1]+['b'],'base'),
           'expanded':(list(model.legacy_module.HarmonicPhoneticVerifier('expanded').slots),'expanded')}
    comparisons=[]
    for name,(tokens,mode) in cases.items():
        actual=model.legacy(tokens,mode);assert actual==saved[name]
        comparisons.append(dict(case=name,input=tokens,expected=saved[name],observed=actual,format_difference=None,passed=True))
    (ROOT/'legacy-comparisons.json').write_text(json.dumps(comparisons,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    encoded=model.encode(graph,Profile('profile:proto',graph.grid.script_labels[0],model.baseline_hash))
    (ROOT/'sefer-encoding.json').write_text(serialize(encoded)+'\n',encoding='utf-8')
    (ROOT/'sefer-missing-m-receipt.json').write_text(serialize(model.reconstruct([v for v in SLOT_ALIASES.values() if v!='m']))+'\n',encoding='utf-8')
    syntax=[]
    for p in ROOT.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'),filename=str(p));syntax.append(p.name)
    dependency=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True)
    (ROOT/'dependency-check.log').write_text(dependency.stdout+dependency.stderr,encoding='utf-8')
    prior=json.loads((PROJECT/'work/ariadne-inverse/residual-results.json').read_text(encoding='utf-8'))
    from collections import Counter
    residual_counts=dict(Counter(r['status'] for r in prior['records']));assert residual_counts['unknown']==4 and residual_counts['unresolved_label']==1
    assets=[]
    review=Path('C:/Users/Brend/Desktop/morphiq-one/## Recommended approach add a Rabbi.txt')
    for url in sorted(set(re.findall(r'https?://[^\s<>\)\]"|]+',review.read_text(encoding='utf-8')))):
        assets.append(dict(url=url,category='BIBLIOGRAPHIC_LEAD',revision=None,maintainer=None,lineage='UNVERIFIED',license='UNVERIFIED',quality='NOT_EVALUATED',role='discovery only',leakage='previously exposed recommendation',chronology='UNVERIFIED',acquired=False))
    (ROOT/'asset-registry.json').write_text(json.dumps(dict(version='EU-001R-v1',assets=assets,bulk_ingestion=False),indent=2)+'\n',encoding='utf-8')
    finding_files=['results-v2/measured.json','carrier-statistics.json','permutation-results.json','residual-results.json']
    audit={name:dict(status='REPORTED BUT NOT REEXECUTED',sha256=sha(PROJECT/'work/ariadne-inverse'/name)) for name in finding_files}
    audit['residual-accounting']=dict(status='CONFIRMED BY RECORD RECONCILIATION',counts=residual_counts,missing_five='four unknown values and one unresolved s³')
    quarantine=['universal zero residual','90-degree acoustic vowel rotation','22-to-28/30 isomorphism','pure Sabaic/Futhorc permutations','intentional cryptography from order','Etruscan unknown equals silence','universal phoneme-music equivalence']
    receipt=dict(tests=checks,unit_test_count=checks[0]['test_count'],original_test_count=checks[1]['test_count'],full_demo_equal=True,original_demo_checks=3,
       source_hash=graph.source.byte_hash,g0_invariants=g0,source_preserved=src_ok and frozen_ok and old_ok,
       syntax_checked=syntax,dependency_check_exit=dependency.returncode,prior_experiments=audit,quarantined_claims=quarantine,
       gates={'G0':'PARTIAL','G1':'PARTIAL',**{f'G{i}':'LOCKED' for i in range(2,8)}},
       blockers=['Two named prior work-state logs not retrieved in the bounded Desktop/morphiq-one filename search; full authority reconciliation incomplete',
                 'Cross-domain historical samples are explicitly synthetic; source-specific recension and Resh claims not retrieved',
                 'No independent code-review or type-checking tool executed; no new manual Jev architectural decision'],
       verified_checkpoint='Lossless matrix migration and original Sefer compatibility reproduced; broader EU-001R certification remains partial')
    (ROOT/'eu001r-verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('unit_test_count','original_test_count','full_demo_equal','original_demo_checks','source_preserved','dependency_check_exit','gates')},indent=2))
if __name__=='__main__':main()
