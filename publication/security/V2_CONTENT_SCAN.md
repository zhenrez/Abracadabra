# Selected-product content refresh

The versioned delta scanner executed successfully with exit 0 in 239.2 seconds.
All 6,101 selected product files were hashed and bound to 2,475,522,823 observed
bytes. The final hash pass matched every bound file, with no read errors, pattern
findings, or changes observed during individual reads or the final pass.

Exact prior content hashes reused the v1 no-hit result for 5,779 text files.
Another 115 fresh text digests were scanned once, with one additional duplicate
reusing a fresh result. All 195 binary files and 11 all-zero diagnostics have
separate source roles; no OCR or audio/private-content certification is claimed.

The v2 JSONL covers every selected file, including binaries, with explicit `kind`,
`method`, and `text_pattern_status` fields. A JSONL row must not be interpreted
automatically as a text-pattern scan. The report's `skipped` array preserves that
distinction.

Final readback found 31 changed v1 text paths and 16 regenerated delivery
screenshots. Current screenshot hashes and all 17 new media roles are recorded in
`media-review-v2.LOCAL-ONLY.json`. The original 17 media holds remain; the separate
18-candidate exclusion ledger also retains the restricted full HTML capture.

Fourteen paths differed from the preceding metadata inventory by a total of
24,210 bytes before their scans. Their exact current bytes remained stable during
the bounded observation. `v2-scan-readback.LOCAL-ONLY.json` lists those differences;
copying must bind the current observed hashes rather than stale metadata sizes.

V1 receipts were not overwritten. This is a finite per-file observation, not an
atomic filesystem snapshot or a claim about future writes. Publication rights,
historical conclusions, and remote publication are separate decisions. No Git or
remote operations were performed by this scanning unit.
