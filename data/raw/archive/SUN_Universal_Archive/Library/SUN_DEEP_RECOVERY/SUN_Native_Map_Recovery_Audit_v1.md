# SUN Native Map Recovery Audit v1
**Date:** 2026-09-30  
**Status:** `COMPLETE_FOR_CURRENT_EVIDENCE`

The remaining executable source-native maps have been recovered or implemented to the strongest level actually supported by the evidence.

## Exact executable maps

- SUN / sanfen scalar actions
- Zhu equal-step symbolic action
- serial \(T/I/R/RI\)
- neo-Riemannian \(P/L/R\)

## Web-expanded executable source recovery

These were absent from the frozen minimum claims at executable detail, so outside source material was used explicitly rather than silently filling the gaps.

### Guidonian mutation
Recovered structure:

- natural hexachord: C–D–E–F–G–A
- hard: G–A–B–C–D–E
- soft: F–G–A–B♭–C–D
- mutation occurs at a pitch shared by overlapping hexachords;
- sounding pitch persists while solmization/hexachord address changes.

Executable map: `guidonian_mutation`.

### Euclidean rhythm
Recovered constructor:

\[
E(k,n)
\]

returns a cyclic \(n\)-pulse rhythm with \(k\) onsets distributed as evenly as possible.

The implementation preserves **cyclic rotation as an equivalence**, rather than making a software start-point convention ontological.

Executable maps:
- `euclidean_rhythm`
- `euclidean_equivalence_class`

### Xenakis sieve
Recovered arithmetic:

\[
M_r=\{x\in\mathbb Z:x\equiv r\pmod M\}
\]

with Boolean/set operations:

\[
\cup,\qquad\cap,\qquad{}^c.
\]

Executable maps:
- `ResidueClass`
- `residue_sieve`
- union/intersection/complement.

### Mūrchanā
External recovery establishes seven starting-point rotations of a seven-svara grāma.

Executable maps:
- `murchana_rotation`
- `all_murchanas`

This is tagged `WEB-EXPANDED`, because the frozen minimum claim named grāma–mūrchanā–jāti structure without encoding the rotation law.

### Messiaen
Recovered executable distinctions:

- uniform augmentation/diminution;
- added short value;
- inserted added note/rest;
- dot as duration extension;
- reversal as separate operation;
- non-retrogradation as reversal fixed-point predicate.

Executable maps:
- `scale_durations`
- `add_value_to_duration`
- `insert_added_event`
- `dot_added_value`
- generic reversal `J`.

## Source-supported executable schema

### Joint hocket/interlock
The source corpus supports genuine joint constitution.

Executable schema:

\[
J(x_1,\ldots,x_k)\Rightarrow M.
\]

`hocket_merge` preserves arity and rejects collisions rather than silently flattening them.

## Executable schemas that require native parameters

### Xenakis Markov
The source supplies:

\[
P(X_{t+1}\mid X_t).
\]

It does not supply one universal numeric transition matrix.

`MarkovKernel` is therefore executable once a native matrix is supplied.

### IDyOM
The source supplies a learned context-conditioned probability distribution over possible next events.

`ContextExpectation` executes:
- probability;
- information content;
- entropy;

but the trained model/distribution must be supplied.

### GTTM / Schenker
The corpus supports hierarchical reduction structures. A reduction-tree representation is executable.

The current evidence does **not** support pretending that one recovered deterministic total algorithm automatically chooses every head/branch.

`ReductionNode` therefore executes the representation, while automatic preference-rule inference remains unclaimed.

### Spatial texture
The source supports topology/structural properties remaining recognizable through continuous change or recurrent shapes.

`spatial_texture_transform` is an invariant-preservation schema requiring a supplied transformation.

A universal native iteration law is **not recovered**.

## Test result

\[
\boxed{14/14\text{ native-action tests pass}}
\]

## Completion boundary

The remaining absent total maps are **not implementation TODOs**. They are explicit source limitations:

- Xenakis numeric transition matrix;
- trained IDyOM model;
- full automatic GTTM reducer;
- full automatic Schenkerian reducer;
- universal Nyström spatial-texture iteration law.

Until a source supplies those objects, inventing them would violate the project evidence rules.
