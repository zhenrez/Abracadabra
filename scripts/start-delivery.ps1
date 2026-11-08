param([ValidateRange(1024,65535)][int]$Port=8767)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'process-lifecycle.ps1')
$sunnyDeliveryPython=Join-Path $script:SunnyLifecycleRoot 'runtime\.venv\Scripts\python.exe'
$sunnyDeliveryScript=Join-Path $PSScriptRoot 'delivery_server.py'
Start-SunnyManagedService -Name "delivery-$Port" -Executable $sunnyDeliveryPython -Arguments @('-u',$sunnyDeliveryScript,'--port',"$Port") -WorkingDirectory $script:SunnyLifecycleRoot -Port $Port -LogStem (Join-Path $script:SunnyLifecycleRoot "docs\evidence\delivery-$Port") -Probe {
    $sunnyDeliveryHealth=Invoke-RestMethod -Uri "http://127.0.0.1:$Port/health" -TimeoutSec 2
    return ($sunnyDeliveryHealth.status -eq 'ready' -and $sunnyDeliveryHealth.application -eq 'SUNNY connected delivery')
}
