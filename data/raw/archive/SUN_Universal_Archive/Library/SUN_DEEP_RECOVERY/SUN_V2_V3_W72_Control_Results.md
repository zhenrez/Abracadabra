# SUN V2 / V3 W72 control results

Date: 2026-10-01. Method: parallel, separate formal audits of the current specifications, primary-text checks by the coordinating reviewer, and exhaustive finite computation. This is a masked deductive replay, not a fresh blind discovery or an execution of two implemented decoders. No specifications or historical trial records were changed.

## Result

Both specifications support withholding unsupported W72 conclusions on all seven controls. This is a logical-conformance assessment, not a measured classifier accuracy of 7/7. Both also leave the strongest positive benchmark conditional: a 70-person population that can be paired need not consist of 35 pairs preserved from a particular 72-person population.

The earlier unconditional full-recovery PASS and the claim that V3 is demonstrably faster/better are not substantiated by this replay. V3 supplies a compact mathematical representation; historical assignment of its coordinates still needs an adapter.

## Authoritative inputs

- [V2 specification](https://github.com/AlkaiDynamics/Symphonia-Universalis-Numinous/blob/main/versions/v2/SUN_V2_SYMPHONIA_UNIVERSALIS_NEUMINA.md), retrieved blob `afc135fd13fd2cae56c9cc24dced5440d92a55da`.
- [V3 specification](https://github.com/AlkaiDynamics/Symphonia-Universalis-Numinous/blob/main/versions/v3/SUN_V3_FORMAL_SPECIFICATION.md), retrieved blob `23e9803267fcd2e4e58b885c9888c89c925a7cd1`.

V2 sections II, XIII, XIX, XXVI, XXXI, XXXII separate counts from relations, require lawful adapters, and prohibit unlicensed empirical scoring. Its imported historical 70/72 assertion and numerical unitization examples were excluded as proof premises. The document labels V2 candidate/unlocked and requires attachment of its original musical proof before lock. This audit does not adjudicate that unrecovered original proof.

V3 sections 0, 6, 9 restrict component claims to declared music-native scope, make Addr72 a removable representation, and defer the satisfaction interface. Its mathematical carrier is available; a biblical person-to-address realization is not specified there. The review therefore distinguishes abstract consequences from conditional external realizations.

The reviewers worked concurrently in separate contexts. Both received case facts and the instruction to examine pair preservation; this was not an uncontrolled discovery trial, a preregistered new empirical trial, or an independent test of LLM blindness. Neither reviewer received the other review before returning its conclusion.

## Complete control ladder

Here “withhold” means not entailed by the scoped input, not disproved everywhere in the wider tradition. Both audits reached the following outcomes.

| Case | V2 permitted conclusion | V3 permitted conclusion | W72 conclusion withheld |
|---|---|---|---|
| Mark 6:7 | Twelve sent in pairs; six dyads under exhaustive disjoint deployment | Same source-level result; 72-address embedding unnecessary | No 72 population or exceptional pair |
| Exodus 24:1 | Seventy elders | Same source-level count | No underlying 72, actual 35-pair partition, or two excluded persons |
| Numbers 1:20–43 | Tribal organization with unequal census totals | Same; cannot substitute six members per tribe | No uniform 12×6 organization |
| Synthetic ablation: 72 people, no relations | Cardinality 72; arbitrary partitions possible | Abstract Addr72 and CRT fibers constructible | No identified historical pair relation or kinship |
| Luke 10:1, both count readings | 35 or 36 sending pairs in respective readings | Same; 72 reading can be represented after an adapter | No demonstrated subset/removal relation between manuscripts; no shared lineage |
| Acts 13:2–3 | Two named people commissioned together | Same source-level relation | No 70/72 organization or residual-pair status |
| Genesis 40 | Two officials with distinct dreams/outcomes and shared institutional context | Same; an optional two-label representation | No common father/tribe or exceptional W72 pair |

The fourth case is deliberately synthetic, not a newly discovered biblical corpus. It tests the proposed “72 without pairing” condition exactly. The six other cases use the passages listed. They cover the full requested feature ladder, including the separate differentiation-without-genealogy control.

V3's correct response to the fourth case is NOT to deny the algebraic identity 72=36×2. It must distinguish that identity from evidence that the people had that native pairing. Likewise 70=35×2 is true in Exodus; actual pairing of the elders is not established by that arithmetic.

## Positive benchmark, rescored

| Claim | V2 | V3 |
|---|---|---|
| Six per twelve gives 72; seventy plus two gives 72 | Supported arithmetic from supplied textual observations | Same |
| Epiphanius' translators comprise 36 pairs | Source-supplied structure | Same; also compatible with abstract CRT representation |
| Luke's alternative readings yield 35 or 36 pairs | Supported separately | Same |
| Two exceptional men share a father in the Targum | Source-supplied, representable | Source-supplied, representable |
| Tribal assignment through Numbers 34:25 | Conditional on identifying the named father across witnesses | Same |
| Residue must be one pair of the SAME original partition | Not entailed without preservation condition | Not entailed without preservation condition |
| Shared father must be the Z3 coordinate | No | No; CRT provides no father semantics |
| Distinct men imply opposite binary labels | Only after selecting a two-person fiber and injective labeling | Same |
| Faster / lower total assumption cost / better discrimination | Not measured | Not established |

The historical data remain informative. Targum Pseudo-Jonathan supplies shared parentage and differentiated prophecy; Numbers 34:25 names Elizaphan son of Parnach with Zebulun. Encoding those known facts is reconstruction, not a withheld prediction. Neither text establishes a global partition into three paternal pairs per tribe.

Sanhedrin's lottery and the account of Eldad/Medad's voluntary remaining must retain their distinct witness interpretations; the two blank slips must not automatically be equated with these named men across every account. Luke's manuscript variants likewise are alternative counts, not automatically a temporal 72-to-70 removal event. Epiphanius' pairing concerns translators; transferring it to elders requires a relation-preserving correspondence.

## Exact theorem and counterexample

Let X be a set of 72 with a fixed-point-free pairing involution q. Let A be a subset with 70 elements. Then:

**A is a union of original pairs if and only if X minus A is one original pair.**

Proof: q-invariance of A implies q-invariance of its two-element complement. Since q has no fixed point, it swaps those two elements. The converse follows by deleting one orbit from a disjoint union of pair orbits.

Merely saying A admits some pairing does not imply q-invariance. Remove one endpoint from each of two different original pairs. Keep the other 34 pairs and pair the two surviving endpoints together. Now A again has 35 pairs, but its complement is not an original pair. This defeats the stronger inference even within one population, before any cross-text identification issue arises.

For V3 let X=Z12×Z6, with q(p,k)=(p,k+3 mod 6). CRT sends (p,k) to (p,k mod 3,k mod 2). The original fibers fix p and k mod 3. Remove (0,0) and (0,1): the people share p, but occupy different fibers. A shared-father predicate can be assigned to those two without violating the algebra, because V3 defines no equation identifying father with k mod 3. Thus common tribe and father still do not force the claimed fiber without the genealogical adapter.

## Executed finite verification

A Python exhaustive check completed with exit code 0. It verified the CRT bijection, all 36 original fibers, the theorem for every two-address removal, and an explicit 35-pair re-pairing counterexample.

| Quantity | Actual result |
|---|---:|
| Addresses | 72 |
| Original fibers | 36 |
| All unordered two-address removals | 2,556 |
| Removals of one original fiber | 36 |
| Removals breaking two fibers | 2,520 |
| Pair-preservation equivalence failures | 0 |

These are enumeration counts, not empirical probabilities or a historical significance test.

Reproduction code for the executed mathematical check:

```python
from itertools import combinations, product
from math import comb
X = set(product(range(12), range(6)))
def proj(x): return x[0], x[1] % 3
def mate(x): return x[0], (x[1] + 3) % 6
pairs = {frozenset((x, mate(x))) for x in X}
assert len(X) == 72 and len(pairs) == 36
assert len({(p, k % 3, k % 2) for p, k in X}) == 72
intact = broken = 0
for removed in combinations(sorted(X), 2):
    A = X - set(removed)
    invariant = all(mate(x) in A for x in A)
    same = proj(removed[0]) == proj(removed[1])
    assert invariant == same
    intact += same
    broken += not same
A = X - {(0, 0), (0, 1)}
survivors = sorted(A)
new_pairs = list(zip(survivors[::2], survivors[1::2]))
assert len(new_pairs) == 35
assert not all(mate(x) in A for x in A)
assert {x for pair in new_pairs for x in pair} == A
assert (comb(72, 2), intact, broken) == (2556, 36, 2520)
print('CRT and all 2556 removal cases verified; re-pairing counterexample verified')
```

## Evidence and limits

Primary passages checked online:

- [Mark 6:7](https://www.biblegateway.com/passage/?search=Mark+6%3A7&version=KJV)
- [Exodus 24](https://www.biblegateway.com/passage/?search=Exodus+24&version=KJV)
- [Numbers 1](https://www.biblegateway.com/passage/?search=Numbers+1&version=KJV)
- [Luke 10, including variant footnote](https://www.biblegateway.com/passage/?search=Luke+10&version=NIV)
- [Acts 13:2–3](https://www.biblegateway.com/passage/?search=Acts+13%3A2-3&version=NIV)
- [Genesis 40](https://www.biblegateway.com/passage/?search=Genesis+40&version=NIV)
- [Numbers 11:16–30](https://www.biblegateway.com/passage/?search=Numbers+11%3A16-30&version=KJV)
- [Numbers 34:25](https://www.biblegateway.com/passage/?search=Numbers+34%3A25&version=KJV)
- [Sanhedrin 17a](https://www.sefaria.org/Sanhedrin.17a?with=Talmud)
- [Targum Jonathan on Numbers 11:26](https://www.sefaria.org/Targum_Jonathan_on_Numbers.11.26)
- [Epiphanius, Weights and Measures, Dean translation](https://www.tertullian.org/fathers/epiphanius_weights_03_text.htm)

Sefaria's opened pages sometimes returned only interface text; relevant Sanhedrin and Targum passages were confirmed through indexed primary-page extracts. No full critical-edition or manuscript collation was performed.

The package cannot simultaneously provide Epiphanius' “36 cells, two per cell” fact and claim that recovery of 36×2 is an unseen prediction. It can exclude earlier W72 interpretation while retaining that source fact, but then the arithmetic is source-assisted reconstruction.

No full original W72 prediction ledger, timings, or proof trace was recovered in this run. No new empirical V1-D score is claimed. The result revises the immediately preceding replay assessment only; it does not retroactively invalidate the original historical trial.

The next unresolved proof obligation is specific: justify and freeze a biblical adapter that preserves the same pair relation and maps genealogy to the proposed address coordinates. Without that, V3's shorter notation is confirmed, but superior predictive performance is unresolved.
