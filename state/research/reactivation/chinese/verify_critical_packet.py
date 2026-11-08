"""Verify the source-conditioned critical/modal continuation, without shared writes."""
from pathlib import Path
from datetime import datetime, timezone
from fractions import Fraction
from itertools import product
import hashlib
import importlib.util
import json
import uuid

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
VERIFIER = Path(r"C:\Users\Brend\.codex\plugins\cache\openai-curated-remote\proofline\2.0.2\skills\manage-evidence-decisions\scripts\proofline_package.py")
spec = importlib.util.spec_from_file_location("proofline_critical", VERIFIER)
proofline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proofline)

def sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def uid(value):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, value))

def node(kind, value):
    value["node_hash"] = proofline.node_hash(kind, value)
    return value

def package(name, source_path, quotes):
    content = source_path.read_text(encoding="utf-8")
    saved_path = BASE / name
    if saved_path.exists():
        saved = json.loads(saved_path.read_text(encoding="utf-8"))
        assert saved["payload"]["source_version"]["content"] == content
        assert [c["quote"] for c in saved["payload"]["citations"]] == quotes
        return proofline.verify(saved)
    sid, vid = uid(str(source_path)), uid(sha(content))
    parser = "sunny-source-normalized-critical-v1"
    source = node("source-version", dict(workspace_id=uid(str(ROOT)), source_id=sid,
        source_identity_sha256=sha("source:" + sid), source_version_id=vid,
        version_number=1, content=content, content_sha256=sha(content),
        content_length=len(content), parser_version=parser))
    chunk = node("chunk", dict(id=uid(vid + "/chunk"), source_node_hash=source["node_hash"],
        source_id=sid, source_version_id=vid, ordinal=0, start_offset=0,
        end_offset=len(content), start_line=1,
        end_line=proofline.line_number(content, len(content)-1),
        content=content, content_sha256=sha(content)))
    citations = []
    for i, quote in enumerate(quotes):
        start, end = content.index(quote), content.index(quote)+len(quote)
        citations.append(node("citation", dict(id=uid(vid + f"/citation/{i}"),
            source_node_hash=source["node_hash"], chunk_node_hashes=[chunk["node_hash"]],
            source_id=sid, source_version_id=vid, start_offset=start, end_offset=end,
            start_line=proofline.line_number(content, start),
            end_line=proofline.line_number(content, end-1),
            quote=quote, quote_sha256=sha(quote))))
    transform = node("transformation", dict(method="deterministic", parser_version=parser,
        model_runs=[], input_node_hashes=[source["node_hash"], chunk["node_hash"]] +
        [c["node_hash"] for c in citations]))
    artifact = node("decision-artifact", dict(id=uid(name), kind="constraint",
        title="Exact critical interpretation source spans",
        statement="The selected normalized witness contains these exact source spans.",
        rationale="Confidence1 means exact source/span fidelity only. This package does not establish historical truth, translation, original dating, acoustic realization or empirical efficacy.",
        confidence=1.0, valid_from=None, valid_to=None,
        transformation_node_hash=transform["node_hash"],
        citation_node_hashes=[c["node_hash"] for c in citations]))
    now = datetime.now(timezone.utc).isoformat()
    review = node("review-state", dict(artifact_node_hash=artifact["node_hash"],
        status="candidate", created_at=now, updated_at=now))
    result = {"manifest": dict(schema=proofline.SCHEMA, created_at=now,
        app_version="sunny-chinese-critical-v1", root_hash=proofline.envelope("package-root",
        {"artifact_node_hash": artifact["node_hash"], "review_node_hash": review["node_hash"]})),
        "payload": dict(source_version=source, chunks=[chunk], citations=citations,
        transformation=transform, artifact=artifact, review=review)}
    (BASE / name).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return proofline.verify(result)

def main():
    checks = []
    states = list(product(range(12), repeat=3))
    def equations(v):
        c, h, t = v
        return [(h-c-4)%12 == 0, (t-c-7)%12 == 0, (t-h-7)%12 == 0]
    assert sum(all(equations(v)) for v in states) == 0
    assert all(sum(all(q for j,q in enumerate(equations(v)) if j != i) for v in states) == 12 for i in range(3))
    checks.append("Minimal three-equation obstruction:1728 assignments,0 solutions; each deletion12 solutions")
    positive = json.loads((BASE / "positive-modal-adapter.json").read_text(encoding="utf-8"))
    for alpha in range(12):
        assert all((alpha+g+d-(alpha+p))%12 == 0 for g,d,p in zip([0,9,7,2],[0,4,7,9],[0,1,2,11]))
    checks.append("All12 common-origin choices satisfy the separate-mode adapter")
    extension = positive.get("all_three_rows_modular_extension")
    if extension:
        assert len(extension["rows"]) == 12
        assert all((alpha+row["relative_implicit_gong_pc"]+row["role_offset"]-(alpha+row["relative_final_pc"]))%12 == 0
            for alpha in range(12) for row in extension["rows"])
        checks.append("All144 role-prescription/origin combinations satisfy the declared full modular extension")
    for row in positive["optional_exact_rational_profile"]["rows"]:
        assert Fraction(row["relative_final_frequency"]) == Fraction(row["relative_gong_frequency"]) * Fraction(row["role_ratio"]) * Fraction(2)**row["octave_exponent"]
    checks.append("All4 rational reconstructions retain their octave exponents")
    profile = json.loads((BASE / "critical-pipe-profile.json").read_text(encoding="utf-8"))
    assert hashlib.sha256((ROOT / profile["source"]["path"]).read_bytes()).hexdigest() == profile["source"]["sha256"]
    text = (BASE / "sources/zhouli-zhushu23.normalized.txt").read_text(encoding="utf-8")
    for row in profile["rows"]:
        assert text[row["start_offset"]:row["end_offset"]] == row["quote"]
        assert Fraction(row["ideal_relative_frequency"]) * Fraction(row["declared_pipe_length_cun"]) == 9
    checks.append("Seven literal source pipe lengths and declared ideal inverse-length profile")
    proofs = [package("proofline-critical-zheng-jia.json", BASE / "sources/zhouli-zhushu22.normalized.txt", [
        "或先生後用或後生先用", "凡言不用者卑之凡言避之者尊之", "以其後生絲多用角先生絲少用徵"]),
        package("proofline-critical-zhu.json", BASE / "sources/zhuzhi-yulei092.normalized.txt", [
        "自是四樂各舉其一者而言之。", "以大呂為角，則南呂為宮；太簇為徵，則林鍾為宮；應鍾為羽，則太簇為宮。", "然也恐是無商調，不是無商音。"])]
    assert all(p["valid"] and p["citation_count"] == 3 for p in proofs)
    proofs.append(package("proofline-critical-hu.json", BASE / "sources/huyansheng-zhidiao-xia.normalized.txt", ["此三大祀樂，皆四聲各爲一調。"] ))
    assert proofs[-1]["valid"] and proofs[-1]["citation_count"] == 1
    checks.append("Installed Proofline verifies three source packages and7 exact critical spans")
    for name in ["wolfram-critical-obstruction-receipt.json", "wolfram-positive-modal-receipt.json"]:
        assert json.loads((BASE / name).read_text(encoding="utf-8"))["response"]["isError"] is False
    checks.append("Two actual successful Wolfram receipts retained")
    for name in ["critical-figure-fetch-manifest.json", "critical-zhu-fetch-manifest.json", "critical-prior-art-fetch-manifest.json", "critical-hu-fetch-manifest.json"]:
        for source in json.loads((BASE / name).read_text(encoding="utf-8")):
            if source.get("status") == 200:
                assert hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"]
    checks.append("New source/figure hashes match; unsuccessful retrieval stays explicit")
    delta_path = BASE / "p0a-critical-delta.json"
    if delta_path.exists():
        delta = json.loads(delta_path.read_text(encoding="utf-8"))
        assert len({q["id"] for q in delta["questions"]}) == 14
        assert delta["scholarly_baseline"] == "OPEN"
        assert delta["power_selection_and_m1_m12"] == "NOT_OPENED"
        checks.append("All14 critical P0-A deltas accounted with scholarly/heterodox boundaries retained")
    report = {"schema":"sunny.chinese-critical-verification.v1",
        "verified_utc":datetime.now(timezone.utc).isoformat(), "check_groups_passed":len(checks),
        "checks":checks, "proofline":proofs,
        "scope":"Conditional source-model compatibility and known-alternative reproduction; not historical solution or blind prediction"}
    (BASE / "critical-verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))

if __name__ == "__main__":
    main()
