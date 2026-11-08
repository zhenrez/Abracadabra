"""Reconcile exact source contacts after publication; never certify semantic completion.

Use --dry-run for a read-only preview, or --apply after the coordinating agent has
published the stable derived model. Original input-preservation receipts and the
database are read-only inputs. Prior coverage outputs are retained by SHA-256.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE_MODULES = ("decisions", "music-geometry", "correspondences", "alignment", "tables")
MATH_MODULES = (
    "native-derivations", "native-execution", "orientation-predictions",
    "tol-history-math", "generational-constraints", "algebraic-extension",
    "derived-laws", "master-score",
    "hierarchy-atlas", "musical-hierarchies", "angelic-hierarchy-supplement", "hierarchy-atlas-combined",
)
TABLES = ("sources", "conversations", "messages", "nodes", "documents", "refs", "decisions", "search_index")
COVERAGE_PATH = "state/reconstruction/coverage.json"
DOC_PATH = "docs/reconstruction/COVERAGE.md"
INPUT_RECEIPT = "docs/evidence/mandate-input-preservation.json"
RECEIPT_PATH = "docs/evidence/continuation-coverage-reconciliation.json"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def load(path: Path):
    return json.loads(path.read_bytes().decode("utf-8-sig"))


def collect_exact_ids(value, message_ids: set[str], source_ids: set[str]):
    """Count exact string values, not substring matches or inferred source use."""
    mids, sids = set(), set()
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
        elif isinstance(item, str):
            if item in message_ids:
                mids.add(item)
            if item in source_ids:
                sids.add(item)
    return mids, sids


def reported_status(unit: dict) -> dict:
    keys = ("status", "unit_status", "canonicalPromotion", "globalCompleteness",
            "canonical_orientation_selected", "blind_prediction")
    return {key: unit[key] for key in keys if key in unit}


def current_path(root: Path, recorded: str) -> Path:
    path = Path(recorded)
    return path if path.is_absolute() else root / path


def plan_reconciliation(root: Path = ROOT):
    """Read a consistent DB census and explicit modules; return proposed bytes only."""
    root = root.resolve()
    prior_raw = (root / COVERAGE_PATH).read_bytes()
    prior_doc = (root / DOC_PATH).read_bytes()
    prior = json.loads(prior_raw.decode("utf-8-sig"))
    preservation = (root / INPUT_RECEIPT).read_bytes()
    connection = sqlite3.connect((root / "data/sunny.sqlite").as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("BEGIN")
        counts = {table: connection.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]
                  for table in TABLES}
        sources = {row["id"]: dict(row) for row in connection.execute("SELECT * FROM sources")}
        messages = {row["id"]: dict(row) for row in connection.execute(
            "SELECT id,source_id,role,content_sha256 FROM messages")}
        documents = [dict(row) for row in connection.execute("SELECT id,source_id FROM documents")]
        statistics = {
            "distinct_message_content_sha256": connection.execute(
                "SELECT COUNT(DISTINCT content_sha256) FROM messages").fetchone()[0],
            "message_roles": dict(connection.execute("SELECT role,COUNT(*) FROM messages GROUP BY role")),
            "source_statuses": dict(connection.execute("SELECT status,COUNT(*) FROM sources GROUP BY status")),
            "source_kinds": dict(connection.execute("SELECT kind,COUNT(*) FROM sources GROUP BY kind")),
        }
        database_coverage = [dict(row) for row in connection.execute("SELECT * FROM coverage")]
        foreign_keys = [list(row) for row in connection.execute("PRAGMA foreign_key_check")]
    finally:
        connection.close()

    refs, missing_math = {}, []
    all_mids, all_sids = set(), set()
    math_units = []
    message_ids, source_ids = set(messages), set(sources)
    for name in BASE_MODULES + MATH_MODULES:
        relative = "state/reconstruction/" + name + ".json"
        path = root / relative
        if not path.exists():
            if name in BASE_MODULES:
                raise ValueError("Required base module missing: " + relative)
            missing_math.append(relative)
            continue
        raw = path.read_bytes()
        data = json.loads(raw.decode("utf-8-sig"))
        mids, sids = collect_exact_ids(data, message_ids, source_ids)
        all_mids |= mids
        all_sids |= sids
        refs[name] = {
            "path": relative, "sha256": digest(raw),
            "kind": "base_source_reconstruction" if name in BASE_MODULES else "mathematical_execution_or_law",
            "distinct_message_ids_referenced": len(mids),
            "distinct_source_ids_referenced": len(sids),
            "message_ids": sorted(mids), "source_ids": sorted(sids),
        }
        if name in MATH_MODULES:
            math_units.append({
                "name": name, "unit": relative, "sha256": digest(raw),
                "source_message_contacts": len(mids), "source_occurrence_contacts": len(sids),
                "reported_status_fields": reported_status(data),
                "coverage_boundary": "Current artifact status and exact ID contact only; not a fresh proof audit or exhaustive semantic coverage certificate.",
            })

    by_source = defaultdict(list)
    for message in messages.values():
        by_source[message["source_id"]].append(message)
    source_rows = []
    for sid, source in sorted(sources.items()):
        rows = by_source[sid]
        source_rows.append({
            **source,
            "message_occurrences": len(rows),
            "roles": dict(Counter(message["role"] for message in rows)),
            "current_path_is_file": current_path(root, source["path"]).is_file(),
            "message_ids_referenced_by_reconstruction": sum(message["id"] in all_mids for message in rows),
            "module_source_reference_present": sid in all_sids,
            "semantic_complete": None,
            "semantic_complete_basis": "Exact references do not certify exhaustive semantic processing.",
        })

    prior_sources = {source["id"]: source for source in prior.get("sources", [])}
    added_sids = source_ids - set(prior_sources)
    removed_sids = set(prior_sources) - source_ids
    added_sources = [{"id": sid, "path": sources[sid]["path"], "kind": sources[sid].get("kind"),
                      "sha256": sources[sid]["sha256"],
                      "is_derived_reconstruction": sources[sid].get("kind") == "derived_current_model_reconstruction"}
                     for sid in sorted(added_sids)]
    new_source_documents = [document for document in documents if document["source_id"] in added_sids]
    old_counts = prior["counts"]
    delta = {table: counts[table] - old_counts[table] for table in TABLES}
    manifest = [[mid, messages[mid]["content_sha256"]] for mid in sorted(messages)]
    snapshot_refs = [
        {"path": "state/checkpoint-history/before-coverage-" + Path(relative).name + "-" + digest(raw) + ".snapshot",
         "sha256": digest(raw), "original_path": relative}
        for relative, raw in [(COVERAGE_PATH, prior_raw), (DOC_PATH, prior_doc)]
    ]
    reconciliation = {
        "prior_outputs": snapshot_refs, "prior_counts": old_counts, "current_counts": counts,
        "count_delta": delta, "added_source_occurrences": added_sources,
        "removed_source_ids": sorted(removed_sids),
        "document_projections_attached_to_added_sources": new_source_documents,
        "document_identity_boundary": "Previous coverage does not contain every document ID; this list covers documents attached to newly observed source IDs, not a complete document-ID change audit.",
        "current_message_id_content_manifest_sha256": digest(encoded(manifest)),
        "message_identity_boundary": "Current manifest is recorded for later comparison; equal message counts alone do not establish unchanged identities or contents.",
        "historical_comparison_boundary": "Prior checkpoint comparisons are preserved exactly as historical evidence, not relabeled as fresh comparisons against this census.",
    }
    current = dict(prior)
    current.update({
        "schema": "sunny.accountable-corpus-coverage.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "read_only_database": str(root / "data/sunny.sqlite"), "counts": counts,
        "projection_statistics": statistics,
        "reconstruction_module_references": refs,
        "continued_mathematical_reconstruction": math_units,
        "pending_mathematical_unit_artifacts": missing_math,
        "semantic_coverage": {
            "messages_with_exact_id_mentioned_in_current_modules": len(all_mids),
            "messages_without_such_module_id_reference": len(messages) - len(all_mids),
            "fully_semantically_processed_messages": None,
            "interpretation": "Exact complete string-ID mentions across the declared base and mathematical modules establish traceable contact only. No semantic completion percentage follows.",
            "unprocessed_or_untouched": "Unknown at whole-message level; no ID mention does not prove unread in other conversations.",
        },
        "database_coverage_rows": database_coverage, "sources": source_rows,
        "source_path_existence_check": {
            "present_files": sum(source["current_path_is_file"] for source in source_rows),
            "missing_files": [{"source_id": source["id"], "path": source["path"], "recorded_status": source.get("status")}
                              for source in source_rows if not source["current_path_is_file"]],
            "scope": "Current existence of each recorded occurrence path, not full-file digest verification or proof of historical retention.",
        },
        "current_reconciliation": reconciliation,
        "exact_id_contact_contract": {
            "included_base_modules": list(BASE_MODULES), "included_math_modules": list(MATH_MODULES),
            "excluded_recursive_inventories": ["coverage", "model"],
            "match_rule": "A JSON string value equals a current database message/source ID; object keys, substrings and filenames are not inferred as contacts.",
        },
        "input_preservation_receipt": {"path": INPUT_RECEIPT, "sha256": digest(preservation), "modified": False},
        "foreign_key_violations": foreign_keys,
    })
    registration_path=root/'docs/evidence/hierarchy-source-registration.json'
    if registration_path.exists():
        registration_raw=registration_path.read_bytes();registration=json.loads(registration_raw)
        current['registered_hierarchy_source_bindings']={
            'receipt':'docs/evidence/hierarchy-source-registration.json','sha256':digest(registration_raw),
            'bindings':registration['mapping'],
            'contract':'Graph source IDs map explicitly to database occurrences. These bindings are separate from literal-ID-contact counts and do not certify semantic completeness.'}
    # Preserve the original reported-count reconciliation unchanged. Its dated
    # comparison is distinct from the current census and count delta above.
    current["historical_exact_reconciliation"] = prior.get("historical_exact_reconciliation", prior.get("exact_reconciliation"))
    current["exact_reconciliation"] = {
        "reported_initial": prior.get("exact_reconciliation", {}).get("reported_initial", 59894),
        "current": counts["messages"],
        "current_search_index_identity_holds": counts["search_index"] == counts["messages"] + counts["documents"],
        "historical_reconciliation": "See historical_exact_reconciliation and preserved prior output.",
    }
    # No percentage is inferred from copies, table projections or ID contacts.
    history = list(prior.get("reconciliation_history", []))
    history.append({"reconciled_utc": current["created_utc"], "prior_outputs": snapshot_refs,
                    "prior_module_count": len(prior.get("reconstruction_module_references", {})),
                    "current_module_count": len(refs)})
    current["reconciliation_history"] = history

    derived_total = sum(source.get("kind") == "derived_current_model_reconstruction" for source in sources.values())
    derived_added = sum(source["is_derived_reconstruction"] for source in added_sources)
    contact = current["semantic_coverage"]
    lines = ["# Corpus coverage checkpoint", "",
             f"Current census: {counts['messages']:,} message/event source occurrences, {counts['documents']:,} document projections, {counts['sources']:,} source occurrences and {counts['conversations']:,} conversation occurrences.", "",
             f"The search index contains {counts['search_index']:,} projections: {counts['messages']:,} messages/events plus {counts['documents']:,} documents. The count identity is {'satisfied' if current['exact_reconciliation']['current_search_index_identity_holds'] else 'NOT satisfied'}; searchability is not semantic reconstruction.", "",
             f"The {len(refs)} currently present declared modules mention {len(all_mids):,} distinct database message IDs and {len(all_sids):,} source IDs. These are exact source contacts, not completed semantic cases. Full semantic processing remains unknown; {contact['messages_without_such_module_id_reference']:,} records have no exact message-ID mention under this declared test.", "",
             f"Current recorded source paths: {current['source_path_existence_check']['present_files']:,} present and {len(current['source_path_existence_check']['missing_files']):,} missing. Existence is checked by occurrence path; full source-file hashes are not recomputed by this census.", "",
             "## Change from the preserved previous coverage", "",
             f"Sources {delta['sources']:+,}; documents {delta['documents']:+,}; messages/events {delta['messages']:+,}; search projections {delta['search_index']:+,}.", "",
             f"There are {derived_total:,} source occurrences tagged as derived current-model reconstructions; {derived_added:,} of the newly observed sources carry that tag. They are editorial reconstruction documents, not native user messages or independent corroboration. Document IDs linked to newly added source IDs are enumerated in the machine register; the older coverage lacks a full document-ID baseline.", "",
             "Prior coverage JSON and this document are retained by SHA-256 before replacement. Earlier database checkpoint comparisons remain historical evidence. Equal message counts alone do not prove unchanged identities or contents; a current ID/content manifest is recorded for future comparison.", "",
             "## Continued mathematical units", ""]
    for unit in math_units:
        status = json.dumps(unit["reported_status_fields"], ensure_ascii=False, sort_keys=True)
        lines.append(f"- {unit['name']}: `{unit['sha256']}`; {unit['source_message_contacts']} message-ID contacts, {unit['source_occurrence_contacts']} source-ID contacts; artifact reports {status}.")
    for pending in missing_math:
        lines.append("- Pending artifact: " + pending + ".")
    lines += ["", "The preceding statuses are artifact reports with exact hashes, not fresh mathematical audits or whole-source completion certificates.", "",
              "## Input preservation and scope", "",
              f"The existing input-preservation receipt is unchanged, SHA-256 `{digest(preservation)}`. Its retained input/source-role/Q6 evidence is preserved; this reconciliation does not regenerate it or reopen image-access experiments.", "",
              "Coverage/model inventories are excluded from contact counting to prevent recursive self-inflation. Occurrence histories, earlier comparison evidence and explicit acquisition gaps remain in the machine register. Whole live-account coverage, exhaustive semantic reconstruction, global orientation and Mission I completion are not established.", "",
              "Machine register: state/reconstruction/coverage.json. Reconciliation receipt: docs/evidence/continuation-coverage-reconciliation.json.", ""]
    doc_raw = "\n".join(lines).encode("utf-8")
    proposed = {COVERAGE_PATH: encoded(current), DOC_PATH: doc_raw}
    receipt = {
        "schema": "sunny.coverage-reconciliation.v1", "created_utc": current["created_utc"],
        "method_receipt": "docs/evidence/continuation-coverage-design-jev-result.json",
        "database_read_only": True, "database_counts": counts,
        "prior_outputs": snapshot_refs,
        "outputs": [{"path": path, "sha256": digest(raw)} for path, raw in proposed.items()],
        "input_preservation_receipt": current["input_preservation_receipt"],
        "module_revisions": [{"name": name, "path": ref["path"], "sha256": ref["sha256"]} for name, ref in refs.items()],
        "module_count": len(refs), "math_unit_count": len(math_units),
        "pending_math_units": missing_math,
        "message_contacts": len(all_mids), "source_contacts": len(all_sids),
        "semantic_completion": None, "current_reconciliation": reconciliation,
        "scope": "Census, occurrence paths and exact module-ID contacts only. No native source or mathematical module mutation; no whole-account, semantic, proof or MissionI completion claim.",
    }
    return {"proposed": proposed, "receipt": receipt,
            "prior_bytes": {COVERAGE_PATH: prior_raw, DOC_PATH: prior_doc},
            "input_receipt_bytes": preservation}


def atomic_write(path: Path, raw: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".coverage-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def apply_reconciliation(plan: dict, root: Path = ROOT):
    root = root.resolve()
    receipt = plan["receipt"]
    if (root / INPUT_RECEIPT).read_bytes() != plan["input_receipt_bytes"]:
        raise ValueError("Input-preservation receipt changed after read; no outputs written")
    for path, raw in plan["prior_bytes"].items():
        if (root / path).read_bytes() != raw:
            raise ValueError("Coverage output changed after read: " + path)
    for ref in receipt["module_revisions"]:
        if digest((root / ref["path"]).read_bytes()) != ref["sha256"]:
            raise ValueError("Referenced module changed after read: " + ref["path"])
    for relative in receipt["pending_math_units"]:
        if (root / relative).exists():
            raise ValueError("Pending mathematical module appeared after read: " + relative)
    for ref in receipt["prior_outputs"]:
        raw = plan["prior_bytes"][ref["original_path"]]
        target = root / ref["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if target.read_bytes() != raw:
                raise ValueError("Prior-output snapshot collision")
        else:
            with target.open("xb") as handle:
                handle.write(raw)
    previous_receipt = root / RECEIPT_PATH
    if previous_receipt.exists():
        raw = previous_receipt.read_bytes()
        saved = root / "state/checkpoint-history" / ("before-coverage-receipt-" + digest(raw) + ".snapshot")
        if saved.exists() and saved.read_bytes() != raw:
            raise ValueError("Prior receipt snapshot collision")
        if not saved.exists():
            with saved.open("xb") as handle:
                handle.write(raw)
    for path, raw in plan["proposed"].items():
        atomic_write(root / path, raw)
    if (root / INPUT_RECEIPT).read_bytes() != plan["input_receipt_bytes"]:
        raise ValueError("Input-preservation receipt changed concurrently; reconciliation is not accepted")
    for ref in receipt["outputs"]:
        if digest((root / ref["path"]).read_bytes()) != ref["sha256"]:
            raise ValueError("Written coverage output hash mismatch")
    receipt["input_preservation_unchanged_verified"] = True
    receipt["structured_exit_code"] = 0
    atomic_write(root / RECEIPT_PATH, encoded(receipt))
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="read-only preview; write no files")
    mode.add_argument("--apply", action="store_true", help="apply only after stable publication")
    args = parser.parse_args()
    planned = plan_reconciliation()
    result = apply_reconciliation(planned) if args.apply else planned["receipt"]
    print(json.dumps({
        "status": "applied" if args.apply else "dry_run", "exit_code": 0,
        "database_read_only": True, "counts": result["database_counts"],
        "modules": result["module_count"], "math_units": result["math_unit_count"],
        "pending_math_units": result["pending_math_units"],
        "message_contacts": result["message_contacts"], "source_contacts": result["source_contacts"],
        "semantic_completion": None, "input_receipt_sha256": result["input_preservation_receipt"]["sha256"],
        "writes": [*planned["proposed"], RECEIPT_PATH] if args.apply else [],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
