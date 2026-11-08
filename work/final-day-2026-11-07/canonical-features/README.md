# Canonical G0 feature bridge

This adapter connects the exact frozen fifteen-script table to the existing articulatory and NumPy functions. It imports the accepted G0 parser instead of the earlier manually transcribed table, preserving all540positions, all three raw fields, source coordinates and stable cell identities.

The main arrays have shape15×36×20: fifteen articulatory features followed by five geometric descriptors. Each value has an availability mask. The normalized view uses the existing zero-preserving normalization. An all-zero cosine is undefined and cannot establish similarity.

Supported atomic sound values occupy the main articulatory block. Ordered alternatives and sequences retain their native15Dsegment features, stress, modifiers and coarse-feature limitations in a JSON sidecar; they are never averaged into a fictitious phoneme. English letter names remain typed as names and excluded from phonemic vectorization. Old Persian retains its three vowel signs and33syllabograms. Four supplied Etruscan question marks, the Sabaic unresolved s³ label and159blank positions remain different states.

Geometry defaults to five zeros and five false masks. No historical shape is inferred from a Unicode proxy. The optional explicit font renderer reuses the existing implementation and records the exact glyph, font SHA-256, rendering size and threshold. It measures that modern font only.

The canonical source and imported implementations are pinned in source-bindings.json. Derived output contains matrix.npz, vectors.json, summary.json, source.tsv, manifest.json and a human-readable README. The archive contains no object arrays and loads with allow_pickle=False. Fixed ZIP timestamps and canonical JSON make repeated bundles byte-identical within the declared implementation/environment.

Run acceptance through an authorized Python environment:

    python -B -m unittest discover -s work/final-day-2026-11-07/canonical-features -p test_canonical_features.py -v

Write a new strict bundle:

    python -B work/final-day-2026-11-07/canonical-features/run_canonical.py --output work/final-day-2026-11-07/results/canonical-features-v2

The output directory must be new. The adapter edits no original source, feature dictionary or frozen SUN kernel. Its arrays describe the supplied comparison table; they do not establish historical glyph topology, genealogy, original pronunciation, musical frequency or a recovered universal root mechanism.

The existing coarse feature limitations remain unchanged: the main15Dspace merges several articulatory distinctions and omits vowel quality, aspiration and length as separate dimensions. Where supported, the original parser retains those extended values in the sidecar. Untied affricates and diphthongs remain literal segment sequences; no new historical segmentation is asserted. Normalization is a numerical convention, not a calibrated perceptual or historical distance.

The coordinator observed the intended missing-module failure before implementation, then executed all five canonical acceptance tests successfully, exit0. The tests cover exact540-cell/raw-field conservation, typing and unavailable values, atomic emphasis and ordered alternatives, deterministic normalized artifacts and strict absent geometry, and rejected source/import-binding tampering. This is an attributed coordinator result; the restricted child did not execute Python.

The coordinator also executed the strict CLI successfully, exit0. Independent artifact readback verified the five manifest-listed files by size and SHA-256. The generated summary reports282atomic sound values,22ordered alternatives,46sequences,26excluded English names,4unknown readings,1unresolved label and159blanks, covering540positions. No geometric cell is available in this strict run. See artifact-readback.json and handoff.json for the distinct execution and byte-binding evidence. Optional font-proxy execution was not tested in this bridge run; its original implementation remains separately preserved.

An independent review then found that v1 accepted deliberately altered sidecar fields and derived arrays even though its original observed output was correct. The coordinator reproduced thirteen failing tamper subtests before correction. Method canonical-v2 now derives the complete expected sidecar and arrays afresh from the same canonical bytes and pinned implementations, then requires exact field, type, dtype and value equality. Both public construction and writing validate; there is no caller-selectable bypass flag.

The coordinator's fresh seven-test suite and v2 CLI both passed, exit0. Independent readback verified all five v2 payloads, the current bridge-code hash, and byte-identical matrix.npz and source.tsv files between v1 and v2. The v1 bundle and exact v1 source preimage remain preserved; no corruption of those observed data is claimed. The current accepted bundle is results/canonical-features-v2, with artifact-readback-v2.json recording the new validation. The numerical features and historical limitations are unchanged.
