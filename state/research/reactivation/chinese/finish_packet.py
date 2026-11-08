"""Finish this bounded Chinese packet; all writes stay beside this script."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
CLIENT = Path(r"C:\Users\Brend\.codex\plugins\cache\created-by-me-remote\superjev\0.1.0\skills\superjev\scripts\superjev.py")
PROOFLINE = Path(r"C:\Users\Brend\.codex\plugins\cache\openai-curated-remote\proofline\2.0.2\skills\manage-evidence-decisions\scripts\proofline_package.py")

def read_json(name):
    return json.loads((BASE / name).read_text(encoding="utf-8"))

def run_jev():
    receipt = BASE / "jev-handoff-next-receipt.json"
    if receipt.exists() and json.loads(receipt.read_text(encoding="utf-8")).get("status") == "judged":
        return json.loads(receipt.read_text(encoding="utf-8"))
    for phase, extra in [("preview-utf8", []), ("receipt", ["--live"])]:
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(CLIENT), "decide", "--input",
             str(BASE / "jev-handoff-next-request.json"), *extra],
            capture_output=True, text=True, encoding="utf-8", timeout=25,
        )
        (BASE / f"jev-handoff-next-{phase}.json").write_text(result.stdout, encoding="utf-8")
        if result.stderr:
            (BASE / f"jev-handoff-next-{phase}.stderr.txt").write_text(result.stderr, encoding="utf-8")
        parsed = json.loads(result.stdout)
        required = "preview" if phase == "preview-utf8" else "judged"
        if result.returncode != 0 or parsed.get("status") != required:
            raise RuntimeError(f"Jev {phase}: {parsed.get('status')}")
    return parsed

def verify_packet():
    results = []
    for path in BASE.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    results.append("All owned JSON files parse")
    relation = read_json("native-role-relation.json")
    content = (BASE / "sources/zhouli-zhushu22.normalized.txt").read_text(encoding="utf-8")
    assert all(relation["checks"].values())
    for case in relation["cases"]:
        assert content[case["start_offset"]:case["end_offset"]] == case["quote"]
        assert hashlib.sha256(case["quote"].encode()).hexdigest() == case["quote_sha256"]
    results.append("Five native relation checks and all three exact source spans")
    control = read_json("register-transfer-control.json")
    assert [p % 12 for p in control["unfolded_T_minus2"]] == [p % 12 for p in control["source_scoped_playable_lift"]]
    assert control["source_scoped_playable_lift"][1] - control["source_scoped_playable_lift"][0] == -10
    results.append("Pitch-class equality and directed register interval")
    p0 = read_json("p0a-baseline.json")
    assert len(p0["p0_a_questions"]) == 14
    assert len({q["id"] for q in p0["p0_a_questions"]}) == 14
    assert p0["domain_complete"] is False
    assert p0["m1_m12"].startswith("NOT_OPENED")
    results.append("All14 P0-A questions accounted; wider baseline remains open")
    for source in read_json("reused-source-register.json"):
        assert hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"]
    for source in read_json("source-fetch-manifest.json"):
        assert hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"]
    results.append("Three reused source hashes and new source hash match")
    proof = subprocess.run(
        [sys.executable, "-X", "utf8", str(PROOFLINE), "verify", str(BASE / "proofline-source-spans.json")],
        capture_output=True, text=True, encoding="utf-8", timeout=15,
    )
    assert proof.returncode == 0, proof.stderr
    proof_result = json.loads(proof.stdout)
    assert proof_result["valid"] is True and proof_result["citation_count"] == 3
    results.append("Fresh installed Proofline verification:3 citations, valid")
    assert read_json("wolfram-register-control-receipt.json")["response"]["isError"] is False
    assert read_json("supermemory-search-receipt.json")["isError"] is False
    results.append("Actual successful Wolfram and Supermemory receipts retained")
    saved = read_json("supermemory-checkpoint-request.json")["content"]
    returned = read_json("supermemory-checkpoint-readback.json")["structuredContent"]["document"]
    assert returned["content"] == saved and returned["contentTruncated"] is False
    assert returned["status"] == "done"
    results.append("Supermemory checkpoint saved and full content read back")
    return results, proof_result

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    jev = run_jev()
    checks, proof = verify_packet()
    report = {
        "schema": "sunny.chinese-packet-verification.v1",
        "verified_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "check_groups_passed": len(checks),
        "proofline": proof,
        "jev": {"status": jev["status"], "model": jev["resolved_model"], "answers": jev["answers"]},
        "scope": "Bounded source/control packet only; no historical sound restoration or full SUNNY completion",
        "readable_document": {
            "path": "docs/research/reactivation-chinese.md",
            "sha256": hashlib.sha256((ROOT / "docs/research/reactivation-chinese.md").read_bytes()).hexdigest(),
        },
        "artifact_hashes": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in BASE.iterdir() if p.is_file() and p.name != "packet-verification.json"
        },
    }
    (BASE / "packet-verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"passed_groups": len(checks), "jev": report["jev"]}, ensure_ascii=False))
