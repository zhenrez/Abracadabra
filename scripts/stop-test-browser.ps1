param(
    [Parameter(Mandatory=$true)][int]$BrowserPid,
    [Parameter(Mandatory=$true)][string]$Profile,
    [switch]$CaptureOnly
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'process-lifecycle.ps1')
$testProfile = [IO.Path]::GetFullPath($Profile)
$testTemp = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\') + '\'
if (-not $testProfile.StartsWith($testTemp, [StringComparison]::OrdinalIgnoreCase) -or
    [IO.Path]::GetFileName($testProfile) -notmatch '^sunny-edge-check-[a-zA-Z0-9_-]+$') {
    throw 'Refusing browser cleanup outside a dedicated SUNNY test profile.'
}
$testExecutable = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$testArgument = '(?:^|\s)"?--user-data-dir=' + [regex]::Escape($testProfile) + '"?(?=\s|$)'
$testRecordPath = Join-Path $testProfile 'sunny-process-ownership.json'
$testRecord = $null
if (Test-Path -LiteralPath $testRecordPath -PathType Leaf) {
    $testRecord = Get-Content -LiteralPath $testRecordPath -Raw | ConvertFrom-Json
    if ($testRecord.profile -cne $testProfile -or $testRecord.root_identity.pid -ne $BrowserPid -or
        $testRecord.root_identity.executable_path -ine $testExecutable) { throw 'Browser ownership record does not match this test.' }
    if (@($testRecord.processes | Where-Object { $_.executable_path -ine $testExecutable }).Count) { throw 'Unexpected executable in test-browser record.' }
}
# Capture before graceful close, retaining birth identities if the parent exits first.
$testCurrentRoot = Get-CimInstance Win32_Process -Filter "ProcessId=$BrowserPid"
if ($testCurrentRoot -and $testCurrentRoot.ExecutablePath -eq $testExecutable -and $testCurrentRoot.CommandLine -match $testArgument) {
    $testIdentity = Get-SunnyProcessIdentity -ProcessId $BrowserPid
    if (-not $testIdentity -or ([DateTimeOffset]$testIdentity.creation_utc).UtcTicks -ne $testCurrentRoot.CreationDate.ToUniversalTime().Ticks -or
        $testIdentity.parent_pid -ne $testCurrentRoot.ParentProcessId -or
        $testIdentity.command_sha256 -cne (Get-SunnyTextHash $testCurrentRoot.CommandLine)) { throw 'Browser identity changed while capturing ownership.' }
    if ($testRecord -and (([DateTimeOffset]$testIdentity.creation_utc).UtcTicks -ne ([DateTimeOffset]$testRecord.root_identity.creation_utc).UtcTicks -or
        $testIdentity.command_sha256 -cne $testRecord.root_identity.command_sha256)) { throw 'Browser PID has been reused.' }
    $testFresh = @(Get-SunnyOwnedTree -Identity $testIdentity | Where-Object { $_.executable_path -ieq $testExecutable })
    $testPrior = if ($testRecord) { @($testRecord.processes) } else { @() }
    $testSeen = @{}
    $testProcesses = @($testPrior + $testFresh | Where-Object {
        $testKey = [string]$_.pid + ':' + [string]([DateTimeOffset]$_.creation_utc).UtcTicks
        if ($testSeen.ContainsKey($testKey)) { return $false }; $testSeen[$testKey] = $true; return $true
    })
    $testRecord = [pscustomobject]@{profile=$testProfile;root_identity=$testIdentity;processes=$testProcesses}
    $testRecord | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $testRecordPath -Encoding utf8
}
if (-not $testRecord) { throw 'No verified browser ownership snapshot is available; cleanup cannot be certified.' }
if ($CaptureOnly) {
    [ordered]@{status='captured';profile=$testProfile;identities=@($testRecord.processes).Count} | ConvertTo-Json -Compress
    return
}
$testResults = @(Stop-SunnyOwnedTree -Record $testRecord)
$testKnownRemaining = @($testRecord.processes | Where-Object { Test-SunnyProcessIdentity $_ })
$testProfileRemaining = @(Get-CimInstance Win32_Process -Filter "Name='msedge.exe'" | Where-Object {
    $_.ExecutablePath -eq $testExecutable -and $_.CommandLine -match $testArgument
})
if ($testKnownRemaining.Count -or $testProfileRemaining.Count) { throw 'A captured browser descendant or dedicated-profile process is still running.' }
[ordered]@{status='reaped';profile=$testProfile;captured_identities=@($testRecord.processes).Count;stopped_pids=@($testResults | Where-Object status -EQ 'stopped_verified_identity' | ForEach-Object pid);remaining_known_processes=0;remaining_profile_processes=0} | ConvertTo-Json -Depth 4 -Compress
