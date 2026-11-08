"""Expose audited plugin records plus explicitly sourced current observations."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for line in (ROOT/'docs'/'PLUGIN_CAPABILITIES.md').read_text(encoding='utf8').splitlines():
    if not line.startswith('| '): continue
    cells=[x.strip() for x in line.strip().split('|')[1:-1]]
    if len(cells)!=4 or cells[0] in ('Requested plugin','---'): continue
    rows.append({'name':cells[0],'version_or_capability':cells[1],'historical_application':cells[2],'historical_boundary':cells[3]})
updates={
 'SuperJev':('executed_live_cloud_and_local','Installed coordination/recovery/verification skills applied. Fresh cloud connection actually returned judged jev-1.14.0; pinned local model decisions retain separate full receipts. No cloud/local parity claim.','docs/evidence/superjev-live-connection.json; state/superjev-connection-check.json; scripts/jev_tool.py; state/jev-receipts; state/superjev-checkpoint.json'),
 'Supermemory':('executed_read_write','Continuity checkpoints accepted and initial document read back; extraction/search can lag. No account-completeness claim.','docs/evidence/supermemory-checkpoint-save.json; saved document IDs in task checkpoint'),
 'AgentJev Decisions':('executed_live','Native health/info/evaluate/score succeeded after local bootstrap. CPU8149 remains default; GPU environment and prior bounded comparison retained. Service running state must be checked separately; owned workers are closed when finished.','docs/evidence/jev-native-bootstrap-result.json; docs/JEV_RUNTIME.md; state/processes'),
 'Sefirot Workbench':('executed_graph_and_jev_review','Pinned graph inspected; ten explicit source-defined perspective questions evaluated by the same actual Jev model. Not ten independent experts.','docs/SEFIROT_REVIEW.md; state/jev-receipts/000007-196825822a67.json'),
 'AgentProof':('executed_capture_and_verify','New read-only child receipt valid/MATCH;2observedcommands bothfailed and0changedfileschecked. Integrity/ordering only; no successful child check claimed.','docs/evidence/agentproof-sunny-scope.json'),
 'Proofline':('executed_project_verification','Actual user-instruction evidence package verifies. Numeric1 denotes exact span fidelity only; research confidence remains unknown; unsigned.','docs/evidence/proofline-sunny-decision.json; docs/evidence/proofline-sunny-scope.json'),
 'MightShape':('applied_and_checker_executed','Evidence firewall and TEST_FIRST BuildGate applied; synthetic model outputs remain separate from user evidence; complete five-record checker result retained in work queue.','docs/GUARDRAILS.md; state/work-queue.json'),
 'HUMMBL Operations':('applied_live_jev_plan','Actual Jev-selected queue, dependencies, source statuses and operating brief; contrary model outputs preserved under user authority.','docs/HUMMBL_PLAN.md; state/work-queue.json'),
 'Agent Skills':('applied_specialist_reviews','Frontend/browser/context/code review guidance applied with actual source, HTTP and decision-guard checks; source content treated as data.','docs/UI.md; docs/evidence/decision-guard-regression.json'),
 'Wolfram':('executed_math_checks','Actual standard geometry and finite C6 calculations; erroneous host orbit expression retained alongside corrected36-unordered-orbit audit, never erased.','docs/evidence/math-wolfram-evaluator.json; docs/evidence/wolfram-orbit-input-error.json; docs/NATIVE_KERNEL_AUDIT.md'),
 'Research Evidence Finder':('applied_source_verification','Exact source spans and byte hashes retained; new native artifact bindings being audited; no literature or full-account certificate.','docs/REQUIREMENTS.json; docs/evidence/recovery-integrity.json'),
 'Prumo + Jev Research':('executed_arithmetic_and_applied_research','Exact720/360 computation plus source-recovery research workflow; actual Jev decisions now use independent live service.','docs/evidence/prumo-result.json; docs/NATIVE_KERNEL_AUDIT.md'),
 'Research Methodology':('applied_research_workflow','Source-backed specification, objective/finding ledgers and current bounded native audit; discovery and adjudication remain separate.','docs/SPECIFICATION.md; docs/NATIVE_KERNEL_AUDIT.md')
}
for r in rows:
    status,detail,evidence=updates.get(r['name'],('historical_record',r['historical_application'],r['historical_boundary']))
    r.update(status=status,detail=detail,description=detail,boundary=r['historical_boundary'],evidence=evidence)
assert len(rows)==24 and len({r['name'] for r in rows})==24
out={'schema':'sunny.capability-ledger.v1','selected_by':'state/jev-receipts/000018-d31a1e7ee9d3.json','plugins':rows,'supplemental_specialists':[{'name':'12ui-design','status':'skill_applied_cli_dry_run','detail':'Dedicated UI instructions applied; initial CLI install spawnEINVAL onWindows retained, then direct CLI dry-run recovered. Hosted sign-in/paid design generation not executed.','evidence':'docs/UI.md'},{'name':'Riqor','status':'evidence_engineering_applied','detail':'Observable cleanup criteria, current process ownership inspection, focused lifecycle regressions and independent review applied. No model-weight or AGI claim.','evidence':'docs/PROCESS_AUDIT.md; docs/PROCESS_LIFECYCLE.md; docs/evidence/browser-process-cleanup.json'}],'boundary':'Current observations supersede earlier outages only within their stated scope. An inspected skill, an executed diagnostic, a model vote and scientific verification are distinct.'}
(ROOT/'state'/'capabilities.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'requested_plugins':len(rows),'supplemental_specialists':len(out['supplemental_specialists']),'output':'state/capabilities.json'}))
