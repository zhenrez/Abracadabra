"""Bounded, source-exact mission genealogy; never changes SUNNY's operational state."""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sqlite3
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/evidence/mission-semantics-source-review.json"
PINS = ROOT / "docs/evidence/mission-semantics-sources"
PINS.mkdir(parents=True, exist_ok=True)
sources, spans, texts = [], [], {}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(data, suffix):
    path = PINS / (sha(data) + suffix)
    if path.exists():
        assert path.read_bytes() == data
    else:
        path.write_bytes(data)
    return str(path.relative_to(ROOT)).replace("\\", "/")


def file_source(sid, path, role, **extra):
    path = pathlib.Path(path)
    data = path.read_bytes()
    snapshot = pin(data, path.suffix or ".txt")
    row = dict(id=sid, original_path=str(path), snapshot=snapshot, sha256=sha(data),
               bytes=len(data), role=role, **extra)
    sources.append(row)
    texts[sid] = data.decode("utf-8-sig")
    return texts[sid]


def excerpt(eid, sid, needle, *, turn=None, end=None, exact=None, attribution=None, note=None):
    text = texts[sid]
    lo, hi = 0, len(text)
    role = next(x["role"] for x in sources if x["id"] == sid)
    timestamp = None
    if turn is not None:
        markers = list(re.finditer(r"^## (Prompt|Response):\s*$", text, re.M))
        lo = markers[turn].end()
        hi = markers[turn + 1].start() if turn + 1 < len(markers) else len(text)
        role = "user" if markers[turn].group(1) == "Prompt" else "assistant"
        timestamp = text[lo:hi].strip().splitlines()[0]
    k = text.find(needle, lo, hi)
    assert k >= 0, (eid, needle)
    if exact is not None:
        a, b = k, k + len(exact)
        assert text[a:b] == exact, eid
    elif end is not None:
        a, b = k, text.find(end, k, hi)
        assert b > a, (eid, end)
    else:
        breaks = list(re.finditer(r"\r?\n[ \t]*\r?\n", text[lo:k]))
        a = lo + breaks[-1].end() if breaks else lo
        br = re.search(r"\r?\n[ \t]*\r?\n", text[k:hi])
        b = k + br.start() if br else hi
    while a < b and text[a].isspace():
        a += 1
    while b > a and text[b - 1].isspace():
        b -= 1
    quote = text[a:b]
    row = dict(id=eid, source_id=sid, source_role=role, turn_index=turn,
               timestamp=timestamp, start_character=a, end_character_exclusive=b,
               line_start=text.count("\n", 0, a) + 1,
               line_end=text.count("\n", 0, b) + 1,
               exact_quote=quote, quote_sha256=sha(quote.encode("utf-8")))
    if attribution:
        row["embedded_attribution"] = attribution
    if note:
        row["scope_note"] = note
    spans.append(row)
    return row


attachment = pathlib.Path("C:/Users/Brend/.codex/attachments/9e8a9e86-cd7d-4923-8da0-1ead7954ca88/Pasted text.txt")
file_source("initiating_concept_attachment", attachment, "role-delimited exported conversation",
            imported_document_not_current_instruction=True,
            original_chat_url="https://chatgpt.com/c/6ae4e753-014c-83e8-b86e-2dd4900f5f6e",
            database_source_id="7c5cd4c51ad9da8020d497ab449770e5dd38b3d334bf8ad612e1c9f8e747f125")

native_path = pathlib.Path("C:/Users/Brend/.codex/sessions/2026/10/30/rollout-2026-10-30T17-44-55-01a18f6a-af21-78c1-83e2-02117c13aa7a.jsonl")
with native_path.open("rb") as stream:
    for line_no, line in enumerate(stream, 1):
        if b"build SUNNY" not in line:
            continue
        obj = json.loads(line)
        payload = obj.get("payload", {})
        if payload.get("role") != "user":
            continue
        text = "\n".join(x.get("text", "") for x in payload.get("content", []) if isinstance(x, dict))
        if "Let's build SUNNY" not in text:
            continue
        sid = "native_initiating_assignment"
        sources.append(dict(id=sid, original_path=str(native_path), source_line=line_no,
                            snapshot=pin(text.encode(), ".txt"), sha256=sha(text.encode()),
                            bytes=len(text.encode()), role="user", timestamp=obj.get("timestamp"),
                            native_record_snapshot=pin(line, ".jsonl"),
                            native_record_sha256=sha(line),
                            boundary="Native role=user record; original session is append-only and not treated as a frozen whole-file hash."))
        texts[sid] = text
        break
    else:
        raise AssertionError("Pinned native initiating user record not found")

current_receipt = json.loads((ROOT / "docs/evidence/current-semantics-native-user.json").read_text(encoding="utf-8-sig"))
latest = current_receipt["selected_latest"]
file_source("native_current_semantic_correction", ROOT / latest["text_snapshot"], "user",
            native_original_path=latest["source_path"], native_source_line=latest["source_line"],
            timestamp=latest["timestamp"], native_record_snapshot=latest["record_snapshot"],
            governing_current_direct_user_correction=True)
assert sources[-1]["sha256"] == latest["text_sha256"]

file_source("adopted_mandate", ROOT / "data/raw/mandate-inputs/99dabf2083b9a04c7f7302546651726548a29f5c10a5c7f7a934f983a6e58f63/Pasted text.txt",
            "user-adopted mandate", boundary="Explicitly adopted in the current chat; interpreted within the later direct correction, not erased.")
file_source("operational_task_snapshot", ROOT / "state/task.json", "assistant-maintained task state",
            boundary="Snapshot of implementation wording when reviewed; not a new instruction and not edited by this review.")

conn = sqlite3.connect("file:" + (ROOT / "data/sunny.sqlite").as_posix() + "?mode=ro", uri=True)
conn.row_factory = sqlite3.Row


def message_source(sid, mid):
    row = dict(conn.execute("select m.*,s.path,s.sha256 as raw_sha256 from messages m join sources s on m.source_id=s.id where m.id=?", (mid,)).fetchone())
    raw = pathlib.Path(row["path"]).read_bytes()
    assert sha(raw) == row["raw_sha256"], sid
    text = row["text"]
    assert sha(text.encode()) == row["content_sha256"], sid
    occurrences = [dict(x) for x in conn.execute("select id,conversation_id,native_id,role,source_id,locator from messages where content_sha256=? order by id", (row["content_sha256"],))]
    sources.append(dict(id=sid, original_path=row["path"], original_file_sha256=row["raw_sha256"],
                        snapshot=pin(text.encode(), ".txt"), sha256=sha(text.encode()), bytes=len(text.encode()),
                        role=row["role"], message_id=mid, native_id=row["native_id"],
                        database_source_id=row["source_id"], locator=row["locator"],
                        conversation_id=row["conversation_id"], occurrences=occurrences,
                        boundary="Exported role is preserved. Embedded quoted conversation does not automatically inherit that role or become current instruction."))
    texts[sid] = text


message_source("scoped_music_only_trial", "36a500349db9ac3ea2eb25c560c38585b1dacdde211d0b0e1a28c44456b89181")
message_source("historical_layer_preservation", "e55c4b6abe4a1251d2cf10fdac3dc129e62ef09e523081646b61e84854ded2d8")
message_source("prior_adapter_omission_diagnosis", "702aa9f32eb845442b5994783066fec2a821ce14955464872b3923e823aaff9b")

docid = "f61d2ead943f3f0632d20ff16109269bf8e20ecd1105f7dac1a0d230f7b9bd67"
row = dict(conn.execute("select d.*,s.path,s.sha256 as raw_sha256 from documents d join sources s on d.source_id=s.id where d.id=?", (docid,)).fetchone())
assert sha(pathlib.Path(row["path"]).read_bytes()) == row["raw_sha256"]
text = row["text"]
sources.append(dict(id="chinese_source_locked_bridge", original_path=row["path"],
                    original_file_sha256=row["raw_sha256"], snapshot=pin(text.encode(), ".txt"),
                    sha256=sha(text.encode()), bytes=len(text.encode()), role="supplied research artifact; author not established here",
                    document_id=docid, database_source_id=row["source_id"],
                    boundary="Recovered artifact's conditional result and composition contract, not an independently rerun historical or mathematical proof."))
texts["chinese_source_locked_bridge"] = text
conn.close()

S = "initiating_concept_attachment"
excerpt("initial_two_purposes", S, "The purpose of sunny is primarily two-fold", turn=0)
excerpt("initial_continuity_purpose", S, "1. Solving our contextual continuity", turn=0)
excerpt("initial_typed_recognition", S, "2. Equipping ourselves", turn=0)
excerpt("assistant_initial_adjudication", S, "distinguish what is already established", turn=1)
excerpt("user_rejects_host_adjudication", S, "I DO NOT want you deciding", turn=2)
excerpt("clock_13_without_clock_redraw", S, "the hour is still the 13th hour", turn=4)
excerpt("assistant_rejects_known_geometry", S, "avoid presuming the final geometry", turn=5)
excerpt("user_assume_geometry_for_predictions", S, "ABSOLUTELY IMPERATIVE", turn=6)
excerpt("user_theory_testing_mission", S, "THIS is the purpose of SUNNY", turn=6)
excerpt("user_full_western_and_chinese", S, "It is Western Music AND Chinese music", turn=10)
excerpt("user_monochord_tol_adapter", S, "keplarian/fluddic monochord to TOL AB/BA", turn=10)
excerpt("assistant_recovers_bridge_dimension", S, "The Fludd–Kepler monochord", turn=11)
excerpt("user_three_restoration_goals", S, "1. rectify the correct zodiacal", turn=12,
        end="This is the only way")
excerpt("user_cascade_is_conditional", S, "if that theory holds water", turn=12)
excerpt("user_forensic_purpose", S, "assess ALL data", turn=14)
excerpt("user_prior_sequence_to_mature_progress", S, "the second is, once it reconstructs", turn=14)
excerpt("user_progressive_type_law", S, "progressively attained type law", turn=16)
excerpt("prior_phonetic_dimension", S, "phonetic realization", turn=13)

excerpt("native_assignment_build", "native_initiating_assignment", "Let's build SUNNY")
excerpt("native_assignment_twofold", "native_initiating_assignment", "2. Equipping ourselves")
excerpt("historical_holdout_music_only", "scoped_music_only_trial", "removing the the completed harmony")
excerpt("historical_holdout_trial_question", "scoped_music_only_trial", "THEN **forget**")
excerpt("historical_preserve_fkch_user_like_text", "historical_layer_preservation", "i want to keep our current",
        attribution="The archive's outer message is role=user, but this long pasted dialogue contains both user-like and assistant-like speech. The local sentence is user-like; independently normalized inner role is not established here.")
excerpt("historical_preserve_fkch_assistant_like_text", "historical_layer_preservation", "The new operator-first TOL work",
        attribution="Assistant-like reply embedded in an outer role=user source. It is a historical formulation, not a new direct user command.")
excerpt("historical_missing_adapter", "prior_adapter_omission_diagnosis", "did not execute the recovered recursive TOL constraints")
excerpt("historical_full_adapter_not_proven_unique", "prior_adapter_omission_diagnosis", "NOT ESTABLISHED")
excerpt("chinese_bridge_composition_contract", "chinese_source_locked_bridge", "Composition order.", end="Each musical unit")
excerpt("chinese_conditional_graph_not_ten_beings", "chinese_source_locked_bridge", "Result: conditional pass.", end="Plain-language reading.")

M = "adopted_mandate"
excerpt("mandate_full_music_bridges", M, "The Western and Chinese musical systems")
excerpt("mandate_working_axiom", M, "The existence of this complete structure")
excerpt("mandate_correction_scope", M, "A user's later correction")
excerpt("mandate_prediction_sufficient_reconstruction", M, "Once Mission I has produced")

C = "native_current_semantic_correction"
excerpt("current_actual_background_request", C, "I require background reconstruction", exact="I require background reconstruction to continue between turns.&#x20;")
excerpt("current_ophiuchus_no_presumed_slice", C, "not necessarily our position that Ophiuchus")
excerpt("current_parallel_forensics", C, "The main purpose centers around several hypothesis")
excerpt("current_common_geometry_native_hierarchies", C, "A meta-goal that could be considered")
excerpt("current_continue_mature_alignment", C, "Once arriving at the general point of progress")
excerpt("current_calendar_phonetic_outcomes", C, "Two of the more explicitly stated")
excerpt("current_negative_examples_language_priorities", C, "I believe that while the majority")
excerpt("current_jev_multiscale_director", C, "The entire point of utilizing Jev")
excerpt("current_strategy_options_request", C, "Observing your potential alight misalignments")

jev_path = ROOT / "docs/evidence/mission-semantics-superjev.json"
jev = json.loads(jev_path.read_text(encoding="utf-8-sig"))
request_path = ROOT / "docs/evidence/mission-semantics-jev-request.json"
request = json.loads(request_path.read_text(encoding="utf-8-sig"))
payload = {"model": request.get("model") or "jev-latest", "state": request["state"], "questions": request["questions"]}
canonical_request_sha256 = sha(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode())
assert canonical_request_sha256 == jev["request_sha256"]
assert jev["resolved_model"] == "jev-1.14.0"
assert jev["answers"]["semantic_review_route"]["winner"] == "parallel_tracks_with_scoped_bridge_rules"

review = dict(
    schema="sunny.mission-semantics-source-review.v1",
    created_utc=datetime.now(timezone.utc).isoformat(),
    status="source-reviewed draft for coordinator adoption; operational state not edited",
    current_governing_source="native_current_semantic_correction",
    source_accounting=dict(sources=len(sources), exact_spans=len(spans),
                           bounded_scope="Initiating eighteen-turn specification, native initiating/current user records, adopted mandate, selected bridge-history witnesses and one task-state snapshot; not exhaustive account reconstruction."),
    sources=sources, spans=spans,
    genealogy=[
        dict(id="G1", references=["initial_two_purposes", "initial_continuity_purpose", "initial_typed_recognition", "native_assignment_build"],
             interpretation="Jev both constructs and operates SUNNY; continuity serves a typed musical relational alignment/prediction system, not an inventory-only mission."),
        dict(id="G2", references=["assistant_initial_adjudication", "user_rejects_host_adjudication"],
             interpretation="The host's premature established/hypothetical adjudication was explicitly rejected during concept articulation. Preserve user axioms and Jev's assigned substantive role; separately account exact proof scope without replacing the mission with host ontology."),
        dict(id="G3", references=["assistant_rejects_known_geometry", "user_assume_geometry_for_predictions", "user_theory_testing_mission", "mandate_working_axiom"],
             interpretation="The complete geometry is SUNNY's adopted working axiom for conditional investigation. Exact realizations and successful general predictions remain work to derive; axiom use does not establish external physical truth."),
        dict(id="G4", references=["historical_holdout_music_only", "historical_holdout_trial_question", "historical_preserve_fkch_user_like_text", "user_full_western_and_chinese", "user_monochord_tol_adapter", "mandate_full_music_bridges"],
             interpretation="Music-only holdout was a scoped trial and past blind-method report. The retained full stack includes native Western AND Chinese music, Completed Harmony/Fludd–Kepler and TOL. Neither a universal bridge exclusion nor a permanent ban on ablations follows."),
        dict(id="G5", references=["user_three_restoration_goals", "user_cascade_is_conditional", "current_calendar_phonetic_outcomes", "current_negative_examples_language_priorities"],
             interpretation="Explicit outcomes involve historical/counterfactual calendar continuity and original symbol representation PLUS phonetic transmission. A symbol/sound correction cascading through other alignments remains the user's causal hypothesis, not an achieved result."),
        dict(id="G6", references=["user_forensic_purpose", "user_prior_sequence_to_mature_progress", "mandate_prediction_sufficient_reconstruction", "current_parallel_forensics", "current_continue_mature_alignment", "mandate_correction_scope"],
             interpretation="An earlier user really specified reconstruction to mature correlation followed by bigger predictions. The current correction refines that dependency: targeted parallel forensic recovery supports continued mature alignment, and exhaustive accounting is not a universal stop gate. Keep earlier wording and localized dependency requirements."),
        dict(id="G7", references=["clock_13_without_clock_redraw", "current_ophiuchus_no_presumed_slice"],
             interpretation="Ophiuchus treatment is an unresolved representational question: explicit, implicit, symbolic or counted in a way that adds no angular slice are possible. No thirteenth-sector requirement is authorized."),
        dict(id="G8", references=["current_common_geometry_native_hierarchies", "user_progressive_type_law", "current_jev_multiscale_director", "current_strategy_options_request", "current_actual_background_request"],
             interpretation="Continue source-native cross-system hierarchy alignment and derive type laws progressively. Jev directs the substantive route; present strategy alternatives. Actual background operation requires a real verified mechanism and cannot be inferred from a checkpoint or an agent's promise."),
    ],
    semantic_categories={
        "literal_current_requirements": ["Jev directs substantive investigation and is intrinsic to SUNNY.", "Continue mature cross-system alignment with parallel forensic restoration.", "Keep native Western and Chinese systems and their lawful bridges; identify precisely when a scoped holdout applies.", "Calendar counterfactuals and historical changes; original symbol representation AND phonetic transmission; Paleo-Hebrew/Aramaic/English first, Greek/Latin also.", "No presumption that Ophiuchus adds an angular sector.", "Offer strategic workflow alternatives and implement genuinely supported background continuation."],
        "adopted_working_axioms": ["Complete intended musical-geometric topology, systemic/generational wheels, two class rotations/lift, intended toroidal realization and tetrahedral Monad.", "Music as deterministic reference, with its complete native structures rather than scalar SUN alone."],
        "open_hypotheses": ["Cross-system common geometry can enable progressively distant deterministic predictions.", "Correct symbol/sound reconstruction may cause cascading resolution of other misalignments.", "Specific historical alterations, lost symbols/phonemes and hidden genealogical consequences are candidates to discriminate, not findings established by their inclusion in the user's quoted examples."],
        "research_strategies": ["Targeted pre-nomenclature forensic tracing; preserve both omitted and over-carried material.", "Blind music-only ablations, gap-aware investigations, native-hierarchy comparisons, invariant/residual and counterfactual-calendar tests.", "Oldest recoverable witness preference concerns historical investigation; no fixed numeric priority or identity collapse between traditions."],
    },
    bridge_contract=[
        dict(id="B1", rule="Retain the recovered full-stack pathway as available operating structure: native musical relations → Fludd/Kepler/Completed Harmony bridge → TOL relational adapter → source-native target interpretation. Western and Chinese constructions remain simultaneously available, not normalized into a scalar-only substitute.", references=["user_full_western_and_chinese", "user_monochord_tol_adapter", "chinese_bridge_composition_contract", "current_parallel_forensics"]),
        dict(id="B2", rule="A scoped music-only trial may withhold bridge/attribution inputs to generate independent consequences. Record included inputs, withheld edges/answers, prediction before target inspection, test locality and exact comparison/restoration boundary. Holding aside is an experimental view, not deletion of the bridge or prior results.", references=["historical_holdout_music_only", "historical_holdout_trial_question", "current_parallel_forensics"]),
        dict(id="B3", rule="Historical Fludd/Kepler/Completed Harmony–TOL and later operator-first constructions retain separate identities and histories; compare them without silently rewriting either.", references=["historical_preserve_fkch_user_like_text", "historical_preserve_fkch_assistant_like_text"]),
        dict(id="B4", rule="Distinguish intended architecture, source-artifact conditional passes and actually reproduced formulas. An incomplete scalar-only certificate cannot establish underdetermination of a fuller adapter it did not execute; neither may an intended adapter be declared a proven unique global solution.", references=["historical_missing_adapter", "historical_full_adapter_not_proven_unique", "chinese_conditional_graph_not_ten_beings"]),
    ],
    drift_findings=[
        dict(id="D1", status="directly documented assistant misread and user correction", issue="Concept articulation displaced by host epistemic adjudication.", references=["assistant_initial_adjudication", "user_rejects_host_adjudication"]),
        dict(id="D2", status="directly documented assistant misread and user correction", issue="Known-geometry working axiom weakened into an initial requirement not to presume it.", references=["assistant_rejects_known_geometry", "user_assume_geometry_for_predictions"]),
        dict(id="D3", status="direct user report of recurrent compression; assistant's later repair preserved", issue="Complete music reduced to particular scalar ratios, dropping Western/Chinese interaction and bridges.", references=["user_full_western_and_chinese", "user_monochord_tol_adapter", "assistant_recovers_bridge_dimension"]),
        dict(id="D4", status="current direct user correction; a prior assistant's adapter omission diagnosis is separately sourced", issue="Whole-history reconstruction/inventory treated as sole mission or universal prerequisite; current user restores its supporting forensic purpose.", references=["current_parallel_forensics", "current_continue_mature_alignment", "historical_missing_adapter"]),
        dict(id="D5", status="current direct user correction and recurrence prevention", issue="Goal labels can erase counterfactual calendar choices, original intended phonetic transmission, or the non-sector possibilities for Ophiuchus.", references=["current_calendar_phonetic_outcomes", "current_negative_examples_language_priorities", "current_ophiuchus_no_presumed_slice"]),
        dict(id="D6", status="not established as a specific deletion in this bounded review", issue="A scoped historical holdout must not be retroactively treated as a permanent exclusion. This review identifies the scope rule but does not prove which later source or input was deleted.", references=["historical_holdout_trial_question", "current_parallel_forensics"]),
    ],
    operational_state_semantics=dict(
        source="operational_task_snapshot",
        observation="The reviewed goal emphasized preserving continuity and deriving type laws through reconstruction; its next actions emphasized upper-transition and witness reconstruction. Those remain valid work but are narrower than the current user's explicit alignment/calendar/phonetic/parallel-track correction.",
        action="Coordinator should append/adopt the corrected mission and explicit outcome dependencies while preserving this hash-pinned prior state and all mathematical gains.",
        changed_here=False),
    jev=dict(request_path=str(request_path.relative_to(ROOT)).replace("\\", "/"),
             request_file_sha256=sha(request_path.read_bytes()), normalized_request_sha256=canonical_request_sha256,
             receipt_path=str(jev_path.relative_to(ROOT)).replace("\\", "/"),
             receipt_sha256=sha(jev_path.read_bytes()), resolved_model=jev["resolved_model"],
             winner=jev["answers"]["semantic_review_route"]["winner"],
             scope="Operational source-review route. Initial request recorded a parent attestation before the exact native current correction was recovered; source conclusions below now bind actual native text. Probability is not mathematical authority or calibrated domain truth."),
    memory=dict(retrieved_document_id="LBs64p1QE2Cn5zk2VjFigA", conversation_id="01a18f6c-9603-75ca-9edc-887906a97d98",
                caution="Automatic summary overstated musical operators and a Goetic join relative to the saved content. Exact content/source artifacts govern; a get_document success does not establish summary accuracy."),
    gaps=["The bounded sources do not independently normalize all speakers inside the long user-pasted historical conversation.",
          "Exact bridge AB/BA formulas, complete historical bindings and admissible global orientations are not re-derived by this semantic review.",
          "No original sacred phoneme set, hidden Biblical message, counterfactual present date or historical culprit is established here.",
          "The current user's long triple-quoted examples are proposed/negative research material; their claims of factual proof are not imported as verified results or plugin instructions.",
          "Background continuation implementation and strategy execution are coordinator-owned; no service or persistent child was started by this source review.",
          "This is an authored source review, not an independent audit of this agent's earlier hierarchy implementation."],
    protected_path_authorization="Read-only access to explicitly supplied attachment and known current native session to recover this assignment's initiating/current user instructions. No .codex configuration, memories, skills or originals were edited.",
)

exact_request_path = ROOT / "docs/evidence/mission-semantics-exact-source-jev-request.json"
exact_receipt_path = ROOT / "docs/evidence/mission-semantics-exact-source-superjev.json"
if exact_request_path.exists() and exact_receipt_path.exists():
    exact_request = json.loads(exact_request_path.read_text(encoding="utf-8-sig"))
    exact_receipt = json.loads(exact_receipt_path.read_text(encoding="utf-8-sig"))
    exact_payload = {"model": exact_request.get("model") or "jev-latest", "state": exact_request["state"], "questions": exact_request["questions"]}
    exact_digest = sha(json.dumps(exact_payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode())
    assert exact_receipt["status"] == "judged"
    assert exact_receipt["resolved_model"] == "jev-1.14.0"
    assert exact_receipt["request_sha256"] == exact_digest
    by_id = {s["id"]: s for s in spans}
    for selected in exact_request["state"]["source_spans"]:
        assert selected["exact_quote"] == by_id[selected["id"]]["exact_quote"]
        assert selected["source_role"] == by_id[selected["id"]]["source_role"]
        if by_id[selected["id"]].get("embedded_attribution"):
            assert selected["embedded_attribution"] == by_id[selected["id"]]["embedded_attribution"]
    review["source_bound_jev"] = dict(
        request_path=str(exact_request_path.relative_to(ROOT)).replace("\\", "/"),
        request_file_sha256=sha(exact_request_path.read_bytes()), normalized_request_sha256=exact_digest,
        receipt_path=str(exact_receipt_path.relative_to(ROOT)).replace("\\", "/"),
        receipt_sha256=sha(exact_receipt_path.read_bytes()), resolved_model=exact_receipt["resolved_model"],
        source_spans_verified=len(exact_request["state"]["source_spans"]), answers=exact_receipt["answers"],
        preliminary_report_reference=dict(sha256=exact_request["state"].get("source_review_sha256"),
            note="The inline-excerpt request was sent against an earlier draft before the separate continuity excerpt and this receipt binding were added. The twelve inline exact excerpts are preserved in the request and rechecked against source pins; the earlier whole-report draft is not separately retained. Do not describe its framing hash as the current report hash."),
        scope="Actual Jev directs operating mission, bridge experiment contract and outcome semantics using exact user/source excerpts and embedded-role warnings. Does not prove the universal theory or historical quoted examples.")
review["validation_history"] = [dict(
    outcome="Initial validator exited 1 on receipt hash assertion, corrected before acceptance.",
    cause="SuperJev hashes its normalized payload with model default and canonical JSON, not the raw request file bytes.",
    correction="Both raw-file hash and normalized-payload hash now retained; normalized digest matches the actual receipt. No source content was altered to make the check pass.")]

# Small, exact source validator; fails nonzero on any damaged pin, quote or role boundary.
for source in sources:
    data = (ROOT / source["snapshot"]).read_bytes()
    assert sha(data) == source["sha256"], source["id"]
    assert data.decode("utf-8-sig") == texts[source["id"]]
    if source.get("original_file_sha256"):
        assert sha(pathlib.Path(source["original_path"]).read_bytes()) == source["original_file_sha256"]
    if source.get("native_record_sha256"):
        assert sha((ROOT / source["native_record_snapshot"]).read_bytes()) == source["native_record_sha256"]
for span in spans:
    text = texts[span["source_id"]]
    actual = text[span["start_character"]:span["end_character_exclusive"]]
    assert actual == span["exact_quote"]
    assert sha(actual.encode()) == span["quote_sha256"]
assert sha(attachment.read_bytes()) == next(x["sha256"] for x in sources if x["id"] == S)
review["validation"] = dict(status="PASS", exit_code=0, source_snapshots_verified=len(sources),
                            exact_spans_verified=len(spans),
                            initiating_attachment_unchanged=True,
                            original_source_file_hashes_verified=sum(bool(x.get("original_file_sha256")) for x in sources),
                            native_initiating_role="user", current_native_role="user",
                            command="python -X utf8 scripts/review_mission_semantics.py",
                            limits="Checks source bytes, extracted-text pins, exact span positions/hashes and role boundaries; does not prove the proposed universal geometry or independently validate the cited historical/math assertions.")
OUT.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(dict(status="PASS", exit_code=0, sources=len(sources), spans=len(spans),
                      report=str(OUT.relative_to(ROOT)), sha256=sha(OUT.read_bytes())), ensure_ascii=False))
