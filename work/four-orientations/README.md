# Four native orientations — evidence checkpoint

This checkpoint implements the common evidence layer and four independently specified mathematical models requested in the attached design. It enables comparison tests, but keeps cross-orientation historical reconstruction disabled. Native contract tests are separate from independent historical validation: no external reviewer or new held-out manuscript dataset was used.

## Evidence contract

`evidence.schema.json` defines sources, observations and typed relations. `evidence.py` checks source hashes, reference bindings and relation kinds and supplies reversible compression. `evidence.json` preserves 540 original table cells and 17 raw sources, including the complete attached specification, the supplied matrix and snapshots of existing project code/state. `evidence.zlib` decodes to the identical structured bundle; original source bytes—including line endings—are independently recovered and compared. This is an evidence-retention codec, not a demonstrated optimal MDL model.

Every observation retains its source identity, native address, original cell, proxy/reading role, uncertainty, witness and historical-time fields. Unknown witnesses/dates stay null; a Unicode proxy never becomes an ancient attestation. Existing witness relationships, primordial alternatives and W72 conditions remain in the preserved raw state/source snapshots; they have not been silently normalized into new observations or adjudicated. The new relation table is empty until specific source-bound relationships are admitted. No historical relation is invented merely to populate the schema.

Identity, order, function, generation, realization, association and contradiction have distinct relation types. Operator adapters have explicit domain and codomain types. The comparison layer rejects noncomposable diagrams and unlike operator-relation kinds. Counts alone never create an adapter.

## Native implementations and boundaries

| Model | Executable contract | Explicit limits |
|---|---|---|
| Western | Exact rational length operators R=2/3, L=3/4, O=1/2; rational octave decomposition with register; seven selected classes; chromatic transposition; Pythagorean comma | Abstract chromatic address selection is separate from exact ratios; no forced equal-temperament frequency assignment. Greek tetrachords, Fludd, Kepler, voice-leading and rhythm remain separate source adapters to implement. |
| Chinese | Exact D=2/3 and U=4/3 length operators; 12×5 context enumeration; independent address/function rotations; formal alternating-index 6+6 classification | The 60 cells are formal contexts, not 60 attested instruments. Address rotation does not assign tuning. Historic six-plus-six labels, pipe-generation variants and native gong prescriptions require their sources. |
| Indian | Six ordered Ri–Ga choices × two Ma choices × six ordered Dha–Ni choices; 72 unique seven-position configurations; 36 involutive Madhyama pairs; seven svara roles | Positions encode a conventional parent-scale grammar, not measured frequencies. Twenty-two shruti ratios require an explicit source-selected profile; none is invented. Raga practice and Katapayadi decoding remain future independently sourced adapters. |
| Sefer | Reuses the existing 3/7/12 slot validator; 29 tagged states; 231 unordered distinct-letter pairs; 32 explicitly typed sefirah/letter objects | Formal possible pairs are not necessarily attested words. The seventh double's alternate realization remains unassigned. No letter-to-frequency rule is inferred. |

The native models share evidence and exact arithmetic conventions, not each other's acceptance rules. Python `Fraction` supplies exact test arithmetic; existing TypeScript scalar and contextual-alignment implementations remain intact and are included in the provenance snapshot. The Sefer model reuses `work/ariadne-inverse/harmonic_verifier.py` directly instead of duplicating its validator.

## Operator preservation

For source operation S, target operation T and typed adapters A/B, the implemented test is B(S(x))=T(A(x)). Each discrepancy exports the input and both exact path outputs. Tests establish preservation on the declared sample domain; a sampled pass is not a general theorem or historical identification.

Positive control: SUN R and Chinese D have the same declared scalar 2/3. Negative control: SUN RL maps 1 to 1/2; Chinese DU maps 1 to 8/9. For input 7/11, the outputs are 7/22 and 56/99. Therefore the proposed equality of these composite operations is refuted under the identity length adapter. U equals the inverse of L as a scalar; U is not L. No W72/Melakarta bijection is selected from their shared count of 72.

`reconstruct` reports determined only when one survivor remains, the caller explicitly attests that the declared finite candidate family is exhausted, and independent evidence is supplied. These attestations are input obligations, not independently verified by the function. Multiple survivors remain ambiguous; an exhausted empty family is falsified. The checkpoint enables no historical cross-orientation reconstruction.

## Tests and reproduction

```powershell
python work/four-orientations/build_checkpoint.py
python -m unittest discover -s work/four-orientations -p test_models.py -v
```

Tests include raw-byte roundtrip and tamper rejection; exact SUN identities and negative/positive register changes; fifth-cycle nonclosure; all Chinese contexts and inverse rotations; an independently expressed exhaustive Indian enumeration; all Madhyama pair involutions; Sefer duplicate rejection and distinct gate types; operator counterexamples; typed-diagram rejection; and ambiguity controls. `checkpoint.json` records outcomes and before/after hashes for protected project sources and selected state files. The tests are mathematical unit/property tests, not chronology-respecting historical holdouts.

The attached user's text is preserved as the design specification, not treated as independently authenticated historical scholarship. Earlier model outputs remain available and have not been relabeled as historical proof. Exact fractions and finite combinatorics in this checkpoint follow the supplied contracts; external claims require source-specific follow-up.

## Plugin use and remaining gates

Agent Skills API/interface-design was read and applied to the new schema and boundary checks. Existing SuperJev coordination and Riqor evidence-engineering contracts were applied, and the recovered HUMMBL plan informed Now/Next/Later/Resolve sequencing. No native plan tool is exposed, so `PLAN.md` records local progress without claiming native plan execution. No new Jev inference ran: the prior hosted-context disclosure rejection is still unresolved. No Proofline verification of this new bundle, AgentProof capture, independent reviewer, or new Supermemory checkpoint is claimed. Existing packages and checkpoints retain their original scope.

Next gate: independently source and freeze the tuning/witness profiles and typed adapters, then run source-held-out reconstruction, genealogy baseline, negative controls and fixed-coding MDL comparisons. Native mathematical success is necessary but insufficient for that gate.
