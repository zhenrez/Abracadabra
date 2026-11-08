"""Recover exact current-chat matrix and preserve the existing baseline, without editing it."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys,importlib.metadata
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
SESSION=Path('C:/Users/Brend/.codex/sessions/2026/11/05/rollout-2026-11-05T21-52-30-01a1af33-7e1f-7a13-b0da-24adc96bb98d.jsonl')
def digest(raw):return hashlib.sha256(raw).hexdigest()
def preserve(name,raw):
    path=ROOT/'frozen'/name;path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_bytes()!=raw:raise ValueError('Refusing to overwrite frozen bytes: '+name)
    else:
        with path.open('xb') as f:f.write(raw)
    return dict(path=str(path.relative_to(ROOT)),sha256=digest(raw),bytes=len(raw))
def main():
    if (ROOT/'source-manifest.json').exists():raise SystemExit('Checkpoint already exists; verify rather than overwrite')
    found=[]
    for number,line in enumerate(SESSION.read_bytes().splitlines(keepends=True),1):
        obj=json.loads(line);payload=obj.get('payload',{})
        if obj.get('type')=='response_item' and payload.get('role')=='user':
            for part in payload.get('content',[]):
                text=part.get('text','')
                if text.startswith('Alphabet\t1\t2'):found.append((number,line,text))
    if len(found)!=1:raise ValueError('Expected exactly one original matrix message')
    number,line,text=found[0]
    source=preserve('source/matrix-message.txt',text.encode('utf-8'))
    event=preserve('source/matrix-event.jsonl',line)
    old=PROJECT/'work/ariadne-inverse'
    files={name:preserve('sefer/'+name,(old/name).read_bytes()) for name in ['harmonic_verifier.py','test_harmonic_verifier.py','harmonic-demo.json','HARMONIC_VERIFIER.md']}
    legacy_inputs={name:preserve('earlier-derived/'+name,(old/name).read_bytes()) for name in ['table.json','table.tsv','build_dataset.py','jev-attempt.json']}
    attachment=Path('C:/Users/Brend/.codex/attachments/842ba713-dafd-47df-8356-8e87e7012250/Pasted text.txt')
    attached=preserve('source/orientation-context.txt',attachment.read_bytes())
    baseline_test=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(old),'-p','test_harmonic_verifier.py','-v'],capture_output=True,text=True)
    preserve('sefer/original-test-output.txt',(baseline_test.stdout+baseline_test.stderr).encode())
    fresh=subprocess.run([sys.executable,'-B',str(old/'harmonic_verifier.py')],capture_output=True,text=True)
    saved=json.loads((old/'harmonic-demo.json').read_bytes());current=json.loads(fresh.stdout)
    checks=[saved==current,current['complete']['status']=='Valid',current['missing_m']['reconstruction_suggestion']=='m',current['expanded']['harmonic_checksum']['matched_slots']==29]
    if baseline_test.returncode or fresh.returncode or not all(checks):raise ValueError('Baseline regression failed')
    names=['state/task.json','docs/HUMMBL_PLAN.md','AGENTS.md','data/raw/archive/SUN_Universal_Archive/Library/HISTORICAL_MUSIC/SUN_Final_Hypergraph_and_Template_Results_v1.md']
    context={name:preserve('context/'+Path(name).name,(PROJECT/name).read_bytes()) for name in names}
    all_old={str(p.relative_to(PROJECT)):digest(p.read_bytes()) for p in sorted(old.iterdir()) if p.is_file()}
    src={str(p.relative_to(PROJECT)):digest(p.read_bytes()) for p in sorted((PROJECT/'src').glob('*.ts'))}
    manifest=dict(workspace=str(PROJECT),repository=dict(status='NO_GIT_METADATA',branch=None,head=None,working_tree=None,open_prs='NOT_EVALUATED; no GitHub operation'),
        acquired_utc=datetime.now(timezone.utc).isoformat(),source=dict(**source,availability='VERIFIED',kind='USER_SUPPLIED_COMPARATIVE_DATASET',
        locator=str(SESSION),line=number,event=event,encoding='utf-8',byte_scope='Exact decoded user-message text encoded as UTF-8; original serialized event bytes separately retained; no external-document byte claim'),
        attachment=attached,baseline=files,earlier_derived=legacy_inputs,context=context,existing_work_hashes=all_old,src_hashes=src,
        original_tests=dict(count=6,exit_code=baseline_test.returncode,full_demo_equal=checks[0],original_demo_checks=checks[1:]),
        dependencies={x:importlib.metadata.version(x) for x in ['numpy','scipy','networkx']},python=sys.version,
        expected_counts=dict(scripts=15,positions=540,populated=381,empty=159),scope='G0/G1 only; G2–G7 locked')
    (ROOT/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(source_hash=source['sha256'],baseline_tests=manifest['original_tests'],status='checkpoint preserved')))
if __name__=='__main__':main()
