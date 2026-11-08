"""Bounded reliability regressions; fixtures are not scientific progress or live Jev."""
import importlib.util,json,os,subprocess,tempfile,time,unittest
from datetime import datetime,timezone
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("background_reliability",ROOT/"scripts/background_reconstruction.py")
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
STATE=ROOT/"state/background/reactivation-20261102"
class BackgroundReliability(unittest.TestCase):
 def setUp(self):
  parent=STATE/"support-tests";parent.mkdir(parents=True,exist_ok=True)
  self.temp=tempfile.TemporaryDirectory(dir=parent);self.base=Path(self.temp.name)
 def tearDown(self):self.temp.cleanup()
 def test_touching_completed_artifact_does_not_renew_progress(self):
  run=self.base/"runs"/"known-result";run.mkdir(parents=True)
  p=run/"result.json"
  p.write_text(json.dumps({"status":"candidate_source_reconstruction","completed_utc":datetime.fromtimestamp(1000,timezone.utc).isoformat(),"source_records":[{"proofline":{"valid":True}}]}))
  os.utime(p,(1700,1700))
  forecast=w.forecast_cadence(self.base,4,20,1700)
  self.assertEqual(forecast["seconds_since_completion"],700)
  self.assertEqual(forecast["alert"],"completion overdue")
 def test_empty_queue_is_explicit_blocker_not_meaningful_heartbeat(self):
  with patch.object(w,"BASE",self.base):
   w.supervise(self.base,poll=1,lease=60,once=True)
  self.assertTrue((self.base/"blocker.json").is_file(),"An idle owned worker must flag its exact empty-queue blocker.")
  first=w.load(self.base/"blocker.json");progress=w.load(self.base/"cadence.json")
  self.assertTrue(first["active"]);self.assertEqual(first["id"],"empty_eligible_queue")
  self.assertEqual(progress["completed_result_count"],0)
  with patch.object(w,"BASE",self.base):
   w.supervise(self.base,poll=1,lease=60,once=True)
  second=w.load(self.base/"blocker.json");again=w.load(self.base/"cadence.json")
  self.assertEqual(first["raised_utc"],second["raised_utc"])
  self.assertEqual(progress["last_meaningful_action_utc"],again["last_meaningful_action_utc"])
 def test_expired_lease_is_explicit_and_never_renewed(self):
  w.save(self.base/"lease.json",{"started_utc":datetime.fromtimestamp(1,timezone.utc).isoformat(),"deadline_unix":2})
  with patch.object(w,"BASE",self.base):w.supervise(self.base,poll=1,lease=86400,once=True)
  self.assertEqual(w.load(self.base/"lease.json")["deadline_unix"],2)
  self.assertTrue((self.base/"blocker.json").is_file(),"Lease expiry needs a durable exact blocker.")
  self.assertEqual(w.load(self.base/"blocker.json")["id"],"lease_expired")
 def test_new_allocation_cap_is_loaded_not_silently_defaulted(self):
  w.save(self.base/"authorization.json",{"schema":"sunny.background-authorization.v1","instance":self.base.name,"maximum_new_model_requests":3,"maximum_owned_worker_processes":1,"lease_seconds":60,"maximum_meaningful_action_gap_seconds":600,"authorized_utc":datetime.now(timezone.utc).isoformat()})
  budget=w.ModelBudget(self.base)
  self.assertEqual(budget.remaining,3)
  self.assertIn("authorization_sha256",budget.state)
 def test_no_output_deadline_is_flagged_even_before_first_completion(self):
  w.save(self.base/'cadence.json',{'schema':'sunny.background-cadence.v1','monitor_started_utc':'2000-01-01T00:00:00+00:00','last_meaningful_action_utc':None,'last_completed_result_utc':None,'completed_result_count':0})
  w.record_cadence(self.base,remaining=20)
  self.assertTrue((self.base/'blocker.json').is_file(),'A first completion cannot be postponed indefinitely without a blocker.')
  self.assertEqual(w.load(self.base/'blocker.json')['id'],'meaningful_action_overdue')
 def test_live_readiness_timeout_does_not_reap_owned_process(self):
  # Execute the real manager's timeout branch. Only OS identity/stop boundaries
  # are doubles; no worker process is launched and no real PID is terminated.
  script=r"""
$sourcePath=Join-Path (Get-Location) 'scripts/manage-background-reconstruction.ps1'
$tokens=$null;$errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($sourcePath,[ref]$tokens,[ref]$errors)
$node=$ast.FindAll({param($n) $n -is [Management.Automation.Language.IfStatementAst] -and $n.Clauses[0].Item1.Extent.Text -eq '-not $sunnyReady'},$true)|Select-Object -Last 1
if(-not $node){throw 'Could not locate the actual readiness branch.'}
$script:stopCalls=0
function Test-SunnyProcessIdentity {param($Identity) return $true}
function Stop-SunnyOwnedTree {param($Record) $script:stopCalls++; return @()}
$sunnyReady=$false;$sunnyIdentity=[pscustomobject]@{pid=123;creation_utc='2000-01-01T00:00:00Z'}
$sunnyRecord=[pscustomobject]@{status='starting';root_identity=$sunnyIdentity}
$sunnyRecordPath=Join-Path $env:SUNNY_TEST_SCOPE 'ownership.json'
$sunnyBase=$env:SUNNY_TEST_SCOPE
$failure=$null
try{& ([scriptblock]::Create($node.Extent.Text))|Out-Null}catch{$failure=$_.Exception.Message}
[ordered]@{stop_calls=$script:stopCalls;failure=$failure;status=$sunnyRecord.status}|ConvertTo-Json
"""
  env=dict(os.environ,SUNNY_TEST_SCOPE=str(self.base))
  result=subprocess.run(["powershell.exe","-NoProfile","-NonInteractive","-Command",script],cwd=ROOT,env=env,capture_output=True,text=True,encoding="utf8",timeout=15)
  self.assertEqual(result.returncode,0,result.stderr);data=json.loads(result.stdout)
  self.assertEqual(data["stop_calls"],0,"Readiness polling timeout must leave the verified live worker intact.")
  self.assertEqual(data["status"],"live_readiness_unconfirmed")
if __name__=="__main__":unittest.main(verbosity=2)
