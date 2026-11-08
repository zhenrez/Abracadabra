"""Reproduce bounded G3/G4 assertions and emit native source/command receipts."""
from pathlib import Path
from datetime import datetime,timezone
from fractions import Fraction
import ast,hashlib,json,platform,re,subprocess,sys,time
import east_models as east
from evidence import serialize

ROOT=Path(__file__).resolve().parent

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def simple(value):
    if isinstance(value,Fraction):return str(value)
    if isinstance(value,dict):return {k:simple(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [simple(v) for v in value]
    return value
def save(name,value):
    (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    inputs=list(ROOT.glob('*.py'))+[ROOT/'source-profiles.json']+list(ROOT.glob('*-extraction.json'))
    inputs += [east.LEGACY_PATH,east.PROJECT/'work/unit001/contracts.py',east.PROJECT/'work/unit001/evidence.py']
    before={str(p):sha(p) for p in inputs}
    command=[sys.executable,'-B','-m','unittest','discover','-s',str(ROOT),'-p','test_native_east.py','-v']
    started=time.monotonic();result=subprocess.run(command,capture_output=True,text=True)
    output=result.stdout+result.stderr;(ROOT/'native-tests.log').write_text(output,encoding='utf-8')
    if result.returncode:raise RuntimeError('Native tests failed; inspect native-tests.log')
    count=re.search(r'Ran (\d+) tests',output)
    if count is None:raise RuntimeError('No observed test count')
    for path in ROOT.glob('*.py'):ast.parse(path.read_text(encoding='utf-8'))
    c,g,m=east.ChineseModel(),east.GramaModel(),east.MelakartaModel()
    validations={}
    for name,model in [('chinese',c),('grama',g),('melakarta',m)]:
        encoded=model.encode(None);validation=model.validate_native(encoded)
        if validation.status!='VALID':raise RuntimeError('Native profile invalid: '+name)
        (ROOT/(name+'-encoding.json')).write_text(serialize(encoded)+'\n',encoding='utf-8')
        validations[name]=json.loads(serialize(validation))
    native={'assertion_tested':'Exact native computations on the declared finite source profiles',
        'chinese':{'twelve_lu':c.generation(),'thirteenth_projected_label':c.generation(count=13)[12],
                   'formal_context_count':len(c.contexts()),'comma':'531441/524288','length_reference':'1',
                   'operators':{'D':'2/3','U':'4/3'},'directions':[r['operator'] for r in c.generation()][1:]},
        'grama':{'shadja':g.allocations('shadja'),'madhyama':g.allocations('madhyama'),
                 'murchanas':g.murchanas(),'frequency_ratios':None},
        'melakarta':{'configurations':m.configurations(),'count':len(m.configurations()),
                     'madhyama_pairs':[(i+1,i+37) for i in range(36)],'position_type':'symbolic_svarasthana','frequency_ratios':None}}
    save('native-results.json',simple(native))
    cases={'chinese_ambiguous':c.reconstruct({0:None},{'reference_lengths':('1','2')}),
           'chinese_unique_under_profile':c.reconstruct({1:'2/3'},{'reference_lengths':('1','2')}),
           'chinese_no_solution':c.reconstruct({0:'7/3'}),
           'grama_ambiguous':g.reconstruct({'start_note':'Sa'}),
           'melakarta_ambiguous':m.reconstruct((0,2,4,None,7,9,11))}
    save('native-reconstruction-receipts.json',{k:json.loads(serialize(v)) for k,v in cases.items()})
    after={str(p):sha(p) for p in inputs}
    if before!=after:raise RuntimeError('Checked input changed during run')
    if sha(east.LEGACY_PATH)!=east.LEGACY_HASH:raise RuntimeError('Legacy source changed')
    outputs={p.name:sha(p) for p in ROOT.glob('*-encoding.json')}
    for name in ('native-results.json','native-reconstruction-receipts.json','native-tests.log'):outputs[name]=sha(ROOT/name)
    receipt={'created_utc':datetime.now(timezone.utc).isoformat(),'run':{'status':'completed','exit_code':result.returncode,
        'elapsed_seconds':time.monotonic()-started,'command':command},'observed_tests':int(count.group(1)),
        'software':{'python':sys.version,'platform':platform.platform(),'new_dependencies':[]},
        'assertion_tested':native['assertion_tested'],'domain':{'chinese_generation_indices':'0..12','formal_contexts':60,
          'grama_murchanas':14,'melakarta_scales':72,'madhyama_pairs':36},'validations':validations,
        'inputs_before':before,'inputs_after':after,'outputs':outputs,
        'legacy_reuse':{'path':str(east.LEGACY_PATH),'sha256':east.LEGACY_HASH,
            'extracted_definitions':['positive','Chinese','Indian'],'module_top_level_executed':False,'sefer_import_executed':False},
        'source_manifest':'source-profiles.json','source_capture_kind':'native web-tool extractions; not original HTTP/PDF/manuscript bytes',
        'red_evidence':['red-tests.log','red-profile-immutability.log','red-numeric-type.log'],
        'historical_claims':'NOT_VERIFIED','cross_orientation_reconstruction':'NOT_ACTIVATED',
        'scope_verdict':{'G3':'PASSED_BOUNDED_NATIVE_PROFILE','G4':'PASSED_BOUNDED_NATIVE_PROFILES'},
        'limitations':['Earliest surviving manuscript not certified','Modern sampurna grammar kept distinct from older asampurna variants',
            'No measured22shruti intonation or inferred correspondence','Formal60contexts are not60attested instruments',
            'No global MDL score emitted','Native model uniqueness is not historical identification',
            'No new manual Jev inference by this worker; root strategy receipt retained separately']}
    save('native-verification.json',receipt)
    print(json.dumps({'status':'PASSED','tests':int(count.group(1)),'exit_code':result.returncode,
                      'counts':receipt['domain'],'frozen_reuse_hash_unchanged':True},indent=2))

if __name__=='__main__':main()
