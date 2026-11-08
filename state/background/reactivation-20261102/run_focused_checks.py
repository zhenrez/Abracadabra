from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
# This file lives in state/background/reactivation-20261102.
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
cmd=[sys.executable,'-X','utf8','-B','-m','unittest','tests.background_reconstruction_test','tests.background_intake_test','tests.background_reliability_test','-v']
run=subprocess.run(cmd,cwd=ROOT,capture_output=True,encoding='utf8',timeout=45)
(BASE/'focused-green-tests.txt').write_text(run.stdout+run.stderr,encoding='utf8')
report={'schema':'sunny.background-reactivation-tests.v1','checked_utc':datetime.now(timezone.utc).isoformat(),'command':cmd,'exit_code':run.returncode,'passed':run.returncode==0,'output_path':str((BASE/'focused-green-tests.txt').relative_to(ROOT)),'tested_code_sha256':hashlib.sha256((ROOT/'scripts/background_reconstruction.py').read_bytes()).hexdigest(),'manager_sha256':hashlib.sha256((ROOT/'scripts/manage-background-reconstruction.ps1').read_bytes()).hexdigest(),'scope':'18focused source/intake/cadence/budget/readiness/Proofline/lock contracts. Synthetic fixture scope, no live model requests in the test suite. Actual process/output evidence is separate.'}
(ROOT/'docs/evidence/background-reactivation-tests.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report));raise SystemExit(run.returncode)
