param([ValidateRange(15,300)][int]$TimeoutSeconds=180)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'process-lifecycle.ps1')
$auditScope=Join-Path $script:SunnyLifecycleRoot 'work\mandate-agentproof-2026-10-31'
$auditOut=Join-Path $script:SunnyLifecycleRoot 'docs\evidence'
$auditLauncher='C:\Users\Brend\.codex\plugins\cache\openai-curated-remote\agentproof\0.1.0\skills\agentproof\scripts\agentproof.py'
if (-not (Test-Path -LiteralPath (Join-Path $auditScope '.git'))) {throw 'Intended isolated Git scope missing.'}
$auditRoot=$null;$auditTracked=@{};$auditCleanup=@();$auditTimedOut=$false
try {
 $auditProc=Start-Process -FilePath (Get-Command python).Source -ArgumentList @('-B',('"'+$auditLauncher+'"'),'--request','.agentproof/request.json') -WorkingDirectory $auditScope -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $auditOut 'mandate-agentproof-capture.json') -RedirectStandardError (Join-Path $auditOut 'mandate-agentproof-error.json')
 $auditRoot=Get-SunnyProcessIdentity $auditProc.Id
 if (-not $auditRoot) {throw 'Capture ended before its process identity could be recorded.'}
 $auditDeadline=[DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
 while (-not $auditProc.HasExited) {
  foreach($auditIdentity in @(Get-SunnyOwnedTree $auditRoot)) {$auditTracked[[string]$auditIdentity.pid]=$auditIdentity}
  if([DateTime]::UtcNow -ge $auditDeadline){$auditTimedOut=$true;break}
  Start-Sleep -Milliseconds 500
  $auditProc.Refresh()
 }
} finally {
 if($auditRoot){$auditCleanup=@(Stop-SunnyOwnedTree ([pscustomobject]@{root_identity=$auditRoot;processes=@($auditRoot)+@($auditTracked.Values)}))}
 $auditRemaining=@($auditTracked.Values | Where-Object {Test-SunnyProcessIdentity $_})
 [pscustomobject]@{scope=$auditScope;timed_out=$auditTimedOut;tracked_process_count=$auditTracked.Count;remaining_owned_count=$auditRemaining.Count;cleanup=$auditCleanup;processes=@($auditTracked.Values)} | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $auditOut 'mandate-agentproof-processes.json') -Encoding utf8
}
if($auditTimedOut){throw 'Bounded capture timed out; verified owned processes were closed.'}
Get-Content -LiteralPath (Join-Path $auditOut 'mandate-agentproof-capture.json')
