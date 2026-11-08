param(
    [ValidateSet('cpu','cuda:0')][string]$Device = 'cpu',
    [ValidateRange(1024,65535)][int]$Port = 8149
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'process-lifecycle.ps1')
$jevRepo = Join-Path $script:SunnyLifecycleRoot 'runtime\agent-jev'
$jevPython = Join-Path $script:SunnyLifecycleRoot 'runtime\.venv\Scripts\python.exe'
$jevWeights = Join-Path $jevRepo 'models\agentjev-v1\model.safetensors'
$jevEvidence = Join-Path $script:SunnyLifecycleRoot 'docs\evidence'
foreach ($jevRequired in @($jevPython,$jevWeights)) {
    if (-not (Test-Path -LiteralPath $jevRequired -PathType Leaf)) { throw "Missing runtime file: $jevRequired" }
}
New-Item -ItemType Directory -Path $jevEvidence -Force | Out-Null
$jevLogTag = if ($Port -eq 8149) { '' } else { "-$Port" }
$jevArguments = @('-u','-m','jev_service.server','--checkpoint','models/agentjev-v1/model.safetensors','--model-path','models/agentjev-v1','--temperatures','models/agentjev-v1/temperatures.json','--port',"$Port",'--device',$Device)
$jevEnvironment = @{HF_HUB_OFFLINE='1'; TRANSFORMERS_OFFLINE='1'; HF_HUB_DISABLE_TELEMETRY='1'; HF_HUB_DISABLE_IMPLICIT_TOKEN='1'; TOKENIZERS_PARALLELISM='false'}
if ($Device -eq 'cpu') { $jevEnvironment.OMP_NUM_THREADS='4'; $jevEnvironment.MKL_NUM_THREADS='4' }
$jevPreviousEnvironment = @{}
try {
    foreach ($jevKey in $jevEnvironment.Keys) { $jevPreviousEnvironment[$jevKey]=[Environment]::GetEnvironmentVariable($jevKey,'Process'); [Environment]::SetEnvironmentVariable($jevKey,$jevEnvironment[$jevKey],'Process') }
    Start-SunnyManagedService -Name "jev-$Port" -Executable $jevPython -Arguments $jevArguments -WorkingDirectory $jevRepo -Port $Port -LogStem (Join-Path $jevEvidence "jev-runtime-service$jevLogTag") -Probe {
        $jevHealth = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/health" -TimeoutSec 2
        return ($jevHealth.status -eq 'ready' -and $jevHealth.checkpoint_sha256 -eq '8166e46dc6019ae13f0d8fc97d603cdbcc2d20eb1882c7350c8deb9fc6bae215')
    }
} finally {
    foreach ($jevKey in $jevPreviousEnvironment.Keys) { [Environment]::SetEnvironmentVariable($jevKey,$jevPreviousEnvironment[$jevKey],'Process') }
}
