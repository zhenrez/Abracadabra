# SUN — Fourth-Step Boundary Activation Dependency Audit v0.1

## Claim under audit

Does the frozen SUN mechanism contain a rule that **derives** the switch

\[
C_3\to C_4
\]

from ordinary scalar generation into the lifted FK boundary, or is that switch an independent structural stipulation?

## Primary verdict

\[
\boxed{\textbf{INDEPENDENT STRUCTURAL STIPULATION}}
\]

The full frozen SUN specification **requires** exactly three ordinary generations and then a boundary transition. But the recovered sources do not derive the activation of that boundary from \(R,L,\kappa\), the scalar state \(C_3\), the comma invariant, or the reciprocal FK arithmetic.

In other words:

\[
\boxed{
\text{forced by the frozen grammar as an axiom}
\neq
\text{derived from the earlier algebra}.
}
\]

## Dependency graph

The numerical dependency stack is:

\[
R=\frac23,\qquad L=\frac34
\]

\[
S=RL=\frac12,\qquad T=L/R=\frac98,\qquad Q=L^{-1}=\frac43
\]

\[
\lambda=R^2L^{-3}=\frac{256}{243}
\]

plus the independent 5-limit generator

\[
\kappa=\frac{81}{80},
\]

which gives

\[
\rho=\kappa\lambda=\frac{16}{15}.
\]

These values determine the numerical constants used by the FK boundary, but none yields a predicate of the form

\[
\boxed{
\operatorname{BoundaryNow}(C_n,R,L,\kappa)=
\begin{cases}
0,&n<3\\
1,&n=3.
\end{cases}
}
\]

No recovered source supplies such a predicate.

Instead the source states directly that the grammar contains exactly three ordinary recursive generations followed by a distinct boundary transition.

## Decisive countermodel

Normalize \(F=1\).

The ordinary scalar law alone gives

\[
C_n=2^{-n}.
\]

At the fourth step it remains perfectly well-defined:

\[
C_3=\frac18,
\]

\[
R_3=\frac1{12},
\qquad
L_3=\frac3{32},
\]

and

\[
\frac{R_3L_3}{C_3}
=
\frac1{16}
=
C_4.
\]

So **Model A** is:

\[
\frac18
\to
\left(\frac1{12},\frac3{32}\right)
\to
\frac1{16}.
\]

The frozen FK boundary instead gives **Model B**:

\[
\frac18
\to
\frac{2}{15}
\to
\frac1{16},
\]

with local lifted labels

\[
(\rho,0)\star(\rho^{-1},1)=(1,1),
\qquad
\rho=\frac{16}{15}.
\]

Both models use the same frozen numerical constants and agree on the same scalar endpoint:

\[
\boxed{
C_4=\frac1{16}.
}
\]

They differ only in internal path/history and the presence of the lifted grade.

Therefore the numerical algebra does not entail the switch. If it did, Model A could not satisfy the same numerical kernel.

## What *is* frozen

The boundary switch is frozen as part of the structural grammar:

\[
C_0\to C_1\to C_2\to C_3
\xrightarrow{\mathcal B}
C_4.
\]

That makes the switch a legitimate component of SUN's formal hypothesis.

But its status is:

\[
\boxed{
\text{structural axiom / hypothesis}
}
\]

rather than

\[
\boxed{
\text{theorem derived from }R,L,\kappa.
}
\]

The same source family explicitly records that the FK generation increment is assigned rather than derived from the reciprocal ratios.

## Smallest missing implication

To turn the boundary from an independent stipulation into a generated mechanism, SUN needs one additional implication:

\[
\boxed{
\text{state/history condition at }C_3
\Longrightarrow
\text{ordinary representation becomes insufficient}
\Longrightarrow
\mathcal B.
}
\]

No such implication is present in the recovered frozen specification.

It would have to explain **why the richer path/history representation becomes necessary specifically there**, while preserving the fact that the scalar endpoint is unchanged.

## Strongest safe statement

The recovered SUN stack establishes:

\[
\boxed{
\text{three ordinary scalar generations}
+
\text{a stipulated lifted fourth transition with the same scalar endpoint}.
}
\]

It does **not** establish:

\[
\boxed{
\text{why the lifted transition must activate after the third ordinary generation}.
}
\]

That is now the exact irreducible gap.
