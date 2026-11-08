$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..\scripts\process-lifecycle.ps1')
$sunnyTestRoot = $script:SunnyLifecycleRoot
$sunnyTestDirectory = Join-Path $sunnyTestRoot ('work\lifecycle-test-' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $sunnyTestDirectory -Force | Out-Null
$script:SunnyProcessDirectory = Join-Path $sunnyTestDirectory 'records'
$sunnyTestNode = (Get-Command node).Source
$sunnyTestFixture = Join-Path $PSScriptRoot 'lifecycle-worker.mjs'
$sunnyTestChecks = [Collections.Generic.List[string]]::new()
$sunnyTestRecords = [Collections.Generic.List[object]]::new()
$sunnyTestSucceeded=$false
function Assert-SunnyTest([bool]$Condition,[string]$Message) { if (-not $Condition) { throw $Message }; $sunnyTestChecks.Add($Message) }
function Get-SunnyTestPort { $sunnyListener=[Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback,0); $sunnyListener.Start(); try { return $sunnyListener.LocalEndpoint.Port } finally { $sunnyListener.Stop() } }
try {
    $sunnyMinimalListener=[Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback,0)
    $sunnyMinimalListener.Start()
    try { Assert-SunnyTest ((Get-SunnyLoopbackPortState $sunnyMinimalListener.LocalEndpoint.Port) -eq 'occupied') 'Direct loopback guard detects an owned listener independently of enumeration' } finally {$sunnyMinimalListener.Stop()}
    $sunnySnapshotAccepted = & {
        $sunnyMockRoot=[pscustomobject]@{pid=990001;parent_pid=1;creation_utc='2026-10-30T01:00:00Z';executable_path='fixture-root';command_sha256='root'}
        function Get-SunnyProcessIdentity([int]$ProcessId) {
            if($ProcessId -eq 990001){return $sunnyMockRoot}
            return [pscustomobject]@{pid=990002;parent_pid=7;creation_utc='2026-10-30T02:00:00Z';executable_path='unrelated-reused-pid';command_sha256='replacement'}
        }
        function Get-CimInstance { return [pscustomobject]@{ProcessId=990002;ParentProcessId=990001;CreationDate=[DateTime]::Parse('2026-10-30T01:00:01Z');ExecutablePath='original-child';CommandLine='original'} }
        return @(Get-SunnyOwnedTree $sunnyMockRoot).Count
    }
    Assert-SunnyTest ($sunnySnapshotAccepted -eq 1) 'Stale child snapshot cannot enroll a reused PID'
    $sunnyTestPort = Get-SunnyTestPort
    $sunnyTestParameters = @{Name='fixture-reuse'; Executable=$sunnyTestNode; Arguments=@("`"$sunnyTestFixture`"",[string]$sunnyTestPort); WorkingDirectory=$sunnyTestRoot; Port=$sunnyTestPort; LogStem=(Join-Path $sunnyTestDirectory 'reuse'); TimeoutSeconds=10; Probe={ (Invoke-RestMethod "http://127.0.0.1:$sunnyTestPort" -TimeoutSec 1).fixture -eq 'sunny-lifecycle' }}
    $sunnyFirst = Start-SunnyManagedService @sunnyTestParameters; $sunnyTestRecords.Add($sunnyFirst.record)
    Assert-SunnyTest ($sunnyFirst.created -and $sunnyFirst.record.processes.Count -ge 2) 'Launch records the service and its child worker'
    $sunnySecond = Start-SunnyManagedService @sunnyTestParameters
    Assert-SunnyTest (-not $sunnySecond.created -and $sunnySecond.status -eq 'reused_owned' -and $sunnySecond.record.root_identity.pid -eq $sunnyFirst.record.root_identity.pid) 'Repeated start reuses exactly the recorded process'
    $sunnyReloaded = Get-Content -LiteralPath (Join-Path $script:SunnyProcessDirectory 'fixture-reuse.json') -Raw | ConvertFrom-Json
    Assert-SunnyTest (Test-SunnyProcessIdentity $sunnyReloaded.root_identity) 'Identity survives JSON serialization and date parsing'
    $sunnyTampered = $sunnyReloaded.root_identity | Select-Object *
    $sunnyTampered.creation_utc = ([DateTimeOffset]$sunnyTampered.creation_utc).AddSeconds(1).ToString('o')
    Stop-SunnyOwnedTree ([pscustomobject]@{root_identity=$sunnyTampered; processes=@($sunnyTampered)}) | Out-Null
    Assert-SunnyTest (Test-SunnyProcessIdentity $sunnyFirst.record.root_identity) 'Changed creation identity cannot authorize termination'
    $sunnyUnrelated = Start-Process -FilePath $sunnyTestNode -ArgumentList @("`"$sunnyTestFixture`"",'idle') -WindowStyle Hidden -PassThru
    $sunnyUnrelatedIdentity = Get-SunnyProcessIdentity $sunnyUnrelated.Id
    $sunnyUnrelatedRecord = [pscustomobject]@{root_identity=$sunnyUnrelatedIdentity; processes=@($sunnyUnrelatedIdentity)}; $sunnyTestRecords.Add($sunnyUnrelatedRecord)
    Stop-SunnyOwnedTree $sunnyFirst.record | Out-Null
    Assert-SunnyTest (@($sunnyFirst.record.processes | Where-Object { Test-SunnyProcessIdentity $_ }).Count -eq 0) 'Scoped stop waits for the entire captured tree to exit'
    Assert-SunnyTest (Test-SunnyProcessIdentity $sunnyUnrelatedIdentity) 'Scoped stop preserves an unrelated same-name process'
    $sunnyFailurePort = Get-SunnyTestPort
    $sunnyFailure = $false
    try { Start-SunnyManagedService -Name 'fixture-failure' -Executable $sunnyTestNode -Arguments @("`"$sunnyTestFixture`"",[string]$sunnyFailurePort) -WorkingDirectory $sunnyTestRoot -Port $sunnyFailurePort -LogStem (Join-Path $sunnyTestDirectory 'failure') -TimeoutSeconds 1 -Probe {$false} | Out-Null } catch { $sunnyFailure=$true }
    $sunnyFailedRecord = Get-Content -LiteralPath (Join-Path $script:SunnyProcessDirectory 'fixture-failure.json') -Raw | ConvertFrom-Json
    $sunnyTestRecords.Add($sunnyFailedRecord)
    Assert-SunnyTest ($sunnyFailure -and $sunnyFailedRecord.status -eq 'startup_failed_cleaned' -and @($sunnyFailedRecord.processes | Where-Object { Test-SunnyProcessIdentity $_ }).Count -eq 0) 'Failed readiness cleans up its own service tree'
    $sunnyOccupiedPort = Get-SunnyTestPort
    $sunnyOccupiedWorker = Start-Process -FilePath $sunnyTestNode -ArgumentList @("`"$sunnyTestFixture`"",[string]$sunnyOccupiedPort) -WorkingDirectory $sunnyTestRoot -WindowStyle Hidden -PassThru
    $sunnyOccupiedIdentity = Get-SunnyProcessIdentity $sunnyOccupiedWorker.Id
    $sunnyOccupiedRecord = [pscustomobject]@{root_identity=$sunnyOccupiedIdentity;processes=@(Get-SunnyOwnedTree $sunnyOccupiedIdentity)}; $sunnyTestRecords.Add($sunnyOccupiedRecord)
    $sunnyOccupiedReady=$false
    for($sunnyPoll=0;$sunnyPoll -lt 30;$sunnyPoll++){ try { Invoke-RestMethod "http://127.0.0.1:$sunnyOccupiedPort" -TimeoutSec 1 | Out-Null; $sunnyOccupiedReady=$true; break } catch { Start-Sleep -Milliseconds 100 } }
    Assert-SunnyTest $sunnyOccupiedReady 'Unrecognized-port fixture is listening before refusal check'
    $sunnyRejected=$false
    try { Start-SunnyManagedService -Name 'fixture-occupied' -Executable $sunnyTestNode -Arguments @("`"$sunnyTestFixture`"",[string]$sunnyOccupiedPort) -WorkingDirectory $sunnyTestRoot -Port $sunnyOccupiedPort -LogStem (Join-Path $sunnyTestDirectory 'occupied') -TimeoutSeconds 1 -Probe {$false} | Out-Null } catch { $sunnyRejected=$true }
    $sunnyOccupiedStillLive=Test-SunnyProcessIdentity $sunnyOccupiedIdentity
    $sunnyOccupiedRecordCreated=Test-Path -LiteralPath (Join-Path $script:SunnyProcessDirectory 'fixture-occupied.json')
    Assert-SunnyTest ($sunnyRejected -and $sunnyOccupiedStillLive -and -not $sunnyOccupiedRecordCreated) "Occupied unrecognized port is left untouched without launching a duplicate (rejected=$sunnyRejected; live=$sunnyOccupiedStillLive; record=$sunnyOccupiedRecordCreated)"
    $sunnyConcurrentPort=Get-SunnyTestPort
    $sunnyConcurrentScript=Join-Path $PSScriptRoot 'lifecycle-concurrent-start.ps1'
    $sunnyConcurrentShell=(Get-Command powershell.exe).Source
    $sunnyConcurrentWorkers=@()
    for($sunnyWorkerIndex=0;$sunnyWorkerIndex -lt 2;$sunnyWorkerIndex++){
        $sunnyConcurrentArguments=@('-NoProfile','-File',"`"$sunnyConcurrentScript`"",'-RecordDirectory',"`"$script:SunnyProcessDirectory`"",'-Port',[string]$sunnyConcurrentPort,'-LogStem',"`"$(Join-Path $sunnyTestDirectory 'concurrent-service')`"")
        $sunnyConcurrentWorker=Start-Process -FilePath $sunnyConcurrentShell -ArgumentList $sunnyConcurrentArguments -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $sunnyTestDirectory "concurrent-$sunnyWorkerIndex.json") -RedirectStandardError (Join-Path $sunnyTestDirectory "concurrent-$sunnyWorkerIndex.stderr.log")
        $sunnyConcurrentIdentity=Get-SunnyProcessIdentity $sunnyConcurrentWorker.Id
        $sunnyConcurrentRecord=[pscustomobject]@{root_identity=$sunnyConcurrentIdentity;processes=@(Get-SunnyOwnedTree $sunnyConcurrentIdentity)}; $sunnyTestRecords.Add($sunnyConcurrentRecord)
        $sunnyConcurrentWorkers+= $sunnyConcurrentWorker
    }
    $sunnyConcurrentError=$null
    try { $sunnyConcurrentWorkers | Wait-Process -Timeout 30 -ErrorAction Stop } catch { $sunnyConcurrentError=$_ }
    $sunnyConcurrentRecordPath=Join-Path $script:SunnyProcessDirectory 'fixture-concurrent.json'
    if(Test-Path -LiteralPath $sunnyConcurrentRecordPath){$sunnyTestRecords.Add((Get-Content -LiteralPath $sunnyConcurrentRecordPath -Raw | ConvertFrom-Json))}
    if($sunnyConcurrentError){throw $sunnyConcurrentError}
    $sunnyConcurrentResults=@(0..1 | ForEach-Object { Get-Content -LiteralPath (Join-Path $sunnyTestDirectory "concurrent-$_.json") -Raw | ConvertFrom-Json })
    Assert-SunnyTest (@($sunnyConcurrentResults | Where-Object created).Count -eq 1 -and @($sunnyConcurrentResults.pid | Select-Object -Unique).Count -eq 1 -and @($sunnyConcurrentResults | Where-Object status -EQ 'reused_owned').Count -eq 1) 'Concurrent Windows PowerShell starts launch one service and reuse its exact identity'
    $sunnyTestSucceeded=$true
} finally {
    foreach($sunnyTestRecord in $sunnyTestRecords){ Stop-SunnyOwnedTree $sunnyTestRecord | Out-Null }
    $sunnySurvivors=@($sunnyTestRecords | ForEach-Object { $_.processes } | Where-Object { Test-SunnyProcessIdentity $_ })
    $sunnyTestReport=[pscustomobject]@{checked_utc=[DateTime]::UtcNow.ToString('o');status=$(if($sunnyTestSucceeded){'passed'}else{'failed'});checks=@($sunnyTestChecks);surviving_owned_processes=@($sunnySurvivors);test_directory=$sunnyTestDirectory;scope='Synthetic short-lived workers only; real app/model startup is verified separately.'}
    $sunnyTestReport | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $sunnyTestRoot 'docs\evidence\process-lifecycle-check.json') -Encoding utf8
    $sunnyTestReport | ConvertTo-Json -Depth 8
    if($sunnySurvivors.Count){throw 'Lifecycle test leaked owned workers.'}
}
