# SUN Music-Native Alphabet Equivalence Registry v1
**Date:** 2026-09-30

## Status

All currently recovered executable/generative music mechanisms are now assigned to a frozen **generator-family equivalence class** or retained as an explicit supporting relation.

Equivalence is typed. The registry distinguishes exact action equivalence, generator-family equivalence, abstract algebra equivalence, shared operation form, root extension, fixed-point/quotient relation, and singleton-unmerged status.

## Generative equivalence classes

### MEC-01 — SCALAR_MULTIPLICATIVE_ACTION
Canonical: `S_c(x)=c x, c>0`

- **SUN scalar kernel** — R=2/3, L=3/4, O=RL=1/2; NATIVE
- **sanfen sunyi** — D=2/3, U=4/3; EXACT_GENERATOR_FAMILY_EQUIVALENCE to SUN on positive scalar carrier
- **Zhu equal division** — q=2^(1/12); ROOT_EXTENSION / SAME OPERATION FORM, NOT SAME SUBGROUP
- **Messiaen augmentation/diminution** — duration scaling c and c^-1; SAME OPERATION FORM, DIFFERENT CARRIER/SEMANTICS

- Receipt: <R,L> = {2^a 3^b} ≅ Z^2
- Receipt: sanfen D=R and U=L^-1
- Receipt: q not in <R,L> but q^12=2
- Receipt: O=RL is constructible

**Status:** `FROZEN_EQUIVALENCE_CLASS`

### MEC-02 — DIHEDRAL_D12_ACTION
Canonical: `<s,t | s^12=e, t^2=e, tst=s^-1>`

- **serial pitch-class T/I** — T1, I; NATIVE D12 action
- **neo-Riemannian PLR** — L, R; ABSTRACT GROUP / GENERATOR-FAMILY EQUIVALENCE

- Receipt: <T1,I> ≅ D12 order 24
- Receipt: <L,R> ≅ D12 order 24
- Receipt: T1 -> LR, I -> L defines abstract isomorphism

**Status:** `FROZEN_EQUIVALENCE_CLASS`

### MEC-03 — REVERSAL_INVOLUTION
Canonical: `J_n(x)_j=x_{n-1-j}, J_n^2=id`

- **serialism** — retrograde R; NATIVE reversal action
- **Messiaen rhythm** — retrograde operator, non-retrogradable fixed points; SAME REVERSAL MECHANISM; fixed-point predicate not generator

- Receipt: serial retrograde = J_12
- Receipt: non-retrogradable w satisfies J_n(w)=w
- Receipt: full serial group ≅ D12 × C2

**Status:** `FROZEN_EQUIVALENCE_CLASS`

### MEC-04 — PARTIAL_ADDRESS_REPRESENTATION_TRANSITION
Canonical: `m:(object,address_a) ⇀ (same_object,address_b)`

- **Guidonian hexachord** — mutation; WEB-EXPANDED executable partial map

- Receipt: mutation requires overlapping hexachords/shared pitch
- Receipt: pitch identity preserved while syllable/hexachord address changes

**Status:** `FROZEN_SINGLETON_CLASS`

### MEC-05 — CYCLIC_INDEX_ROTATION
Canonical: `rho_k(x_0,...,x_{n-1})=(x_k,...,x_{k-1})`

- **grāma–mūrchanā** — seven mūrchanās; WEB-EXPANDED C7-type starting-point rotations

- Receipt: seven starts of a seven-svara grāma produce seven rotations

**Status:** `FROZEN_SINGLETON_CLASS`

### MEC-06 — EUCLIDEAN_DISTRIBUTION_CONSTRUCTOR
Canonical: `E(k,n) -> cyclic n-slot binary pattern with k evenly distributed onsets`

- **Euclidean rhythm generation** — E(k,n); WEB-EXPANDED exact constructor modulo cyclic rotation

- Receipt: E(5,13) implementation reproduces the published cyclic pattern up to rotation

**Status:** `FROZEN_SINGLETON_CLASS`

### MEC-07 — MODULAR_BOOLEAN_SIEVE_CONSTRUCTOR
Canonical: `residue classes M_r combined by union/intersection/complement`

- **Xenakis sieve theory** — residue class, union, intersection, complement; WEB-EXPANDED exact set constructor algebra

- Receipt: M_r = {x in Z | x ≡ r mod M}
- Receipt: compound sieves constructed by Boolean set operations

**Status:** `FROZEN_SINGLETON_CLASS`

### MEC-08 — LOCAL_DURATION_ADDED_VALUE_TRANSFORM
Canonical: `d_i -> d_i + δ, or insert short note/rest/dot-derived duration`

- **Messiaen rhythm** — added value; WEB-EXPANDED executable local duration/event transform

- Receipt: distinct from uniform scalar augmentation/diminution
- Receipt: dot case multiplies selected duration by 3/2

**Status:** `FROZEN_SINGLETON_CLASS`

### MEC-09 — JOINT_CONSTITUTION_HYPEREDGE
Canonical: `J(x1,...,xk) => M`

- **Central African hocket** — interlocking/meshing; SOURCE-SUPPORTED
- **Andean qantu** — ira/arka; SOURCE-SUPPORTED
- **Balinese interlocking** — kotekan/interlocking composite; SOURCE-SUPPORTED
- **West African cross-rhythm** — ensemble relations; SOURCE-SUPPORTED

- Receipt: joint incidence/part complementarity is information-bearing
- Receipt: pairwise-only projection may lose joint sufficiency

**Status:** `FROZEN_EQUIVALENCE_CLASS`

### MEC-10 — CONDITIONAL_NEXT_EVENT_KERNEL
Canonical: `K(context,y)=P(next=y | context)`

- **Xenakis Markovian systems** — first-order transition probability; context = preceding state
- **IDyOM-style expectation** — next-event distribution; variable learned sequential context

- Receipt: first-order Markov is the context-length-1 special case
- Receipt: IDyOM-style expectation is a conditional next-event distribution over richer context

**Status:** `FROZEN_EQUIVALENCE_CLASS`

## Supporting relation grammar

These remain first-class in the hypergraph but do not inflate the executable generator count:

- **SRG-01 PATH_TRAJECTORY** — STRUCTURAL_NON_GENERATOR; examples: modal course, voice leading, spatial trajectory
- **SRG-02 RECURRENCE_CYCLE** — STRUCTURAL_NON_GENERATOR; examples: tala, usul, timeline cycles
- **SRG-03 TYPED_BOUNDARY** — STRUCTURAL_RELATION; examples: synaphe, diazeuxis
- **SRG-04 HIERARCHY_REDUCTION** — EXECUTABLE_SCHEMA_NOT_TOTAL_NATIVE_MAP; examples: Schenker prolongation, GTTM time-span/prolongational reduction
- **SRG-05 MAPPING_EQUIVALENCE** — RECEIPT_RELATION; examples: GIS representation equivalence, typed crosswalks
- **SRG-06 INVARIANT_FIXED_POINT** — PREDICATE_RELATION; examples: limited transposition stabilizer, non-retrogradation
- **SRG-07 MEASURE_RATIO_DISTANCE** — MEASURE_RELATION; examples: interval, ratio, tonal distance
- **SRG-08 EVENT_REALIZATION** — REALIZATION_RELATION; examples: performance/recording realization
- **SRG-09 OBSERVER_EXPECTATION_PROJECTION** — OBSERVER_LAYER; examples: Hasty, ITPRA
- **SRG-10 RESIDUAL_CLOSURE** — VALIDATION_RELATION; examples: comma residual, integrability residual
- **SRG-11 ORBIT_STABILIZER** — DERIVED_RELATION; examples: limited transposition, group orbits
- **SRG-12 ADDRESS_HISTORY_CONTEXT** — IDENTITY_BEARING_METADATA_RELATION; examples: register, address, path/history
- **SRG-13 TOPOLOGY_PRESERVATION** — SOURCE_SUPPORTED_INVARIANT; NO UNIVERSAL ITERATION LAW; examples: spatial texture

## Sufficiency

The registry currently contains **10 generative equivalence classes** and **13 supporting relation classes**.

The ten generative classes are sufficient to place every currently recovered executable/generative mechanism without silently identifying different carriers or histories.

## Minimality

Global minimality across the ten classes is **not claimed**. A more abstract programming language can encode several classes with one meta-operator, but that does not prove scientific equivalence.

## Template-count firewall

Do **not** compare the raw count `10` or the administrative total `23` against Yetzirah or Shem. Those are catalogue class counts, not source-native member/generator counts. Template tests remain downstream and must use the appropriate declared counting operator.