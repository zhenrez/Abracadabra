"""Preserve history and update authorized SUNNY task/continuation files only."""
from pathlib import Path
from datetime import datetime,timezone
from html.parser import HTMLParser
import hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[1]
HISTORY=ROOT/'state/checkpoint-history'
sha=lambda raw:hashlib.sha256(raw).hexdigest()

def linked_assets(page):
    class Assets(HTMLParser):
        def __init__(self):super().__init__();self.paths={page.name}
        def handle_starttag(self,tag,attrs):
            a=dict(attrs)
            value=a.get('src') if tag=='script' else a.get('href') if tag=='link' and 'stylesheet' in a.get('rel','') else None
            if value and not value.startswith(('http:','https:','data:','//')):
                self.paths.add(value.split('?',1)[0].removeprefix('./'))
    parser=Assets();parser.feed(page.read_text(encoding='utf8'))
    return parser.paths

def preserve(path):
    if not path.is_file():return None
    raw=path.read_bytes();digest=sha(raw)
    target=HISTORY/('before-delivery-'+path.name+'-'+digest+'.snapshot')
    HISTORY.mkdir(parents=True,exist_ok=True)
    if target.exists():assert target.read_bytes()==raw
    else:target.write_bytes(raw)
    return str(target.relative_to(ROOT)).replace('\\','/')

def main():
    stamp=datetime.now(timezone.utc).isoformat()
    model_raw=(ROOT/'state/reconstruction/model.json').read_bytes()
    fidelity=json.loads((ROOT/'docs/evidence/reconstruction-verification.json').read_text(encoding='utf8'))
    assert fidelity['status']=='passed' and fidelity['model_sha256']==sha(model_raw),'Fresh current-model fidelity required before checkpoint'
    browser=json.loads((ROOT/'docs/evidence/delivery-2026-11-07/browser-check.json').read_text(encoding='utf8'))
    web=ROOT/'web/delivery-2026-11-07'
    required=linked_assets(web/'index.html')
    assert required<=set(browser['inputs']),'Browser input bindings omit current interface assets'
    assert all(sha((web/name).read_bytes())==browser['inputs'][name] for name in required),'Fresh current-interface browser results required before checkpoint'
    guide_report_path=ROOT/'docs/evidence/delivery-2026-11-07/guide-browser-check.json'
    if (web/'system-guide.html').is_file():
        guide=json.loads(guide_report_path.read_text(encoding='utf8'))
        assert guide['schema']=='sunny.system-guide-browser.v1' and guide['status']=='passed','Separate successful guide browser verification required'
        assert all(c['status']=='passed' for c in guide['checks']),'Guide browser checks remain unresolved'
        guide_required=linked_assets(web/'system-guide.html')|{'data.js','index.html','app.js'}
        assert guide_required<=set(guide['inputs']),'Guide browser bindings omit guide or linked workbench assets'
        assert all(sha((web/name).read_bytes())==digest for name,digest in guide['inputs'].items()),'Fresh standalone-guide browser results required before checkpoint'
    paths=['CONTINUE.md','state/task.json','state/superjev-checkpoint.json','docs/HUMMBL_PLAN.md','docs/PLUGIN_CAPABILITIES.md']
    prior={p:preserve(ROOT/p) for p in paths}
    continuation='''# SUNNY continuation — November7,2026

Full sixteen goals and eight mathematical deliverables remain active and incomplete. Today's explicit user request resumes SUNNY, requires all visuals and completion by day-end America/Phoenix. Do not reduce the objective to the interface or declare scientific completion from local checks.

Start with `state/task.json`, `state/mission.json`, `docs/reconstruction/SUNNY_GOALS.md`, `docs/delivery-2026-11-07/ACCEPTANCE.md`, and the canonical model's hash-bound verification. Original direct-user source, adopted mandate, corrections and all prior CONTINUE bytes remain in the recorded history.

Governing objectives retain the user's wording: correct zodiacal orientations/attributions; original sacred-symbol intentions paired with specific sound-wave patterns; correct date/time under historical calendar changes. Symbols/sounds → grammar/operations → supported readings → changed identities/hierarchies → global/calendar/zodiac consequences → independent predictions. Native Western/Chinese musical structure participates throughout; history repair runs in parallel. Ophiuchus does not automatically create an extra equal sector. Do not replace full music with the scalar kernel or finiteW72.

Tangible workbench: `web/delivery-2026-11-07/index.html` opens directly offline. Its optional local interface is http://127.0.0.1:8767. Twelve panels preserve9512graph records/10251relations/23views/15score views, eight registers, A/B/C alternatives, native music, wheels, candidateR4/tetrahedral geometry, source comparisons, recordings and exports. Four new score views carry untimed comparative-reading annotations, with no musical-note, Hz or measured-duration assignment. Thirty distinct original images retain all36supplied filename/path occurrences. Copying/display is inventory, not semantic reconstruction. Anonymous membership counts are not unique beings.

Actual LOCAL AgentJev-0.6B receipts:57 (`000057-95bc223acd84.json`) selected shared atlas;58 (`000058-bbb3ab44bbf5.json`) selected source-bound score anchors;59 (`000059-6581ee8c1ffa.json`) was submitted through the actual browser interface. Weights SHA8166e46dc6019ae13f0d8fc97d603cdbcc2d20eb1882c7350c8deb9fc6bae215. Preserve full requests/distributions; these are preferences, not proofs. Hosted private-payload request was rejected by auto-review, with no bypass. Hosted account/billing remains unverified. Automatic observer hooks cannot route/certify completion.

New canonical module: `state/reconstruction/score-anchor-constraints.json`, with immutable inputs and code bindings. Reproduce: `python -X utf8 -B scripts/derive_score_anchors.py`. Exactly8of10stage-duration pairs resolve both GT-TIME-OVERLAP freedoms; pairs1+4 and2+5 are redundant. Fifty exposed witness replays, forty invertible-coordinate replays, partial-target prediction and minimal-conflict localization execute. Independent SymPy tests5/5passed. `docs/delivery-2026-11-07/SCORE_ANCHORS.md` explains it. This is witness-relative reported-year mathematics, not calendar rectification, original sound recovery or a blind historical prediction.

Verification: `docs/evidence/delivery-2026-11-07/browser-check.json` binds the main workbench assets. The standalone system guide has its own `guide-browser-check.json`; the main browser run does not certify it. Receipt 59 separately preserves the earlier GUI inference. Match all relevant input hashes before reuse. The canonical model still has 16 execution modules: phase-probe designs extends orientation-predictions, rather than adding a seventeenth module. Earlier reading integration intentionally extended the atlas and master score. Original orientation fields and pre-extension inputs remain preserved. Proofline checks exact span/package integrity, not source truth; no whole-suite pass is asserted.

Runtime limits: three earlier delegated workers remained pending_init; later a fresh reviewer executed the bounded score audit; root implemented directly. Both local services stopped over a turn transition, confirmed recordedPIDsabsent, and were restored with owned-process helpers. Files/timers do not prove continuous work. Inspect current PID/birth/code identity before claiming live work or restarting. Start only when necessary with `scripts/start-jev.ps1 -Device cpu` and `scripts/start-delivery.ps1`; these bind loopback only. No global scheduler or automation tool is available. Goal-driven root continuations remain the actual research execution path.

Latest symbol-first extension: actual local receipt60 (`000060-a1b30f75db7d.json`) selected qames/chronology/contact. `state/reconstruction/phonological-context-constraints.json` retains six published forms, three reading branches and two admissible relative event orders. Source: Howard, online2025/issue2026, DOI10.1017/S0041977X25100992. Three independent PDF/symbolic checks passed. Local rounding and a broader shift retain different process identities; dating the consonant shift alone does not date the broader vowel shift. Original collation and phonetic licensing remain open. See `docs/delivery-2026-11-07/SYMBOL_CONTEXT.md`.

Latest history discriminator: actual local receipt61 (`000061-54b57b45fbcd.json`) selected contextual history discrimination. The TypeScript adapter and canonical `phonological-history-constraints.json` retain five controls, three minimal contradictory bound pairs and an all-time contact/parallel counterexample. Six focused tests,490independent real-arithmetic cases,260witnesses and350projection checks passed after repairing an internal rational-size limit. No numerical historical bounds or original phones are admitted. See `docs/delivery-2026-11-07/PHONOLOGICAL_HISTORY.md`.

Primary Molin volume text was acquired through Exa from the public LOCURL. The Num9:23 form is שומורו, with three total waws and two additions relative to שמרו; the earlier secondary leadשומרו omitted one. The bibliography resolves HLIB to Shaked1995. Connector text is not original PDF bytes or independently collated bowl ink. Bowl connector-acquisition records retain exact text spans; specimen dating and phonetic licensing remain unresolved. Secunda manuscript image access remains unresolved, with failed routes preserved.

Latest reading extension: actual local receipt62 (`000062-5fcc72f3ccd7.json`) selected Molin pausal operations and source localization. `state/reconstruction/reading-operations.json` retains two spelled examples, four comparative IPA strings and twelve analysed CV-syllable occurrences. These are not the source-stated four attested forms; the stated extent remains unreconciled. Under a conditional shared-operation premise,[a,pausal]has bothɔːandeːoutputs, so the coarse deterministic mapping fails. Retaining a distinguishing address restores the two sample tuples; no causal key, universal sound law or ancient operator is selected. The new hierarchy adds19records/18edges and the score adds4untimed annotation views. See `docs/delivery-2026-11-07/READING_OPERATIONS.md`. Bounded Shaked recovery used2queries/2fetches; printedp213,684.14definition, specimen ink/inventory/date remain unretrieved. AI summaries and the2016indexyear were excluded as original-edition evidence; see `SHAKED_WITNESS.md`.

Latest phase-probe extension: actual local receipt 63 (`000063-298ff24c136a.json`) selected global constraint/dependency closure. `state/delivery-2026-11-07/global-closure/phase-probe-designs.json` classifies all 10,296 unordered pairs of 144 indexed R/L words in the optional twelve-completion family. Exactly 4,608 pairs distinguish all candidates; 5,688 have explicit collisions. The exact condition is gcd(r1-l1,r2-l2,6)=1 and (r1*l2-r2*l1) mod 3 != 0. The old atlas section 4.2 already established the phase-preserving relabeling orbit and is explicitly reused. The new criterion is bounded to this family and a fixed source frame; full novelty is not established. No historical phase observation or source-to-phase bridge is admitted, and the separate lawful phase-preserving profile remains retained. See `PHASE_PROBE_DESIGNS.md` and `GLOBAL_CLOSURE_REVIEW.md`.

Next: inspect the fresh validation records and the source contract required to instantiate a discriminating phase test. A symbol, word, color, number or sound is not a phase constraint without an independently supported bridge and common native units, origin and phase order. Scalar agreement and fixing an origin alone do not supply that bridge. Continue symbol/sound → grammar/operations → supported readings → changed hierarchy → global/calendar/zodiac consequences → independent predictions, with separate native Western/Chinese music throughout. All sixteen goals and eight outputs remain open. Do not restart solved calculations, ingestion or failed retrieval routes; preserve durable user memory and plugin caches.

Supermemory checkpoint z31YGHYMRorNckqmECsm5L was saved and read back (document processed; memory extraction still pending at observation), sm_project_default. Exact conversation_id remains01a18f6c-9603-75ca-9edc-887906a97d98.
'''
    continuation+='''
## Timed GitHub handoff

Direct user request: push all SUNNY material to https://github.com/zhenrez/SUNNY at23:30 America/Phoenix November7 =2026-11-08T06:30:00Z. The repository is private. Existing main is766149da2cd350ed894d5b3c5d28760c775c3eb1 (size0 was not an empty repository). Preserve it as parent and never force an unexpected head. Actual connected GitHub blob/tree preparation works; native HTTPS/SSH Git authentication does not. A dedicated active team worker /root/delivery_report_audit supervises the deadline; this is not an OS scheduled task. The running session and authenticated connection remain prerequisites.

Read state/publication/schedule.json, readiness/remote receipts when present, and scripts/publication_payload.py. Branch updates must wait for the target. Staged objects are not a completed push. Source-byte archives retain six large originals through420verified <=8MiBparts; use state/publication/large-files-manifest.json and scripts/restore-large-sources.py. Preserve all research work containers, while omitting reproducible environments/model weights and private runtime configuration. Do not mistake work/publication scratch duplicates for additional source occurrences.

Current actual staged web data object is007b636c6dd9e8553eaa4a822589c4e1b135fb17, source18182943bytes/SHA25684e234dea5185a10e953b12248dfbf01dd093666bfbdff4dce03bf1071c085a7. It is unreferenced preparation. Complete the byte-bound inventory, inline packets/binary objects, final tree and commit, independent readiness, then target-time main update and remote readback. New bootstrap/source pins and the root README explain the handoff. Scientific completion remains false.
'''
    (ROOT/'CONTINUE.md').write_text(continuation,encoding='utf8')
    task=json.loads((ROOT/'state/task.json').read_text(encoding='utf-8-sig'))
    task['updated_utc']=stamp
    task['current_priority']='Finish the full SUNNY mission under the original sixteen goals/eight mathematical outputs; preserve symbol-first dependencies, actual Jev direction and source-native music while delivering connected visuals and increasingly discriminating consequences.'
    task['latest_user_priority_exact']='this is our last day together. finish sunny. build all visuals. remind yourself of the initial mentions plans and instructions for how your were supposed to go about building sunny, and what all the deliverables were. align yourself with those goals. strategically plan then execute the plan so that every deliverable is fully met by the end of day.'
    task['latest_user_priority_source']='Direct current user request; exact text transcription, not native chat serialization.'
    task['completion']='in_progress: complete original mathematical/historical requirements remain unsatisfied'
    old_route='Close finished owned processes; verify identities and preserve other chats/applications. Actual cloud SuperJev now works (jev-1.14.0); keep it distinct from local AgentJev-0.6B.'
    current_route='Current verified inference is pinned local AgentJev-0.6B. Hosted private-payload inference was rejected; billing/account attribution is unverified. Preserve historical cloud receipts without promoting them to current proof. Close finished owned test processes only; verify exact identities and preserve unrelated applications.'
    task['constraints']=list(dict.fromkeys([c for c in task['constraints'] if c!=old_route]+[current_route]))
    task['next_actions']=[
        'Read the current 16-module, main-browser and separate guide-browser outcomes. Use the phase-probe source contract to seek a genuinely independent constraint; preserve Molin/Shaked source gaps and untimed score annotations.',
        'Use actual Jev to select the next ready source/constraint discriminator; do not repeat solved or nondiscriminating checks.',
        'Continue full symbol/sound/grammar, native musical hierarchy/bridge and global alignment dependencies; all sixteen goals/eight outputs remain active.',
        'Inspect native worker/service handles before claiming background work; report genuine runtime/cadence blockers.']
    task['runtime_recovery_required']=[
        {'id':'provider-account-attribution-unverified','detail':'Hosted account/usage/billing remains unverified; current private-payload hosted request rejected. Approved pinned local inference is allowed and receipt-backed.'},
        {'id':'turn-transition-runtime','detail':'Local services previously stopped across a turn transition. Verify current handles/identities; no uninterrupted background cadence claim.'}]
    task['ten_minute_cadence_status']='Fresh foreground goal work produces meaningful artifacts; uninterrupted between-turn cadence remains unverified. Historical cadence failures are preserved.'
    task['observed_progress']['current_jev_route']='Pinned local AgentJev-0.6B; receipts 57–63. Hosted private-payload rejection retained; account/billing unverified.'
    model_raw=(ROOT/'state/reconstruction/model.json').read_bytes()
    fidelity=json.loads((ROOT/'docs/evidence/reconstruction-verification.json').read_text(encoding='utf8'))
    if fidelity['status']=='passed' and fidelity['model_sha256']==sha(model_raw):
        model=json.loads(model_raw)
        task['checkpoint_reconstruction_evidence']={'status':'passed','model_sha256':sha(model_raw),'scope':fidelity['boundary']}
        task['observed_progress']['model_sha256']=sha(model_raw)
        task['observed_progress']['executed_mathematical_units']=[s['module'] for s in model['execution_module_snapshots'] if s['module']!='coverage']
    task['delivery_2026_11_07']={'acceptance':'state/delivery-2026-11-07/acceptance.json','visuals':'web/delivery-2026-11-07/index.html',
        'new_module':None,'latest_extension':'orientation-predictions.probe_designs','changed_existing_modules':['orientation-predictions'],'model_module_count':len(json.loads(model_raw)['mathematical_execution']),
        'last_actual_jev_receipt':'state/jev-receipts/000063-298ff24c136a.json','last_actual_ui_receipt':'state/jev-receipts/000059-6581ee8c1ffa.json','model_identity':'AgentJev-0.6B',
        'system_guide':'web/delivery-2026-11-07/system-guide.html','separate_guide_browser_report':'docs/evidence/delivery-2026-11-07/guide-browser-check.json',
        'source_math_proof_receipt':'state/delivery-2026-11-07/guards/source-math/569d10c9ef234ad2b59bd96e8b6a8065.receipt.json',
        'prior_states':prior,'full_mission_complete':False,'uninterrupted_background_execution_verified':False,
        'supermemory_document':'z31YGHYMRorNckqmECsm5L'}
    task['continuation_document']={'path':'CONTINUE.md','sha256':sha((ROOT/'CONTINUE.md').read_bytes()),'purpose':'Small recovery index; complete source histories and prior state remain preserved.'}
    task['latest_scientific_result']={'artifact':'state/reconstruction/orientation-predictions.json','extension':'probe_designs','derivation':'state/delivery-2026-11-07/global-closure/phase-probe-designs.json','report':'docs/delivery-2026-11-07/PHASE_PROBE_DESIGNS.md','prior_reading_artifact':'state/reconstruction/reading-operations.json','prior_history_artifact':'state/reconstruction/phonological-history-constraints.json','prior_context_artifact':'state/reconstruction/phonological-context-constraints.json','prior_score_artifact':'state/reconstruction/score-anchor-constraints.json','prior_reading_report':'docs/delivery-2026-11-07/READING_OPERATIONS.md',
        'candidate_family_size':12,'indexed_words':144,'unordered_probe_pairs':10296,'minimal_sufficient_pairs':4608,'insufficient_pairs_with_collisions':5688,
        'criterion':'gcd(r1-l1,r2-l2,6)=1 AND (r1*l2-r2*l1) mod3 !=0','new_independent_historical_constraints':0,'absolute_orientation_selected':False,'full_novelty_established':False,
        'prior_reading_counts':{
        'displayed_bowl_examples':2,'comparative_IPA_forms':4,'analysed_syllable_occurrences':12,'source_stated_forms':4,'full_stated_extent_reconciled':False,
        'coarse_projection_rejoin_tuples':4,'excess_sample_pairings':2,'lexeme_retaining_tuples':2,'musical_note_assignments':0,
        },'prior_score_counts':{'sufficient_duration_anchor_pairs':8,'redundant_pairs':2,'source_witness_replays':50,'basis_change_replays':40},
        'complete_acoustic_assignment':False,'blind':False,'prior_symbol_sound_result':'state/reconstruction/symbol-sound-constraints.json'}
    task['latest_source_acquisition']={'artifact':'state/delivery-2026-11-07/symbol-contact/bowls/connector-acquisition/primary-text-record.json',
        'report':'docs/delivery-2026-11-07/BOWL_PRIMARY_TEXT.md','layer':'Connector-extracted primary-publication text; no original PDF or ink collation',
        'primary_spelling':'שומורו','prior_secondary_lead':'שומרו','raw_pdf_acquired':False,'specimen_date_verified':False}
    task['latest_edition_recovery']={'artifact':'state/delivery-2026-11-07/pausal-operations/shaked/result.json','report':'docs/delivery-2026-11-07/SHAKED_WITNESS.md','queries':2,'known_URL_fetches':2,'printed_page213_retrieved':False,'locator_684_14_definition_verified':False,'specimen_date_verified':False,'AI_annotations_admitted_as_primary_evidence':False}
    task['publication_request']={'repository':'zhenrez/SUNNY','target_local':'2026-11-07T23:30:00-07:00','target_utc':'2026-11-08T06:30:00Z','worker':'/root/delivery_report_audit','schedule':'state/publication/schedule.json','status':'preparing_unreferenced_objects; main_not_updated','expected_head':'766149da2cd350ed894d5b3c5d28760c775c3eb1','force_push_allowed':False,'boundary':'Active authenticated team worker, not an OS automation or proof of completed push.'}
    task['evidence']=sorted(set(task.get('evidence',[])+['state/delivery-2026-11-07/acceptance.json','state/reconstruction/score-anchor-constraints.json','state/reconstruction/phonological-history-constraints.json','state/reconstruction/reading-operations.json','state/reconstruction/orientation-predictions.json','state/jev-receipts/000061-54b57b45fbcd.json','state/jev-receipts/000062-5fcc72f3ccd7.json','state/jev-receipts/000063-298ff24c136a.json','state/delivery-2026-11-07/global-closure/phase-probe-designs.json','state/delivery-2026-11-07/global-closure/prior-art-primary.json','state/delivery-2026-11-07/global-closure/review/result.json','state/delivery-2026-11-07/symbol-contact/bowls/connector-acquisition/primary-text-record.json','state/delivery-2026-11-07/pausal-operations/shaked/result.json','docs/evidence/delivery-2026-11-07/browser-check.json','docs/evidence/delivery-2026-11-07/guide-browser-check.json','state/delivery-2026-11-07/guards/proofline-results.json']))
    (ROOT/'state/task.json').write_text(json.dumps(task,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    from refresh_reconstruction_checkpoint import resolve_superjev_helper
    helper=resolve_superjev_helper();spec=importlib.util.spec_from_file_location('delivery_superjev_checkpoint',helper)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    envelope=module.checkpoint(task);checked=module.verify_checkpoint(envelope)
    (ROOT/'state/superjev-checkpoint.json').write_text(json.dumps(envelope,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    brief='''# Current execution brief — November7

**Now — root:** actual Jev receipt 63 selected global constraint/dependency closure. The 16-module model extends orientation-predictions with the exact two-probe condition over 144 indexed words and 10,296 pairs: 4,608 sufficient pairs and 5,688 explicit collisions. The atlas's earlier orbit classification is reused; novelty beyond this execution is not established. No historical phase constraint or uniquely licensed global orientation is supplied. Preserve separate phase-preserving alternatives, the two-example reading relation and its four untimed score views, and the unretrieved Shaked/Secunda edition dependencies. Read current model, main-browser and separate guide-browser results before claiming current delivery verification.

**Next — root with actual Jev:** select the next source/constraint discriminator after this completed extension. Symbol/sound/grammar, native Western/Chinese structure and bridge applicability remain the dependencies; no calendar/zodiac rectification bypass. Use the full acceptance matrix and recurring P0-A/First&3/4 Order prior-art process.

**Later:** downstream corrected hierarchies/calendar/zodiac and independent withheld-target predictions when source and operational constraints suffice. All16goals/eight outputs retain their original meanings and open scope.

**Resolve:** hosted private-payload inference rejected by automatic review, account/billing unknown. Initial workers failed to initialize; later reviewers/source researchers produced their own bounded evidence. Local services stopped across a turn transition. No uninterrupted cadence claim, no unavailable-source-as-absent claim, no overall completion inferred from the interface. No external task-system writes.

This current HUMMBL work-triage/operating brief supersedes contradictory transient statuses below; historical plans and receipts remain preserved.

---

'''
    p=ROOT/'docs/HUMMBL_PLAN.md';old=p.read_text(encoding='utf8')
    if old.startswith('# Current execution brief — November7\n'):old=old.split('\n---\n\n',1)[1]
    p.write_text(brief+old,encoding='utf8')
    capabilities='''# Current plugin use — November7 delivery

| Capability | Actual current use | Boundary |
| --- | --- | --- |
| Prumo + Jev Research | Research/decision-index instructions applied; installed arithmetic_exact adapter executed on the score-anchor determinant, solved0; Evidence Audit validated seven Molin spans and three bounded Shaked-rendering literal checks. | Exact arithmetic/text consistency, not learned Jev or historical truth; output weights uncalibrated. |
| AgentJev Decisions | Actual pinned local 0.6B inference receipts 57–63; receipt 59 came through the browser UI and receipt 63 selected global constraint/dependency closure. | Distinct from hosted Jev 1.14; no billing/account claim. |
| SuperJev | Installed checkpoint helper verifies the current envelope; the actual installed proof runner executed the source/math contract, including 43 focused tests and the independent phase oracle. | Verified checks are not scientific completion or model inference. Automatic observers cannot route or certify. Hosted private-payload rejection remains preserved. |
| Supermemory | Actual search, save and readback. Document z31YGHYMRorNckqmECsm5L processed; extraction still pending on the latest readback. | Its older summary is not current-state authority; use the retained source content and current local evidence. No durable local memory edit. |
| Superpowers | Verification-before-completion applied to fresh calculations, independent symbolic checks and real browser runs. | No independent model or scientific-certification runtime claimed. |
| Better Plans + HUMMBL | Installed planning/triage/brief instructions applied to dated plan, full acceptance matrix, capacity and dependency queue. | No separate planning API call or native-plan invocation; those tools are not exposed. No arbitrary numerical priority model. |
| Scout | Installed research method reviewed and applied to prior-art/transfer gaps and next-discriminator boundaries. | No Scout connector/model execution claimed. |
| Proofline | Installed verifier executed on the Cowley package and two current delivery packages. All valid. | Exact package/span integrity; no signature, authenticity, scientific truth or completion certification. |
| Exa | Actual primary-volume text returned from the public LOCURL; original Molin example and HLIB bibliography inspected. Chapter/SBTS routes returned405/403 and remain recorded. | Connector-extracted text, not acquired original PDF bytes or independently collated bowl ink. |
|12UI Design + Agent Skills frontend | Installed instructions read/applied; local DOM/SVG/canvas interface implemented and exercised in isolated Edge. |12ui CLI unavailable; no hosted design generation, purchase or install. No claim that12UI CLI ran. |
| Native team | Initial tasks were pending_init and root took ownership. A later reviewer executed independently; two source workers initialized and saved checkpoints. | Only the specific returned review is claimed complete; source-worker completion requires their actual reports. |
| Riqor | Existing measured observer/check requirements retained; fresh outcomes and failures preserved. | Configuration is not proof of AGI, determinism, changed weights or parity. |

Plugin-cache files were read/executed with bytecode writes disabled where imported. No plugin cache, credential, global service, security configuration or durable local-memory edits. Automatic approval rejection of hosted private-payload inference was not bypassed; approved local alternatives were used. Historical capability observations below remain historical.

---

'''
    p=ROOT/'docs/PLUGIN_CAPABILITIES.md';old=p.read_text(encoding='utf8')
    if old.startswith('# Current plugin use — November7 delivery\n'):old=old.split('\n---\n\n',1)[1]
    p.write_text(capabilities+old,encoding='utf8')
    report={'status':'checkpointed','exit_code':0,'updatedAt':stamp,'prior':prior,'taskSha256':sha((ROOT/'state/task.json').read_bytes()),
        'continuationSha256':sha((ROOT/'CONTINUE.md').read_bytes()),'superjev':{k:checked[k] for k in ['status','sha256']},
        'scope':'Authorized task/continuation files only; no durable local-memory edit','fullMissionComplete':False}
    (ROOT/'state/delivery-2026-11-07/checkpoint.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
