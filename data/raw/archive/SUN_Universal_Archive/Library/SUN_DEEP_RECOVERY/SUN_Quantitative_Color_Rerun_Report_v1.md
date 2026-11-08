# SUN Quantitative Color Rerun v1

## 1. Acoustic analogue correction

Yes: absorption and scattering have legitimate sound analogues, and these are stronger operator-level analogues than sonoluminescence.

The best comparison to subtractive material color is:

**broadband spectrum → frequency-dependent material operator → altered spectrum**

For acoustics:
`P_out(f) = |H(f)|² P_in(f)` in a simple linear spectral-filter picture.

For optics:
`S_out(λ) = T(λ) S_in(λ)` for a simple spectral-transmission picture.

Cascaded filters multiply transfer/transmission functions. In logarithmic attenuation measures, losses add.

Multiple-scattering theory is also genuinely cross-wave: sound and light both admit scattering, transport and diffusion-level descriptions.

This does NOT make pigment and acoustic materials physically identical. It identifies a common operator family:
**spectral filtering + absorption + scattering + transport.**

## 2. Historical score recovered exactly

The old aggregate scores were reproducible:

- 3-state: 0.501630
- 6-state: 0.643856
- 12-state: 0.162930

The recovered formula is:

`S_n = (1/3) Σ_i n |p_i - nearest_n_grid(p_i)|`

So the remembered `0.502 / 0.644 / 0.163` sequence is genuine project arithmetic.

## 3. Quantitative carriers frozen before scoring

Carrier freeze SHA-256:

`d7386e215239422a250858e0a40ff09fcd0419bfb7ba9f86589bab6468112b0f`

Frozen tests:
1. historical equal-sector RYB baseline;
2. linear-light sRGB mixture wheel represented in CIE 1931 xy hue angle;
3. same physical states in CIE 1976 u'v' hue angle;
4. same states in CIELAB hue angle;
5. CIE 1931 spectral-boundary projection/arclength;
6. monochromatic-wavelength diagnostic.

No sound-dependent rotation, rescaling or color-state reassignment was allowed.

The original slot map stayed:

`0, 2, 4, 5, 7, 9, 11, 12`.

## 4. Results

| Carrier | Score | Relative to old 12-sector score |
|---|---:|---:|
| Historical equal RYB 12 | 0.162930 | 1.00× |
| sRGB → CIE 1976 u'v' hue | 0.542657 | 3.33× |
| sRGB → CIELAB hue | 0.930247 | 5.71× |
| sRGB → CIE 1931 xy hue | 1.010780 | 6.20× |
| CIE 1931 boundary arclength | 1.252725 | 7.69× |

The old global alignment does **not** survive these quantitative embeddings.

The best quantitative version tested here is CIE 1976 u'v', but its score is still about
**3.33× worse**
than the equal-sector RYB result.

## 5. Spectral carrier result

The CIE-boundary projection produces real dominant wavelengths for additive states 0–8.

States 9–11 land on the **line of purples**, not the monochromatic spectral locus.

So:

**a one-dimensional wavelength carrier cannot represent the full 12-state closed color wheel.**

The wheel closure is partly a generated/perceptual/additive construction, not simply the visible wavelength line folded into a circle.

## 6. F/G residual correction

The old equal-wheel result placed F and G at `5/12` and `7/12`.

Because:

`log2(4/3) + log2(3/2) = 1`

and:

`5/12 + 7/12 = 1`,

their signed residuals must be exact opposites.

Therefore the old ±0.5865° symmetry is **algebraically forced by the chosen symmetric color slots**, not an independent validation signal.

Some quantitative carriers approximately retain fourth/fifth complementarity, especially CIE-boundary and u'v', but with much larger residuals. That can be tested separately without treating the original symmetry as evidence.

## 7. Current conclusion

What survives is narrower:

- the abstract 3-generator / pairwise-combination / joint-aggregate grammar;
- legitimate cross-wave absorption/scattering/filtering analogues;
- a possible complementarity question;
- the need to test scale-transition structure separately from equal-sector hue geometry.

What does **not** survive this first quantitative rerun is the claim that the old near-perfect 12-sector sound/color positional alignment is representation-invariant.

That is a useful falsification/constraint, not a failure of the whole SUN program.
