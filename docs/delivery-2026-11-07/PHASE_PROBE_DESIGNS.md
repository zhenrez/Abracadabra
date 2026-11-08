# Which two phase observations can distinguish the candidates?

**Two appropriately chosen observations can distinguish all twelve candidates in the recovered optional phase-completion family.** The new result gives an exact condition for choosing any such pair, and records a colliding candidate pair whenever the condition fails. No historical phase observations have been admitted, so this does not select an actual historical orientation.

Actual local AgentJev-0.6B receipt `000063-298ff24c136a.json` selected the global constraint/dependency extension. The calculation reuses the existing prediction engine and extends `orientation-predictions.probe_designs`. The canonical model still has **sixteen modules**, not seventeen.

## The question being answered

The recovered family holds the angular labels and coordinate origin fixed. Each candidate has a phase increment `b` for R and a combined increment `s` for RL, where `b` is one of six values and `s` is either 1 or 5, all modulo 6. Thus there are twelve candidates. For a word consisting of `r` R operations followed by `l` L operations, its predicted phase is

`q(R^r L^l) = (r − l)b + ls  (mod 6)`.

A “probe” here means a proposed observation of that phase in the declared source frame. It is currently a mathematical test design, not a measured historical event or a supplied symbol-to-phase mapping.

The calculation covers all **144 indexed words** with `0 ≤ r,l < 12` and their **10,296 unordered pairs of distinct word IDs**. Different indexed words can have the same phase behavior; the counts refer to these declared words, not distinct equivalence classes of tests.

## The exact condition

For the two words `(r₁,l₁)` and `(r₂,l₂)`, their joint observations distinguish all twelve candidates exactly when **both** conditions hold:

1. `gcd(r₁ − l₁, r₂ − l₂, 6) = 1`.
2. `r₁l₂ − r₂l₁` is nonzero modulo 3.

The first condition separates different `b` values with the same `s`. The second separates candidates with opposite `s` values. Testing only one condition is insufficient.

| Two proposed observations | Result within this family | Why |
| --- | --- | --- |
| R and RL | Sufficient | They directly reveal `b` and `s` |
| R and L | Sufficient | The two increments determine their sum `s` |
| R² and L² | Insufficient | Squaring loses a distinction: `(b,d) = (0,1)` and `(3,4)` both produce `(0,2)` modulo 6 |

Of the 10,296 pairs, **4,608 are sufficient** and **5,688 are insufficient**. Every insufficient pair has an explicit collision witness in the saved result. No single probe has more than six possible outputs, so it cannot distinguish all twelve candidates; each sufficient pair is therefore minimal in number of probes.

The proof compares two candidates using `(rᵢ − lᵢ)Δb + lᵢΔs = 0 (mod 6)`. When `Δs = 0`, the gcd condition is necessary and sufficient to force `Δb = 0`. For opposite `s` values, `Δs` is even and nonzero modulo 3. Under the gcd condition, reduction modulo 2 forces `Δb` even, while reduction modulo 3 admits a collision precisely when the determinant vanishes. Combining those congruences gives the stated necessary-and-sufficient condition. This proof and the exhaustive finite enumeration have different roles; neither supplies a missing source observation.

## What was reused

The recovered *SUN/SOL Orientation Atlas*, section 4.2, already classifies the twelve completions as one orbit under the allowed angular-label-preserving relabelings. Section 3 already distinguishes changing coordinates together with all labels from moving a map against fixed source labels. The present calculation explicitly replays that result; it does not claim to discover the orbit again.

The external baseline is Berman, DasGupta and Kao, [*Tight Approximability Results for Test Set Problems in Bioinformatics*](https://bdasgup.github.io/resume/publ/papers/ber3-swat04.pdf). Its test-set formulation asks for observations that distinguish every pair of candidates. The actual Exa retrieval is preserved in `global-closure/prior-art-primary.json`; it is connector-rendered text, not original PDF bytes. This small finite family is enumerated exactly; no approximation algorithm or arbitrary weighting is used. The arbitrary two-word criterion is newly derived against these recovered execution artifacts. Novelty across the full research literature or archive is **not established**.

## What an independent source test must supply

An applicable historical test needs an authenticated mapping from each observed entity or event to the declared R/L word and phase label. Both observations must use the same admitted frame, phase order, origin and native semantic units. Assigning those labels from the preferred candidate would be circular.

A glyph, word, number, color or sound is not a phase observation until its source-defined bridge is established. Exact scalar values of fixed R/L/O words are independent of `b` and `s`, so repeating a scalar calculation alone cannot choose a phase completion. A relabeling that carries every source label with the coordinates remains a coordinate change, rather than a historically selected orientation.

The separate lawful phase-preserving profile is retained. The criterion is sufficient only within the declared twelve-completion family; it does not eliminate that profile or unspecified larger families. This extension adds **zero independent historical constraints**, selects no absolute orientation and establishes no blind prediction. The symbol/sound, grammar and separate native Western/Chinese musical dependencies remain in force.

## Reproduction and current checks

The reproducible builder is `scripts/derive_phase_probe_designs.mjs`. The full result is `state/delivery-2026-11-07/global-closure/phase-probe-designs.json`, including all indexed words, candidate outputs, sufficient pairs, failure witnesses, source contracts and immutable input/code bindings. The canonical orientation artifact appends the same result plus its pre-extension snapshot reference; all earlier orientation fields are preserved.

Four focused tests in `tests/phase-probe-designs.test.mjs` passed in this documentation verification. They check accounting, collision witnesses, repeated native translations, preservation and evidence boundaries. The current fidelity report checks sixteen modules and 10,296 probe pairs. The [independent Python review](GLOBAL_CLOSURE_REVIEW.md) also reports all 10,296 pairs checked, the same 4,608/5,688 split and zero criterion mismatches. A 48-group main-workbench browser run passed for its recorded inputs; the standalone guide has its own browser report. Later asset edits require the relevant input hashes to be checked again.

All sixteen SUNNY goals and eight mathematical outputs remain open. The next useful constraint must be source-authenticated and discriminate the admitted alternatives; the calculation does not license bypassing symbol/sound → grammar/operations → supported readings → hierarchy → calendar/zodiac consequences → independent predictions.
