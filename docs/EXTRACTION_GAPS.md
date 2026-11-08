# Extraction gap recovery

- [100%] Reproduce the current NPZ, archive-depth and JSONL extraction gaps against preserved source bytes.
- [100%] Obtain actual Jev method choices and implement source-preserving additions with a database backup.
- [100%] Run regression, exact-value, source hash, search and foreign-key checks; preserve counts and boundaries.

The two preserved JSONL snapshots are valid when split at physical LF bytes. The prior importer used Python `str.splitlines()`, which also splits legal U+2028 characters inside quoted JSON strings. This produced sixteen fragment-level parse errors spanning seven missing native records. These observations are saved in `evidence/gaps-jsonl-reproduction.json`; source bytes and existing records have not been changed.

The NPZ safely loads three `uint8` arrays using `allow_pickle=False`, with shapes16x32,32x24,24x8. The two depth-limited archives were inventoried before any database mutation:57 immediate members with4,455,029 uncompressed bytes and32 with700,348 bytes. Full names, sizes and member hashes are preserved in `evidence/gaps-inspection.json`.

The actual recovery methods, full model distributions and runtime identity will be attached through the shared Jev receipt log. These are extraction choices, not judgments about SUN's mathematical or historical content.

Current verified result supersedes the progress prose above: `evidence/gaps-repair-report.json` records7 recovered native records,2366 exact source-position rows,2359 retained locator-history rows and3 metadata/inventory documents. Existing message payloads and preserved source bytes are unchanged; source hash mismatches, invalid positions, foreign-key violations, duplicate/missing search IDs and orphan search IDs are all zero. The original backup and pre-repair report remain identified in that report. Current totals are2042 source occurrences,1032 conversation occurrences,59901 message/event records and1934 extracted/metadata documents.

The future importer uses physical LF bytes and exact UTF8 spans, covered by the regression preserving literal U+2028/U+2029 inside JSON strings. NPZ remains metadata-only under receipt20; array values are preserved in raw bytes and inspection evidence. The2 deferred ZIP inventories contain57 and32 immediate members; `evidence/deferred-zip-hash-overlap.json` finds every one of those89 byte hashes already indexed elsewhere. This reconciles byte presence only, without claiming full account coverage or semantic equivalence. The original slow verification attempt is retained; receipt42 selected the efficient ID set/count verification that passed.
