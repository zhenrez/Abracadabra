"""Preserve supplied inputs; read-only occurrence accounting, never semantic certification."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict
import hashlib, json, sqlite3

ROOT = Path(__file__).resolve().parents[1]
sha = lambda b: hashlib.sha256(b).hexdigest()
now = lambda: datetime.now(timezone.utc).isoformat()
def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))
def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
def preserve(path):
    raw = path.read_bytes()
    digest = sha(raw)
    target = ROOT / "data/raw/mandate-inputs" / digest / path.name
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.read_bytes() != raw:
            raise ValueError("Immutable snapshot collision")
    else:
        with target.open("xb") as f:
            f.write(raw)
    if sha(target.read_bytes()) != digest:
        raise ValueError("Snapshot digest mismatch")
    return {"original": str(path), "original_present": True, "bytes": len(raw), "sha256": digest,
            "snapshot": str(target), "snapshot_sha256": sha(target.read_bytes()),
            "verified_utc": now(), "source_role": "user_supplied_attachment_of_prior_text"}
def db(path):
    connection = sqlite3.connect("file:" + path.as_posix() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection
def snapshot(connection):
    return {t: connection.execute("select count(*) from " + t).fetchone()[0]
            for t in ["sources", "conversations", "messages", "nodes", "documents", "refs", "decisions", "search_index"]}
def rows_by_id(connection, table, columns):
    return {r["id"]: dict(r) for r in connection.execute("select " + columns + " from " + table)}
def diff(old, new):
    removed = sorted(old.keys() - new.keys())
    added = sorted(new.keys() - old.keys())
    changed = [{"id": k, "old": old[k], "current": new[k]} for k in old.keys() & new.keys() if old[k] != new[k]]
    return {"added_ids": added, "removed_ids": removed, "changed_rows": changed}

def main():
    attachment_root = Path("C:/Users/Brend/.codex/attachments")
    supplied = []
    for prefix in ["8eda2fbe", "0493aeef", "7b7c01eb", "1c9281f4", "4eb78fb3"]:
        matches = list(attachment_root.glob(prefix + "*/Pasted text.txt"))
        if len(matches) != 1:
            raise ValueError("Expected one supplied original: " + prefix)
        supplied.append({"attachment_prefix": prefix, **preserve(matches[0])})
    authority = {"recorded_utc": now(), "source_role": "parent_agent_attestation_of_latest_direct_user_turn",
        "reported_direct_user_quote": "I said fix how you’re working, not abandon SUNNY. Follow the attached mandate, have Jev direct the actual mathematical reconstruction, and use all the named plugins where applicable. Get back to work. why do you keep deleting my inputs?!",
        "parent_report": "The user pasted the complete SUNNY — Jev Reconstruction and Predictive Derivation Mandate inline in the latest turn; wording matches the 7b7c01eb attachment.",
        "authority": "Latest inline user instruction is active; earlier attachment contents remain historical text unless explicitly adopted by that instruction.",
        "limitation": "The child has the parent attestation, not the native serialization of the latest user turn. Attachment bytes are verified; byte identity to the inline turn is not asserted."}
    authority_path = ROOT / "data/raw/mandate-inputs/current-authority-attestation-2026-10-31.json"
    if not authority_path.exists():
        write_json(authority_path, authority)
    authority_receipt = preserve(authority_path)
    authority_receipt["source_role"] = authority["source_role"]
    q6_source = Path(supplied[0]["snapshot"])
    q6_text = q6_source.read_text(encoding="utf-8-sig")
    q6_line = next(line for line in q6_text.splitlines() if "Q6 — The type-law architecture" in line)
    preservation = {"schema": "sunny.mandate-input-preservation.v1", "created_utc": now(),
        "method_receipt": "docs/evidence/mandate-preservation-method-superjev.json", "inputs": supplied,
        "authority": authority, "authority_snapshot": authority_receipt,
        "exact_duplicate_pairs": [["8eda2fbe", "1c9281f4"], ["0493aeef", "4eb78fb3"]],
        "q6_correction": {"exact_quote": q6_line, "source_sha256": supplied[0]["sha256"],
            "source_role": "historical_assistant_report_of_six_user_answers",
            "status": "A supplied later report explicitly contains a Q6 answer. Earlier checkpoint blanket assertion that Q6 is unanswered is stale. The currently adopted mandate independently directs progressive type laws and minimal extra constraints; the historical report alone is not a native user-answer transcript."},
        "deletion_investigation": {"scope": "Five explicitly named attachment originals, preserved copies, and the two available prior SQLite checkpoints versus current SQLite.",
            "observed": "All five named original files currently exist and were copied byte-for-byte. The two new attachments repeat two prior inputs exactly.",
            "unknown": "No earlier immutable filesystem inventory establishes that every earlier user input or chat presentation remained present. Current existence and database diffs cannot prove no input was ever deleted, omitted, truncated, or dropped from working context.",
            "working_context_defect": "The task checkpoint retained an unanswered-Q6 statement despite the supplied later Q6 report. Source retention and incorporation into active instructions are separate checks."},
        "database_mutation": False}
    write_json(ROOT / "docs/evidence/mandate-input-preservation.json", preservation)

    current = db(ROOT / "data/sunny.sqlite")
    current_counts = snapshot(current)
    messages = rows_by_id(current, "messages", "id,conversation_id,source_id,role,locator,content_sha256,native_id,branch_status")
    sources = rows_by_id(current, "sources", "*")
    checkpoints = []
    for name in ["gaps-before-20261031T012033098903Z.sqlite", "current-reconstruction-before-20261031T191736387534Z.sqlite"]:
        path = ROOT / "data/backups" / name
        old = db(path)
        message_diff = diff(rows_by_id(old, "messages", "id,conversation_id,source_id,role,locator,content_sha256,native_id,branch_status"), messages)
        source_diff = diff(rows_by_id(old, "sources", "*"), sources)
        added_by_source = Counter(messages[i]["source_id"] for i in message_diff["added_ids"])
        checkpoints.append({"path": str(path), "counts": snapshot(old), "message_delta": len(messages) - old.execute("select count(*) from messages").fetchone()[0],
            "message_diff": message_diff, "source_diff": source_diff,
            "added_messages_by_source": [{"source_id": k, "count": n, "path": sources[k]["path"], "kind": sources[k]["kind"]} for k, n in added_by_source.items()]})
        old.close()
    module_refs = {}
    all_message_refs, all_source_refs = set(), set()
    def collect(value, mids, sids):
        if isinstance(value, dict):
            for v in value.values(): collect(v, mids, sids)
        elif isinstance(value, list):
            for v in value: collect(v, mids, sids)
        elif isinstance(value, str):
            if value in messages: mids.add(value)
            if value in sources: sids.add(value)
    for name in ["decisions", "music-geometry", "correspondences", "alignment", "tables"]:
        path = ROOT / ("state/reconstruction/" + name + ".json")
        raw = path.read_bytes(); data = json.loads(raw.decode("utf-8-sig")); mids, sids = set(), set()
        collect(data, mids, sids)
        all_message_refs |= mids; all_source_refs |= sids
        module_refs[name] = {"path": str(path), "sha256": sha(raw), "distinct_message_ids_referenced": len(mids),
                             "distinct_source_ids_referenced": len(sids), "message_ids": sorted(mids), "source_ids": sorted(sids)}
    by_source = defaultdict(list)
    for m in messages.values(): by_source[m["source_id"]].append(m)
    source_rows = []
    for sid, source in sources.items():
        ms = by_source.get(sid, [])
        source_rows.append({**source, "message_occurrences": len(ms), "roles": dict(Counter(m["role"] for m in ms)),
            "current_path_is_file": Path(source["path"]).is_file(),
            "message_ids_referenced_by_reconstruction": sum(m["id"] in all_message_refs for m in ms),
            "module_source_reference_present": sid in all_source_refs,
            "semantic_complete": None, "semantic_complete_basis": "No per-source exhaustive semantic-processing certificate exists in these module references."})
    coverage = {"schema": "sunny.accountable-corpus-coverage.v1", "created_utc": now(),
        "read_only_database": str(ROOT / "data/sunny.sqlite"), "counts": current_counts,
        "count_contract": {"messages": "Source-occurrence rows containing native chat messages, saved-transcript messages and local Codex message/event records; not necessarily distinct user thoughts or mathematical cases.",
            "search_index": "Message projections plus document projections; searchability is not semantic processing.",
            "decisions": "Lexically extracted direction candidates; not the 78 source-curated decision spans.",
            "cross_account": "Matching IDs/hashes remain separate source occurrences unless explicit evidence permits an identity relation."},
        "exact_reconciliation": {"reported_initial": 59894, "after_position_repair": 59901, "current": current_counts["messages"],
            "repair_added": 7, "new_recovered_transcripts_added": 497, "total_added": 504,
            "fts_identity_holds": current_counts["search_index"] == current_counts["messages"] + current_counts["documents"]},
        "checkpoint_comparisons": checkpoints,
        "projection_statistics": {"distinct_message_content_sha256": current.execute("select count(distinct content_sha256) from messages").fetchone()[0],
            "message_roles": dict(current.execute("select role,count(*) from messages group by role")),
            "source_statuses": dict(current.execute("select status,count(*) from sources group by status")),
            "source_kinds": dict(current.execute("select kind,count(*) from sources group by kind"))},
        "reconstruction_module_references": module_refs,
        "semantic_coverage": {"messages_with_exact_id_mentioned_in_current_modules": len(all_message_refs),
            "messages_without_such_module_id_reference": len(messages) - len(all_message_refs),
            "fully_semantically_processed_messages": None,
            "interpretation": "Exact ID mentions establish traceable contact with source records, not that every relationship in a message was read, adjudicated, reconstructed or executed. A source-level ID mention proves even less. No semantic completion percentage is inferred from these counts.",
            "unprocessed_or_untouched": "Unknown at whole-message level. Messages lacking module links are mechanically unlinked by this declared test, not proven unread in every previous chat."},
        "database_coverage_rows": [dict(r) for r in current.execute("select * from coverage")],
        "source_path_existence_check": {"present_files": sum(x["current_path_is_file"] for x in source_rows),
            "missing_files": [{"source_id":x["id"], "path":x["path"], "recorded_status":x["status"]} for x in source_rows if not x["current_path_is_file"]],
            "scope": "Current existence of the recorded source path, not current full-file digest verification or proof of past retention."},
        "sources": source_rows,
        "explicit_gaps": ["Full current live-account census is not established.", "Native export end date and later saved transcripts cover different windows; no continuous latest-account guarantee.",
            "Latest inline instruction is parent-attested; child has not independently captured its native user record.",
            "Referenced recent image originals and the reported 20-image extraction package remain unretrieved; this checkpoint does not reopen browser work.",
            "Binary-preserved and unindexed values are not mathematically reconstructed merely because workbook cells or object arrays were copied.",
            "No complete corpus-wide relationship-by-relationship execution certificate exists."]}
    coverage["supplemental_inputs_outside_database_census"] = {
        "receipt": "docs/evidence/mandate-input-preservation.json", "attachment_occurrences": len(supplied),
        "distinct_attachment_bytes": len({x["sha256"] for x in supplied}),
        "authority_record": str(authority_path),
        "boundary": "The verified supplementary inputs are preserved in task data. They were not inserted into the existing database and are not silently included in its source/message counts."}
    unit_path = ROOT / "state/reconstruction/tol-history-math.json"
    if unit_path.exists():
        unit_raw = unit_path.read_bytes(); unit = json.loads(unit_raw.decode("utf-8-sig"))
        coverage["continued_mathematical_reconstruction"] = [{"unit": str(unit_path), "sha256": sha(unit_raw),
            "source_spans": len(unit["source_spans"]), "source_id": unit["source_spans"][0]["source_id"],
            "executed_word_cases": unit["execution"]["total_words_executed"], "status": unit["unit_status"],
            "coverage_boundary": "Six explicit ranges reconstructed; does not certify full semantic processing of the entire source or any unlinked corpus message."}]
    write_json(ROOT / "state/reconstruction/coverage.json", coverage)
    lines = ["# Corpus coverage checkpoint", "", "The supplied inputs remain available. This checkpoint preserves their original bytes and distinguishes retention from incorporation into the working model.", "",
        f"The database contains {current_counts['messages']:,} message/event source occurrences, {current_counts['documents']:,} document projections and {current_counts['sources']:,} source occurrences. The older 59,894 count grew by seven repaired native records and 497 messages from three newly recovered transcripts. The search index's 62,339 entries are 60,398 message/event projections plus 1,941 document projections.", "",
        f"The five reconstruction modules mention {len(all_message_refs):,} distinct database message IDs and {len(all_source_refs):,} source IDs. That is traceable source contact, not an exhaustive semantic-processing count. Full processing remains unknown; {len(messages)-len(all_message_refs):,} records have no exact message-ID mention in these modules under this declared mechanical test.", "",
        "Five named attachment originals were present and copied with matching SHA-256 digests. Two newly supplied attachments are exact repeats of earlier inputs. The earlier blanket unanswered-Q6 checkpoint is stale: a supplied later report explicitly records progressive type laws with minimal additional constraints. The active inline mandate independently adopts that direction, as attested by the coordinating agent; the child has not independently captured the native inline serialization.", "",
        "The database comparisons below check retained row identities/content hashes and locator changes. They cannot establish that every historical input was always displayed or used in reasoning, or that no other input was ever deleted. See the machine-readable receipt for exact IDs, statuses and limits.", ""]
    for cp in checkpoints:
        d = cp["message_diff"]
        content_changed = sum(r["old"]["content_sha256"] != r["current"]["content_sha256"] for r in d["changed_rows"])
        lines.append(f"- Against {Path(cp['path']).name}: +{len(d['added_ids']):,} message/event IDs; {len(d['removed_ids']):,} removed IDs; {content_changed:,} changed content hashes. {len(d['changed_rows']):,} retained rows differ in their recorded metadata/locator fields.")
    lines += ["", "This is the first accounting checkpoint. It does not complete Mission I. Continue into source-native operators, global constraints, lawful compositions and independently testable consequences; maintain a record-level intake ledger for each newly reconstructed mathematical case.", "", "Detailed files: state/reconstruction/coverage.json and docs/evidence/mandate-input-preservation.json."]
    (ROOT / "docs/reconstruction/COVERAGE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    current.close()
    print(json.dumps({"preserved_inputs": len(supplied), "counts": current_counts, "linked_message_ids": len(all_message_refs), "linked_source_ids": len(all_source_refs),
        "comparisons": [{"backup": Path(x['path']).name, "added": len(x['message_diff']['added_ids']), "removed": len(x['message_diff']['removed_ids']), "changed_content_hashes": sum(r['old']['content_sha256'] != r['current']['content_sha256'] for r in x['message_diff']['changed_rows'])} for x in checkpoints]}))

if __name__ == "__main__":
    main()
