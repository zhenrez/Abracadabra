param([switch]$StatusOnly)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'process-lifecycle.ps1')
Invoke-SunnyLifecycleLock {
    $sunnyResults = @()
    foreach ($sunnyName in @('sunny-app','jev-8150','jev-8149')) {
        $sunnyRecordPath = Join-Path $script:SunnyProcessDirectory ($sunnyName + '.json')
        if (-not (Test-Path -LiteralPath $sunnyRecordPath -PathType Leaf)) { $sunnyResults += @{name=$sunnyName; status='not_tracked'}; continue }
        $sunnyRecord = Get-Content -LiteralPath $sunnyRecordPath -Raw | ConvertFrom-Json
        if ($sunnyRecord.workspace -ine $script:SunnyLifecycleRoot -or $sunnyRecord.name -cne $sunnyName) { throw 'Service ownership record does not match this SUNNY workspace.' }
        $sunnyLive = @($sunnyRecord.processes | Where-Object { Test-SunnyProcessIdentity $_ })
        if ($StatusOnly) { $sunnyResults += @{name=$sunnyName; status=$(if ($sunnyLive.Count) {'running_owned'} else {'not_running'}); process_count=$sunnyLive.Count}; continue }
        $sunnyStopped = @(Stop-SunnyOwnedTree $sunnyRecord)
        $sunnyRecord.status='stopped'; Save-SunnyServiceRecord $sunnyRecord
        $sunnyResults += @{name=$sunnyName; status='stopped_or_already_absent'; processes=$sunnyStopped}
    }
    $sunnyResults | ConvertTo-Json -Depth 8
}
