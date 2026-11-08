# Exact native scalar root extension

Zhu's source q=2^(1/12) is now represented exactly, with no frequency approximation. The module extends the native scalar carrier using finite positive prime monomials with rational exponents. It covers G, q, 16/15 and81/80; it does not claim every algebraic real. The original native-execution register remains unchanged.

The source is SUN_GG_v1_final.json, occurrence 9e03168cabf04e3887245d93c75f1f9d0034a53bead61e5d8b5a5e0315b259e8, SHA-256 6a92f9710fa6cd2937b9b07c42315b7d9c80644bd453c659f17318f95c55f95d, pointer /generative_registry/0. Full literal MEC-01 definition and exact computed inputs are retained in the [machine register](../../state/reconstruction/algebraic-extension.json).

## Exact carrier and proof

**ALG-FAITHFUL: Positive prime-monomial normal form is faithful.**

If two products are equal, divide and raise to a common positive multiple N of every exponent denominator. Moving negative powers to the other side gives equality of positive integers with prime factorizations. Unique prime factorization forces every N*(alpha_p-beta_p)=0, hence alpha_p=beta_p. Conversely identical exponents give identical positive products.

**ALG-G: G=<R,L>={2^a3^b:a,b in Z}.**

R,L have (nu2,nu3) columns(1,-1),(-2,1), determinant-1. Thus they span the complete integer lattice. Explicitly2=R^-1 L^-1 and3=R^-2 L^-1.

**ALG-H: H=<G,q>={2^(a/12)3^b:a,b in Z}, H/G is C12.**

Adding q adds(1/12,0) to the G lattice. Modulo G only a mod12 survives. Distinct residues0..11 cannot collapse because faithfulness would require their prime2exponent difference to be an integer.

**ALG-OCTAVE: H/<2> is C12 x Z and is infinite.**

The homomorphism2^(a/12)3^b -> (a mod12,b) is surjective, with kernel{2^m:m in Z}. The second coordinate remains an arbitrary integer. This quotient differs from H/G, which also discards all integer prime3powers.

**ALG-FIFTH: delta=q^7/(3/2)=2^(19/12)/3 is nonidentity and delta^12=524288/531441=(531441/524288)^-1.**

Subtract the pure-fifth exponent vector(-1,1) from q^7=(7/12,0). The result(19/12,-1) is nonzero. Multiplication by12 gives(19,-12); exact rational materialization gives2^19/3^12. The ordinary twelve-fifths/seven-octaves residual has vector(-19,12).

The implementation checks source bytes before binding the extension. Prime powers are combined, reduced and sorted exactly. Prime bases are bounded to1000000, at most64 input terms, exponent strings128 digits, rational-factorization inputs10^12, and materialized rational output32768bits. Unsupported output size stays exact in monomial form; it never becomes a rounded value. These are computational bounds, not claims that the mathematical groups are finite.

## Octave and dial distinction

Taking the quotient by integer octaves removes only the INTEGER part of the prime2exponent. The fractional part survives. Thus q has root residue1 and is not the identity. For exponent-1/12, the exact remainder is11/12 with removed octave-1. The returned representative normalizes the exponent of prime2 into[0,1); it does not normalize numeric frequency into[1,2). No frequency-ordering procedure is claimed.

H/G discards every integer3exponent and has12cosets. H/<2> retains that unbounded integer coordinate and is C12 x Z. A twelve-dial label shared by pure3/2 and q^7, if independently declared, is insufficient to establish exact pitch equality. Here their exact exponent vectors are(-1,1) and(7/12,0), respectively, and their difference is(19/12,-1). No universal dial map or historical wheel orientation is inferred.

## Actual decisions and verification

Actual SuperJev resolved jev-1.14.0, selected prime rational exponents1.0 and retaining the comma0.96; it assessed the quotient hypothesis true0.67 and exact fifth equality false0.88. The [full request](../evidence/algebraic-extension-jev-request.json) and [full result](../evidence/algebraic-extension-jev-result.json) remain separate from the exact proofs.

Build and all7focused tests pass. Tests verify the source root relation, generator lattice witnesses, twelve distinct cosets, retained integer3coordinates-40..40, negative fractional-octave reduction, exact delta/comma cancellation, bridge rational preservation and input/resource boundaries. Wolfram independently returns q^12=2, delta^12=524288/531441, fifth equality False, comma cancellation True, negative remainder11/12 and determinant-1. [Full Wolfram receipt](../evidence/algebraic-extension-wolfram-result.json).

This is a source-conditional extension and connected mathematical consequence, not a blind discovery or a global historical orientation result. Reproduce with npm run build, then node scripts/reconstruct_algebraic_extension.mjs. No service or background worker is created.
