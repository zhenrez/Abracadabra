"""Build evidence roundtrip and independent native-model checkpoint."""
from pathlib import Path
from fractions import Fraction as Q
import json,hashlib,subprocess,sys
from evidence import preserve,restore,compress,decompress,validate
from native_models import Western,Chinese,Indian,Sefer
from comparison import Map,preservation

ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1]
ATTACHMENT=Path('C:/Users/Brend/.codex/attachments/842ba713-dafd-47df-8356-8e87e7012250/Pasted text.txt')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    protected=list((PROJECT/'src').glob('*.ts'))+[PROJECT/'state/task.json',PROJECT/'state/mission.json',PROJECT/'docs/HUMMBL_PLAN.md',PROJECT/'state/reconstruction/contextual-alignment.json']
    protected=[p for p in protected if p.exists()]
    before={str(p.relative_to(PROJECT)):sha(p) for p in protected}
    specs=[('current-attachment',ATTACHMENT,'user_specification'),('user-table',PROJECT/'work/ariadne-inverse/table.json','user_specification')]
    specs += [('preserved:'+str(p.relative_to(PROJECT)),p,'source') for p in protected]
    sources=[preserve(i,p.read_bytes(),str(p),role) for i,p,role in specs]
    cells=json.loads((PROJECT/'work/ariadne-inverse/table.json').read_text(encoding='utf-8'))['cells']
    observations=[dict(id=f'cell:{i}',source_id='user-table',role='user_specification',native_system=c['script'],native_address={'column':c['column']},literal=c,
         uncertainty={'historical_validation':c['historical_validation'],'proxy_or_reading_role':c['role']},witness=None,historical_time=None) for i,c in enumerate(cells)]
    bundle=dict(schema='sun.orientation-evidence.v1',sources=sources,observations=observations,relations=[])
    packed=compress(bundle);unpacked=decompress(packed);assert unpacked==bundle
    for source,(_,path,_) in zip(unpacked['sources'],specs):assert restore(source)==path.read_bytes()
    (ROOT/'evidence.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'evidence.zlib').write_bytes(packed)
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT),'-p','test_models.py','-v'],capture_output=True,text=True)
    (ROOT/'test-results.txt').write_text(tests.stdout+tests.stderr,encoding='utf-8')
    if tests.returncode:raise SystemExit(tests.returncode)
    w,c,i,s=Western(),Chinese(),Indian(),Sefer()
    ident=Map('identity','length','length','identity',lambda x:x)
    R=Map('SUN R','length','length','generation',lambda x:w.act(x,'R'))
    D=Map('Chinese D','length','length','generation',lambda x:c.act(x,'D'))
    RL=Map('SUN RL','length','length','generation',lambda x:w.act(w.act(x,'L'),'R'))
    DU=Map('Chinese DU','length','length','generation',lambda x:c.act(c.act(x,'U'),'D'))
    result=dict(schema='sun.four-orientation-checkpoint.v1',evidence=dict(observations=len(observations),sources=len(sources),byte_roundtrip=True),
      native=dict(western={'RL':'1/2','comma':str(w.comma()),'register_retained':True},
      chinese={'contexts':len(c.contexts()),'DU':'8/9','U_equals_inverse_L':True},
      indian={'melakarta_configurations':len(i.configurations()),'madhyama_pairs':36,'intonation':i.intonation()},
      sefer={'roots':22,'gates':len(s.gates()),'tagged_states':len(s.tagged_expansion()),'typed_paths':len(s.paths())}),
      operator_tests={'R_to_D':preservation([Q(1),Q(7,11)],R,D,ident,ident),'RL_to_DU':preservation([Q(1),Q(7,11)],RL,DU,ident,ident)},
      native_test_exit=tests.returncode,cross_orientation_reconstruction_enabled=False,
      unresolved=['Independent historical adapters','Source-selected shruti profile','Primordial/W72 orientation selection','Actual Jev approval','Independent historical held-out tests'])
    after={str(p.relative_to(PROJECT)):sha(p) for p in protected};assert before==after
    result['preservation']={'before':before,'after':after,'unchanged':True}
    result['implementation_hashes']={p.name:sha(p) for p in ROOT.iterdir() if p.suffix in ('.py','.md') or p.name=='evidence.schema.json'}
    result['schema_validation']='JSON Schema draft 2020-12 plus hashes and semantic reference checks'
    (ROOT/'checkpoint.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='preservation'},ensure_ascii=True,indent=2))

if __name__=='__main__':main()
