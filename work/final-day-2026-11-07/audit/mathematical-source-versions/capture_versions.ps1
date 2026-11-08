param([switch]$VerifyOnly)
$ErrorActionPreference = 'Stop'
$captureRoot = [IO.Path]::GetFullPath($PSScriptRoot)
$projectRoot = [IO.Path]::GetFullPath((Join-Path $captureRoot '../../../..'))
$manifestPath = Join-Path $captureRoot 'version-manifest.json'
$censusPath = Join-Path $projectRoot 'work/final-day-2026-11-07/audit/deliverables.json'

function Get-BytesHash([byte[]]$Bytes) {
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($algorithm.ComputeHash($Bytes))).Replace('-','').ToLowerInvariant() }
    finally { $algorithm.Dispose() }
}
function Project-Path([string]$Path) {
    $resolved = [IO.Path]::GetFullPath((Join-Path $projectRoot $Path))
    if (-not $resolved.StartsWith($projectRoot.TrimEnd('\','/')+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) {
        throw 'Source reference escapes the authorized project'
    }
    return $resolved
}
function Relative-Path([string]$Path) {
    return $Path.Substring($projectRoot.TrimEnd('\','/').Length+1).Replace('\','/')
}
function Capture-Bytes([string]$Path,[string]$ExpectedHash='') {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw ('Required source unavailable: '+$Path) }
    $before = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    $sourceInfo = Get-Item -LiteralPath $Path
    $raw = [IO.File]::ReadAllBytes($Path)
    $actual = Get-BytesHash $raw
    $after = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($before -ne $actual -or $after -ne $actual -or $raw.Length -ne $sourceInfo.Length) {
        throw ('Source changed while being read: '+$Path)
    }
    if ($ExpectedHash -and $actual -ne $ExpectedHash.ToLowerInvariant()) { throw ('Expected source hash differs: '+$Path) }
    $targetDirectory = Join-Path $captureRoot ('by-sha/'+$actual)
    $null = [IO.Directory]::CreateDirectory($targetDirectory)
    $target = Join-Path $targetDirectory 'content.json'
    if (Test-Path -LiteralPath $target) {
        if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $actual) { throw 'Existing content-addressed snapshot is corrupt' }
    } else {
        $stream = [IO.File]::Open($target,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
        try { $stream.Write($raw,0,$raw.Length) } finally { $stream.Dispose() }
    }
    if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $actual) { throw 'Snapshot readback hash mismatch' }
    if ((Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $actual) { throw 'Source changed during capture' }
    $status = $null; $reportedDates = @{}
    try {
        $document = [Text.Encoding]::UTF8.GetString($raw) | ConvertFrom-Json
        if ($document.PSObject.Properties.Name -contains 'status') { $status = $document.status }
        foreach ($name in @('computed_utc','generated_utc','created_utc','timestamp_utc','updated_utc')) {
            if ($document.PSObject.Properties.Name -contains $name) { $reportedDates[$name]=$document.$name }
        }
    } catch { throw ('Mathematical source JSON could not be parsed: '+$Path) }
    return [ordered]@{
        path=(Relative-Path $target); sha256=$actual; availability='VERIFIED_EXACT_BYTES'; bytes=$raw.Length;
        recovered_from=(Relative-Path $Path); observed_source_modified_utc=$sourceInfo.LastWriteTimeUtc.ToString('o');
        reported_source_status=$status; reported_source_dates=$reportedDates;
        capture_check='BEFORE_HASH_EQUALS_READ_BYTES_EQUALS_AFTER_HASH_EQUALS_SNAPSHOT_HASH'
    }
}
function Verify-Manifest {
    $document = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    $sourceCensus = Get-Content -LiteralPath (Project-Path $document.source_census.snapshot_path) -Raw | ConvertFrom-Json
    if ((Get-FileHash -LiteralPath (Project-Path $document.source_census.snapshot_path)).Hash.ToLowerInvariant() -ne $document.source_census.sha256) { throw 'Preserved census hash mismatch' }
    $rows = @($sourceCensus.requirements | Where-Object { $_.id -match '^M0[1-8]$' })
    if ($rows.Count -ne 8 -or $document.sources.Count -ne $document.counts.unique_paths) { throw 'Source coverage count mismatch' }
    foreach ($row in $rows) {
        foreach ($evidence in $row.evidence) {
            $entry = @($document.sources | Where-Object { $_.original_path -eq $evidence.path })
            if ($entry.Count -ne 1 -or $entry[0].original_sha256 -ne $evidence.sha256 -or $entry[0].per_M_ids -notcontains $row.id) { throw 'Manifest does not bind exact original census evidence' }
        }
    }
    foreach ($entry in $document.sources) {
        foreach ($version in @($entry.initial_version,$entry.current_version)) {
            if ($version.availability -ne 'VERIFIED_EXACT_BYTES') { throw 'An exact version is unavailable' }
            $target = Project-Path $version.path
            if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $version.sha256 -or (Get-Item -LiteralPath $target).Length -ne $version.bytes) { throw 'Immutable version snapshot changed' }
            $null = Get-Content -LiteralPath $target -Raw | ConvertFrom-Json
        }
        if ($entry.initial_version.sha256 -ne $entry.original_sha256) { throw 'Initial version does not match initial census SHA' }
        $relation = if ($entry.current_version.sha256 -eq $entry.original_sha256) { 'UNCHANGED_INITIAL_BYTES' } else { 'NEWLY_OBSERVED_VERSION' }
        if ($entry.version_relation -ne $relation) { throw 'Version classification mismatch' }
    }
    return $document
}
if ($VerifyOnly) {
    $verified = Verify-Manifest
    @{status='PASSED';unique_sources=$verified.sources.Count;initial_versions=$verified.sources.Count;current_versions=$verified.sources.Count;drifted=$verified.counts.drifted; live_sources_required=$false} | ConvertTo-Json
    exit 0
}
if (Test-Path -LiteralPath $manifestPath) { throw 'Version manifest already exists; use -VerifyOnly rather than overwrite' }
$censusSnapshot = Capture-Bytes $censusPath
$census = Get-Content -LiteralPath (Project-Path $censusSnapshot.path) -Raw | ConvertFrom-Json
$requirements = @($census.requirements | Where-Object { $_.id -match '^M0[1-8]$' })
if ($requirements.Count -ne 8) { throw 'Exactly eight original mathematical output requirements required' }
$allEvidence = @($requirements | ForEach-Object { $row=$_; foreach($entry in $row.evidence) { [PSCustomObject]@{id=$row.id;entry=$entry} } })
$paths = @($allEvidence | ForEach-Object { $_.entry.path } | Sort-Object -Unique)
$sources = @()
foreach ($originalPath in $paths) {
    $references = @($allEvidence | Where-Object { $_.entry.path -eq $originalPath })
    $expected = @($references | ForEach-Object { $_.entry.sha256 } | Sort-Object -Unique)
    if ($expected.Count -ne 1 -or -not $expected[0]) { throw ('Conflicting or absent initial source hashes: '+$originalPath) }
    $current = Capture-Bytes (Project-Path $originalPath)
    if ($current.sha256 -eq $expected[0]) {
        $initial = $current
        $relation = 'UNCHANGED_INITIAL_BYTES'
    } else {
        $candidate = Project-Path ('data/raw/reconstruction-integrations/'+$expected[0]+'/'+[IO.Path]::GetFileName($originalPath))
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { throw ('Exact initial version not retrieved: '+$originalPath) }
        $initial = Capture-Bytes $candidate $expected[0]
        $relation = 'NEWLY_OBSERVED_VERSION'
    }
    $sources += [ordered]@{
        original_path=$originalPath; original_sha256=$expected[0];
        per_M_ids=@($references | ForEach-Object { $_.id } | Sort-Object -Unique);
        original_evidence_refs=@($references | ForEach-Object { [ordered]@{requirement_id=$_.id;original_evidence=$_.entry} });
        initial_version=$initial; current_version=$current; version_relation=$relation;
        data_role='DERIVED_SCIENTIFIC_STATE'; historical_truth='NOT_EVALUATED_BY_VERSION_CAPTURE';
        version_preference='NO_CANONICAL_OR_SCIENTIFIC_PREFERENCE_ASSERTED'
    }
}
$manifest = [ordered]@{
    schema='sun.mathematical-source-versions.v1';captured_utc=[DateTime]::UtcNow.ToString('o');workspace=$projectRoot;
    source_census=[ordered]@{path=(Relative-Path $censusPath);sha256=$censusSnapshot.sha256;snapshot_path=$censusSnapshot.path};
    counts=[ordered]@{requirements=$requirements.Count;evidence_references=$allEvidence.Count;unique_paths=$paths.Count;
        current_versions_verified=$sources.Count;initial_versions_verified=$sources.Count;
        drifted=@($sources | Where-Object { $_.version_relation -eq 'NEWLY_OBSERVED_VERSION' }).Count;
        unique_content_versions=@($sources | ForEach-Object { $_.initial_version.sha256; $_.current_version.sha256 } | Sort-Object -Unique).Count};
    requirements_original=$requirements;sources=$sources;
    policy='Exact original requirement/status objects retained; both byte versions preserved without semantic reclassification. New observations of derived scientific state are not historical truth. Consumers must verify snapshot hashes and must not fall back to mutable live paths.'
}
$json = $manifest | ConvertTo-Json -Depth 100
$rawManifest = [Text.UTF8Encoding]::new($false).GetBytes($json+"`n")
$manifestStream=[IO.File]::Open($manifestPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try { $manifestStream.Write($rawManifest,0,$rawManifest.Length) } finally { $manifestStream.Dispose() }
$verified=Verify-Manifest
@{status='PASSED';manifest=(Relative-Path $manifestPath);manifest_sha256=(Get-FileHash -LiteralPath $manifestPath).Hash.ToLowerInvariant();counts=$verified.counts;drifted_paths=@($verified.sources | Where-Object { $_.version_relation -eq 'NEWLY_OBSERVED_VERSION' } | ForEach-Object { $_.original_path })} | ConvertTo-Json -Depth 6
