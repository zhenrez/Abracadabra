# SUN / ARIADNE evidence workbench

Open `SUN_ARIADNE_Workbench.html` locally. It is a standalone interactive view of the supplied delivery results; it requires no server, network connection, account or installation.

The five sections provide:

- **Evidence:** all540 native source positions, with tradition, reading-state and Unicode search filters; blank positions and unknown readings remain distinct. Select a row to inspect every supplied field.
- **Musical models:** seven Western mode profiles, the twelve-lü generation sequence and formal contexts, two22-unit grāma allocations, named mūrchanās, and72melakarta configurations with36Madhyama pairs.
- **Compression:** actual coding measurements and full coding/fold records, with their conditional and historical limits.
- **Relationships:** exact declared positive and negative mathematical controls, retaining all residuals and the historical reconstruction boundary.
- **Delivery board:** all106 source requirements, their current engineering assessments, separately labeled original audit statuses, gate decisions, source references and unresolved limitations.

Every original JSON field remains embedded in the full record and can be exported. `dashboard-data.snapshot.json` preserves the exact original source bytes independently. The derived `current_delivery` and `current_delivery_source` fields bind the separate current assessment document and its SHA-256; `current-deliverables.snapshot.json` preserves that document's original bytes. Original requirement rows remain verbatim. Display formatting does not replace the source. No cultural glyph-to-pitch correspondence, frequency tuning or historical conclusion is invented by the interface.

The musical-model section also includes the preserved first Sefer baseline, with its22letter slots,29tagged states and231/462/484pair constructions. These figures come from the referenced Unit001 acceptance receipt, preserved separately in `sefer-baseline.snapshot.json` with its source hash. The Sefer view explicitly identifies a structural letter model and introduces no musical pitch assignment.

Rebuild after the delivery results change:

```powershell
python -B work/final-day-2026-11-07/dashboard/build_dashboard.py
python -B -m unittest discover -s work/final-day-2026-11-07/dashboard -p test_dashboard.py -v
```

The builder reads `../results/dashboard-data.json`, the separate `../current-deliverables.json`, and the identified preserved Sefer receipt. `--assessments` can select an explicit assessment document. It rejects altered original rows, mismatched coverage and duplicate requirement identities. A missing primary evidence file produces an explicit waiting state and exit2; it does not populate invented counts. A successful build returns exit0 and writes `build-receipt.json` with source, assessment, Sefer, template and HTML hashes. Python tests check exact data recovery, source-byte preservation, current-versus-original status separation, script-safe embedding, count validation and all requested surfaces.

The earlier interface version passed seven real Chromium interaction groups with zero page errors and desktop/mobile screenshots. The revised checker requires nine groups, adding the current-versus-original EG5 distinction and source-bound Sefer counts. A new pass applies to the revised interface only after that checker executes successfully; its actual outcome is recorded in `browser-verification.json`. Root uses the existing cached Playwright and installed Chromium through its approved execution route. Earlier browser-version mismatch, sandbox launch denial and aborted approval remain separately recorded in `browser-attempt-history.json`. No dependency download or security bypass is used.

`browser-verification.json` records actual browser behavior and checked input hashes. Each successful browser run automatically writes and reads back `browser-data-bindings.json`, binding the receipt and screenshots to the current source, HTML, template, build receipt, current-assessment snapshot and original ledger, and Sefer snapshot and preserved receipt. The browser itself checks that original source fields remain exact and current statuses match the source catalog; it rejects changed inputs during the run. Earlier evidence, musical-model and mobile screenshots received visual inspection, but that observation is not automatically inherited by a later screenshot. These are interface checks, not historical or scientific certification.

The installed12ui-design guidance was read for the UI work. Its CLI was unavailable, so no hosted12ui generation or target-image conformance is claimed. The delivered local interface uses the existing source/verification boundaries and was checked in an actual browser. No audio, publishing, original-core modification or old-atlas replacement occurred.
