# Which observations resolve the recovered score?

Actual local AgentJev-0.6B selected this extension in receipt000058-bbb3ab44bbf5. The mathematical result is derived independently of that preference.

The retained GT-TIME-OVERLAP experiment has five positive ordered stage durations and three lifespan equations:

`lA=d1+d2+d3`, `lB=d2+d3+d4`, `lC=d3+d4+d5`.

The stages are soloA, A+B, A+B+C, B+C and soloC. Units remain the witness's reported years. Birth/entrance and death/exit are declared experiment conditions; lifetime is not defined as audible sustain.

Two timing freedoms remain. Two further observations resolve them only if their restrictions to that two-dimensional ambiguity are independent. Exactly eight of the ten pairs of individual stage durations suffice. Pairs **d1+d4** and **d2+d5** remain redundant because:

`d4-d1=lB-lA`, `d5-d2=lC-lB`.

Knowing d1 already fixes d4, and knowing d2 already fixes d5. Measuring both members of either pair leaves one unresolved timing freedom. Every other pair resolves both freedoms within this source-conditioned linear system.

For example, with the exposed MT lifespans438,433,464, anchors d1=35 and d2=30 imply d3=373,d4=30,d5=61. With d1 alone, d4=30 follows while the other durations retain alternatives. Positive ordering requires d1>5,d2>0,d1+d2<438; an algebraically unique answer that violates these inequalities does not describe the retained ordering.

A deliberately inconsistent example, d1=35 and d4=31, conflicts with lifespanA438 and lifespanB433. Those four equations are the minimal incompatible subset. LifespanC is irrelevant to that conflict. This is a synthetic control, not evidence of an error in an ancient witness.

The method also predicts arbitrary supplied linear observables within this domain: a target is fixed exactly when its covector annihilates every remaining null vector. An invertible change from stage durations to cumulative event offsets preserves solutions when every equation and anchor transforms consistently. This does not supply adapters for arbitrary historical, phonetic or nonlinear domains.

Execution covers all ten anchor pairs across all five retained numerical witnesses:50exposed replays. All40independent-pair replays also reconstruct correctly after the invertible coordinate change. Five independent tests use installed SymPy1.14.0 to verify symbolic formulas, ranks, all50cases, minimal incompatibility, partial predictions and the negative-duration control. The actual Prumo adapter separately computes a redundant-pair determinant as0; its hand-set weights are not historical probabilities.

The linear-algebra method reuses [row-space/nullspace duality](https://math.mit.edu/~gs/linearalgebra/ila5/linearalgebra5_6Great.pdf) and [exact Gauss–Jordan methods](https://docs.sympy.org/latest/modules/matrices/matrices.html). SUNNY's added result is the concrete sufficient/redundant observation classification and consequences for this recovered score, not a claim of a new general theorem.

Reproduce with `python -X utf8 -B scripts/derive_score_anchors.py` and `runtime/.venv/Scripts/python.exe -X utf8 -B tests/score_anchors_independent.py -v`. The canonical module is `state/reconstruction/score-anchor-constraints.json`; it includes preserved input snapshots, source conditions, all alternatives, code hashes and Jev receipt. The workbench's Constraints panel exposes the same cases.

This advances the native mathematical, transformation, generational timing, constraint, proof, discrepancy, prediction and master-score registers within its declared scope. Original sounds, complete geometry, global alignment and blind historical prediction remain unresolved.
