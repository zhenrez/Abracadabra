# Mathematical evidence source versions

`version-manifest.json` binds all evidence references for the original M01–M08 requirements to immutable byte snapshots. It retains the eight original requirement objects and their statuses without semantic reclassification. The entire original106-row census is independently preserved by content hash.

Observed reconciliation:53references resolve to12unique paths. All12current versions and all12initial versions are available as verified exact bytes. Ten paths are unchanged. Two paths have a newly observed version: `state/reconstruction/master-score.json` and `state/reconstruction/orientation-predictions.json`. Their initial bytes were found in the existing `data/raw/reconstruction-integrations/<expected-sha>/` archives and independently matched the original census hashes before capture.

There are14distinct mathematical content versions, plus one content-addressed copy of the original census. Snapshot paths are project-relative and use `by-sha/<sha256>/content.json`. No original source was modified. Capture checked the source hash before reading, the hash of the actual bytes read, the source hash after reading, and the snapshot hash; all had to agree. Existing content-addressed files are verified and never overwritten.

Consumers should use `sources[].initial_version.path` when replaying the exact initial census, checking its SHA against `sources[].original_sha256`. `current_version.path` preserves the additional observed version. Both remain useful evidence. Neither filename, date nor successful engineering replay establishes scientific or historical truth or a preference between versions.

Verify the immutable manifest without requiring mutable live source files:

```powershell
& 'work/final-day-2026-11-07/audit/mathematical-source-versions/capture_versions.ps1' -VerifyOnly
```

The executed verification passed with exit0:12unique sources,12initial versions,12current versions and two changed paths. `verification-receipt.json` records the actual returned result. The capture script refuses to overwrite an existing manifest; later captures require a separately identified version record.

Source status and reported dates are metadata copied from JSON-decoded fields where supplied; file modification timestamps are separately labeled. Exact lexical representations remain recoverable from the original byte snapshots. A new snapshot is a newly observed version of derived scientific state, not a historical attestation or automatic scientific correction.
