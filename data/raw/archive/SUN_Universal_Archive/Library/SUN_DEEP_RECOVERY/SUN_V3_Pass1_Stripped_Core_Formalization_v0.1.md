# SUN V3 Pass 1 — Formalization of the Stripped Carrier-Independent Core

## Decision boundary

Map only the six earned SUN roles

\[
G,\;C,\;I,\;K,\;L,\;\pi
\]

to the weakest mature mathematical structures that faithfully express the behavior already earned by the music-native work.

No new SUN behavior is added. No ARGO requirements are used. Fludd–Kepler is validation-only and is not promoted into the carrier-independent core.

## Result

\[
oxed{	extbf{PASS 1 COMPLETE: all six roles admit mature formalizations without requiring one monolithic formalism.}}
\]

The strongest common architecture is therefore not a new equation. It is an interoperable family of six formal roles.

## G — generation / differentiation

**Weakest mature formalism:** typed labelled transition system (equivalently, a directed multigraph/quiver with operation labels)

**Fit:** `EXACT`

**Preserves:** state identity; source/target typing; branching; direction; multiple distinct transitions between the same endpoints; operation labels

**Does not assert / loses:** no composition law by itself; no linearity; no invertibility; no metric; no claim that every transition is deterministic

**First formal consequence:** Distinct transitions and paths can remain distinct even when they share endpoints. Passing to the path category makes histories first-class without identifying them.

**Firewall:** Do not promote the transition graph itself to a universal ontology.

## C — composition / closure

**Weakest mature formalism:** many-sorted partial algebra of admissible n-ary operations; use a multicategory only when composition of such n-ary operations is itself needed

**Fit:** `EXACT`

**Preserves:** typed multi-input closure; explicit domain of admissibility; outputs; distinction between undefined composition and a defined composition with a particular result

**Does not assert / loses:** does not assume multiplication, commutativity, associativity, binary arity, or total closure universally

**First formal consequence:** SUN can state closure rules as partial operations c:D⊆X1×…×Xn→Y. This cleanly separates 'not an admissible composition' from 'admissible and evaluates to y'.

**Firewall:** Multiplication in the music realization is one implementation of C, not the carrier-independent definition.

## I — preserved relational invariant

**Weakest mature formalism:** invariant map / conserved observable on the subcollection of transformations claimed to preserve it

**Fit:** `EXACT`

**Preserves:** the declared aggregate or relation; level sets/fibers of equal invariant value; distinction between preserved aggregate and changed internal allocation

**Does not assert / loses:** does not identify states inside one invariant fiber; does not say which transformations ought to preserve I

**First formal consequence:** If I∘f=I and I∘g=I wherever defined, then I∘(g∘f)=I wherever the composite is defined. Invariance is closed under lawful composition.

**Firewall:** An invariant does not determine the mechanism that preserves it.

## K — representation adequacy / admissibility criterion

**Weakest mature formalism:** typed admissibility predicate or constraint relation K(R,q)∈{0,1} on a representation R relative to a requirement q

**Fit:** `EXACT for the earned conditional claim`

**Preserves:** separation of numerical/algebraic validity from structural admissibility; explicit scope of the current representation class

**Does not assert / loses:** does not choose a repair; does not imply minimality; does not guarantee that a richer representation exists

**First formal consequence:** A state/transition may satisfy the numerical equations while failing K. Therefore numerical success is not sufficient for representational admissibility.

**Firewall:** K=0 licenses 'current representation insufficient'; it does not license any specific lift.

## L — richer-state lift

**Weakest mature formalism:** state-space extension/refinement with lifted dynamics and a commuting projection (semiconjugate extension); covering/fibration only as special cases

**Fit:** `EXACT at the abstract level; COVERING/FIBRATION = PARTIAL/SPECIAL`

**Preserves:** the old observable behavior through projection while allowing extra hidden state/history coordinates

**Does not assert / loses:** does not require local triviality, topology, deck groups, minimal dimension, unique lift, or a particular hidden coordinate

**First formal consequence:** For π∘T~=T∘π, every lifted trajectory projects to a valid base trajectory. Different lifted trajectories may project to the same observable trajectory.

**Firewall:** Do not promote FK monodromy or any specific covering-space model into L.

## π — realization / projection

**Weakest mature formalism:** observation map π:X~→Y together with its kernel equivalence x~πy iff π(x)=π(y)

**Fit:** `EXACT`

**Preserves:** the exposed/realized value and whatever structure is explicitly required of π

**Does not assert / loses:** all distinctions inside a fiber unless separately encoded; no homomorphism/functor claim unless verified per carrier

**First formal consequence:** Every map factors through the quotient X~/~π onto im(π). Thus π(x)=π(y) implies observational equivalence, not state identity; identity follows only if π is injective.

**Firewall:** The quotient is set-theoretic by default; algebraic/topological quotient structure must be earned separately.

## Cross-role assembly

The six roles can be composed without collapsing them into one formalism:

\[
\boxed{
G
\rightarrow
C
\rightarrow
I
\rightarrow
K
\rightarrow
L
\rightarrow
\pi
}
\]

with the following interpretation:

- `G` supplies typed generation transitions.
- `C` states which tuples of generated objects may lawfully compose/close.
- `I` states what relation/aggregate is preserved by a selected transformation family.
- `K` decides whether the current representation remains structurally admissible for a requirement.
- `L` supplies a richer state space when one is actually constructed.
- `π` realizes/forgets that richer state back to the exposed observable.

The strongest exact carrier-independent statement earned in this pass is:

\[
\boxed{
\pi(\tilde x)=\pi(\tilde y)
\;\not\Rightarrow\;
\tilde x=\tilde y
}
\]

unless \(\pi\) is injective.

The strongest transition statement is:

\[
\boxed{
K(R,q)=0
\;\Rightarrow\;
\text{the current representation is insufficient for }q
}
\]

but **not**

\[
K(R,q)=0
\;\Rightarrow\;
\text{a unique/minimal lift exists}.
\]

And where a lifted transition \(\widetilde T\) and base transition \(T\) satisfy

\[
\boxed{
\pi\circ\widetilde T=T\circ\pi,
}
\]

the richer dynamics preserve the old realized behavior while permitting extra state/history information.

## What V3 gains immediately

1. `G`: history can be represented without identifying equal endpoints.
2. `C`: multi-input closure can be typed without assuming multiplication or binary arity.
3. `I`: invariant preservation composes, while mechanism identity remains underdetermined.
4. `K`: structural inadmissibility becomes formally distinct from numerical failure.
5. `L`: richer state can preserve old behavior through a commuting projection without assuming coverings/fibrations.
6. `π`: observational equivalence is formally separated from state identity by the kernel equivalence of the observation map.

## Explicit non-promotions

This pass does **not** earn:

- universal binary complementarity;
- universal multiplication;
- universal minimal extension;
- universal covering-space or monodromy structure;
- universal integer grading;
- a unique repair after inadequacy;
- a single formalism that subsumes all six roles.

## Outcome classification

- `G`: EXACT
- `C`: EXACT at the partial-operation level
- `I`: EXACT
- `K`: EXACT for the conditional adequacy claim
- `L`: EXACT as extension/semiconjugacy; covering/fibration only PARTIAL/SPECIAL
- `π`: EXACT as observation/quotient-by-kernel-equivalence

No role remains `UNKNOWN` at the requested abstraction level.

## Stop condition

The requested V3 Pass 1 definition of done is satisfied. No comparative-domain search, V4 activation, bridge reopening, or ontology expansion is needed in this pass.
