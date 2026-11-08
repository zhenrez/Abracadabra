"""Reproducible bounded native validation; no historical correspondence search."""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime, timezone
import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys

from western_model import WesternOrientation, Interval, Pitch, canonical_json, source_profiles, ROOT, PROJECT


def run(output):
    model=WesternOrientation();checks=[]
    for label,directory,pattern in (
            ('new_native_contracts',ROOT,'test_western_model.py'),
            ('preserved_unit002_regressions',PROJECT/'work/unit002','test_western.py')):
        command=[sys.executable,'-B','-m','unittest','discover','-s',str(directory),'-p',pattern,'-v']
        result=subprocess.run(command,capture_output=True,text=True)
        match=re.search(r'Ran (\d+) tests?',result.stdout+result.stderr)
        checks.append({'label':label,'command':command,'exit_code':result.returncode,
                       'test_count':int(match.group(1)) if match else None,
                       'output':result.stdout+result.stderr})
        if result.returncode:raise RuntimeError(label+' failed')
    manifest=json.loads((ROOT/'reuse-manifest.json').read_text(encoding='utf-8'))
    for item in manifest.values():
        assert hashlib.sha256((PROJECT/item['path']).read_bytes()).hexdigest()==item['sha256']
    modes={};encoded={}
    for name in model.core.MODE_NAMES:
        native=model.core.mode(name)
        fixture={'kind':'scale','mode':name,'source_ref':'engineering:exact-Pythagorean-mode-profile',
                 'observations':[{'record_id':name+':'+str(i),'ratio':str(r),'onset':str(i),'voice':'single'}
                                 for i,r in enumerate(native['ratios'])]}
        e=model.encode(fixture);validation=model.validate_native(e)
        assert validation.status=='VALID'
        modes[name]={'ratios':list(map(str,native['ratios'])),'chromatic_steps':native['chromatic_steps'],
                     'status':validation.status,'source_role':'configured engineering profile; historical tuning not inferred'}
        encoded[name]=json.loads(canonical_json(e))
    property_cases=0
    for power in range(-8,9):
        for factor in (F(1),F(9,8),F(4,3),F(3,2),F(243,128)):
            pitch=Pitch(F(2)**power*factor)
            assert pitch.register==power
            assert pitch.pitch_class*F(2)**pitch.register==pitch.ratio
            for interval in (Interval(4,7,F(3,2)),Interval(3,5,F(4,3)),Interval(7,12,F(2))):
                assert pitch.transpose(interval).transpose(interval.inverse())==pitch
                property_cases+=1
    # Independent integer expression checks the exact nonclosure benchmark.
    cycle=model.core.fifth_cycle()
    assert cycle['comma']==F(3**12,2**19)==F(531441,524288)
    assert cycle['twelve_fifths']!=cycle['seven_octaves']
    assert F(9,8)**2*F(256,243)==F(4,3)
    missing=model.reconstruct({'ratios':['1','9/8',None,'4/3','3/2','27/16','243/128'],'tonic':'1'}, {'mode':'ionian'})
    ambiguous=model.reconstruct({'ratios':['1']+[None]*6,'tonic':'1'})
    assert missing.identifiability['status']=='UNIQUE_UNDER_MODEL'
    assert len(ambiguous.candidates.solutions)==7
    for p in ROOT.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
    value={'timestamp_utc':datetime.now(timezone.utc).isoformat(),
           'namespace':model.namespace,'native_gate':'PASSED_BOUNDED_G2_NATIVE',
           'full_historical_profile_gate':'PARTIAL','checks':checks,
           'exact_property_cases':property_cases,'modes':modes,'encoded_profiles':encoded,
           'nonclosure':{k:str(v) if isinstance(v,F) else v for k,v in cycle.items()},
           'tetrachord':json.loads(canonical_json(model.tetrachord())),
           'reconstruction':{'missing_degree':json.loads(canonical_json(missing)),
                             'seven_mode_ambiguity':json.loads(canonical_json(ambiguous))},
           'source_profiles':source_profiles(),'reused_sources_unchanged':True,
           'scope':'exact interval/modal/register/rhythm/polyphony contracts; not all historical Western witness interpretations',
           'plugin_use':{'Superpowers':'TDD applied; observed red and green tests retained',
                         'Mathbox':'actual bundled bounded computation runner and manifest validator invoked separately',
                         'Jev':'parent strategy receipt; no child inference claimed'},
           'source_gaps':['Greek genera beyond this tone-tone-limma profile not reconstructed',
                          'Fludd1638 local image and Cornell1617 record not equated or fully collated',
                          'Kepler dynamics and Completed Harmony preserved as source-specific unevaluated profiles',
                          'Earliest surviving manuscript priority not established for translated Plato source'],
           'cross_orientation_used':False,'MDL':json.loads(canonical_json(model.describe())),
           'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')}}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'native_gate':value['native_gate'],'full_historical_profile_gate':'PARTIAL',
                      'test_counts':[c['test_count'] for c in checks],'property_cases':property_cases,
                      'comma':str(cycle['comma']),'cross_orientation_used':False},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
