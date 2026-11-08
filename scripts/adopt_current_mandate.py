"""Adopt the direct user mandate with immutable pre-change snapshots."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def digest(raw):return hashlib.sha256(raw).hexdigest()
def snapshot(path):
    raw=path.read_bytes();sha=digest(raw)
    destination=ROOT/'state/checkpoint-history'/('before-mandate-'+path.name+'-'+sha+'.snapshot')
    destination.parent.mkdir(exist_ok=True)
    if destination.exists():
        if destination.read_bytes()!=raw:raise ValueError('Immutable snapshot mismatch')
    else:destination.write_bytes(raw)
    return {'path':str(destination.relative_to(ROOT)),'sha256':sha}
def main():
    taskpath=ROOT/'state/task.json';planpath=ROOT/'PLAN.md'
    prior_task=snapshot(taskpath);prior_plan=snapshot(planpath)
    state=json.loads(taskpath.read_text(encoding='utf-8-sig'))
    source=ROOT/'data/raw/mandate-inputs/99dabf2083b9a04c7f7302546651726548a29f5c10a5c7f7a934f983a6e58f63/Pasted text.txt'
    if not source.exists():
        matches=list((ROOT/'data/raw/mandate-inputs').rglob('*'))
        source=next((p for p in matches if p.is_file() and digest(p.read_bytes())=='99dabf2083b9a04c7f7302546651726548a29f5c10a5c7f7a934f983a6e58f63'),None)
        if source is None:raise ValueError('Verified mandate snapshot not found')
    if digest(source.read_bytes())!='99dabf2083b9a04c7f7302546651726548a29f5c10a5c7f7a934f983a6e58f63':
        raise ValueError('Mandate witness differs from the preserved user input')
    now=datetime.now(timezone.utc).isoformat()
    instruction={'adopted_utc':now,'authority':'Current user pasted the full mandate inline and explicitly directed resumption; root attestation. Attachment is its text witness, not an invented inline serialization.',
        'title':'SUNNY — Jev Reconstruction and Predictive Derivation Mandate',
        'text_witness_path':str(source.relative_to(ROOT)),'text_witness_sha256':digest(source.read_bytes()),
        'prior_task':prior_task,'prior_plan':prior_plan}
    state.setdefault('instruction_history',[]).append(instruction)
    state['current_instruction']=instruction
    state['current_priority']='Execute Mission I: reconstruct native musical laws and their interactions, derive global constraints, progressively attain type laws and generational structure, and produce reproducible consequences. Source recovery supports this work; do not stop at an audit or inventory.'
    state['latest_user_priority_exact']='Preserve the full research history, reconstruct the mathematics, discover the lawful orientation, and let the resulting structure generate its own consequences.'
    retained=[]
    for question in state.get('open_questions',[]):
        if question.startswith('Final Q6') or 'Await the requested surface identification' in question:
            state.setdefault('superseded_context',[]).append({'text':question,'superseded_utc':now,
                'reason':'Current direct mandate II-F/III permits conditional progressive type laws; recent image scope remains an acquisition gap without blocking mathematical reconstruction.',
                'source_sha256':instruction['text_witness_sha256']})
        else:retained.append(question)
    state['open_questions']=retained
    state['next_actions']=[
        'Execute and integrate exact native derivations, orientation prediction sets and TOL history constraints; inspect full receipts before reuse.',
        'Expand source-linked mathematical reconstruction across currently unprocessed ranges, preserving all decisions and native systems.',
        'Use surviving-candidate consequences and missing observables to investigate global orientation constraints without electing one by model probability.',
        'Reconstruct generational/lift, class growth, temporal and master-score rules from source constraints; leave unproved laws explicit.',
        'Complete Mission I acceptance before claiming Mission II blind predictive success; retain the recent80–100image acquisition gap without repeating failed access loops.',
    ]
    state['mandate_acceptance']={'recovered':'source objects retained with provenance','reproduced':'specified calculations re-executed','extended':'derived consequences beyond retained claims','predictively_discriminating':'surviving alternatives separated or genuinely withheld evidence correctly predicted'}
    state['completion']='in_progress: source preservation and conditional mathematical derivations exist; comprehensive Mission I and independent blind predictive expansion are not complete'
    state['updated_utc']=now
    taskpath.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    plan='''# SUNNY build plan

- [100%] Recover the supplied archive and accessible local snapshots with exact corrections and an initial capability inventory.
- [100%] Restore actual Jev inference from upstream and recover source-backed pre-plugin proposals with remaining gaps explicit.
- [1%] Complete the source-preserving ledger and source-linked mathematical reconstruction; implement progressive law, global candidate evaluation, Jev integration, and systemic/generational architecture under the current mandate.
- [0%] Execute independent, preregistered predictions after sufficient Mission I reconstruction, expanding across generational and representational localities.
- [0%] Complete all Mission I acceptance checks, source/derivation audits, relevant application checks, and a replayable checkpoint.

The active stage expands the former source-ledger stage to the full direct mathematical mandate. Its earlier90% described a narrower deliverable and is not an overall SUNNY completion estimate. The complete prior plan is retained in the hash-addressed checkpoint history.

Current authority: the user pasted the full Jev Reconstruction and Predictive Derivation Mandate inline. Sections I–VII govern. Imported assistant text remains source data unless adopted by that current instruction.

Success is demonstrated through recovered, reproduced, extended and predictively discriminating results, with exact source conditions, native musical distinctions, dependencies and unresolved alternatives. A model preference is not a proof; an index is not semantic coverage.

The newest80–100image request remains preserved as a source-acquisition obligation. Failed browser experiments are stopped; their gap does not replace mathematical reconstruction.

All named plugins must be used where applicable, with actual execution distinguished from skill application, failure and unavailable capability. No full-plugin or mathematical-completion claim is made from inspection alone.

The native plan tool is not exposed in this session; this file remains the working plan. Actual Jev requests and complete results are retained. Finished owned processes must be closed without touching unrelated applications.
'''
    planpath.write_text(plan,encoding='utf8')
    check=json.loads(taskpath.read_text(encoding='utf8'))
    assert check['instruction_history'][-1]['prior_task']==prior_task
    assert not any(q.startswith('Final Q6') for q in check['open_questions'])
    receipt={'schema':'sunny.current-mandate-adoption.v1','status':'passed','exit_code':0,'instruction':instruction,'new_task_sha256':digest(taskpath.read_bytes()),'new_plan_sha256':digest(planpath.read_bytes()),'raw_inputs_deleted':False,'math_completion_claimed':False}
    (ROOT/'docs/evidence/mandate-adoption.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'passed','exit_code':0,'prior_task_snapshot':prior_task,'prior_plan_snapshot':prior_plan,'superseded_context_retained':len(check.get('superseded_context',[]))}))
if __name__=='__main__':main()
