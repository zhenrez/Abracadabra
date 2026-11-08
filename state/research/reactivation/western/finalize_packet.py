"""Finalize only the assigned Western packet, preserving the prior checkpoint."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json,re,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
WORKSPACE=ROOT.parents[3]
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
previous=read(ROOT/"checkpoint-02.json")
# Validate the previous prefixes/statuses before inferring completion percentages.
percents=[int(x["step"].split("%] ",1)[0].lstrip("[")) for x in previous["plan"]]
assert len(percents)==5 and all(0<=x<=100 for x in percents) and sum(0<x<100 for x in percents)==1
for x,p in zip(previous["plan"],percents):
 assert (x["status"]=="complete" and p==100) or (x["status"]=="pending" and p==0) or (x["status"]=="in_progress" and 0<p<100)
superjev_path=Path("C:/Users/Brend/.codex/plugins/cache/created-by-me-remote/superjev/0.1.0/skills/superjev/scripts/superjev.py")
spec=importlib.util.spec_from_file_location("west_final_superjev",superjev_path)
superjev=importlib.util.module_from_spec(spec);spec.loader.exec_module(superjev)
bindings=[]
for name in ["operational-method","observation-route","handoff"]:
 req=read(ROOT/f"jev-{name}-request.json");rec=read(ROOT/f"jev-{name}-receipt.json")
 digest=superjev.digest(superjev.validate_request(req))
 assert rec["request_sha256"]==digest and rec["status"]=="judged" and rec["resolved_model"]=="jev-1.14.0" and rec["network_calls"]==1
 bindings.append({"request":f"jev-{name}-request.json","receipt":f"jev-{name}-receipt.json","canonical_request_sha256":digest,"resolved_model":rec["resolved_model"],"network_calls":rec["network_calls"]})
verification=read(ROOT/"verification-02.json")
assert verification["status"]=="passed" and verification["passed"]==13
for path,digest in verification["packet_hashes"].items():assert sha(ROOT/path)==digest,path
proof=read(ROOT/"proofline-result-02.json");might=read(ROOT/"mightshape-result-02.json")
assert proof["exit_code"]==0 and proof["result"]["valid"]
assert might["exit_code"]==0 and might["result"]["firewall"]=="PASS" and might["result"]["record_count"]==4
report=WORKSPACE/"docs/research/reactivation-western.md"
missing=[]
for link in re.findall(r"\]\(([^)]+)\)",report.read_text(encoding="utf8")):
 if "://" not in link and not (report.parent/link).resolve().is_file():missing.append(link)
assert not missing,missing
json_count=0
for path in ROOT.glob("*.json"):read(path);json_count+=1
plugin_use={
 "schema":"sunny.western-plugin-use.v1","created_utc":datetime.now(timezone.utc).isoformat(),
 "actual":[
  {"plugin":"SuperJev","role":"coordination/research route and handoff","status":"3actual live cloud calls","model":"jev-1.14.0","receipts":bindings,"boundary":"Directions are conditional preferences; no source-truth or completion probability."},
  {"plugin":"Proofline2.0.2","role":"exact review-record/span/hash fidelity","status":"actual bundled verifier exit0,validtrue","result":"proofline-result-02.json","boundary":"Unsigned candidate. No authenticity, historical truth, signature, trusted timestamp or complete source review."},
  {"plugin":"MightShape1.0.1","role":"supported evidence-provenance checker","status":"actual bundled checker exit0,PASS4records","result":"mightshape-result-02.json","boundary":"Repeated-source and zero direct-participant warnings retained. No synthetic Council or invented participants."}
 ],
 "method_applied":[
  {"plugin":"HUMMBL Operations0.1.0","skill":"work-triage","role":"Now/Next/Later/Resolve with actual dependencies and owners","runtime":"No separate runtime or external task-system write."},
  {"plugin":"Web Research Assistant0.1.0","role":"targeted primary-source search, claim/applicability register, direct citations","runtime":"Skill method and native web retrieval used; no separate scholarly-search backend claimed."},
  {"plugin":"ScholarResearch1.1.0 find-sources","role":"concept blocks/terminology and backward source chaining","runtime":"Installed method read/applied; no standalone research backend invoked."}
 ],
 "unavailable_or_not_executed":[
  {"plugin":"AgentJev Decisions","status":"Actual health/info returned connection refused127.0.0.1:8149","evidence":"plugin-attempts-02.json","boundary":"No service launched; cloud model kept distinct from local0.6B."},
  {"plugin":"Supermemory","status":"Actual continuity search tool unavailable","evidence":"plugin-attempts-02.json","boundary":"Verified local source-bound continuity used; no remote save or local durable memory edit claimed."},
  {"plugin":"Wolfram","status":"Actual Context and LanguageEvaluator both unavailable","evidence":"math-plugin-attempts-02.json","boundary":"Exact parameter arithmetic executed locally; no remote Wolfram verification claimed."},
  {"plugin":"AgentProof","status":"Installed skill/contracts and original historical receipt inspected only; no fresh capture/verify","boundary":"Supported workflow requires a fixed request path outside this worker's assigned write scope. No child, installation, Git baseline or alternate capture route attempted. Historical2events both exit1;checkedfilecount0 is not a current source check."}
 ],
 "native_plan":"No native plan tool exposed; scoped checkpoints carry validated percentage prefixes. SharedPLAN.md unchanged.",
 "local_execution_note":"A handoff preview initially hit Windows stdout encoding; explicit PythonUTF8 yielded a zero-network preview then a successful live receipt. No probabilities invented on failure.",
 "protected_path_validation":"Installed .codex skill/scripts were read or executed as instructed; no credential inspection, plugin source edit, memory edit or global setting change. Python-B used for guard/finalization imports."
}
write(ROOT/"plugin-use-02.json",plugin_use)
names=["source-register-02.json","operational-constraint.json","p0a-14-western.json","query-log-02.json","method-audit.json","paired-reading-access.json","verification-02.json","proofline-package-02.json","proofline-result-02.json","mightshape-input-02.json","mightshape-result-02.json","plugin-use-02.json","jev-operational-method-request.json","jev-operational-method-receipt.json","jev-observation-route-request.json","jev-observation-route-receipt.json","jev-handoff-request.json","jev-handoff-receipt.json"]
integrity={"schema":"sunny.western-final-integrity.v1","checked_utc":datetime.now(timezone.utc).isoformat(),"status":"passed","validated_json_file_count":json_count,"local_report_links_missing":missing,"canonical_live_receipt_bindings":bindings,"packet_hashes":{x:sha(ROOT/x) for x in names},"human_report":{"path":"docs/research/reactivation-western.md","sha256":sha(report)},"verification":{"passed":13,"total":13},"proofline_valid":True,"mightshape_firewall":"PASS","limits":"Current record/hash/link/receipt consistency only. This is a bounded source-method packet; audio observation and full SUNNY remain unfinished."}
write(ROOT/"final-integrity-02.json",integrity)
plan=[]
for item in previous["plan"]:
 text=item["step"].split("%] ",1)[1]
 plan.append({"step":"[100%] "+text,"status":"complete"})
checkpoint={"schema":"sunny.western-reactivation.checkpoint.v3","created_utc":datetime.now(timezone.utc).isoformat(),"scope":"Bounded assigned packet ready for root; complete does not mark SUNNY, allnative music or the prospective acoustic observation complete.","prior_checkpoint":{"path":"checkpoint-02.json","sha256":sha(ROOT/"checkpoint-02.json")},"plan":plan,"delivered":["docs/research/reactivation-western.md",*names,"final-integrity-02.json"],"findings":["Exact source-qualified Genesis1.1 Alef roles and prospective same-profile reading/melody comparison bound.","Primary speech-analysis/glottal-event methods and exact parameter/transfer limitations registered.","Three original official-method code/prose discrepancies retained and arithmetic audited."],"unperformed":["Audio decoding/listening/alignment/measurement","Ancient pronunciation/intention reconstruction","FullnativeWestern/Chinese repertoire/operation reconstruction","NewM1–M12,blind prediction or downstream hierarchy/calendar rectification"],"next":"Root independently reviews and integrates only the source-qualified conditional constraint, then pursues decoder/token-alignment and native prescription/chronology dependencies.","source_independence":"Repeated Praat and Khan/OBP source ancestry retained; model votes are not corroborating evidence.","verification":"final-integrity-02.json","owned_scope":"Only state/research/reactivation/western and docs/research/reactivation-western.md authored. No shared task/model/runtime/checkpoint state changed."}
write(ROOT/"checkpoint-03.json",checkpoint)
print(json.dumps({"status":"passed","json_files_validated":json_count,"receipt_bindings":len(bindings),"source_parameter_checks":13,"proofline_valid":True,"mightshape":"PASS","human_report":str(report)},ensure_ascii=True))
