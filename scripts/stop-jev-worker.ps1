param(
    [Parameter(Mandatory=$true)][ValidateSet('capture','stop')][string]$Action,
    [Parameter(Mandatory=$true)][int]$WorkerPid,
    [Parameter(Mandatory=$true)][string]$Script,
    [Parameter(Mandatory=$true)][string]$Executable,
    [Parameter(Mandatory=$true)][string]$CreatedAfter
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'process-lifecycle.ps1')
$workerScript = [IO.Path]::GetFullPath($Script)
if ([IO.Path]::GetFileName($workerScript) -cne 'jev_tool.py' -or
    [IO.Path]::GetFileName([IO.Path]::GetDirectoryName($workerScript)) -cne 'scripts') {
    throw 'Only the fixed Jev request script can be tracked.'
}
$workerExecutable = if ([IO.Path]::IsPathRooted($Executable)) { [IO.Path]::GetFullPath($Executable) } else { (Get-Command -Name $Executable -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source }
$workerArgument = '(?:^|\s)"?' + [regex]::Escape($workerScript) + '"?(?=\s|$)'

if ($Action -eq 'capture') {
    $workerObserved = Get-CimInstance Win32_Process -Filter "ProcessId=$WorkerPid"
    if (-not $workerObserved -or $workerObserved.ExecutablePath -ine $workerExecutable -or
        $workerObserved.CommandLine -notmatch $workerArgument -or
        $workerObserved.CreationDate.ToUniversalTime() -lt ([DateTimeOffset]$CreatedAfter).UtcDateTime.AddSeconds(-1)) {
        throw 'The worker PID does not match the launched executable, fixed script and birth window.'
    }
    $workerIdentity = Get-SunnyProcessIdentity $WorkerPid
    if (-not $workerIdentity -or $workerIdentity.parent_pid -ne $workerObserved.ParentProcessId -or
        ([DateTimeOffset]$workerIdentity.creation_utc).UtcTicks -ne ([DateTimeOffset]$workerObserved.CreationDate).UtcTicks -or
        $workerIdentity.executable_path -ine $workerObserved.ExecutablePath -or
        $workerIdentity.command_sha256 -cne (Get-SunnyTextHash ([string]$workerObserved.CommandLine))) {
        throw 'Worker identity changed during ownership capture.'
    }
    # stdin stays open in Node until this snapshot completes. The actual tool waits
    # for EOF, so its Windows venv interpreter child cannot finish before capture.
    $workerProcesses = @(Get-SunnyOwnedTree $workerIdentity)
    if ($workerExecutable -match '[\\/]Scripts[\\/]python\.exe$') {
        $workerDeadline = [DateTime]::UtcNow.AddSeconds(3)
        while ($workerProcesses.Count -lt 2 -and [DateTime]::UtcNow -lt $workerDeadline -and (Test-SunnyProcessIdentity $workerIdentity)) {
            Start-Sleep -Milliseconds 50
            $workerProcesses = @(Get-SunnyOwnedTree $workerIdentity)
        }
        if ($workerProcesses.Count -lt 2) { throw 'The venv interpreter child was not captured; input was not submitted.' }
    }
    if (-not (Test-SunnyProcessIdentity $workerIdentity)) { throw 'Worker exited during ownership capture.' }
    [ordered]@{kind='sunny-http-worker';script=$workerScript;executable=$workerExecutable;root_identity=$workerIdentity;processes=$workerProcesses} | ConvertTo-Json -Depth 12 -Compress
    exit 0
}

$workerRecord = [Console]::In.ReadToEnd() | ConvertFrom-Json
if ($workerRecord.kind -cne 'sunny-http-worker' -or $workerRecord.script -cne $workerScript -or
    $workerRecord.executable -ine $workerExecutable -or $workerRecord.root_identity.pid -ne $WorkerPid) {
    throw 'Worker ownership record does not match the fixed request.'
}
$workerTargets = @($workerRecord.processes)
foreach ($workerKnown in @($workerRecord.processes)) {
    if (Test-SunnyProcessIdentity $workerKnown) { $workerTargets += @(Get-SunnyOwnedTree $workerKnown) }
}
$workerRecord.processes = $workerTargets
$workerStopped = @(Stop-SunnyOwnedTree $workerRecord)
$workerRemaining = @($workerTargets | Where-Object { Test-SunnyProcessIdentity $_ })
if ($workerRemaining.Count -gt 0) { throw 'An owned request worker is still running.' }
[ordered]@{status='reaped';remaining_owned_processes=0;processes=$workerStopped} | ConvertTo-Json -Depth 12 -Compress
