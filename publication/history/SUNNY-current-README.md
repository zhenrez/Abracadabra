# SUNNY

**Symphonia Universalis Numinous Nominal YARN**

This is a working research handoff, with a usable visual workbench and reproducible bounded calculations. **The complete scientific reconstruction is unfinished.** All sixteen goals and eight mathematical deliverables retain their original scope; software checks do not settle historical sound, global geometry, calendars or zodiacal orientation.

## Start with the visuals

Double-click **Open SUNNY.cmd**, or open [the systems guide](web/delivery-2026-11-07/system-guide.html) in a browser. It works offline. [The workbench](web/delivery-2026-11-07/index.html) links the atlas, native Western/Chinese/Indian music, Biblical witness comparisons, color carriers, construction classes, wheels, candidate geometry, source-reading comparisons, score, bridges, constraints, calendars, sources and Jev receipts.

The guide explains every **captured** hierarchy view and its actual units. Select a source, unit and record to trace its typed relationships and inspect GEN/MEM/TIME/ADR/FUNC/TRN. Unknown generations, sound assignments and joins remain visibly unknown. This does not claim that every participating historical system or generational class has already been reconstructed.

![The systems guide](docs/evidence/delivery-2026-11-07/guide-overview-desktop.png)

- 37 source-qualified hierarchy views; 35,072 records and 89,971 relationships, preserving every earlier record.
- 7,911 generated anonymous membership occurrences, counted separately from named identities and unique beings.
- 15 executable source-qualified score views, including four untimed comparative-reading annotations.
- 30 distinct supplied images preserving all 36 recorded occurrences.
- A/B/C remain alternative primordial starting configurations; no unsupported primordial-to-legion joins are inserted.

## What is established within the stated assumptions

The [delivery report](docs/delivery-2026-11-07/DELIVERY.md) separates results, source conditions and missing premises. It includes the exact timing-anchor solver, conditional phonological-history constraints, primary-source spelling correction, context-sensitive reading relations and phase-observation designs.

The [phase-probe calculation](docs/delivery-2026-11-07/PHASE_PROBE_DESIGNS.md) classifies all 10,296 pairs of 144 R/L-word occurrences: 4,608 distinguish twelve optional fixed-label phase completions and 5,688 retain explicit collisions. Historical source-to-phase observations are still missing. The earlier coordinate-orbit classification is reused and identified as prior work.

The [native-system delivery report](docs/delivery-2026-11-07/NATIVE_SYSTEMS_DELIVERY.md) explains the bounded Indian (2,556) and Western (2,670) mixed-unit censuses, Chinese 2,240 records / 1,671 mixed memberships, genealogy/legion limits and class construction. These totals do not establish complete musical universes or global generation assignments.

Current verification: **48 main-workbench browser groups, 13 native-system groups, 7 guide groups, 237 view/unit selections, 47 focused tests, exact offline hydration and an independent 10,296-pair oracle**. The 22-module source-fidelity check reports zero errors. All eight scientific deliverables remain partial. See [the exact validation record](state/delivery-2026-11-07/final-validation.json).

## Source preservation

Original research files remain at their recorded local paths, including `data/raw`. The [original-path manifest](state/publication/large-files-manifest.json) preserves the six large-source entries and their hashes. The current offline visuals open directly in this workspace; no archive restoration or GitHub transfer is required.

Earlier publication preparation produced a byte-preserving representation in `work/publication/large`. Its [historical verification report](state/publication/large-files-verification.json) records checks of six source files and 420 parts. The planned `archives/large-files` repository directory is not present, and publication was cancelled. The manifest and restoration tools retain that historical packaging context. A checksum proves byte integrity, not historical authenticity or SQLite logical consistency.

## Reproduce calculations and live Jev

```powershell
npm ci
npm run build
node --max-old-space-size=3072 --test --test-concurrency=2 tests/phase-probe-designs.test.mjs tests/reading-relations.test.mjs tests/reading-integration.test.mjs tests/prediction.test.mjs tests/score.test.mjs tests/hierarchy.test.mjs tests/musical-hierarchies.test.mjs tests/generational-classes.test.mjs tests/native-system-integration.test.mjs tests/delivery-data-hydration.test.mjs
powershell -File scripts/bootstrap-research.ps1 -CheckJevSource
```

[Reproducibility instructions](docs/publication/REPRODUCIBILITY.md) specify research dependencies and the public Jev source/model pins. Environments, dependency caches and upstream model weights are reconstructed rather than committed. Live decisions require the actual pinned AgentJev-0.6B service; the offline guide does not. [Full inference receipts](state/jev-receipts) distinguish local execution, historical hosted results and automatic observations. Hosted account/billing remains unverified.

Source-fidelity and plugin guard checks also depend on their recorded source paths and installed verifier versions. A clean environment, complete source restoration and full-project test pass are distinct claims; consult the actual bootstrap and validation reports for what ran.

## Continue without restarting

Read [CONTINUE.md](CONTINUE.md), [task state](state/task.json), [the full acceptance matrix](docs/delivery-2026-11-07/ACCEPTANCE.md) and [plugin capability evidence](docs/PLUGIN_CAPABILITIES.md). Keep original symbols/sounds, language and grammar before revised readings, changed hierarchies and downstream calendar/zodiac rectification. Native musical structure participates throughout; historical reasoning repair remains parallel.

The GitHub publication request was **cancelled by the user**. No timed branch update remains active. [Publication state](state/publication) must distinguish prepared Git objects, an actual branch update and remote readback. No force push is authorized. The prior README is preserved in `docs/publication/history`.
