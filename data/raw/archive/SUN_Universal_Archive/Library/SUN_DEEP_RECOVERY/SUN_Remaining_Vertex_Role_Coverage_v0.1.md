# SUN Remaining Vertex Role Coverage v0.1
**Date:** 2026-09-30

## Coverage

After removing:

- the 27 P1 operator/operator-relation records;
- the 74 P2 relation/process/structure records;
- the 117 empirical relation objects/hyperedges;

the remaining vertex population is:

\[
\boxed{209/209}
\]

and divides as:

- **Address/role vertices:** 30
- **State/class/parameter vertices:** 115
- **Entity/carrier/faculty vertices:** 64

## Decision

These records remain first-class ontology vertices.

They do **not** create a fifth operation mode merely because a class, state, dimension, or entity can participate in generation.

The correct representation is:

\[
\text{typed vertex}
+
\text{source-backed generative relation/action}
\]

not:

\[
\text{CLASS}\Rightarrow\text{automatic generator}.
\]

This preserves the recovered SUN rule that a class may be a **relational generative state** while still requiring the actual generative transition to be explicit.

## Consequence

No fifth operation mode is required by the remaining 209 vertices.

Therefore the current full-corpus operation-shape candidate remains:

\[
\boxed{
\Omega_{\rm SUN}^{(0.1)}=
\{A1,A2,A3,A4\}
}
\]

where:

- **A1:** typed deterministic action;
- **A2:** parameterized constructor/composition;
- **A3:** joint-constitution hyperedge;
- **A4:** stochastic transition/expectation kernel.

This is now sufficient for:

- all 27 P1 operator records;
- all 74 P2 relation/process/structure records;
- all 117 empirical hyperedges;
- all 209 remaining typed vertices as operands/states/addresses/classes/carriers.

Total semantic declarations accounted for:

\[
27+74+117+209=427.
\]

\[
\boxed{427/427\ \text{semantically accounted for}}
\]

## Important limitation

This is a **sufficiency result**, not a proof that four is globally minimal.

A smaller mathematical encoding is possible by erasing distinctions (for example representing deterministic maps as degenerate stochastic kernels), but that is disallowed by the semantic-preservation criterion.

A true minimality proof must show that no two of A1–A4 can be merged **without losing a protected source-supported distinction**.
