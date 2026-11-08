param([Parameter(Mandatory)][string]$RecordDirectory,[Parameter(Mandatory)][int]$Port,[Parameter(Mandatory)][string]$LogStem)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot '..\scripts\process-lifecycle.ps1')
$script:SunnyProcessDirectory=$RecordDirectory
$sunnyNode=(Get-Command node).Source
$sunnyFixture=Join-Path $PSScriptRoot 'lifecycle-worker.mjs'
$sunnyStarted=Start-SunnyManagedService -Name 'fixture-concurrent' -Executable $sunnyNode -Arguments @("`"$sunnyFixture`"",[string]$Port,'800') -WorkingDirectory $script:SunnyLifecycleRoot -Port $Port -LogStem $LogStem -TimeoutSeconds 15 -Probe { (Invoke-RestMethod "http://127.0.0.1:$Port" -TimeoutSec 1).fixture -eq 'sunny-lifecycle' }
$sunnyStarted | Select-Object name,status,created,@{Name='pid';Expression={$_.record.root_identity.pid}} | ConvertTo-Json
