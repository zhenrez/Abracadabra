# SUN Color Operator-Transition Test v1

## Result

**SCOPED_STRUCTURAL_PASS — 3/3 operator tests pass.**

### P1 — filtering/action
Sequential spectral filtering equals the composed transfer function.

- composition error: `0.000e+00`
- log-attenuation additivity error: `2.220e-16`

This matches SUN's **typed deterministic action** role.

### P2 — generated nonspectral state
A positive mixture of the CIE 1931 380 nm and 700 nm endpoint stimuli gives chromaticity:

- 380 nm: `(0.174112, 0.004964)`
- 700 nm: `(0.734690, 0.265310)`
- mixture: `(0.545805, 0.177587)`

It lies strictly inside the chord joining the endpoints:

- line parameter `t = 0.663052`
- chord residual `2.776e-17`

That is the geometry of a generated purple-side chromatic state rather than either monochromatic endpoint.

This matches SUN's **constructor / joint-constitution** role.

### P3 — observer projection / quotient
Using four monochromatic basis components at 450, 500, 550 and 600 nm, the CIE XYZ response is a 3×4 matrix of rank `3`.

Therefore there is a nonzero spectral null direction.

- null residual: `2.238e-16`
- source-spectrum difference norm: `1.821405`
- XYZ difference norm: `4.965e-16`

Two physically distinct nonnegative spectra therefore map to the same XYZ tristimulus vector to numerical precision.

This matches SUN's **mapping/equivalence + observer projection** role.

## Interpretation

The frozen SUN grammar correctly keeps these three operations distinct:

1. transform an existing spectrum;
2. constitute a new chromatic state from multiple components;
3. collapse distinct upstream spectra into one downstream observer-space state.

That is a real structural pass.

It is **not** unique confirmation of SUN, because standard linear algebra and colorimetry independently contain these structures. The harder next test is whether SUN predicts a nontrivial invariant that survives all three transitions.
