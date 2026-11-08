# Western native orientation delivery

The native interval, mode, register and event contract is implemented in `western_model.py:WesternOrientation`. It reuses the preserved `work/unit002/western.py` exact arithmetic instead of replacing it. No Unit001, Unit002, frozen SUN or four-orientation file was changed.

`validate_native`, `encode`, `reconstruct` and `describe` implement the common orientation interface. Native evidence retains its source reference, identity, exact frequency ratio, octave register, onset, duration and voice. Encodings are bound to their canonical source representation and the reused implementation hash. Validation checks actual observations. A changed degree or reused event identity is rejected. Empty evidence is not evaluated. Partial seven-degree reconstruction enumerates the seven configured modes, retaining ambiguity and model-internal uniqueness separately from historical support. Description length remains explicitly unavailable until an evaluated coding scheme is supplied.

Exact frequency ratios remain separate from chromatic interval labels. The reused fifth and fourth compose to an octave. Twelve fifths exceed seven octaves by exactly 531441/524288. The tone-tone-limma tetrachord divides a fourth as 9/8 × 9/8 × 256/243 = 4/3. This is one configured division; it does not replace ancient genus distinctions. Rhythm scaling preserves exact onsets/durations and polyphonic voice identities. These event transformations do not claim a complete counterpoint grammar.

## Executed checks

Fourteen new contract tests and seven preserved Unit002 regression tests passed, exit0. The finite exact audit tested 255 inverse-transport cases: 17 registers from -8 through 8, five within-octave ratios and three intervals. All seven actual degree fixtures validate. Malformed profiles, nonpositive pitches, raw floating inputs, source-binding tampering and duplicate identities are rejected. Unique, ambiguous and infeasible reconstruction cases remain distinct.

The actual Mathbox computation runner executed `run_native.py` with a declared input contract, output cap and 90-second timeout. Its manifest records run status `completed`, child exit0, unchanged input hashes and result hashes. The actual manifest validator also exited0. Evidence: `computation-001/manifest.json`, `computation-001/native-results.json`, `mathbox-contract.json` and `mathbox-launch.json`. This establishes the stated finite assertions and preserved engineering regressions. Mathematical and source interpretation still require the recorded scope limits.

## Sources and coverage

`source-profiles.json` keeps Greek tetrachord material, modern diatonic modes, the Fludd monochord, the Kepler bridge and Completed Harmony independently addressable. `reuse-manifest.json` pins their existing local artifact hashes. MIT's Jowett translation of Plato's Timaeus, 35b–36b, was actually inspected for the ratio construction. Open Music Theory was actually inspected for modern mode rotations and its distinction from medieval church-mode range. Neither source identifies all modern mode labels with ancient Greek usages, nor establishes the earliest surviving manuscript. Exact available web-tool responses are preserved in `sources/`.

The Cornell Fludd catalogue route returned403; that failure is recorded. Its1617item is not equated with the separate local1638image. The frozen Kepler bridge remains explicitly a source-reported hypothesis with unresolved historical implications. The local Completed Harmony PDF is retained without manufacturing its full native interpretation or adopting an absolute frequency reference.

Native-core gate: **PASSED_BOUNDED_G2_NATIVE**. Full historical witness/profile coverage: **PARTIAL**. The remaining coverage concerns ancient genera, actual Fludd diagram transcription, Kepler source dynamics and Completed Harmony interpretation. No cross-orientation adapter is registered or activated by this delivery.

## Reproduction

Run `python -B work/final-day-2026-11-07/western/run_native.py --output work/final-day-2026-11-07/western/native-recheck.json` for a fresh native receipt. The existing Mathbox run is verified with its installed `validate_manifest.py` and the workspace root; a new Mathbox execution must use a fresh output directory. The exact executed argument list is retained in `mathbox-launch.json`.

Plugin use: Superpowers TDD was applied with observed failing tests before implementation and before the Fraction-binding fix. The Mathbox computation-audit skill, bundled runner and validator were actually used. The parent supplied the actual Jev strategy receipt. No child Jev inference, remote mathematical service or historical certification is claimed.
