"""Bounded G2 checks, prior acceptance preservation and exact outputs."""
from pathlib import Path
from fractions import Fraction
import ast,hashlib,json
from western import WesternModel,Interval
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1]
def main():
    prior=json.loads((PROJECT/'work/unit001/final-acceptance/acceptance-receipt.json').read_text(encoding='utf-8'))
    for file,expected in prior['files'].items():
        assert hashlib.sha256((PROJECT/'work/unit001'/file).read_bytes()).hexdigest()==expected,file
    old=json.loads((PROJECT/'work/unit001/source-manifest.json').read_text(encoding='utf-8'))
    for file,expected in old['src_hashes'].items():assert hashlib.sha256((PROJECT/file).read_bytes()).hexdigest()==expected
    model=WesternModel();result={'namespace':model.namespace,'modes':{n:model.mode(n) for n in model.MODE_NAMES},'fifth_cycle':model.fifth_cycle(),
       'fifth_plus_fourth':str(Interval(4,7,Fraction(3,2)).compose(Interval(3,5,Fraction(4,3))).ratio),
       'scope':'Bounded Pythagorean interval/mode/register model; historical Western witness adapters not implemented',
       'gates':{'G0':'PRESERVED_ACCEPTED','G1':'PRESERVED_ACCEPTED','G2':'PARTIAL',**{f'G{i}':'LOCKED' for i in range(3,8)}},
       'preserved_unit001_hashes':True,'preserved_SUN_source_hashes':True}
    for p in ROOT.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
    (ROOT/'native-results.json').write_text(json.dumps(result,default=lambda v:str(v) if isinstance(v,Fraction) else v,indent=2)+'\n',encoding='utf-8')
    print('PASS: Unit001 and SUN source hashes; exact ratios, modes, syntax and bounded scope recorded')
if __name__=='__main__':main()
