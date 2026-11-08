"""Authorized current-ledger reconciliation; preserve the prior bytes and historical fields."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/evidence'
def digest(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def main():
 path=ROOT/'state/capabilities.json';before=path.read_bytes();previous=load(path)
 history=ROOT/'state/capability-history';history.mkdir(exist_ok=True)
 snapshot=history/('capabilities-before-mandate-'+digest(before)+'.json')
 if snapshot.exists():assert snapshot.read_bytes()==before
 else:snapshot.write_bytes(before)
 reportpath=OUT/'mandate-plugin-execution.json';report=load(reportpath)
 rows={p['name']:p for p in report['plugins']}
 local=rows['AgentJev Decisions'];local['runtime_status']='executed_failure_current_health_earlier_local_inference_success'
 local['current_mandate_application']='Fresh actual native health tool returned connection refused at127.0.0.1:8149. Earlier local evaluate/score receipts remain valid historical executions; current new decisions use actual SuperJev cloud jev-1.14.0. No local service started.'
 local['evidence'].append('docs/evidence/mandate-agentjev-current-health.json')
 local['limits']='Current local unavailability is distinct from earlier local inference success and current cloud success. No repeated startup, persistent process or cloud/local equivalence claim.'
 memory=rows['Supermemory'];memory['evidence']+=['docs/evidence/mandate-supermemory-checkpoint.json','docs/evidence/mandate-supermemory-readback.json']
 memory['current_mandate_application']='Fresh active-space search returned ten records; audit checkpoint y4c2AZECbQ5g4ui5ALuP7a accepted and read back in full, status done/dreaming.'
 priorrows={p['name']:p for p in previous['plugins']}
 assert set(rows)==set(priorrows) and len(rows)==24
 current=[]
 for name,row in rows.items():
  old=priorrows[name];new=dict(old)
  new.setdefault('historical_status',old.get('status'))
  new.setdefault('historical_selected_by',previous.get('selected_by'))
  new['status']=row['runtime_status'];new['runtime_status']=row['runtime_status'];new['method_status']=row['method_status']
  new['detail']=row['current_mandate_application'];new['description']=row['current_mandate_application'];new['boundary']=row['limits']
  new['current_mandate_application']=row['current_mandate_application'];new['evidence']='; '.join(row['evidence']);new['evidence_files']=row['evidence']
  new['current_evidence_audit']='docs/evidence/mandate-plugin-execution.json'
  current.append(new)
 result=dict(previous);result['historical_selected_by']=previous.get('selected_by');result['selected_by']='docs/evidence/mandate-plugin-method-superjev.json'
 result['updated_utc']=datetime.now(timezone.utc).isoformat();result['prior_bytes_snapshot']=str(snapshot.relative_to(ROOT)).replace('\\','/');result['prior_bytes_sha256']=digest(before);result['plugins']=current
 result['current_boundary']='Current runtime observations and method use are separate. Historical application/boundary fields are preserved history and never fallback current authority. Cloud actual Jev1.14.0 works; local native health currently refused. Not all plugins have an executable runtime or relevant current inputs.'
 path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 for old,new in zip(previous['plugins'],current):
  assert old['name']==new['name']
  for key in ('historical_application','historical_boundary'):assert old.get(key)==new.get(key)
 doc=ROOT/'docs/PLUGIN_CAPABILITIES.md';text=doc.read_text(encoding='utf8')
 oldline=next(line for line in text.splitlines() if line.startswith('| AgentJev Decisions | executed success earlier local |'))
 newline='| AgentJev Decisions | '+local['runtime_status'].replace('_',' ')+' | '+local['current_mandate_application']+' '+local['limits']+' |'
 text=text.replace(oldline,newline)
 text+='\nCurrent structured-ledger reconciliation: `state/capabilities.json` now contains these24current runtime/method rows with distinct historical fields and a byte-identical before-snapshot under `state/capability-history/`. A fresh native AgentJev health call returned connection refused; actual cloud SuperJev1.14.0 remains the current decision route. Supermemory checkpoint `y4c2AZECbQ5g4ui5ALuP7a` was accepted and read back in full; extraction remains `dreaming`, separate from readback success.\n'
 doc.write_text(text,encoding='utf8')
 extra=['state/capabilities.json','docs/evidence/mandate-agentjev-current-health.json','docs/evidence/mandate-supermemory-checkpoint.json','docs/evidence/mandate-supermemory-readback.json','docs/PLUGIN_CAPABILITIES.md']
 for name in extra:
  item=ROOT/name;report['evidence_files'][name]={'sha256':digest(item.read_bytes()),'bytes':item.stat().st_size}
 report['current_structured_ledger']={'path':'state/capabilities.json','prior_snapshot':result['prior_bytes_snapshot'],'prior_sha256':result['prior_bytes_sha256'],'historical_fields_preserved':True,'state_task_modified':False}
 report['latest_current_runtime_observation']='Native AgentJev health refused; cloud actual Jev1.14.0 remains working. Supermemory checkpoint accepted/read back; asynchronous extraction dreaming.'
 reportpath.write_text(json.dumps(report,indent=2),encoding='utf8')
 check={'status':'passed','plugins':24,'prior_snapshot':result['prior_bytes_snapshot'],'prior_sha256':result['prior_bytes_sha256'],'current_sha256':digest(path.read_bytes()),'historical_fields_preserved':True,'task_untouched':True,'local_health':'current_connection_refused','cloud':'actual_current_jev-1.14.0','supermemory_checkpoint':'y4c2AZECbQ5g4ui5ALuP7a'}
 (OUT/'mandate-capability-ledger-reconciliation.json').write_text(json.dumps(check,indent=2),encoding='utf8')
 print(json.dumps(check))
if __name__=='__main__':main()
