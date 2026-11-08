"""Preserve current task state and record verified hierarchy progress and remaining work."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=ROOT/'state/task.json';raw=p.read_bytes();state=json.loads(raw)
    saved=ROOT/'state/checkpoint-history'/('before-final-hierarchy-state-'+hashlib.sha256(raw).hexdigest()+'.json')
    if not saved.exists():saved.write_bytes(raw)
    state['next_actions']=[
      'Recover complete source-native upper transitions and ancestral rules selected by actual Jev; retain A/B/C and derive conditional downstream consequences.',
      'Expand and reconcile witness-native musical families, variants and actual organizational affiliations beyond the bounded current views.',
      'Investigate independent constraints distinguishing A/B/C and musical orientations; missing joins do not prove invariance.',
      'Apply the method to the two Greek hierarchies after current source-local extents and joins are reconstructed.',
      'Preserve new dependencies and receipts; synchronize CONTINUE.md, task/checkpoint, coverage and Supermemory without repeating settled work.']
    state['completed_current_hierarchy_unit']={
      'graph':'state/reconstruction/hierarchy-atlas-combined.json',
      'sha256':'715ba3a5d3c2b6779418dcb2ba6b5cc8924f173898a5d70153f264f132d970c7',
      'records':9493,'non_slot_records':1582,'generated_membership_slots':7911,'views':22,
      'source_register':'docs/reconstruction/HIERARCHY_SOURCE_REGISTER.md',
      'independent_review':'docs/evidence/hierarchy-independent-review.json',
      'ui':'deliverables/SUNNY_Hierarchy_Atlas.html',
      'ui_verification':'docs/evidence/hierarchy-ui-final-verification.json',
      'scope':'Verified bounded source views; universal hierarchy and Mission I remain incomplete.'}
    state['next_jev_direction']={'receipt':'docs/evidence/hierarchy-continuation-superjev.json',
      'model':'jev-1.14.0','choice':'native_upper_transitions_and_missing_joins',
      'conditional_model_probability':0.72,'interpretation':'Conditional model preference, not proof.'}
    state['evidence']=sorted(set(state['evidence']+['CONTINUE.md','state/hierarchy-direction.md',
      'state/reconstruction/hierarchy-atlas-combined.json','docs/evidence/hierarchy-source-registration.json',
      'docs/evidence/hierarchy-independent-review.json','docs/evidence/hierarchy-ui-final-verification.json',
      'docs/evidence/musical-hierarchy-verification.json','docs/evidence/continuation-coverage-reconciliation.json']))
    state['completion']='in_progress: bounded source hierarchy and UI verified; complete native extents, upper-to-lower joins, global orientation and Mission I/II acceptance unfinished'
    state['updated_utc']=datetime.now(timezone.utc).isoformat()
    p.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'status':'recorded','exit_code':0,'prior_state':str(saved),'current_next_actions':len(state['next_actions'])}))
if __name__=='__main__':main()
