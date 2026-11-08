# SUN music characterization: Chinese lü depth pilot

**Status:** independent music-side depth pilot; no SUN comparison or admission.  
**Checkpoint recovered:** `SUN_GreekPrototype_COMPLETE.xlsx`, sheets `97_Characterization_Gate` and `125_Greek_Prototype_Checkpoint`; breadth population in `Pasted text(20260927-192548).txt`; D2 schema stress test in `Pasted text(20260927-195603).txt`.  
**Later direction:** after the Greek prototype, characterize Chinese music rather than run another Greek planning pass.  
**Scope of this unit:** the twelve pitch-pipe (`lü`/律呂) generation and its relation to five tone positions and rotating `gong`. This is one documented Chinese theoretical strand, not “Chinese music” as a whole.

## Source and provenance ledger

| ID | Source | Role | Limit |
|---|---|---|---|
| CN-S01 | [`Lüshi chunqiu`, “Ancient Music”](https://ctext.org/lv-shi-chun-qiu/gu-yue), transmitted text | Historical textual witness for Ling Lun, Huangzhong, twelve pipes, six male/six female | Mythic origin narrative; not an observed instrument-manufacturing record. |
| CN-S02 | [Jonathan Service, “Chinese Music Theory,” Harvard](https://soundingchina.fas.harvard.edu/Service.html) | Scholarly explanation of the pipe-length algorithm and distinct twelve/five/eight organizations | Secondary synthesis; its simplified acoustics and historical grouping must not be silently recast as primary testimony. |
| CN-S03 | [Nan Lian Lam, “Pentatonic Xuangong Transformations,” *Music Theory Online* 30.1 (2024)](https://mtosmt.org/issues/mto.24.30.1/mto.24.30.1.lam.html) | Original modern formal analysis of five position/twelve pitch-class transformations and musical examples | Modern analytical coordinates; not proof that ancient theorists used mod-12 pairs. |
| CN-S04 | [`Liji` passage reproduced and analyzed by Lam, §2.3](https://mtosmt.org/issues/mto.24.30.1/mto.24.30.1.lam.html) | Textual witness for rotating `gong` | Translation/edition mediated here by CN-S03; independently consult the text and variants before promoting a literal historical claim. |

## Native-object inventory and claim ledger

**Provenance labels:** TEXT = source text reports it; SCHOLARLY = modern scholar's historical account; FORMAL = modern analytic model; DERIVED = consequence computed here. None denotes empirical acoustic validation.

| ID | Object or relation | Claim and native scope | Status / source |
|---|---|---|---|
| CN-C01 | Huangzhong 黃鐘 | The Ling Lun account treats it as a reference for other pipes. | TEXT, CN-S01; mythic framing retained |
| CN-C02 | Twelve tubes / twelve lü | The account names twelve tubes, partitioned six male and six female by phoenix cries. | TEXT, CN-S01 |
| CN-C03 | Pipe-length operation | Subtract one third of a pipe's length, then add one third of the next pipe's length, in the idealized `sanfen sunyi` sequence. | SCHOLARLY, CN-S02 |
| CN-C04 | Musical intervals from ideal pipe length | The subtraction gives an ascending fifth; the addition gives a descending fourth, assuming the stated pipe-length/pitch idealization. | SCHOLARLY, CN-S02 |
| CN-C05 | Five tone positions | `gong, shang, jue, zhi, yu` are distinguishable scale functions; five is not another count of pipes. | SCHOLARLY, CN-S02; FORMAL, CN-S03 |
| CN-C06 | Rotating gong | The `Liji` passage describes pitches/pipes rotating as `gong`. | TEXT via CN-S03/CN-S04 |
| CN-C07 | Ordered-pair address | Lam models a pentatonic pitch class as (pentatonic set keyed by `gong`, position among five tones). | FORMAL, CN-S03 §2.2 |
| CN-C08 | Distinct transformations | Lam's `T_n` changes the twelve-class set key while holding tone position; `t_n` changes the five-position index while holding the set key. | FORMAL, CN-S03 §§2.5–2.7 |
| CN-C09 | Eight materials/sounds | `bayin` classifies sound sources by material; this is an organological classification, not a pitch-generation step. | SCHOLARLY, CN-S02 |
| CN-C10 | Twelve-step nonclosure | Repeated fifth/fourth generation does not close exactly at an octave; later Chinese theorists treated this as a problem. | SCHOLARLY, CN-S02 |

## Typed dependency records

| ID | Antecedent(s) → consequent | Relation | Necessity / qualification | Claim support |
|---|---|---|---|---|
| CN-D01 | reference pipe + shortening rule → next pipe | GENERATIVE, ideal length | Formal within the reconstruction; no claim of one historically invariant starting length | C01, C03 |
| CN-D02 | generated pipe + lengthening rule → following pipe | GENERATIVE, ideal length | Ordered after D01 in the described procedure | C03 |
| CN-D03 | repeated operations → ordered pitch-pipe series | GENERATIVE sequence | History/version of the method must be recorded | C02–C04 |
| CN-D04 | twelve-pipe inventory → selectable tonal reference | ENABLES placement | Does not itself choose the active `gong` | C02, C06 |
| CN-D05 | selected `gong` + five position roles → pentatonic context | CONSTITUTIVE in Lam's model | Modern formalization, not historical causation | C05, C07 |
| CN-D06 | `T_n` + context → changed set key | TRANSFORMATION | Position invariant in the formal model | C08 |
| CN-D07 | `t_n` + context → changed position | TRANSFORMATION | Set key invariant in the formal model | C08 |
| CN-D08 | material category → `bayin` class | CLASSIFICATION | Orthogonal to pipe generation; no causal arrow to a pitch | C09 |

## Independent formal consequences

Let an ideal reference pipe have length `L₀`. CN-C03's first operation gives `L₁ = (2/3)L₀`. Its second operation gives `L₂ = (4/3)L₁ = (8/9)L₀`. Under the *idealized* inverse length–frequency relation, their frequency ratios against the reference are `3/2` and `9/8`. The second value follows from the **ordered path**; endpoint equality alone would not preserve the sequence or the pipe identities. This is a DERIVED computation from CN-C03, not a new historical source claim.

Five tone positions and twelve lü form two address axes in CN-S03's formalization. Their product yields 60 ordered set-position contexts in that model. It does **not** establish 60 historical pipes, 60 empirically attested modes, or a universal Chinese count. The `T` and `t` actions have different preserved coordinates; an implementation must retain both.

The twelve-pipe generation, five-position function, and eight-material classification are separate structures. A single unlabeled “Chinese music number” node would erase their relation types and falsely imply a shared generation law.

## Counterexamples and unresolved points

1. **Myth versus mechanism:** CN-S01's phoenix account is historical evidence for a narrative and classification; it cannot establish how actual ancient instruments were cut or tuned.
2. **Pipe acoustics:** real frequency depends on bore, end correction, temperature, blowing, and material. The length calculation is a mathematical idealization until a physical measurement protocol is attached.
3. **Textual variants:** the transmitted Huangzhong reference length has variant traditions. Keep the reference length nullable and versioned; do not pick a value from this pilot.
4. **Period collapse:** `Lüshi chunqiu`, `Liji`, later numerical methods, and Lam's 2024 analytic notation occupy different provenance/time layers. No single timeless ontology is asserted.
5. **Closure:** exact twelve-step/octave equality is not licensed by the third operations. A numerical residual should be recorded rather than rounded away.
6. **Population:** this pilot does not cover Chinese rhythmic, timbral, notation, regional, or performance systems beyond the narrow `bayin` distinction.

## Pilot result and next gate

This pilot confirms that the existing D2 schema can represent a Chinese case **only if** it keeps (a) order-sensitive generation, (b) functional address distinct from physical carrier, (c) placement separate from set identity, (d) multiple independent classification axes, (e) dated provenance, and (f) exact residuals. These are schema requirements drawn from the cited systems; they are not a SUN fit.

Next bounded unit: independently transcribe the pertinent primary passages with edition/variant identifiers, and add a second Chinese music system with a different native dependency grammar before claiming a representative Chinese depth dossier. Cross-domain comparison remains behind the workbook's `97_Characterization_Gate` row 12.
