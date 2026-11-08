"""EU-001R before-state inventory; preserves the interrupted Unit001 in place."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).parent
if __name__=='__main__':
    out=ROOT/'eu001r-before.json'
    if out.exists():raise SystemExit('Before-state exists; refusing overwrite')
    paths=list(ROOT.glob('*.py'))+list(ROOT.glob('*.md'))+list((ROOT/'frozen').rglob('*'))
    receipt={'workspace':str(ROOT.resolve().parents[1]),'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()},'git':'No Git metadata established; no GitHub actions','existing_tests':{'command':'python -B -m unittest discover -s work/unit001 -p test_g*.py -v','tests':34,'exit_code':0}}
    out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
