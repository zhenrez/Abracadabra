param([switch]$Open)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'process-lifecycle.ps1')
$sunnyEvidence = Join-Path $script:SunnyLifecycleRoot 'docs\evidence'
New-Item -ItemType Directory -Path $sunnyEvidence -Force | Out-Null
Invoke-SunnyLifecycleLock {
    $sunnyJev = $null; $sunnyApp = $null
    try {
        $sunnyJev = & (Join-Path $PSScriptRoot 'start-jev.ps1') -Device cpu -Port 8149
        $sunnyEntry = Join-Path $script:SunnyLifecycleRoot 'dist\server.js'
        if (-not (Test-Path -LiteralPath $sunnyEntry -PathType Leaf)) { throw 'SUNNY is not compiled. Run npm run build from the workspace.' }
        $sunnyNode = (Get-Command node -ErrorAction Stop).Source
        $sunnyApp = Start-SunnyManagedService -Name 'sunny-app' -Executable $sunnyNode -Arguments @("`"$sunnyEntry`"") -WorkingDirectory $script:SunnyLifecycleRoot -Port 4317 -LogStem (Join-Path $sunnyEvidence 'sunny-server') -TimeoutSeconds 20 -Probe {
            $sunnySummary = Invoke-RestMethod -Uri 'http://127.0.0.1:4317/api/summary' -TimeoutSec 2
            return ($sunnySummary.counts.sources -is [ValueType] -and $sunnySummary.counts.messages -is [ValueType] -and $sunnySummary.account_complete -eq $false -and $sunnySummary.scope.status -eq 'Bounded source recovery')
        }
        Write-Output "SUNNY is ready: http://127.0.0.1:4317 ($($sunnyApp.status); Jev $($sunnyJev.status))"
    } catch {
        if ($sunnyApp -and $sunnyApp.created) { Stop-SunnyOwnedTree $sunnyApp.record | Out-Null; $sunnyApp.record.status='launch_failed_cleaned'; Save-SunnyServiceRecord $sunnyApp.record }
        if ($sunnyJev -and $sunnyJev.created) { Stop-SunnyOwnedTree $sunnyJev.record | Out-Null; $sunnyJev.record.status='launch_failed_cleaned'; Save-SunnyServiceRecord $sunnyJev.record }
        throw
    }
}
if ($Open) { Start-Process 'http://127.0.0.1:4317' }
