"""Reproduce the new official-method audit and bind this scoped packet."""
from pathlib import Path
from datetime import datetime, timezone
from fractions import Fraction
from collections import Counter
import hashlib, importlib.util, json, math, re, sys, uuid
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
WORKSPACE=ROOT.parents[3]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding="utf-8-sig"))
def write(name,value): (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def now(): return datetime.now(timezone.utc).isoformat()
checks=[]
def check(name,ok,detail=None): checks.append({"check":name,"passed":bool(ok),"detail":detail})
html=(ROOT/"sources"/"praat_bada.html").read_text(encoding="utf8")
import html as htmlmodule
codes=[htmlmodule.unescape(re.sub("<[^>]+>","",x)).strip() for x in re.findall(r"<code>(.*?)</code>",html,re.S)]
loop=[500+Fraction(2500,9)*(i-1) for i in range(1,11)]
variant=[500+Fraction(2000,9)*(i-1) for i in range(1,11)]
f2points=[]
for line in codes:
 match=re.search(r"Add (formant|bandwidth) point:\s*2,\s*([0-9.]+),\s*(.+)",line)
 if match: f2points.append({"kind":match.group(1),"time_seconds":match.group(2),"value_expression":match.group(3)})
same_time=Counter((x["kind"],x["time_seconds"]) for x in f2points)
check("original_script_formula_present",any("f2_locus = 500 + (2500/9) * (i - 1)" in x for x in codes))
check("original_script_ten_steps_present",any(x=="for i from 1 to 10" for x in codes))
check("source_endpoint_mismatch_exact",loop[0]==500 and loop[-1]==3000 and "2500 Hz for [da]" in html)
check("source_count_mismatch", "in six steps" in html and len(loop)==10)
check("same_time_second_formant_points",same_time[("formant","0.05")]==2 and same_time[("bandwidth","0.05")]==2,f2points)
c=2*math.sqrt(6*math.log(2))/math.pi
bandwidth={str(T):c/T for T in [0.005,0.025,0.030]}
check("gaussian_bandwidth_rounding",round(bandwidth["0.025"],1)==51.9 and round(bandwidth["0.005"])==260 and round(bandwidth["0.03"])==43,bandwidth)
formant=(ROOT.parent/"symbols"/"sources"/"praat_formant.html")
check("reused_formant_source_conditions_present",all(x in formant.read_text(encoding="utf8") for x in ["0.025","0.050","25 percent","50 Hz"]))
audit={
 "schema":"sunny.western-official-method-audit.v1","created_utc":now(),
 "source":{"id":"W07","path":"sources/praat_bada.html","sha256":sha(ROOT/"sources"/"praat_bada.html")},
 "provenance":"RESEARCH_SUPPORTED_INFERENCE","execution":"Original official code inspected and its arithmetic reproduced locally with exact rational numbers. Praat was not installed or executed.",
 "observed_discrepancies":[
  {"id":"PRAAT-BADA-COUNT","source_prose":"six-step description","source_code":"loop1through10","finding":"Inconsistent count; no inferred intended revision."},
  {"id":"PRAAT-BADA-ENDPOINT","source_prose":"F2 endpoints500Hz and2500Hz","source_code_formula":"500+(2500/9)*(i-1)","exact_first_hz":str(loop[0]),"exact_last_hz":str(loop[-1]),"finding":"Code formula ends3000Hz,500Hz above prose endpoint."},
  {"id":"PRAAT-BADA-DUPLICATE-TIME","points":f2points,"finding":"Second-formant frequency and bandwidth each receive two points at0.05s. Effective point-insertion behavior remains unchecked; no overwritten-point claim."}
 ],
 "analyst_defined_variant":{"purpose":"Optional exact endpoint-conforming parameter list only; not attributed to original source intention and not executed synthesis.","formula":"500+(2000/9)*(i-1),i=1..10","exact_endpoints_hz":[str(variant[0]),str(variant[-1])],"retained":"Original source bytes remain unchanged; ten-step variant does not resolve source's six-step wording or duplicate times."},
 "window_contract":{"source":"W05,W06","gaussian_bandwidth_formula":"B(T)=2*sqrt(6*ln(2))/(pi*T)Hz,T in seconds","bandwidth_hz":bandwidth,"effective_formant_window_s":0.025,"actual_gaussian_duration_s":0.05,"automatic_formant_step_s":0.00625,"limit":"Step/bin density is not independent temporal samples or resolving bandwidth. Actual returned sampling can differ; no audio measured."},
 "pulse_unit_contract":{"source":"W08 pp88–89","conditional_translation":"For a declared stable adjacent localperiodP, two-pulse duration=2Pseconds. If adjacentF0=1/P is defined,2P=2/F0seconds;F0 during closure may be undefined.","limit":"Corpus-specific coding convention; not a universal cutoff or phonemic/historical test."},
 "status":"source discrepancies retained; conceptual method adopted conditionally"
}
write("method-audit.json",audit)
# The original14-question instrument is read from shared state and not modified.
mission=read(WORKSPACE/"state"/"mission.json")
official={x["id"]:x["question"] for x in mission["prior_art_research"]["p0_a_questions"]}
baseline=read(ROOT/"p0a-14-western.json")
for q in baseline["questions"]: q["question"]=official[q["id"]]
baseline["prior_art_reused"]=[
 "state/research/reactivation/symbols/p0a-14-baseline.json","state/mission.json:prior_art_research.p0_a_questions",
 "state/research/reactivation/western/checkpoint-01.json","state/research/reactivation/western/source-fetch-manifest.json",
 "state/research/reactivation/western/acoustic-reproduction.json","state/research/reactivation/western/exact-acoustic-check.json",
 "docs/reconstruction/symbol-sound-census/question-freeze.json","docs/reconstruction/symbol-sound-census/scholarly-first-pass.md"]
counts=dict(Counter(q["status"] for q in baseline["questions"]))
check("p0a14_ids_wording_counts",len(baseline["questions"])==14 and set(official)=={q["id"] for q in baseline["questions"]} and counts=={"covered_in_bounded_scope":7,"partial":6,"open":1},counts)
write("p0a-14-western.json",baseline)
# Verify all successfully retrieved original bodies against their preserved manifests.
source_checks=[]
for manifest in ["source-fetch-manifest.json","source-fetch-manifest-02.json"]:
 for row in read(ROOT/manifest):
  path=ROOT/row["local_path"] if row.get("local_path") else WORKSPACE/row["path"]
  if row.get("status") in ["retrieved",200]:
   source_checks.append({"path":str(path.relative_to(WORKSPACE)),"expected":row["sha256"],"actual":sha(path),"passed":sha(path)==row["sha256"]})
check("original_source_body_hashes",len(source_checks)==7 and all(x["passed"] for x in source_checks),source_checks)
source_register=read(ROOT/"source-register-02.json")
for s in source_register["sources"]:
 path=ROOT/s["local_path"]
 s["local_sha256"]=sha(path)
 if s["id"]=="W10": s["hash_scope"]="Access metadata JSON only; audio bodies not retrieved/hashed."
write("source-register-02.json",source_register)
# Check the two live model receipts against their exact canonical payloads.
superjev_path=Path('C:/Users/Brend/.codex/plugins/cache/created-by-me-remote/superjev/0.1.0/skills/superjev/scripts/superjev.py')
spec=importlib.util.spec_from_file_location('sunny_western_superjev_verify',superjev_path)
superjev=importlib.util.module_from_spec(spec);spec.loader.exec_module(superjev)
for name in ["operational-method","observation-route"]:
 req=read(ROOT/f"jev-{name}-request.json"); receipt=read(ROOT/f"jev-{name}-receipt.json")
 # Plugin canonical input digest covers normalized model/state/questions.
 canonical_digest=superjev.digest(superjev.validate_request(req))
 check(f"jev_{name}_canonical_request_binding",receipt.get("request_sha256")==canonical_digest,canonical_digest)
 check(f"jev_{name}_actual_model_receipt",receipt.get("status")=="judged" and receipt.get("network_calls")==1 and receipt.get("resolved_model")=="jev-1.14.0",{"request_sha256":receipt.get("request_sha256"),"resolved_model":receipt.get("resolved_model"),"network_calls":receipt.get("network_calls")})
# Retain exact source-body and local packet hashes in a narrow check record.
result={"schema":"sunny.western-packet-verification.v1","checked_utc":now(),"status":"passed" if all(x["passed"] for x in checks) else "failed","passed":sum(x["passed"] for x in checks),"total":len(checks),"checks":checks,
 "packet_hashes":{name:sha(ROOT/name) for name in ["source-register-02.json","operational-constraint.json","p0a-14-western.json","method-audit.json","paired-reading-access.json"]},
 "boundary":"Literal source/hash, exposed exact parameter arithmetic and bounded instrument/accounting checks. No measured audio, ancient sound, perceptual replication, full native musical completion, calibrated model truth or blind prediction."}
write("verification-02.json",result)
print(json.dumps({"status":result["status"],"passed":result["passed"],"total":result["total"]}))
if result["status"]!="passed": raise SystemExit(1)
