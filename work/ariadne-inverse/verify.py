"""Fresh task-local verification; no kernel write or model/network call."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
from run import analyze,hashes
from numpy_pipeline import table_to_numpy, raw_table_to_data, FontGeometry, validate_normalized

ROOT=Path(__file__).resolve().parent

def main():
    test=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT),'-p','test_*.py','-v'],capture_output=True,text=True)
    (ROOT/'test-results.txt').write_text(test.stdout+test.stderr,encoding='utf-8')
    if test.returncode: raise SystemExit(test.returncode)
    data=json.loads((ROOT/'table.json').read_text(encoding='utf-8'))
    _,recomputed=analyze(data)
    saved=json.loads((ROOT/'results-v2/measured.json').read_text(encoding='utf-8'))
    assert recomputed==saved
    parsed=raw_table_to_data((ROOT/'table.tsv').read_text(encoding='utf-8'))
    assert parsed['cells']==data['cells']
    counts={}
    for folder,font in [('numpy-results-v2',None),('font-proxy-results-v2','C:/Windows/Fonts/seguihis.ttf')]:
        _,array=table_to_numpy(data,FontGeometry(font) if font else None)
        with np.load(ROOT/folder/'matrix.npz',allow_pickle=False) as archive:
            for key in ['vector','mask','normalized','kind']: np.testing.assert_array_equal(archive[key],array[key])
        assert validate_normalized(array['normalized'])
        counts[folder]=dict(shape=list(array['vector'].shape),geometry_cells=int(array['mask'][:,:,15].sum()),reproduction='exact')
    old=json.loads((ROOT/'results-v2/manifest.json').read_text())['src_before']
    current=hashes(ROOT.parents[1]); assert current==old
    bound=[p for p in ROOT.glob('*') if p.is_file() and p.suffix in ('.py','.md','.json','.tsv') and p.name not in ('verification.json','proofline-package.json')]
    output=dict(tests=dict(returncode=test.returncode,total=18,outcome='passed',log='test-results.txt'),
                measured_reproduction='exact',table_roundtrip='exact',numpy=counts,
                src_unchanged=current==old,src_hashes=current,
                files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in bound},
                dependencies={name:importlib.metadata.version(name) for name in ['numpy','scipy','Pillow','fontTools']},
                limitations=['No actual Jev inference completed','No historical tracing or joint model fitting','No Git metadata available'])
    (ROOT/'verification.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in output.items() if k not in ('files','src_hashes')},indent=2))

if __name__=='__main__':main()
