# SUN / ARIADNE inverse glyph–phoneme prototype

Implemented in a separate work directory. The frozen SUN kernel and all `src/*.ts` files were left untouched. This is a reproducible engineering prototype; actual Jev approval and historical mechanism identification remain open.

## Run and use

Dependencies: Python, NumPy, SciPy. Optional font extraction additionally uses Pillow and fontTools. These were already available on the execution host; no installation or global configuration change occurred.

From the project root, use new output directories:

```powershell
python work/ariadne-inverse/build_dataset.py
python -m unittest discover -s work/ariadne-inverse -p 'test_*.py' -v
python work/ariadne-inverse/run.py --output work/ariadne-inverse/my-analysis
python work/ariadne-inverse/numpy_pipeline.py --table-tsv work/ariadne-inverse/table.tsv --output work/ariadne-inverse/my-matrix
python work/ariadne-inverse/numpy_pipeline.py --font C:/Windows/Fonts/seguihis.ttf --output work/ariadne-inverse/my-font-proxy
```

Python API when this directory is on the import path:

```python
import numpy as np
from numpy_pipeline import phoneme_vector, raw_table_to_data, table_to_numpy
from numpy_pipeline import FontGeometry, validate_normalized, record_distance

p = phoneme_vector('tˤ')       # atomic 15-vector; null -> 15 zeros
data = raw_table_to_data(open('table.tsv', encoding='utf-8').read())
scripts, matrix = table_to_numpy(data)  # optionally geometry=FontGeometry(font_path)
assert matrix.shape == (15, 36)
assert matrix['vector'].shape == (15, 36, 20)
assert validate_normalized(matrix['normalized'])
saved = np.load('numpy-results/matrix.npz', allow_pickle=False)
```

The structured NumPy array has `vector`, `mask`, `normalized`, `kind`, `ipa`, `glyph`, and `details` fields. Each vector concatenates P(15) and G(5). Missing data produce zeros with false availability masks. `details` retains ordered candidate/segment vectors; an ambiguous or multi-segment value has a zero acoustic block in the atomic view, rather than a fabricated average phoneme. The NPZ exports numeric arrays, Unicode script names/column indices and kinds without pickle. Full ordered segment data and extensions are in `results-v2/vectors.json`; in-memory `details` includes the expanded concatenations.

## Feature contract

P order: bilabial, labiodental, dental/alveolar, postalveolar/palatal, velar, uvular/pharyngeal, glottal; stop, fricative, nasal, approximant/liquid, vowel; voiced, unvoiced, pharyngealized. Voicing uses complementary flags, so a voicing change affects two coordinates. This redundancy follows the requested 15-feature interface. It is not an independent extra articulatory degree of freedom.

Vowels have inapplicable consonantal-place bits masked out. Additional fields retain vowel height/backness/rounding, aspiration, labialization, duration, stress, raw IPA, and secondary place for /w/. These sidecars preserve information outside the deliberately coarse 15 dimensions. Trills, taps and lateral approximants still merge in the coarse manner class; raw IPA remains necessary. Literal `tˤ` is one segment. Slash alternatives remain separate candidates. Untied `ts`, `dʒ`, `tʃ` and vowel sequences preserve their strings and order without claiming affricate/diphthong boundaries. Unsupported labels fail explicitly; `s³` is retained unresolved rather than silently mapped to /s/. None of this constitutes measured acoustics: no audio was supplied.

G order: endpoint count, junction-region count, stroke-segment count, enclosed-background-hole count, reflection-axis count (0–4). `bitmap_geometry` accepts an ink bitmap and uses deterministic Zhang–Suen thinning, an 8-connected foreground skeleton and 4-connected background. Connected junction pixels contract to a single node. A stroke segment is a skeleton path between nodes; a closed component without nodes contributes one closed path. These are not recoverable pen-lift strokes. The four tested axes are vertical, horizontal and the two diagonals; exact pixel reflection is deliberately strict. Arbitrarily oriented reflection axes are not searched. Curves, touching strokes, calligraphic width and rasterization can change these descriptors.

`FontGeometry` checks the font character map and returns missing for unsupported glyphs; it never substitutes a tofu box or fallback font. Font SHA-256, size 96 and threshold 128 accompany every successful measurement. The supported modern font is a proxy, not a historical witness. `features.graph_features` separately accepts explicitly sourced embedded graphs, returns a richer 17-feature graph descriptor, and distinguishes cycle rank from bitmap hole count. Historical graph extraction remains unavailable until tracings or images are supplied.

Raw, whole-vector L2-normalized, and masked views are separate. Nonzero normalized vectors have unit norm; null vectors remain zero. Cosine on a zero vector is undefined. `record_distance` uses only jointly available informative blocks, normalizes each block, and returns NaN if nothing comparable exists. Feature scaling must be frozen on training data before a fitted multivariate model; whole-vector normalization alone does not balance count features against binary articulation. The coarse P distance cannot recover distinctions already collapsed by the encoding.

## Source and authority

`table.tsv` and `table.json` transcribe the current user-supplied glyph and IPA rows. The English approximation rows are not phonetic ground truth and are not used. No native conversation export was available: the tool catalog had no `read_thread`. Prior local text search did not recover this exact table before the user supplied it. The cached preview was data only.

Recovered project context: `state/task.json`, `docs/HUMMBL_PLAN.md`, `docs/PLUGIN_CAPABILITIES.md`, source modules, the existing cloud Jev receipt `a7009a917f2835b7e2034efaba8c58899acf40409b7e91ee36312193bf23818b.json`, and successful Supermemory retrieval. Archived instructions remain historical. The governing current scope is this bounded glyph–phoneme pipeline.

Important source limits:

- Proto-Sinaitic explicitly uses Phoenician Unicode proxies. Paleo-Hebrew shares the same displayed glyphs. Four rows also repeat the same IPA inventory. Those are dependent inputs, not four independent discoveries.
- Alphabet-column numbers are source order, not an established cross-script homology or time coordinate. No dated transitions, historical period values, witness images, or independent pronunciation validation are supplied.
- Old Persian values are syllabic/table readings. Its `ca`, `ja`, and English glosses warrant historical review: literal IPA /c/ and /j/ must not be silently replaced by /tʃ/ or /dʒ/. English entries are letter names. Square Hebrew combines alternatives/periods; Etruscan has four unknown values. Arabic is explicitly a proxy.
- The primary IPA chart supports feature terminology, not these historical reconstructions: https://www.internationalphoneticassociation.org/content/chart . Unicode identifies encoded Old Persian signs, not a universal sound mechanism: https://www.unicode.org/charts/PDF/U103A0.pdf .

## Measured results

The full transcription has 540 slots, 381 populated and 159 missing. Parsed cells: 283 single segments, 71 sequences, 22 alternative sets, four unknowns and one unresolved label. Across all candidate segment occurrences there are 484 occurrences and 61 distinct segment spellings, reduced to 31 distinct coarse vectors. Collision lists are exported so this loss cannot be mistaken for discovery.

Without a font/tracing, historical G availability is zero. The explicitly identified Segoe UI Historic font supplies proxy G for 307 of 381 populated cells; 74 unsupported glyphs remain masked. All 540 atomic-view vectors pass the nonzero-unit-norm/zero-vector validation. Font geometry is not used in historical model selection.

For the exploratory column diagnostic, 252 unmodified, unambiguous single-segment cells remain after exclusions. Leave-declared-block-out fits use three coarse dependency groups (Semitic, Greek-derived, Old Persian), fitting every prediction from other blocks. Column-majority prediction makes 211 errors/252 (83.73%); a training-global-majority baseline makes 248/252 (98.41%). With 199 seeded within-script column permutations, the observed advantage is 0.146825, permutation mean 0.011546, empirical upper-tail fraction 0.005. This is an exploratory diagnostic of the supplied alignment, not a historical significance test: there are only three coarse, still-related blocks, one with only three eligible test cells. Repeated source values, selective column conventions and exclusions materially limit interpretation.

Canonical table JSON is 99,060 bytes and zlib level-9 output 4,567 bytes. That includes repetitive schema and empty slots. It is serialization compression, not evidence for a generative law or a valid MDL comparison.

## Basis, operators, residuals and identifiability

`inverse.py` implements a finite, explicitly declared four-element action: toggle complementary voicing bits and toggle pharyngealization. Partition the observed coarse vectors into its orbits; choose an unvoiced, non-pharyngealized representative per orbit as a gauge. The result has 19 roots and reconstructs all 484 coarse observations with zero feature edits. One root per orbit is necessary and sufficient **under these fixed operators**. Zero error is guaranteed by this factorization; it does not validate the operators as ancient laws. Canonical roots can be unattested or physiologically inappropriate. Raw IPA, modifiers and vowel fields are typed residuals; no raw distinction is reconstructed from a collapsed vector alone.

For actual joint reconstruction, use a finite-state transducer with state q, operator o, transition q′=δ(q,o), and typed emissions of phoneme sequences and glyph graphs. Compare observations through a declared edit channel, allowing segment insert/delete/substitute, feature changes, graph node/edge edits and source-qualified allography. The root basis is the smallest state set within a predeclared candidate family, with operators and edits charged their own code lengths. The current table has emissions, not observed transitions. δ and a unique joint basis are consequently not identified here.

The next inference contract is: freeze candidate operator grammar and maximum state count; fit training-only roots/operator parameters/typed edit costs; minimize L(B)+L(T)+L(residuals|B,T), including witnesses, ambiguity choices and graph annotations. Compare against independent-inventory, known-transmission, copying/proxy and table-order models. Report equivalent survivor machines modulo state relabeling, geometric gauge and operator conjugacy; do not elect an absolute root by arbitrary naming. For an observation without a chronological/operator label, do not invent a transition.

Required separating tests: leave entire evidential lineages out; remove repeated proxies; shuffle columns preserving each inventory and mask; shuffle sound–glyph pairings within period/script; compare geometry-only and sound-only ablations; repeat independent graph tracings and explicit font/size/threshold perturbations; bootstrap over witnesses rather than individual dependent cells; test uncertain reading branches separately without optimizing them on held-out data; score predeclared predictions on newly acquired, independently transcribed material. Identifiability must be reported as a survivor class or non-identification, not hidden by low reconstruction error. No joint MDL search, learned historical transition system, independent historical holdout or acoustic validation ran.

## Checks and operational boundary

18 focused tests passed after the NumPy/TSV changes. They cover atomic emphasis, voicing, inapplicable vowel place, unknown/null distinctions, alternatives/sequences, malformed input, graph invariants, raster line/ring features, unsupported font coverage, stable font measurements, 36-column round trip, duplicate addresses, unit normalization, missing-aware distance, finite operator inversion, reproducibility and held-out label separation. Determinism is relative to recorded code, dependencies, input and font; it is not a platform-independent guarantee about rasterization.

The first CLI run wrote its outputs but failed when printing IPA through the Windows legacy console encoding. The output routine was corrected to escaped JSON; the fresh `results-v2` run is the final analytic result. Prior output folders are retained as execution history. `verification.json` binds final files, test results, numeric reproducibility, dependency versions and current source hashes. No Git repository metadata is available in this workspace, so no Git-based cleanliness or commit claim is made.

Actual Jev inference did not complete: hosted disclosure was rejected by automatic approval review; existing local Jev refused the connection after an authorized local diagnostic retry. `jev-attempt.json` preserves the full attempt and rejection. This prototype is provisional engineering, not Jev-approved substantive model selection. Permission to disclose the bounded project summary to the configured hosted endpoint remains an open gate. No fallback model, host vote or fixture replaces Jev.
