"""Actual Windows ownership tests; one windowless test worker at a time."""
import json,subprocess,time,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANAGER=ROOT/'scripts/manage-background-reconstruction.ps1'
OUT=ROOT/'state/background/lifecycle-verification.json'
checks=[]
INSTANCE='lifecycle-'+str(os.getpid())
def call(action,instance=INSTANCE,lease=45,ok=True):
    p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-File',str(MANAGER),'-Action',action,'-Instance',instance,'-LeaseSeconds',str(lease)],cwd=ROOT,text=True,encoding='utf-8',capture_output=True,timeout=35)
    if ok and p.returncode:raise RuntimeError(p.stderr)
    return json.loads(p.stdout) if ok else p
def check(value,label):
    checks.append(dict(check=label,passed=bool(value)))
    if not value:raise AssertionError(label)
try:
    first=call('start');second=call('start')
    check(first['created'] and not second['created'] and first['root_identity']==second['root_identity'],'Second start reuses exact process identity')
    state=call('status');check(state['owned_running'] and len(state['ownership']['processes'])==1,'Exactly one windowless owned process; no console or child')
    other=call('start','lifecycle-other',ok=False)
    check(other.returncode!=0 and 'no second worker launched' in other.stderr,'Alternate queue cannot start another worker')
    stopped=call('stop');check(stopped.get('remaining_owned_processes')==0 and not call('status')['owned_running'],'Explicit shutdown leaves zero owned survivors')
    leased=call('start',lease=2)
    # The idle wait is bounded by the polling interval, so 2s lease plus one
    # 15s sleep is allowed; no repeated scientific jobs occur during the wait.
    deadline=time.monotonic()+20
    while time.monotonic()<deadline:
        status=call('status')
        if not status['owned_running']:break
        time.sleep(.25)
    check(not status['owned_running'] and status['worker']['status']=='stopped','Lease expiry closes worker without supervisor restarts')
    result=dict(status='passed',checks=checks,last_identity=leased['root_identity'],scope='Actual detached idle-worker start/reuse/global-exclusion/shutdown/lease. Synthetic lifecycle scope; scientific outputs checked separately.')
finally:
    final=call('stop')
    if 'result' not in globals():result=dict(status='failed',checks=checks)
    result['final_status']=call('status')
    OUT.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(dict(status=result['status'],checks=checks,owned_running=result['final_status']['owned_running'])))
