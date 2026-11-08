"""Reproduce the four-locus extraction OFFLINE from retained source bytes.

Run from anywhere: python -X utf8 <this-file>
No model inference, HTTP requests, source edits, or phonetic measurements.
"""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import re
import unicodedata as U
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
SUN = HERE.parents[3]
SNAPSHOT = SUN / "docs/reconstruction/symbol-sound-census/six-alef-loci.json"
SYMBOLS = SUN / "state/research/reactivation/symbols"
TARGETS = [
    ("Gen.43.26", "uxlc-gen43-26-range.xml", "ויביאו"),
    ("Ezra.8.18", "uxlc-ezra8-18-range.xml", "ויביאו"),
    ("Lev.23.17", "uxlc-lev23-17-range.xml", "תביאו"),
    ("Job.33.21", "uxlc-job33-21-range.xml", "ראו"),
]
REMOVED_FOR_COMPARISON = "/ \u05c0\u05c3"

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def rel(path):
    return path.relative_to(SUN).as_posix()

def cps(text):
    return [{"character": ch, "codepoint": f"U+{ord(ch):04X}",
             "name": U.name(ch, "UNNAMED"), "category": U.category(ch)}
            for ch in text]

def alefs(text):
    result = []
    for i, ch in enumerate(text):
        if ch != "א":
            continue
        end = i + 1
        while end < len(text) and U.category(text[end]).startswith("M"):
            end += 1
        cluster = text[i:end]
        result.append({"index_codepoints_zero_based": i, "text": cluster,
                       "codepoints": cps(cluster), "contains_u05bc": "\u05bc" in cluster,
                       "contains_u05c4": "\u05c4" in cluster,
                       "contains_u05c5": "\u05c5" in cluster,
                       "contains_u05bd": "\u05bd" in cluster})
    return result

def comparison_text(token):
    # This is an explicit edition-format comparison, never a phonetic transform.
    return "".join(ch for ch in token if ch not in REMOVED_FOR_COMPARISON)

def consonants(token):
    return "".join(ch for ch in token if "\u05d0" <= ch <= "\u05ea")

def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def run():
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8-sig"))
    retained = {}
    for book in snapshot["books"]:
        for row in book["rows"]:
            retained[row["verse"]] = (book, row)
    receipts = json.loads((HERE / "retrieval-corrected.json").read_text(encoding="utf-8"))
    by_filename = {Path(r["path"]).name: r for r in receipts if "path" in r}
    rows = []
    checks = []
    for verse, filename, expected_consonants in TARGETS:
        path = HERE / "sources" / filename
        raw = path.read_bytes()
        receipt = by_filename[filename]
        assert digest(path) == receipt["sha256"], (verse, "capture hash mismatch")
        tree = ET.fromstring(raw)
        assert tree.tag == "Tanach", (verse, "not a publisher Tanach record")
        verses = tree.findall("./tanach/book/c/v")
        assert len(verses) == 1, (verse, "expected exactly one requested verse")
        v = verses[0]
        chapter = tree.find("./tanach/book/c")
        assert verse.split(".")[1:] == [chapter.attrib["n"], v.attrib["n"]]
        target = [(i, node) for i, node in enumerate(v) if node.tag in ("w", "q", "k")
                  and consonants("".join(node.itertext())) == expected_consonants]
        assert len(target) == 1, (verse, "lexical target ambiguous or absent")
        child_index, node = target[0]
        token = "".join(node.itertext())
        encoded = token.encode("utf-8")
        spans = [m for m in re.finditer(rb"<w>(.*?)</w>", raw, flags=re.S)
                 if m.group(1) == encoded]
        assert len(spans) == 1, (verse, "target raw-byte span ambiguous")
        span = spans[0].span(1)
        assert raw[span[0]:span[1]].decode("utf-8") == token
        cluster = alefs(token)
        assert len(cluster) == 1, (verse, "lexical target must have exactly one Alef")
        book, old_row = retained[verse]
        assert len(old_row["marked"]) == 1
        old = old_row["marked"][0]["token"]
        old_clusters = alefs(old)
        mark_agreement = [a["text"] for a in cluster] == [a["text"] for a in old_clusters]
        fmt_agreement = comparison_text(old) == comparison_text(token)
        same_tag_ordinal = sum(1 for sibling in list(v)[:child_index + 1] if sibling.tag == node.tag)
        xpath = f"/Tanach/tanach/book/c[@n='{chapter.attrib['n']}']/v[@n='{v.attrib['n']}']/{node.tag}[{same_tag_ordinal}]"
        edition = tree.find("./teiHeader/fileDesc/editionStmt/edition")
        version = {e.tag: e.text for e in edition}
        apparatus = [{"element": e.tag, "text": "".join(e.itertext()),
                      "target": e is node} for e in v if e.tag in ("q", "k")]
        rows.append({
            "locus": verse, "source": {"path": rel(path), "sha256": digest(path),
                "url": receipt["requested_url"], "edition": version,
                "capture_utc": receipt["attempted_utc"], "xpath": xpath,
                "token_byte_span_zero_based_half_open": list(span)},
            "token": token, "token_utf8_sha256": sha256(encoded).hexdigest(),
            "codepoints": cps(token), "alef_clusters": cluster,
            "verse_apparatus": apparatus,
            "retained_wlc_snapshot": {"path": rel(SNAPSHOT), "sha256": digest(SNAPSHOT),
                "commit": snapshot["commit"], "original_book_url": book["url"],
                "reported_original_book_sha256": book["sha256"],
                "original_book_bytes_retrieved_in_this_unit": False,
                "token": old, "attributes": old_row["marked"][0]["attributes"],
                "alef_clusters": old_clusters, "codepoints": cps(old)},
            "comparison": {"raw_token_equal": token == old,
                "alef_cluster_equal": mark_agreement,
                "equal_after_declared_format_filter": fmt_agreement,
                "filter_removes_only": cps(REMOVED_FOR_COMPARISON),
                "uxlc_omitted_by_filter": cps("".join(c for c in token if c in REMOVED_FOR_COMPARISON)),
                "snapshot_omitted_by_filter": cps("".join(c for c in old if c in REMOVED_FOR_COMPARISON))},
        })
        checks.append({"locus": verse, "source_hash_recomputed": True,
                       "exact_requested_verse": True, "one_lexical_target": True,
                       "raw_byte_span_replayed": True,
                       "alef_mark_is_u05bc": cluster[0]["contains_u05bc"],
                       "u05c4_u05c5_not_substituted": not (cluster[0]["contains_u05c4"] or cluster[0]["contains_u05c5"]),
                       "retained_alef_cluster_agrees": mark_agreement,
                       "declared_format_comparison_agrees": fmt_agreement})
    marked_count = sum(r["alef_clusters"][0]["contains_u05bc"] for r in rows)
    cluster_agreement_count = sum(r["comparison"]["alef_cluster_equal"] for r in rows)
    raw_difference_count = sum(not r["comparison"]["raw_token_equal"] for r in rows)
    # A raw encoding contrast within an already requested verse, not an acoustic
    # matched control and not a new corpus or source-context census.
    control_path = HERE / "sources" / "uxlc-gen43-26-range.xml"
    control_raw = control_path.read_bytes()
    control_tree = ET.fromstring(control_raw)
    control_nodes = [e for e in control_tree.findall("./tanach/book/c/v/w")
                     if consonants("".join(e.itertext())) == "את"]
    assert len(control_nodes) == 1
    control_token = "".join(control_nodes[0].itertext())
    control_spans = [m.span(1) for m in re.finditer(rb"<w>(.*?)</w>", control_raw, re.S)
                     if m.group(1) == control_token.encode("utf-8")]
    assert len(control_spans) == 1
    encoding_control = {"locus": "Gen.43.26", "xpath": "/Tanach/tanach/book/c[@n='43']/v[@n='26']/w[6]",
        "source_path": rel(control_path), "source_sha256": digest(control_path),
        "token": control_token, "codepoints": cps(control_token),
        "token_byte_span_zero_based_half_open": list(control_spans[0]),
        "alef_clusters": alefs(control_token),
        "observation": "Same verse has Alef plus U+05B6 SEGOL without U+05BC. Presence of a combining mark alone does not identify a dagesh-or-mapiq encoding.",
        "scope_limit": "Encoding contrast only: different lexical/morphological contexts; no matched acoustic or historical-pronunciation inference."}
    khan_pdf = SYMBOLS / "sources/khan2020.pdf"
    khan_sha = digest(khan_pdf)
    assert khan_sha == "bcab644037f62795041c3c6e6e37f1c1eb28f29d147b6d2c4409fd6bc3c0da24"
    khan_images = []
    for printed in range(140, 145):
        path = (HERE if printed == 141 else SYMBOLS) / f"sources/khan2020-printed{printed}.png"
        khan_images.append({"printed_page": printed, "pdf_page_one_based": printed + 17,
                            "path": rel(path), "sha256": digest(path), "visually_inspected": True})
    write_json(HERE / "khan-page-evidence.json", {"pdf": rel(khan_pdf), "pdf_sha256": khan_sha,
        "pages": khan_images,
        "render_141_method": "pypdfium2 PdfDocument(pdf)[157].render(scale=1.35).to_pil().save(output)",
        "limit": "Author's printed page images, including reproduced BL Or2552 excerpt; not direct Leningrad facsimiles or full Karaite manuscript audit."})
    result = {
        "schema": "sunny.alef-witness-raw-token-test.v1",
        "scope": "Exactly four directed verse records; no corpus census or acoustic experiment.",
        "result": f"{marked_count}/4 current publisher Alef clusters contain U+05BC; {cluster_agreement_count}/4 agree with the retained pinned WLC-derived token snapshot. {raw_difference_count}/4 full token strings differ. Differences are retained, not suppressed or used to force agreement.",
        "direction": {"request": rel(SYMBOLS / "jev-next-native-question-v2-request.json"),
            "request_sha256": digest(SYMBOLS / "jev-next-native-question-v2-request.json"),
            "receipt": rel(SYMBOLS / "jev-next-native-question-v2-receipt.json"),
            "receipt_sha256": digest(SYMBOLS / "jev-next-native-question-v2-receipt.json"),
            "retained_winner": "tiberian_context", "retained_probability": 0.61,
            "retained_model": "jev-1.14.0", "new_model_calls_in_this_unit": 0,
            "account_billing_attribution": "UNVERIFIED"},
        "rows": rows,
        "same_verse_encoding_control": encoding_control,
        "limits": [
            "UXLC and the retained morphhb WLC snapshot descend from Leningrad transcription work; agreement is not two independent ancient manuscripts.",
            "The second comparison input is the retained commit-labeled token snapshot. Its original full-book bytes were not newly retrieved or independently hash-verified in this unit.",
            "U+05BC is named HEBREW POINT DAGESH OR MAPIQ. The codepoint does not decide whether the point signified gemination or consonantal realization.",
            "Job's Alef cluster also includes U+05BD METEG. U+05C4 upper and U+05C5 lower dots are not interchangeable with U+05BC.",
            "Khan's reproduced BL Or2552 excerpt, his scholarly Hebrew print, the Leningrad manuscript and Aleppo/Baghdad/Yemen reading traditions are different source layers.",
            "No direct Leningrad four-token facsimile inspection, full BL Or2552 shadda-distribution audit, recording, exact duration, ratio, frequency, musical interval or ancient-sound determination is claimed.",
            "No blind prediction: all four loci and the Khan interpretation were already exposed.",
        ],
    }
    write_json(HERE / "token-comparison.json", result)
    failed_first_attempts = []
    for receipt in json.loads((HERE / "retrieval.json").read_text(encoding="utf-8")):
        path = HERE / receipt["path"]
        if "Server.xml error" in path.read_text(encoding="utf-8"):
            failed_first_attempts.append({"id": receipt["id"], "http_status": receipt["status"],
                "semantic_result": "publisher citation-format error document, not scripture",
                "sha256": digest(path), "path": rel(path)})
    assert len(failed_first_attempts) == 4
    verification = {"schema": "sunny.alef-witness-verification.v1",
        "verified_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed_with_explicit_scope_limits" if all(all(v for k, v in check.items() if k != "locus") for check in checks) else "completed_with_observed_differences_requiring_review",
        "target_count": len(rows),
        "checks": checks, "initial_http_200_error_documents": failed_first_attempts,
        "source_xml_total_bytes": sum((HERE / "sources" / x[1]).stat().st_size for x in TARGETS),
        "token_comparison_sha256": digest(HERE / "token-comparison.json"),
        "khan_page_evidence_sha256": digest(HERE / "khan-page-evidence.json"),
        "readable_report_sha256": digest(SUN / "docs/research/ALEF_WITNESS_TEST.md"),
        "protected_user_memory_writes": 0, "live_model_calls": 0,
        "background_processes_launched": 0,
        "plugin_use": {"SuperJev_0.1.3": "Installed coordinator/verification skills applied; existing direction receipt reused; no inference.",
                       "Riqor_0.2.5": "Installed documentation verification and skeptical evidence methods applied locally; no delegated or remote specialist runtime.",
                       "Supermemory": "Continuity supplied by root's prior retrieved checkpoint; this unit neither saved nor rewrote durable memory."},
    }
    write_json(HERE / "verification.json", verification)
    for row in rows:
        cluster = row["alef_clusters"][0]
        print(row["locus"], row["token"], " ".join(x["codepoint"] for x in cluster["codepoints"]),
              "mark_agreement=" + str(row["comparison"]["alef_cluster_equal"]))
    print("VERIFIED", len(checks), "target extractions;", verification["source_xml_total_bytes"], "publisher XML bytes")

if __name__ == "__main__":
    run()
