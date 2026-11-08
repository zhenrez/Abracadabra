param(
    [Alias('Action')][ValidateSet('start','status','stop')][string]$Mode='status',
    [ValidatePattern('^[a-z0-9][a-z0-9_-]{0,60}$')][string]$Instance='main',
    [ValidateRange(1,86400)][int]$LeaseSeconds=86400,
    [switch]$Once
)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'process-lifecycle.ps1')
$sunnyWorkerScript=Join-Path $script:SunnyLifecycleRoot 'scripts\background_reconstruction.py'
$sunnyBase=Join-Path $script:SunnyLifecycleRoot ('state\background\'+$Instance)
$sunnyRecordPath=Join-Path $sunnyBase 'ownership.json'
function Read-BackgroundRecord {
    if(Test-Path -LiteralPath $sunnyRecordPath){return Get-Content -LiteralPath $sunnyRecordPath -Raw | ConvertFrom-Json}
    return $null
}
function Assert-BackgroundRecord($Record) {
    if($Record.workspace -cne $script:SunnyLifecycleRoot -or $Record.script -cne $sunnyWorkerScript -or $Record.base -cne $sunnyBase -or $Record.instance -cne $Instance){throw 'Worker ownership scope mismatch; no process affected.'}
    # Records bind exact executable, birth and command hash; a reused PID is never killed.
    if($Record.root_identity.executable_path -notmatch '[\\/]pythonw?(?:\d+(?:\.\d+)?)?\.exe$'){throw 'Unexpected worker executable; no process affected.'}
}
function Start-WindowlessBackgroundWorker([string]$Executable,[string[]]$Arguments,[string]$Directory) {
    # Explicit non-inheritance prevents a detached worker from keeping a
    # launcher's captured pipes open after that launcher has exited.
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public static class SunnyDetachedProcess {
 [StructLayout(LayoutKind.Sequential,CharSet=CharSet.Unicode)] struct STARTUPINFO {
  public int cb;public string lpReserved;public string lpDesktop;public string lpTitle;
  public int dwX,dwY,dwXSize,dwYSize,dwXCountChars,dwYCountChars,dwFillAttribute,dwFlags;
  public short wShowWindow,cbReserved2;public IntPtr lpReserved2,hStdInput,hStdOutput,hStdError;
 }
 [StructLayout(LayoutKind.Sequential)] struct PROCESS_INFORMATION {public IntPtr hProcess,hThread;public int dwProcessId,dwThreadId;}
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)]
 static extern bool CreateProcess(string app,StringBuilder command,IntPtr proc,IntPtr thread,bool inherit,uint flags,IntPtr env,string directory,ref STARTUPINFO startup,out PROCESS_INFORMATION info);
 [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr handle);
 public static int Start(string app,string command,string directory) {
  STARTUPINFO startup=new STARTUPINFO();startup.cb=Marshal.SizeOf(startup);startup.dwFlags=1;startup.wShowWindow=0;
  PROCESS_INFORMATION info;
  if(!CreateProcess(app,new StringBuilder(command),IntPtr.Zero,IntPtr.Zero,false,0x08000200,IntPtr.Zero,directory,ref startup,out info))throw new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error());
  CloseHandle(info.hThread);CloseHandle(info.hProcess);return info.dwProcessId;
 }
}
'@
    $sunnyCommand='"'+$Executable+'" '+($Arguments -join ' ')
    return [SunnyDetachedProcess]::Start($Executable,$sunnyCommand,$Directory)
}
Invoke-SunnyLifecycleLock {
    $sunnyOld=Read-BackgroundRecord
    if($sunnyOld){Assert-BackgroundRecord $sunnyOld}
    $sunnyLive=$sunnyOld -and (Test-SunnyProcessIdentity $sunnyOld.root_identity)
    if($Mode -eq 'status') {
        $sunnyStatePath=Join-Path $sunnyBase 'status.json'
        $sunnyState=if(Test-Path -LiteralPath $sunnyStatePath){Get-Content -LiteralPath $sunnyStatePath -Raw | ConvertFrom-Json}else{$null}
        [ordered]@{instance=$Instance;owned_running=[bool]$sunnyLive;ownership=$sunnyOld;worker=$sunnyState}|ConvertTo-Json -Depth 12
        return
    }
    if($Mode -eq 'stop') {
        if(-not $sunnyLive){[ordered]@{status='already_absent_or_identity_changed';instance=$Instance}|ConvertTo-Json;return}
        [ordered]@{requested_utc=[DateTime]::UtcNow.ToString('o');reason='explicit managed shutdown'}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $sunnyBase 'stop-request.json') -Encoding utf8
        $sunnyStopDeadline=[DateTime]::UtcNow.AddSeconds(18)
        while((Test-SunnyProcessIdentity $sunnyOld.root_identity) -and [DateTime]::UtcNow -lt $sunnyStopDeadline){Start-Sleep -Milliseconds 200}
        if(Test-SunnyProcessIdentity $sunnyOld.root_identity){$sunnyOld.processes=@(Get-SunnyOwnedTree $sunnyOld.root_identity);$sunnyStopped=@(Stop-SunnyOwnedTree $sunnyOld)}else{$sunnyStopped=@()}
        $sunnyRemaining=@($sunnyOld.processes|Where-Object {Test-SunnyProcessIdentity $_})
        if($sunnyRemaining.Count){throw 'Owned worker survived scoped shutdown.'}
        $sunnyOld.status='stopped';$sunnyOld.stopped_utc=[DateTime]::UtcNow.ToString('o');$sunnyOld|ConvertTo-Json -Depth 12|Set-Content -LiteralPath $sunnyRecordPath -Encoding utf8
        [ordered]@{status='stopped';remaining_owned_processes=0;stops=$sunnyStopped}|ConvertTo-Json -Depth 12
        return
    }
    if($sunnyLive){[ordered]@{status='reused_owned';created=$false;root_identity=$sunnyOld.root_identity}|ConvertTo-Json -Depth 8;return}
    $sunnyBackgroundRoot=Join-Path $script:SunnyLifecycleRoot 'state\background'
    if(Test-Path -LiteralPath $sunnyBackgroundRoot){
        foreach($sunnyExistingDirectory in @(Get-ChildItem -LiteralPath $sunnyBackgroundRoot -Directory)){
            $sunnyOtherPath=Join-Path $sunnyExistingDirectory.FullName 'ownership.json'
            if(-not(Test-Path -LiteralPath $sunnyOtherPath)){continue}
            $sunnyOther=Get-Content -LiteralPath $sunnyOtherPath -Raw|ConvertFrom-Json
            if($sunnyOther.workspace -ceq $script:SunnyLifecycleRoot -and $sunnyOther.script -ceq $sunnyWorkerScript -and (Test-SunnyProcessIdentity $sunnyOther.root_identity)){
                throw 'A SUNNY background worker already owns another queue; no second worker launched.'
            }
        }
    }
    New-Item -ItemType Directory -Path $sunnyBase -Force|Out-Null
    $sunnyStopPath=Join-Path $sunnyBase 'stop-request.json'
    if(Test-Path -LiteralPath $sunnyStopPath){Remove-Item -LiteralPath $sunnyStopPath}
    $sunnyPython=(Get-Command python -CommandType Application -ErrorAction Stop|Select-Object -First 1).Source
    $sunnyWindowlessPython=Join-Path ([IO.Path]::GetDirectoryName($sunnyPython)) 'pythonw.exe'
    if(-not(Test-Path -LiteralPath $sunnyWindowlessPython)){throw 'Windowless Python is unavailable; no console worker launched.'}
    $sunnyPython=$sunnyWindowlessPython
    $sunnyArgs=@('-X','utf8','-B',"`"$sunnyWorkerScript`"",'--base',"`"$sunnyBase`"",'--lease-seconds',[string]$LeaseSeconds)
    if($Once){$sunnyArgs+='--once'}
    $sunnyChildId=Start-WindowlessBackgroundWorker -Executable $sunnyPython -Arguments $sunnyArgs -Directory $script:SunnyLifecycleRoot
    $sunnyIdentity=Get-SunnyProcessIdentity $sunnyChildId
    if(-not $sunnyIdentity){throw 'Worker exited before ownership capture; inspect its scoped error log.'}
    $sunnyRecord=[pscustomobject]@{schema='sunny.background-ownership.v1';instance=$Instance;workspace=$script:SunnyLifecycleRoot;script=$sunnyWorkerScript;base=$sunnyBase;status='starting';root_identity=$sunnyIdentity;processes=@(Get-SunnyOwnedTree $sunnyIdentity);created_utc=[DateTime]::UtcNow.ToString('o');stopped_utc=$null}
    $sunnyRecord|ConvertTo-Json -Depth 12|Set-Content -LiteralPath $sunnyRecordPath -Encoding utf8
    $sunnyReady=$false
    $sunnyDeadline=[DateTime]::UtcNow.AddSeconds(10)
    do {
        $sunnyStatePath=Join-Path $sunnyBase 'status.json'
        if(Test-Path -LiteralPath $sunnyStatePath){try{$sunnyState=Get-Content -LiteralPath $sunnyStatePath -Raw|ConvertFrom-Json;$sunnyReady=$sunnyState.pid -eq $sunnyIdentity.pid -and ([DateTimeOffset]$sunnyState.started_utc).UtcDateTime -ge ([DateTimeOffset]$sunnyIdentity.creation_utc).UtcDateTime.AddSeconds(-1)}catch{}}
        if($sunnyReady){break}
        Start-Sleep -Milliseconds 100
    }while([DateTime]::UtcNow -lt $sunnyDeadline -and (Test-SunnyProcessIdentity $sunnyIdentity))
    if(-not $sunnyReady){
        if(Test-SunnyProcessIdentity $sunnyIdentity){
            $sunnyRecord.status='live_readiness_unconfirmed'
            $sunnyRecord|ConvertTo-Json -Depth 12|Set-Content -LiteralPath $sunnyRecordPath -Encoding utf8
            [ordered]@{status='live_readiness_unconfirmed';created=$true;root_identity=$sunnyIdentity;state_directory=$sunnyBase;detail='Verified owned process remains alive. Readiness polling timed out; process preserved and no duplicate launched.'}|ConvertTo-Json -Depth 8
            return
        }
        throw 'Managed worker exited before readiness; no process was restarted or killed.'
    }
    $sunnyRecord.status='started_owned';$sunnyRecord|ConvertTo-Json -Depth 12|Set-Content -LiteralPath $sunnyRecordPath -Encoding utf8
    [ordered]@{status='started_owned';created=$true;root_identity=$sunnyIdentity;state_directory=$sunnyBase}|ConvertTo-Json -Depth 8
}
