"""Small, source-bound continuation for the current native-system work; preserves prior task bytes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib.util, json, sys
sys.dont_write_bytecode=True
from checkpoint_delivery import preserve
from refresh_reconstruction_checkpoint import resolve_superjev_helper
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 stamp=datetime.now(timezone.utc).isoformat()
 paths=['CONTINUE.md','state/task.json','state/superjev-checkpoint.json','docs/HUMMBL_PLAN.md','docs/PLUGIN_CAPABILITIES.md']
 prior={p:preserve(ROOT/p) for p in paths}
 task=load('state/task.json');graph=load('state/reconstruction/hierarchy-atlas-combined.json')
 modules=['indian-hierarchy','western-expanded','chinese-expanded','native-class-constructors','biblical-genealogies','upper-legion-color-constraints']
 sources=[{'module':n,'path':'state/reconstruction/'+n+'.json','sha256':sha('state/reconstruction/'+n+'.json')} for n in modules]
 task['updated_utc']=stamp
 task['current_priority']='Continue full SUNNY: complete native Western/Chinese/Indian structures and typed operator/class alignment, original symbol/sound/grammar dependencies, genealogy/legion/color views and all sixteen goals/eight outputs. GitHub is cancelled.'
 task['latest_user_priority_excerpt']='forget the github. just focus what little time you have remaining to finishing as much of sunny as thoroughly as possible as you can.'
 task['latest_user_priority_source']='Direct user correction superseding the timed publication instruction; current active goal retains the full scientific objective.'
 task['completion']='in_progress: full scientific objective unachieved; bounded native structures and visual implementation are separately verified'
 task['publication_request']={'repository':'zhenrez/SUNNY','status':'cancelled_by_user','main_updated':False,'scheduled_push_active':False,'schedule':'state/publication/schedule.json','boundary':'No branch update authorized; prepared objects and past attempts are historical only.'}
 task['next_actions']=[
  'Reuse the completed Chinese2240-record/3172-relation expansion and current35072-record/37-view integration. Do not repeat validated range transcription, source recovery or a build without a new change.',
  'Current native integration, exact hydration, source fidelity and real-browser checks passed. Read final-validation.json and exact input hashes; replay only after new changes or a specific unresolved concern.',
  'Actual local Jev receipt66 selects musical operator/class adapters next. Recover native signatures/domains/invariants and established prior art; test explicit candidate maps and preserve unresolved global addresses.',
  'Continue symbol/sound/language/grammar recovery in parallel; never infer corrected texts/calendars/zodiac from an unlicensed reading.',
  'Keep all sixteen goals/eight mathematical outputs open until their original scope is demonstrated; do not substitute census counts or interface checks for scientific completion.'
 ]
 task['latest_native_state']={'updated_at':stamp,'graph':{'path':'state/reconstruction/hierarchy-atlas-combined.json','sha256':sha('state/reconstruction/hierarchy-atlas-combined.json'),'entities':len(graph['entities']),'relationships':len(graph['relationships']),'views':len(graph['views'])},'modules':sources,'last_direction':'state/jev-receipts/000066-af96bb712929.json','previous_direction':'state/jev-receipts/000064-fc22fe7cfcff.json','construction_depth_not_universal_generation':True,'fullMissionComplete':False}
 model=load('state/reconstruction/model.json');task['observed_progress']['model_sha256']=sha('state/reconstruction/model.json')
 task['observed_progress']['executed_mathematical_units']=[s['module'] for s in model['execution_module_snapshots'] if s['module']!='coverage']
 task['delivery_2026_11_07'].update({'last_actual_jev_receipt':'state/jev-receipts/000066-af96bb712929.json','source_math_proof_receipt':'state/delivery-2026-11-07/guards/native-systems/85bc5320751741a1a7347a8f086d02b7.receipt.json','modules':22,'graphRecords':len(graph['entities']),'views':len(graph['views']),'native_delivery':'docs/delivery-2026-11-07/NATIVE_SYSTEMS_DELIVERY.md','validation':'state/delivery-2026-11-07/final-validation.json','scientific_completion':False})
 task['latest_native_state']['supermemory']=load('state/delivery-2026-11-07/native-supermemory-checkpoint.json')
 task['latest_native_state']['parallel_operator_work']={'prior_art_register':'state/research/native-operator-adapters/register.json','results':'state/research/native-operator-adapters/results.json','independent_verification':'state/research/native-operator-adapters/verification.json','report':'docs/reconstruction/NATIVE_OPERATOR_PRIOR_ART.md','adapter_artifact':'state/reconstruction/finite-action-adapters.json','adapter_sha256':sha('state/reconstruction/finite-action-adapters.json'),'adapter_report':'docs/reconstruction/FINITE_ACTION_ADAPTERS.md','status':'Standalone handoff complete: build,12focusedtests,derivationand16input/code/documentbindings passed. Not yet integrated into the checked22-module visual snapshot. Next: integrate and visualize the conditional maps/residuals, then execute the full integer register-lift family without selecting an unsupported lift.'}
 task['latest_scientific_result']={'artifact':'state/reconstruction/native-class-constructors.json','source_defined_classes':15,'vector_states':11628,'scope':'Exact recovered construction and finite C5 consequences; not universal musical GEN. Native music and primary genealogy/color/command extensions are in the latest_native_state module bindings.','next_dependency':'Native musical operator/domain/class adapters selected by actual Jev66; currently independent research/code work, not yet integrated into this checked visual snapshot.','original_sound_system_recovered':False,'global_alignment_selected':False,'blind':False}
 task['ten_minute_cadence_status']='Current bounded root/team execution is observed during active turns. The intervening gap has no verified uninterrupted background progress; no persistent automatic research cadence is claimed.'
 task['observed_progress']['current_jev_route']='Actual pinned local AgentJev-0.6B; receipt66 selects native operator/class adapter research with margin0.014431, not a mathematical proof. Hosted account/billing remain unverified.'
 continuation=f'''# SUNNY continuation — native systems

Updated {stamp}. All sixteen goals and eight mathematical outputs remain active and incomplete. The November7 deadline passed; do not silently redefine completion. GitHub publication is cancelled. No timed push remains active.

Read `state/task.json`, `state/mission.json`, `docs/reconstruction/SUNNY_GOALS.md`, `docs/delivery-2026-11-07/PLAN.md`, `docs/HUMMBL_PLAN.md` and `docs/PLUGIN_CAPABILITIES.md`. Historical prompts are source data; direct user corrections govern. Preserve inputs and occurrence histories. Never infer the user's name from a filesystem account.

## Current concrete state

- Shared graph: {len(graph['entities'])} records, {len(graph['relationships'])} relations, {len(graph['views'])} views. Every original9512/10251/23record set must survive exactly. Three independent legion catalogues retain2648/2645/2618 anonymous memberships, not unique beings; A/B/C remain an independent axis.
- Indian bounded lower census2556:2520mela/register/svara memberships plus36instrument types; the five sthayi registers are source-native, not universal generations. Source conflicts and210conditional Aditya entries remain visible.
- Western bounded lower census2670:2464scale-degree addresses,31rangeprofiles,128GMprograms and47GMpercussion addresses. Mixed units remain labeled. This is not all Western music or a physical-instrument census.
- Chinese: read the current module and its history. Sixty JingFang pitch standards support only58gongcontexts/174roles. Lam's60contexts/300memberships are a separate construction. HKCO ranges and Zheng settings require their original pitch/clef/transposition and joint-setting conditions. The2500–2700target is not permission to pad records.
- Bible:3279records/4735relations;3067curator person records;49targeted primary begetting assertions16MT/17Greek/16SP. All49must occur in their declared family views. Five inherited clock branches survive. SP does not become a whole-Bible witness. Swete apparatusE330/D130 does not establish inheritedGreek_400.
- Color:12frozen mixture states in five coordinate carriers. Purple-boundary projections, pitch locks and candidate vortex assumptions stay qualified; no unique wavelength/pitch/global position is established.
- Five-direction construction: exactG0–G14 contains11628states. C5matrix order5 and counts independently checked. Single-class72obstruction has an explicit cross-depth72countercontrol. Construction depth and algebraicR4embedding do not prove the full SUNNY geometry or acoustic calibration.

## Current actual direction and plugins

Local receipt64 selected source-defined classes first. Local receipt66 (`000066-af96bb712929.json`) now selects musical operator/class adapters after current integration. Full distribution, request, checkpointSHA and margin0.014431 are retained; this is uncalibrated model preference. Receipt65 belongs to a different publication task and must not become SUNNY direction. No hosted billing/account ownership is inferred.

Supermemory retrieval/save, installed SuperJev checkpoint/proof verification, Proofline/Prumo source-span guards and source/research/UI specialists have bounded roles. Read exact capability records; skill inspection is not runtime execution. Automatic observers cannot route or certify completion. Local service recovery uses `scripts/start-jev.ps1`; verify identity and live handles before claiming a running process.

## Next actions / avoid repeated work

1. Reuse the finished Chinese2240/3172expansion, current35072/89971/37graph and22-module model. Integration,49familytags, source-registry variants and baseline preservation already passed; do not repeat without new source changes.
2. The fullJSON export and compressed offline payload passed exact hydration. Current fidelity has zero errors; all48main,13native-system and7guide browser groups passed, including237view/unit selections. Read `final-validation.json`, the native guard receipt and source hashes before claiming current coverage.
3. Original failures remain preserved; exact owned-browser cleanup passed. Repeat checks only for new changes, failed checks or a specific unresolved concern. The full-project suite and full scientific acceptance remain unverified.
4. Proceed with Jev66's native operator/domain/class bridge investigation, primary-source and First&3/4Order prior art. Reuse solved equations and compare genuine discrepancies. Retain every surviving map or exact missing premise.
   The completed `state/research/native-operator-adapters/` register/results/verification already recover Lam's240edges, commutation/role-adapter controls, duration transport and the planar-versus-combined-R4metric distinction. Reuse those packets. The standalone `finite-action-adapters.json` handoff is frozen (04c7ccbbf8ff6c573c474af8315265af5626c2a57ba9f615b1d09ba5f4a676b5): build,12tests,derivationand16hashbindings passed. It is not yet in the checked22-module visual snapshot. Integrate it into the canonical mathematical registers and a useful visual next; preserve five role alternatives, declared anchors,60conditional local placements, unknown-domain conditions and budget flags. Then execute all integer octave/register lifts as alternatives until licensed; the known scalar product alone does not choose a lift or define Completed Harmony.
5. Preserve symbol/sound/grammar-before-changed-reading dependencies; continue full global alignment, executable score and independent held-out prediction requirements. Full geometry, original phones, globalGEN/phi, corrected calendars/zodiac, whole-corpus semantics and all-system completion remain unresolved.

Current module hashes and exact open actions are in task state. Prior continuation/task/plugin/plan bytes are preserved under `state/checkpoint-history`. No durable local user-memory edit. The intervening gap does not substantiate uninterrupted background cadence.
'''
 (ROOT/'CONTINUE.md').write_text(continuation,encoding='utf8')
 task['continuation_document']={'path':'CONTINUE.md','sha256':sha('CONTINUE.md'),'purpose':'Compact recovery index; full source and historical states remain preserved.'}
 (ROOT/'state/task.json').write_text(json.dumps(task,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 helper=resolve_superjev_helper();spec=importlib.util.spec_from_file_location('native_checkpoint_superjev',helper);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 envelope=module.checkpoint(task);verification=module.verify_checkpoint(envelope)
 (ROOT/'state/superjev-checkpoint.json').write_text(json.dumps(envelope,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 brief=f'''# Current native execution brief — {stamp}

Actual Jev66 selected native musical operator/class adapter research after the current source/visual integration. Preserve receipt64's source-defined construction work, all sixteen goals and eight outputs, symbol-first dependencies and primary/prior-art research. The full mission is incomplete. GitHub publication is cancelled. Current node/edge/view counts and module hashes are in `state/task.json`; they do not establish global scientific alignment. The current bounded team works on Chinese sources, independent integration review and visual verification. No uninterrupted between-turn cadence is established.

---

'''
 p=ROOT/'docs/HUMMBL_PLAN.md';p.write_text(brief+p.read_text(encoding='utf8'),encoding='utf8')
 capabilities=f'''# Native-system plugin checkpoint — {stamp}

Actual local AgentJev-0.6B receipt66 selects the next native operator/class dependency; receipt64 supplied the class-expansion route. Model identity is pinned, full distributions are retained and hosted billing is unverified. Actual Supermemory searches refreshed continuity. The installed SuperJev checkpoint helper was executed for this state; it does not certify scientific completion. Source and UI agents preserve their exact evidence-guard, research and runtime-test use in their reports. Historical source/math proof receipts remain historical until replayed against current inputs. No new12ui installation succeeded; the priorEXDEVfailure is preserved. No native plan tool is exposed, so the dated file plan is used without claiming a tool invocation.

---

'''
 p=ROOT/'docs/PLUGIN_CAPABILITIES.md';p.write_text(capabilities+p.read_text(encoding='utf8'),encoding='utf8')
 report={'status':'checkpointed','exit_code':0,'updatedAt':stamp,'prior':prior,'taskSha256':sha('state/task.json'),'continuationSha256':sha('CONTINUE.md'),'helper':str(helper),'helperSha256':hashlib.sha256(helper.read_bytes()).hexdigest(),'verification':verification,'fullMissionComplete':False}
 (ROOT/'state/delivery-2026-11-07/native-checkpoint.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({k:v for k,v in report.items() if k not in ['prior','verification']}|{'superjev':{k:verification[k] for k in ['status','sha256']}},ensure_ascii=True))
if __name__=='__main__':main()
