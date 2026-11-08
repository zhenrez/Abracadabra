# Workspace-scoped process identities. Never terminate by executable name alone.
$script:SunnyLifecycleRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$script:SunnyProcessDirectory = Join-Path $script:SunnyLifecycleRoot 'state\processes'

function Get-SunnyTextHash([string]$Text) {
    $sunnyHasher = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sunnyHasher.ComputeHash([Text.Encoding]::UTF8.GetBytes($Text)))).Replace('-', '').ToLowerInvariant() }
    finally { $sunnyHasher.Dispose() }
}

function Get-SunnyProcessIdentity {
    param([Parameter(Mandatory)][int]$ProcessId)
    $sunnyItem = Get-CimInstance Win32_Process -Filter "ProcessId=$ProcessId" -ErrorAction SilentlyContinue
    if (-not $sunnyItem -or -not $sunnyItem.ExecutablePath -or -not $sunnyItem.CommandLine) { return $null }
    [pscustomobject]@{
        pid = [int]$sunnyItem.ProcessId
        parent_pid = [int]$sunnyItem.ParentProcessId
        creation_utc = $sunnyItem.CreationDate.ToUniversalTime().ToString('o')
        executable_path = [string]$sunnyItem.ExecutablePath
        command_sha256 = Get-SunnyTextHash ([string]$sunnyItem.CommandLine)
    }
}

function Test-SunnyProcessIdentity {
    param([Parameter(Mandatory)]$Identity)
    $sunnyCurrent = Get-SunnyProcessIdentity -ProcessId $Identity.pid
    return ($null -ne $sunnyCurrent -and ([DateTimeOffset]$sunnyCurrent.creation_utc).UtcTicks -eq ([DateTimeOffset]$Identity.creation_utc).UtcTicks -and
        $sunnyCurrent.executable_path -ieq $Identity.executable_path -and $sunnyCurrent.command_sha256 -ceq $Identity.command_sha256)
}

function Get-SunnyOwnedTree {
    param([Parameter(Mandatory)]$Identity)
    if (-not (Test-SunnyProcessIdentity $Identity)) { return @() }
    $sunnyAll = @(Get-CimInstance Win32_Process)
    $sunnyTree = [Collections.Generic.List[object]]::new()
    $sunnyTree.Add($Identity)
    for ($sunnyIndex = 0; $sunnyIndex -lt $sunnyTree.Count; $sunnyIndex++) {
        $sunnyParent = $sunnyTree[$sunnyIndex]
        foreach ($sunnyChild in $sunnyAll) {
            if ($sunnyChild.ParentProcessId -eq $sunnyParent.pid -and $sunnyChild.CreationDate.ToUniversalTime() -ge ([DateTimeOffset]$sunnyParent.creation_utc).UtcDateTime) {
                $sunnyIdentity = Get-SunnyProcessIdentity -ProcessId $sunnyChild.ProcessId
                # A PID from an old snapshot may have been reused before this fresh read.
                if ($sunnyIdentity -and $sunnyIdentity.parent_pid -eq $sunnyParent.pid -and
                    ([DateTimeOffset]$sunnyIdentity.creation_utc).UtcTicks -eq ([DateTimeOffset]$sunnyChild.CreationDate).UtcTicks -and
                    $sunnyIdentity.executable_path -ieq $sunnyChild.ExecutablePath -and
                    $sunnyIdentity.command_sha256 -ceq (Get-SunnyTextHash ([string]$sunnyChild.CommandLine)) -and
                    (Test-SunnyProcessIdentity $sunnyParent) -and -not ($sunnyTree.pid -contains $sunnyIdentity.pid)) { $sunnyTree.Add($sunnyIdentity) }
            }
        }
    }
    return $sunnyTree.ToArray()
}

function Stop-SunnyOwnedTree {
    param([Parameter(Mandatory)]$Record)
    $sunnyIdentities = @($Record.processes)
    if ($Record.root_identity -and (Test-SunnyProcessIdentity $Record.root_identity)) {
        $sunnyIdentities += @(Get-SunnyOwnedTree $Record.root_identity)
    }
    $sunnySeen = @{}
    $sunnyResults = @()
    # Stop the root first so it cannot create new workers during cleanup.
    foreach ($sunnyIdentity in $sunnyIdentities) {
        if (-not $sunnyIdentity -or $sunnySeen.ContainsKey([string]$sunnyIdentity.pid)) { continue }
        $sunnySeen[[string]$sunnyIdentity.pid] = $true
        if (-not (Test-SunnyProcessIdentity $sunnyIdentity)) {
            $sunnyResults += [pscustomobject]@{pid=$sunnyIdentity.pid; status='absent_or_identity_changed'}
            continue
        }
        Stop-Process -Id $sunnyIdentity.pid -Force -ErrorAction SilentlyContinue
        try { Wait-Process -Id $sunnyIdentity.pid -Timeout 5 -ErrorAction SilentlyContinue } catch { }
        if (Test-SunnyProcessIdentity $sunnyIdentity) { throw "Owned process $($sunnyIdentity.pid) did not exit." }
        $sunnyResults += [pscustomobject]@{pid=$sunnyIdentity.pid; status='stopped_verified_identity'}
    }
    return $sunnyResults
}

function Invoke-SunnyLifecycleLock {
    param([Parameter(Mandatory)][scriptblock]$Action)
    $sunnyMutex = [Threading.Mutex]::new($false, ('Local\SUNNY-' + (Get-SunnyTextHash $script:SunnyLifecycleRoot).Substring(0,24)))
    $sunnyAcquired = $false
    try {
        try { $sunnyAcquired = $sunnyMutex.WaitOne(60000) } catch [Threading.AbandonedMutexException] { $sunnyAcquired = $true }
        if (-not $sunnyAcquired) { throw 'Another SUNNY start/stop is still in progress; no additional worker was launched.' }
        & $Action
    } finally { if ($sunnyAcquired) { $sunnyMutex.ReleaseMutex() }; $sunnyMutex.Dispose() }
}

function Get-SunnyLoopbackPortState {
    param([Parameter(Mandatory)][int]$Port)
    $sunnyClient = [Net.Sockets.TcpClient]::new([Net.Sockets.AddressFamily]::InterNetwork)
    try {
        $sunnyConnect = $sunnyClient.ConnectAsync('127.0.0.1', $Port)
        # Windows on this host reports a closed loopback port after about two seconds.
        if (-not $sunnyConnect.Wait(3000)) { return 'inconclusive' }
        if ($sunnyClient.Connected) { return 'occupied' }
        return 'inconclusive'
    } catch {
        $sunnyConnectError = $_.Exception
        while ($sunnyConnectError -and -not ($sunnyConnectError -is [Net.Sockets.SocketException])) { $sunnyConnectError = $sunnyConnectError.InnerException }
        if ($sunnyConnectError -and $sunnyConnectError.SocketErrorCode -eq [Net.Sockets.SocketError]::ConnectionRefused) { return 'refused' }
        return 'inconclusive'
    } finally { $sunnyClient.Dispose() }
}

function Save-SunnyServiceRecord($Record) {
    New-Item -ItemType Directory -Path $script:SunnyProcessDirectory -Force | Out-Null
    $sunnyDestination = Join-Path $script:SunnyProcessDirectory ($Record.name + '.json')
    $sunnyTemporary = $sunnyDestination + '.' + [Guid]::NewGuid().ToString('N') + '.tmp'
    $Record | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $sunnyTemporary -Encoding utf8
    Move-Item -LiteralPath $sunnyTemporary -Destination $sunnyDestination -Force
}

function Start-SunnyManagedService {
    param(
        [Parameter(Mandatory)][ValidatePattern('^[a-z0-9-]+$')][string]$Name,
        [Parameter(Mandatory)][string]$Executable,
        [Parameter(Mandatory)][string[]]$Arguments,
        [Parameter(Mandatory)][string]$WorkingDirectory,
        [Parameter(Mandatory)][int]$Port,
        [Parameter(Mandatory)][scriptblock]$Probe,
        [ValidateRange(1,120)][int]$TimeoutSeconds = 60,
        [Parameter(Mandatory)][string]$LogStem
    )
    Invoke-SunnyLifecycleLock {
        $sunnyRecordPath = Join-Path $script:SunnyProcessDirectory ($Name + '.json')
        $sunnyOld = if (Test-Path -LiteralPath $sunnyRecordPath) { Get-Content -LiteralPath $sunnyRecordPath -Raw | ConvertFrom-Json } else { $null }
        $sunnyReady = $false
        try { $sunnyReady = [bool](& $Probe) } catch { }
        if ($sunnyReady) {
            $sunnyOwned = $sunnyOld -and (Test-SunnyProcessIdentity $sunnyOld.root_identity)
            if ($sunnyOwned) { $sunnyOld.processes = @(Get-SunnyOwnedTree $sunnyOld.root_identity); Save-SunnyServiceRecord $sunnyOld }
            return [pscustomobject]@{name=$Name; status=$(if ($sunnyOwned) {'reused_owned'} else {'existing_unmanaged'}); created=$false; record=$(if ($sunnyOwned) {$sunnyOld} else {$null})}
        }
        if ($sunnyOld -and (Test-SunnyProcessIdentity $sunnyOld.root_identity)) {
            throw "The recorded $Name worker is running but not ready. It was left intact; no duplicate was launched."
        }
        # On this host enumeration omitted a listener owned by the probing process.
        # The targeted connection is therefore required, with unknown results refusing a launch.
        $sunnyOccupied = [Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners() | Where-Object Port -EQ $Port
        $sunnyPortState = Get-SunnyLoopbackPortState $Port
        if ($sunnyOccupied -or $sunnyPortState -ne 'refused') { throw "Port $Port is occupied or could not be proven available. No worker was launched or stopped." }
        $sunnyProcess = $null; $sunnyRecord = $null
        try {
            $sunnyProcess = Start-Process -FilePath $Executable -ArgumentList $Arguments -WorkingDirectory $WorkingDirectory -WindowStyle Hidden -PassThru -RedirectStandardOutput ($LogStem + '.stdout.log') -RedirectStandardError ($LogStem + '.stderr.log')
            $sunnyIdentity = Get-SunnyProcessIdentity $sunnyProcess.Id
            if (-not $sunnyIdentity) { throw "$Name exited before its ownership identity could be recorded." }
            $sunnyRecord = [pscustomobject]@{schema_version=1; name=$Name; workspace=$script:SunnyLifecycleRoot; port=$Port; status='starting'; root_identity=$sunnyIdentity; processes=@(Get-SunnyOwnedTree $sunnyIdentity); recorded_utc=[DateTime]::UtcNow.ToString('o')}
            Save-SunnyServiceRecord $sunnyRecord
            $sunnyDeadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
            do {
                try { $sunnyReady = [bool](& $Probe) } catch { $sunnyReady = $false }
                if ($sunnyReady) { break }
                if (-not (Test-SunnyProcessIdentity $sunnyIdentity)) { throw "$Name exited before readiness." }
                Start-Sleep -Milliseconds 250
            } while ([DateTime]::UtcNow -lt $sunnyDeadline)
            if (-not $sunnyReady) { throw "$Name did not become ready within its startup limit." }
            $sunnyRecord.status = 'ready'; $sunnyRecord.processes = @(Get-SunnyOwnedTree $sunnyIdentity); Save-SunnyServiceRecord $sunnyRecord
            return [pscustomobject]@{name=$Name; status='started_owned'; created=$true; record=$sunnyRecord}
        } catch {
            $sunnyFailure = $_
            if ($sunnyRecord) { Stop-SunnyOwnedTree $sunnyRecord | Out-Null; $sunnyRecord.status='startup_failed_cleaned'; Save-SunnyServiceRecord $sunnyRecord }
            throw $sunnyFailure
        }
    }
}
