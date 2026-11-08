"""Complete bounded G0/G1 handoff. No downstream model import or execution."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,json,subprocess,sys,re,importlib.util
from evidence import import_matrix,verify_g0_conservation,serialize
from kernel import migrate_matrix
from closeout_fixtures import build
from sefer import SeferModel,Profile,SLOT_ALIASES
from contracts import CrossOrientationRegistry

ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1];OUT=ROOT/'final-acceptance'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    OUT.mkdir(exist_ok=True);checks=[]
    for label,directory,pattern in [('current_G0_G1',ROOT,'test_*.py'),('original_Sefer',ROOT/'frozen/sefer','test_harmonic_verifier.py'),('preserved_pipeline',ROOT.parent/'ariadne-inverse','test_*.py')]:
        command=[sys.executable,'-B','-m','unittest','discover','-s',str(directory),'-p',pattern,'-v']
        result=subprocess.run(command,capture_output=True,text=True);text=result.stdout+result.stderr
        (OUT/(label+'.log')).write_text(text,encoding='utf-8');count=re.search(r'Ran (\d+) tests?',text)
        checks.append(dict(name=label,command=command,exit_code=result.returncode,count=int(count.group(1)) if count else None))
        if result.returncode:raise RuntimeError('Failed required suite: '+label)
    manifest=json.loads((ROOT/'source-manifest.json').read_text(encoding='utf-8'))
    source=ROOT/'frozen/source/matrix-message.txt';assert digest(source)==manifest['source']['sha256']
    for group in ('baseline','earlier_derived','context'):
        for item in manifest[group].values():assert digest(ROOT/item['path'])==item['sha256']
    assert all(digest(PROJECT/name)==value for name,value in manifest['src_hashes'].items())
    assert all(digest(PROJECT/name)==value for name,value in manifest['existing_work_hashes'].items())
    graph=import_matrix(source.read_bytes(),manifest['source']['locator'],{'acquired_utc':manifest['acquired_utc']})
    g0=verify_g0_conservation(graph);store=migrate_matrix(graph)
    assert store.to_json()==type(store).from_json(store.to_json()).to_json()
    model=SeferModel();profile=Profile('final:proto',graph.grid.script_labels[0],model.baseline_hash)
    encoded=model.encode(graph,profile);assert model.validate_native(encoded).status=='VALID'
    (OUT/'source-bound-sefer-encoding.json').write_text(serialize(encoded)+'\n',encoding='utf-8')
    base=list(SLOT_ALIASES.values());ambiguous=[x for x in base if x not in ('s','ʃ')]+['s']
    cases={'A_complete':(base,{}),'B_missing_Mem':([x for x in base if x!='m'],{}),
       'C_sibilant_ambiguity':(ambiguous,{}),'E_duplicate':(base[:-1]+['b'],{}),
       'F_overflow':(list(model.state_inventory('expanded'))+['b'],{'mode':'expanded'}),
       'G_empty':([],{}),'H_exhaustion':(['b'],{'constraints':{0:('sefer:letter:mem',)}}),
       'I_multiple':(['b/g'],{})}
    expected={'A_complete':('VALID','UNIQUE_UNDER_MODEL'),'B_missing_Mem':('INCOMPLETE','UNIQUE_UNDER_MODEL'),
       'C_sibilant_ambiguity':('INCOMPLETE','MULTIPLE_DISTINGUISHABLE'),'E_duplicate':('CONTRADICTION','NO_FEASIBLE_SOLUTION'),
       'F_overflow':('CONTRADICTION','NO_FEASIBLE_SOLUTION'),'G_empty':('NOT_EVALUATED','INSUFFICIENT_INPUT'),
       'H_exhaustion':('CONTRADICTION','NO_FEASIBLE_SOLUTION'),'I_multiple':('INCOMPLETE','MULTIPLE_DISTINGUISHABLE')}
    cases_out={}
    for name,(tokens,kwargs) in cases.items():
        receipt=model.reconstruct(tokens,**kwargs);actual=(receipt.structural['status'],receipt.identifiability['status']);assert actual==expected[name]
        cases_out[name]=dict(input=tokens,expected=expected[name],observed=actual,passed=True,typed_receipt=json.loads(serialize(receipt)))
    resh=model.state_inventory('expanded')['sefer:letter:resh:state:1'];assert resh['phonetic_realization'] is None
    cases_out['D_Resh']=dict(input='r:1',expected='tagged state; no invented realization',observed=dict(resh),passed=True)
    r1=serialize(model.reconstruct(['b/g']));r2=serialize(model.reconstruct(['b/g']));assert r1==r2
    cases_out['J_serialization']=dict(input=['b/g'],expected='byte-identical canonical JSON',observed=hashlib.sha256(r1.encode()).hexdigest(),passed=True)
    saved=json.loads((ROOT/'frozen/sefer/harmonic-demo.json').read_bytes());fresh=json.loads(subprocess.check_output([sys.executable,'-B',str(ROOT/'frozen/sefer/harmonic_verifier.py')]))
    assert saved==fresh
    original_input=[x for group in model.legacy_module.GROUPS.values() for x in group]
    legacy_inputs={'complete':original_input,'missing_m':[x for x in original_input if x!='m'],'duplicate':original_input[:-1]+['b']}
    comparisons=[]
    for name,tokens in legacy_inputs.items():
        actual=model.legacy(tokens);assert actual==saved[name]
        comparisons.append(dict(case=name,input=tokens,expected=saved[name],observed=actual,format_difference=None,passed=True))
    syntax=[]
    for path in ROOT.glob('*.py'):ast.parse(path.read_text(encoding='utf-8'));syntax.append(path.name)
    dependencies=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True)
    (OUT/'dependency-check.log').write_text(dependencies.stdout+dependencies.stderr,encoding='utf-8');assert dependencies.returncode==0
    registry=CrossOrientationRegistry();assert registry.adapters==()
    denied=[]
    for name,operation in [('register',lambda:registry.register({})),('evaluate',lambda:registry.evaluate(None)),('serialized_unlock',lambda:registry.from_json('{"g7":true,"adapters":[]}'))]:
        try:operation()
        except PermissionError:denied.append(name)
        else:raise AssertionError(name+' unexpectedly allowed')
    controls=build();assert len(controls)==4
    prior=json.loads((ROOT/'closeout/authority-correction.json').read_text());assert prior['duplicate_logs_are_current_conversation'] is True
    output=dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),workspace=str(PROJECT),git={'branch':None,'head':None,'reason':'no Git metadata established; no GitHub action'},
       tests=checks,g0=g0,counts={'script_groups':15,'positions':len(graph.cells),'populated':len(graph.witnesses),'empty':sum(c.glyph=='' for c in graph.cells)},
       matrix_sha256=digest(source),G1_cases=cases_out,legacy_comparisons=comparisons,full_original_demo_equal=True,original_demo_checks=3,
       pair_counts=model.pair_counts(),historical_controls=list(controls),all_frozen_hashes_match=True,syntax_checked=syntax,dependency_exit=dependencies.returncode,
       g7_denied=denied,regressions_fixed=['duplicate evidence identity accepted by native validation','missing source-claim binding accepted by native validation'],
       gates={'G0':'PASSED','G1':'PASSED',**{f'G{i}':'LOCKED' for i in range(2,8)}},
       limitations=['Historical source controls verify faithful edition/publication representation, not historical root truth',
         'Earliest surviving manuscript priority has not been established for retrieved digital editions',
         'Lachish original PDF capture failed; separately attributed inspected excerpt is not original artifact bytes',
         'No static type checker or separate linter executed; AST syntax, runtime tests and dependency checks executed',
         'No independent reviewer or new manual Jev inference; automatic observations are not certification'],
       stop='G0/G1 acceptance complete for bounded scope. No G2-G7 implementation or unlock performed.',
       files={p.name:digest(p) for p in ROOT.glob('*.py')})
    (OUT/'acceptance-receipt.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(tests=checks,gates=output['gates'],counts=output['counts'],frozen_integrity=True),indent=2))
if __name__=='__main__':main()
