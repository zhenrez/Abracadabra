# Residual analysis of the supplied table

The result is conditional on the existing, explicitly stipulated operators. It does not establish a universal historical generator. Input: `table.json`; outputs: `residual-results.json`, `dead-nodes.json`, `residual-heatmap.png`. Reproduce with `python work/ariadne-inverse/residual_analysis.py`. Tests: `python -m unittest discover -s work/ariadne-inverse -p test_residual_analysis.py -v`.

## Coordinate and residual contract

All 540 original positions survive. Each record keeps script, target column, glyph, literal reading, available canonical column, operator and prediction. The canonical correspondence domain currently contains six 22-column traditions and five vowel/glide correspondences each for Greek and Latin. The earlier Sabaic/Futhorc permutation test failed; matching a target's observed label to itself cannot become a successful prediction. Such cells remain unmapped.

For categorical readings, epsilon is the set of observed alternatives outside the predicted set. A binary mismatch indicator summarizes whether that set is nonempty. Allowed alternatives absent from the observation are recorded separately. This tests coverage, not exact set equality. Entropy is calculated across repeated column observations; an individual mismatch is not intrinsically high entropy. No likelihood has been fitted, so residual surprisal or acoustic-frequency error is not asserted.

The heatmap uses original target columns; its lower panel uses the supported canonical subset and explicitly reports unequal sample coverage. Green means compatible, red means an unpredicted reading, gray means unscored. Question marks denote unknown phonetic readings. The JSON also provides raw-ordinal entropy across 14 historical/proxy rows, excluding English letter names. Raw ordinal position is not cross-script homology.

## Findings

Of 381 populated cells, 142 are scorable: 136 compatible and six mismatches. The other populated cells are 234 unmapped, four unknown and one unresolved label. All 159 empty slots remain missing.

| Canonical sibilant column | Symbol | Supported observations | Label entropy, bits | Mismatches |
|---|---|---:|---:|---:|
| 7 | z | 6 | 0 | 0 |
| 15 | s | 6 | 0 | 0 |
| 18 | sˤ | 6 | 0.650022 | 1 |
| 21 | ʃ | 6 | 0.650022 | 1 |

These results do not show that sibilants have the highest entropy throughout the table. The sibilant sample is the six aligned traditions; it must not be represented as a completed Greek/Etruscan historical collation. Four identical inventories make the sample dependent.

The user's proposed additional correspondences can be inspected separately: Greek carrier 7→target6 gives z→zd; carrier15→target14 gives s→ks; carrier21→target18 gives ʃ→s. Greek carrier18 has no supplied direct target mapping: absence cannot distinguish deletion from merger. Under the user's Etruscan positional hypothesis, carrier15→target15 gives s→ʃ and carrier21→target21 gives ʃ→s. These are candidate substitution residuals against identity fallthrough; the alignments require source validation before adding them to the canonical entropy pool. They are not consequences of a validated permutation operator. No audio or spectral measurements were supplied, so a 4–8 kHz Shibboleth mechanism was not measured.

## Unknown Etruscan readings and structural preservation

`dead-nodes.json` preserves glyphs at positions 2, 4, 18 and 26. Their phonetic status is **unknown**, not silent. Structural preservation is stipulated in this analysis, satisfying the user's template constraint without using that assumption as evidence of sacred intent. A teaching-table entry, actual speech realization and a religious explanation require different evidence. Unknown labels are excluded from entropy rather than encoded as a common silence category.

## Old Persian comparison

| Metric | Other 13 historical/proxy rows | Old Persian |
|---|---:|---:|
| Populated entries | 319 | 36 |
| Single-segment readings | 279 | 3 |
| Multi-segment readings | 13 | 33 |
| Alternative sets | 22 | 0 |
| Unknown / unresolved | 5 | 0 |
| Cells with supported operator predictions | 142 | 0 |
| Observed mismatches among scored cells | 6 | Not estimable |
| Historical topological mutual information | Not estimable | Not estimable |

The grouping excludes modern English letter names. It does not preclassify the other 13 rows as organic or Old Persian as a cipher. Only d and m have all a/i/u endings in the supplied literal inventory. Other consonants have incomplete subsets; consequently a universal three-state expansion does not reproduce the table as given. The duplicate ja spelling and the distinct literal sh-length label remain source data.

## Mutual information and origin claims

The module implements the categorical estimator I(G;H)=sum p(g,h) log2[p(g,h)/(p(g)p(h))], with analytic tests for independent and identical variables. Historical TMI is JSON null, because paired historical graph descriptors and an independently justified alignment are unavailable. Modern-font topology and pairing unrelated column numbers would answer a different question. Any later test must fix graph discretization, alignment, sample unit and shuffled-pair baseline before evaluating held-out witnesses. With few pairs and many unique graph states, naive empirical MI is upward biased; high MI can be a uniqueness artifact.

Unicode's Old Persian encoding proposal describes a newly devised monumental inventory associated with Darius, comprising consonants, vowels and consonant–vowel sequences. This is external historical scholarship, not an inference from this residual analysis, and does not establish cryptographic encryption: https://www.unicode.org/L2/L2003/03149-n2583-old-persian.pdf . Unicode describes the system as alphabetic with syllabic aspects: https://www.unicode.org/versions/Unicode16.0.0/UnicodeStandard-16.0.pdf . These sources do not validate the user's every-consonant/three-vowels rule.

## Scope and verification

The three new focused tests passed, including known entropy/MI values, Greek index alignment, parity coverage, all 540 retained cells, exact unknown-node positions and unscored Old Persian. The image was visually inspected. Existing frozen SUN source was not edited. SuperJev and Riqor contracts from the session remain applicable; no new Jev inference or historical approval occurred. No new Proofline runtime is claimed for this report; prior packages bind their own earlier content only. Full joint operator identification, historical topology, spectral diagnosis, sacred intent and cipher classification remain open.
