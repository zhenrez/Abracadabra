# EU-001R handoff

## A. Verified checkpoint

Authoritative workspace: `C:\Users\Brend\Documents\ChatGPT\SUN`. No Git metadata was established; no repository was initialized, no branch/commit/PR was created and no GitHub operation occurred. `eu001r-before.json` records the recovered implementation before this reconciliation. The aborted earlier tool call had actually created `sefer.py`; its behavior was inspected rather than rewritten.

The least-transformed matrix was recovered from the exact user-message event in this chat. Its UTF-8 text hash is `d76bee36607f67a72aad404dc98682f0ec647a9cbb0fb3f89df30230f58ca24c`. The serialized event and decoded text are separately preserved under `frozen/source/`. This is not a claim about original external-document bytes. The source contains 46 rows of 37 fields, 15 scripts, 540 positions, 381 populated glyph positions and 159 blanks, including English approximation rows. See `source-manifest.json` and `eu001r-verification.json`.

## B. Architecture decision

Retain the working matrix-specific G0 schema in `evidence.py` and Sefer adapter in `sefer.py`. Add `kernel.py` as a domain-independent provenance layer, linked through `migrate_matrix()`. A matrix witness is a specialized domain record, not the universal ontology. Immutable source bytes, evidence observations, claims, derivations, operator specifications and experiment receipts have distinct records. Separate transformation claims prevent execution from becoming historical attribution. Source licenses and revisions remain explicitly unverified where not known.

Twelve missing-data states distinguish blanks, damaged/illegible/missing signs, unknown pronunciation, supported silence, unattested/source-unavailable values, inferred/superseded/rejected interpretations and inapplicability. Typed domain records support epigraphy, reading layers, diagrams, exact quantities, narrative distinctions, normative rules and morphology without introducing their analytic engines. Operator definitions can be registered; unrestricted execution is denied. Append-only additions return a new immutable store and reject duplicate identities; this is an application contract, not filesystem write protection or an adversarial tamper-proof database.

G7 remains locked in the retained registry. No Western, Chinese, Indian, W72 reconstruction or historical-comparison model is implemented by this unit. Raw matrix normalization has no dependency on orientation models. Model descriptions emit no fictional MDL scores.

## C. Sources and assets

The EU-001R pasted request is the authority for this delta. `## Recommended approach add a Rabbi.txt` is supporting review data; its embedded instructions were not independently adopted. Its URLs are registered as bibliographic leads in `asset-registry.json`, with missing revision, licensing, chronology and responsible-maintainer fields left unverified. No bulk corpus acquisition occurred. T02–T12 fixtures are synthetic schema examples, not claimed ancient objects or retrieved manuscript samples.

The two named prior work-state logs were not retrieved in the bounded Desktop/morphiq-one filename search. The earlier source manifest, actual code, tests and records supplied direct continuity. This does not constitute a comprehensive search of every external location. Frozen SUN scientific 3/7/12 semantics and Sefer letter classes remain distinct namespaces. The existing frozen research context is retained verbatim.

## D. G0 evidence

All original 20 tests pass. Seven new kernel tests cover matrix migration, eleven additional schema fixtures (T02–T12), deterministic serialization, source references, immutable nested values, append-only identity, operator/claim distinction and exposed holdout rejection. These tests demonstrate representability; they do not validate the historical content of a synthetic example. Original G0 source-span, Unicode, unknown-value, proxy and duplicate/reference tests remain applicable. `kernel-evidence.json` and `normalized-evidence.json` preserve both common and specialized views.

## E. G1 evidence

The 14 existing G1 tests pass. The original six-test frozen Sefer suite also passes. The full regenerated demonstration JSON equals its recorded original, including the three previously checked demonstrations. `legacy-comparisons.json` contains full input, expected output and observed legacy-adapter output for complete carrier, missing Mem, duplicate occupancy and expanded states; no semantic/format difference was observed. The ambiguity, Resh, empty input, exhaustion, multiple completions and deterministic receipt cases remain in the G1 test suite.

Missing Mem remains legacy `Invalid`, suggestion `m`, harmonic distance null. The typed receipt reports incomplete structure and unique-under-model identifiability with historical support unverified. `r:1` has no invented phonetic realization. The 231/462/484 pair constructions remain distinct combinatorial spaces. Source-specific recension and Resh evidence is represented only in explicitly synthetic examples pending actual source recovery.

## F. Migration and prior experiments

Added: `kernel.py`, `test_kernel.py`, `reconcile_checkpoint.py`, `verify_reconciliation.py`, this handoff, and their machine-readable outputs. Earlier working algorithms and frozen references were retained. No frozen SUN source or earlier prototype was edited. Earlier PCA/description-length and permutation findings are reported-but-not-reexecuted, with hashes recorded; they were not rerun merely for activity.

Residual accounting reconciles as 136 compatible + 6 unpredicted + 234 unmapped + 4 unknown + 1 unresolved = 381 populated positions. The four unknowns are Etruscan; the unresolved label is Sabaic s³. Contested universal-root, acoustic-rotation, inventory-isomorphism, cryptographic-order, silent-Etruscan and universal harmonic-equivalence claims are quarantined in the verification record, not deleted or promoted.

## G. Gate ledger

G0: PARTIAL — matrix conservation and schema tests pass; broader authority and source-specific historical dependencies unresolved.

G1: PARTIAL — original compatibility reproduced; EU-001R certification depends on G0 and source-specific controls.

G2, G3, G4, G5, G6, G7: LOCKED. No downstream implementation or cross-orientation correspondence added.

## H. Verification and next checkpoint

Run `python -B work/unit001/verify_reconciliation.py`. Exact commands, exit codes, syntax checks, dependency-check outcome and logs are recorded in `eu001r-verification.json`, `unit_tests.log`, `original_six.log` and `dependency-check.log`. No type-checker, independent reviewer or new manual Jev decision is claimed. Existing plugin contracts were applied; the current SuperJev automatic observation is an observation, not routing or certification. No credentials were copied or displayed.

Next checkpoint: recover the two work-state logs and identify small source-pinned recension/Resh/diagram samples; strengthen their provenance controls before full EU-001R certification. Do not advance to G2. This is a verified partial engineering checkpoint, not a release, production-readiness claim or historical reconstruction result.
