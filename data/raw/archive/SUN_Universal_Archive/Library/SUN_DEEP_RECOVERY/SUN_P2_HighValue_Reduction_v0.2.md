# SUN P2 High-Value Relation/Process Reduction v0.2
**Date:** 2026-09-30  
**Scope:** first proof pass over the most algebraically consequential P2 relation/process/structure families.

## 1. Lewinian GIS action relation

Recovered source claim:

- GIS interval structure and a simply transitive group action are equivalent presentations of the complete structure.

Already-proved receipt:

\[
\boxed{\text{GIS interval-function presentation}\simeq\text{simply-transitive right action presentation}}
\]

with carrier, group, and action convention preserved.

**Reduction decision:** `REPRESENTATION_EQUIVALENT`, not a new global generator and not node identity.

---

## 2. Interlocking / hocket as joint constitution

The source corpus contains several independent music-native cases:

- Central African hocket: assigned figures mesh into a hocket/polyphonic result.
- Andean qantu ira/arka: both complementary parts are required to complete the melody.
- Balinese kotekan: complementary interlocking parts constitute the composite.
- West African cross-rhythm: multiple parts participate in larger interlocking cyclic organization.

These are not naturally represented as a single unary map \(x\mapsto y\).

Canonical relation form:

\[
J(x_1,\ldots,x_k)\rightarrow M
\]

where the output/composite \(M\) depends on the joint incidence.

For qantu, the minimal native form is binary:

\[
J(\text{ira},\text{arka})\rightarrow\text{completed melody}.
\]

For higher-part cases, \(k>2\) may be native.

**Reduction decision:** retain `JOINT_CONSTITUTION / COMPLEMENTARY_INTERLOCK` as a hyperedge family.

**Important:** do not replace an irreducibly joint relation with pairwise edges when that loses the source-native sufficiency condition.

---

## 3. Klumpenhouwer transformation-labelled edges

The frozen source supports:

\[
\text{pitch-class node}
\xrightarrow{\text{transformation label}}
\text{pitch-class node}.
\]

This is a relation representation carrying a transformation label.

**Reduction decision:** `TRANSFORMATION_LABELED_RELATION`.

It does not independently establish a new transformation generator; the generator identity comes from the edge label's actual transformation semantics.

---

## 4. Spatial-texture transformation relation

The source-backed minimum says spatial textures have topological organization and transformations acting on them.

But the current semantic audit already proved an obstruction:

- the extracted edge supplies a transformation relation;
- it does **not** supply an iteration law;
- different mathematical completions can have different orders.

Therefore:

\[
\boxed{\text{TRANSFORMATION EXISTS}}
\]

does not yet imply

\[
\boxed{\text{COMPOSABLE GENERATOR WITH KNOWN ORDER}}.
\]

**Reduction decision:** `RELATION_CONFIRMED / GENERATOR_ORDER_UNRESOLVED`.

---

## 5. Messiaen modes of limited transposition

The source-backed claim says the modes are defined by repeating interval structures with only a limited number of distinct transpositions.

The transformation itself is ordinary transposition acting on a pitch-class set.

Thus the new content is not a new generator \(T\); it is the stabilizer/orbit property of a structured set under \(T\).

Canonical form:

\[
\operatorname{Orb}_T(M)=\{T^k(M)\},
\]

with:

\[
|\operatorname{Orb}_T(M)|<12
\]

for a mode of limited transposition.

Equivalently, there exists a nontrivial stabilizer:

\[
\operatorname{Stab}_T(M)\neq\{e\}.
\]

**Reduction decision:**

\[
\boxed{\text{LIMITED TRANSPOSITION}=
\text{TRANSPOSITION ACTION}+\text{NONTRIVIAL STABILIZER}}
\]

not a new primitive transformation family.

This is a major reduction because it turns an apparent generator object into an orbit/invariance receipt.

---

## 6. Mensuration and prolation

The source-backed claim explicitly separates mensuration and prolation as distinct nested proportional structures.

Their scientific value is therefore:

\[
\text{level}_1\ \text{proportion}
\quad+\quad
\text{level}_2\ \text{nested proportion}.
\]

They are not source-supported as two unary state generators.

**Reduction decision:** `TYPED_PROPORTIONAL_HIERARCHY`.

Preserve them as separate relation levels because collapsing them loses hierarchy.

---

## 7. Xenakis Markovian transition

Recovered source claim:

\[
P(X_{t+1}\mid X_t)
\]

governs the next event/state from the preceding state.

This is a genuine generative relation, but of a different type from deterministic actions.

Canonical object:

\[
K(x,y)=P(X_{t+1}=y\mid X_t=x).
\]

Composition occurs by stochastic-kernel composition:

\[
(K_1K_2)(x,z)=\sum_yK_1(x,y)K_2(y,z).
\]

**Reduction decision:** `STOCHASTIC_TRANSITION_KERNEL`.

This survives as a distinct abstract generator family unless SUN later declares stochastic kernels outside its admissible operation vocabulary.

---

## 8. Mūrchanā

The frozen claim establishes that *mūrchanā* is a distinct element within the grāma–mūrchanā–jāti organization, but the minimum source record currently does not provide enough of its native construction law to prove a generator action.

**Reduction decision:** `UNRESOLVED_GENERATIVE_CLASS`.

Do not promote a rotation/mode-generation operator from general knowledge alone.

---

# Current family consequences

## Existing P1 families that absorb P2 records

### TRANSFORMATION / GROUP ACTION
Absorbs:
- GIS action representation
- K-network transformation-labelled relation
- limited-transposition orbit analysis

but representation, action, and orbit property remain distinct record types.

### MULTIPLICATIVE / PROPORTIONAL RELATION
Absorbs:
- mensural/prolation proportional hierarchy as typed nested relation

without calling it a unary generator.

### HYPEREDGE JOINT CONSTITUTION
Now source-supported by multiple interlocking/hocket systems.

This is a genuinely important hypergraph primitive:

\[
\boxed{\text{joint incidence can constitute a result not owned by any individual part}}.
\]

## New abstract family

### STOCHASTIC TRANSITION KERNEL

\[
\boxed{K(x,y)=P(y\mid x)}
\]

is not reducible to the deterministic unary action families already proved.

---

# Revised provisional abstract grammar

The growing grammar now distinguishes:

1. deterministic action;
2. inverse/composed deterministic action;
3. transposition/orbit/stabilizer;
4. scalar/proportional transformation;
5. representation/address transition;
6. parameterized constructor;
7. Boolean/residue constructor;
8. local additive transform;
9. typed boundary relation;
10. joint-constitution hyperedge;
11. path/trajectory process;
12. hierarchical proportional relation;
13. stochastic transition kernel;
14. invariant/fixed-point predicate;
15. representation-equivalence receipt.

These are **typed grammar families**, not the final minimal SUN alphabet.

# Next proof target

Continue through:
- directed modal/course processes;
- cyclic temporal organizations;
- hierarchical reductions (Schenker/GTTM);
- expectation/update processes;
- trajectory/morphology processes.

The goal is to determine which are:
- instances of the grammar above,
- compositions of existing families,
- or genuinely new irreducible relation/generator types.
