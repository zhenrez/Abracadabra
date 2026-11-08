# SUN Empirical Hyperedge Operation Coverage v0.1
**Date:** 2026-09-30  
**Basis:** all source-backed relation objects in the frozen empirical music hypergraph.

## Coverage

\[
\boxed{117/117\ \text{empirical hyperedges classified}}
\]

The operation-shape result is:

- **A1 — typed deterministic action:** 9
- **A2 — parameterized constructor/composition:** 24
- **A3 — joint-constitution hyperedge:** 7
- **A4 — stochastic transition/expectation kernel:** 2
- **supporting non-generator relations:** 75

Therefore:

\[
9+24+7+2=42
\]

empirical hyperedges currently carry active transformation/generation/composition/joint-constitution semantics, while:

\[
117-42=75
\]

remain essential relational structure without enlarging the operation alphabet.

## A1 — Typed deterministic action

Source lane: `TRANSFORMATIONAL`.

Canonical shape:

\[
f:X\rightharpoonup Y.
\]

## A2 — Parameterized constructor / composition

Source lanes:

- `GENERATIVE`
- `GENERATIVE-PROCEDURAL`
- `COMPOSITIONAL`
- `FORMAL COMPOSITION`

except explicitly stochastic cases.

Canonical shape:

\[
F:P\times X_1\times\cdots\times X_k\rightarrow Y.
\]

## A3 — Joint constitution

Source lane: `JOINT CONSTITUTION`.

Canonical shape:

\[
J(x_1,\ldots,x_k)\Rightarrow M.
\]

## A4 — Stochastic kernel

Explicit stochastic/probabilistic generation edges:

- `DC-D051-01` — Xenakis stochastic/Markovian generation
- `SR-D059-01` — Pearce/IDyOM-style probabilistic expectation

Canonical shape:

\[
K(x,y)=P(Y=y\mid X=x).
\]

## Supporting relation grammar

The remaining 75 edges stay first-class.

They include:

- constraint;
- classification;
- parameterization;
- placement/address;
- temporal/history;
- mapping;
- invariance;
- physical realization;
- epistemic relation;
- realization;
- enablement.

They are not discarded merely because they do not enter the operation alphabet.

## Sufficiency result

For the **current empirical edge vocabulary**:

\[
\boxed{
\Omega_{\rm SUN}^{(0.1)}=
\{A1,A2,A3,A4\}
}
\]

is sufficient to type every empirical edge that presently claims generation, transformation, composition, or joint constitution **without stripping its source-native qualifiers or arity**.

This is not yet a minimality theorem.

## Why we do not reduce to one generic function

Mathematically, many of these objects can be encoded as one generalized map or kernel.

SUN deliberately refuses that trivial collapse because it would destroy scientifically protected distinctions:

- deterministic vs stochastic;
- unary transition vs n-ary construction;
- algorithmic construction vs joint constitution;
- carrier/address effects;
- native arity and history.

The minimality criterion must therefore be **semantic-preserving**, not merely set-theoretic.

## Next

The remaining vertex population is now tested as **operands, outputs, parameters, addresses, classes, dimensions, states, carriers, or operator objects**.

A new operation mode is admitted only if one of those vertices has a source-backed generative law that cannot be expressed through A1–A4 plus the supporting relation grammar.
