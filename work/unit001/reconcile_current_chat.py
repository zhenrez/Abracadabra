"""Reconcile completed current-chat artifacts; no new scientific model execution."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parent;OLD=ROOT.parent/'ariadne-inverse'
def main():
    groups=[('matrix_features','Matrix and NumPy feature pipeline',['features.py','numpy_pipeline.py','build_dataset.py'],
      'Implemented; 15x36 grid, P15/G5, availability masks, ordered alternatives and sequences. Font geometry is a proxy.'),
      ('carrier','Six-script carrier extraction',['extract_carrier.py','carrier-statistics.json'],
       'Executed on six rows, not fourteen. Ten zero-entropy columns and 18 literal differences; universal zero residual was not established.'),
      ('vowel','Greek/Latin vowel drift',['vowel_drift.py'],
       'Implemented lookup operator and optional glide conversion. This is the Greek/Latin linguistic operator completed in this conversation, not a Western musical orientation.'),
      ('split','Expansion and parity',['drift_engine.py'],
       'Implemented 28 tagged six-switch states plus explicit inventory extensions; separate from Sefer 29-state model.'),
      ('permutation','Sabaic/Futhorc reindexing',['permutation.py','permutation-results.json'],
       'Implemented and tested. Full supplied targets fail a bijection with C22; partial incidence matrices retained. Negative finding is not a software failure.'),
      ('residual','Residual extraction and heatmap',['residual_analysis.py','residual-results.json','residual-heatmap.png'],
       'Implemented, with 142 scored, 136 compatible, six residuals, 234 unmapped, four unknown, one unresolved; no historical TMI claim.'),
      ('sefer_original','Original harmonic/Sefer model',['harmonic_verifier.py','harmonic-demo.json'],
       'Implemented and frozen: 22 slots, 29 tagged states, matching ambiguity and unique-under-model restoration. No unique historical harmonic root established.')]
    records=[]
    for key,title,files,status in groups:
        evidence=[]
        for name in files:
            p=OLD/name
            if not p.is_file():raise ValueError('Missing recorded artifact: '+str(p))
            evidence.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        records.append(dict(id=key,title=title,status=status,evidence=evidence))
    runs=[]
    for label,path in [('earlier_pipeline',OLD),('consolidated_G0_G1',ROOT)]:
        cmd=[sys.executable,'-B','-m','unittest','discover','-s',str(path),'-p','test_*.py','-v']
        p=subprocess.run(cmd,capture_output=True,text=True)
        log=p.stdout+p.stderr;(ROOT/('reconcile-'+label+'.log')).write_text(log,encoding='utf-8')
        count=re.search(r'Ran (\d+) tests?',log)
        runs.append(dict(group=label,command=cmd,exit_code=p.returncode,test_count=int(count.group(1)) if count else None))
        if p.returncode:raise RuntimeError(label+' tests failed; do not publish success')
    gate_path=ROOT/'closeout/certification-closeout.json';gates=json.loads(gate_path.read_text(encoding='utf-8'))
    assert gates['gates']['G0']=='PASSED' and gates['gates']['G1']=='PASSED'
    assert all(gates['gates']['G'+str(i)]=='LOCKED' for i in range(2,8))
    stats=json.loads((OLD/'carrier-statistics.json').read_text(encoding='utf-8'))
    residual=json.loads((OLD/'residual-results.json').read_text(encoding='utf-8'))
    assert stats['shape']==[6,22] and stats['literal_residual_cells']==18
    from collections import Counter
    counts=dict(Counter(x['status'] for x in residual['records']))
    assert sum(counts.values())==540 and sum(v for k,v in counts.items() if k!='missing')==381
    report=dict(scope='CURRENT CHAT, not a restart of prior SUN research',completed_stages=records,
      consolidated_foundation=dict(status='G0/G1 PASSED for bounded architecture and Sefer compatibility',
         evidence=str(gate_path),sha256=hashlib.sha256(gate_path.read_bytes()).hexdigest(),
         implemented=['lossless source/grid/evidence layers','domain-independent provenance kernel','Sefer canonical-letter adapter','four source-identified representation controls','four-axis receipts','locked cross-orientation registry']),
      tests=runs,gate_ledger=gates['gates'],residual_counts=counts,
      corrections=['Duplicate conversation-log copies are not independent evidence requirements',
        'Greek/Latin linguistic T_vowel was completed here; Western musical OrientationModel was not implemented here',
        'Existing SUN exact-ratio/register/comma work predates the new common interface; reuse must be audited before new implementation',
        'Conceptual proposals and raw ratios do not alone establish a completed native-model adapter',
        'Earlier PARTIAL gate receipts are historical and superseded by the authority-corrected closeout receipt'],
      next_action='G2 compatibility/gap audit: map existing Western/SUN code and tests to the common OrientationModel contract, identify only genuinely missing behaviors; no rebuild of the completed linguistic/Sefer pipeline.',
      next_action_status='Eligible planning/audit target; no G2 implementation or unlock performed by this reconciliation',
      unverified=['Historical root or universal glyph-sound/music equivalence','Unique phoneme-to-frequency mapping','Historical topology independent of fonts','G2-G7 native/cross-model certification'])
    (ROOT/'CURRENT_CHAT_RECONCILIATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Current-chat work reconciliation','',
      'This ledger supersedes status summaries that described already completed current-chat work as a new build. It does not change scientific findings or frozen source bytes.','',
      '| Completed here | Actual state |','|---|---|']
    lines += ['| '+r['title']+' | '+r['status']+' |' for r in records]
    lines += ['| Consolidated G0/G1 | Lossless architecture, Sefer migration, historical representation controls and lock checks completed; current gates PASSED. |','',
       '## What was confused','',
       'Greek/Latin **linguistic** transformations were implemented in this chat. The later gate named Western refers to an independent **musical native model**. Older SUN files already provide substantial musical implementation. Those three scopes must not be described as one unfinished or one completed task.','',
       'The duplicate-log blocker is removed. Older partial reports are retained as history and do not reopen G0/G1. No source is to be requested again merely to reproduce this conversation.','',
       '## What happens next','',report['next_action'],'',
       'The audit should enumerate existing interval composition, mode/transposition, inversion, register and nonclosure behavior, bind each to actual code/test evidence, then identify an adapter-only change or a specific missing implementation. It must not rerun the five-step linguistic analysis, rebuild Sefer, or assume all Western musical work is absent. G2–G7 remain locked until the appropriate authorization and native evidence exist.','',
       '## Fresh verification','']
    lines += [f"- {r['group']}: {r['test_count']} tests, exit {r['exit_code']}." for r in runs]
    lines += ['', 'Recorded numerical findings were checked against their existing JSON records; PCA/MDL fits and other exploratory experiments were not rerun. Full paths, hashes, commands, gate evidence and limitations are in CURRENT_CHAT_RECONCILIATION.json.','',
       'Changed files: reconcile_current_chat.py, RECONCILIATION_PLAN.md, this Markdown/JSON ledger and two current test logs. No scientific model, gate value, source fixture or original implementation was changed. Existing Riqor evidence-engineering guidance was applied; no new Jev inference or independent model review is claimed.','']
    (ROOT/'CURRENT_CHAT_RECONCILIATION.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(dict(tests=runs,gates=report['gate_ledger'],next_action=report['next_action']),indent=2))
if __name__=='__main__':main()
