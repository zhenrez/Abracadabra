# SUN_PROSPECTIVE_TRIAL_0_PREREGISTRATION_CLOSED_DRAFT

**Status:** PREREGISTRATION-CLOSURE DRAFT; NOT COMMITTED  
**SUN version:** SUN V1 B — LOCKED FORMAL HYPOTHESIS  
**Trial family:** SEALED SMALL-FINITE-GRAPH COMPLETION  
**Concrete hidden graph generated:** NO  
**SUN empirical prediction exists:** NO  

This document closes the preregistration blockers identified after review of the first Trial-0 preregistration draft. It does not generate `G_star`, reveal a target, hash a prereveal prediction, or license a confirmatory claim.

---

## 0. Blocking repairs applied

The previous draft is superseded by the following explicit repairs.

1. **Sampler law specified.** The graph sampler, target balancing, mask law, seed custody, and no-resampling rule are now literal.
2. **Native models separated from completion states.** The native model language is singleton: `M_completion`. The `2^m` objects are completion states, not native models.
3. **Oracle-dependency firewall repaired.** The previous global common-neighbor predicate made `Lambda_T_star` expand to the whole graph. The target is now a fixed-window local-cell predicate with static dependency set of six edge bits. The mask contains all six target dependencies plus four decoys, so `Lambda_T_star subset M` holds by construction.
4. **Boundary semantics repaired.** `S_E^(SUN)` now includes both `3G` and the boundary nonordinary clause. The `{0}` prediction branch is removed.
5. **Adapter exhaustion made finite.** The adapter language consists of exactly `2^3 = 8` oriented representatives of one unordered adapter, quotiented by `S_2^3` branch-pair gauge.
6. **Verifier languages instantiated.** Dependency, discovery, noninterference, native-completion, realization, and truth-oracle verifiers are defined as finite checks.
7. **Commitment mechanics frozen.** Canonical serialization, byte encoding, file ordering, hash algorithm, timestamp object, seed custody, and reveal verification are specified.

---

## 1. GOAL CARD

* **GOAL:** Preregister a single Trial-0 shakedown instance family without generating the hidden graph.
* **WHY:** Trial 0 tests whether the SUN V1 B harness can freeze, close, mask, enumerate, commit, stop, reveal, and score one finite target without drift.
* **ALLOWED CONSTRAINTS:** Finite simple undirected graph theory; fixed SUN subgrammar `{3G, B}` only; fixed local-cell graph adapter; SET-mode scoring.
* **STOP CONDITION:** After this preregistration is accepted and committed, no modeling changes are permitted. Before acceptance, no hidden graph may be generated.
* **CURRENT STATE:** Candidate family elected; preregistration closed in draft form; no concrete `G_star`; no licensed prediction.

---

## 2. Native domain and fixed parameters

Let

```math
D = \mathsf{FinSimpleUndirectedGraph}_{n=13,m=10}.
```

The vertex set is fixed:

```math
V = \{0,1,2,3,4,5,6,7,8,9,10,11,12\}.
```

Edges are unordered pairs:

```math
e(i,j)=\{i,j\},\qquad 0\le i<j\le 12.
```

The complete edge universe is

```math
E_{13}=\{e(i,j):0\le i<j\le 12\},\qquad |E_{13}|=78.
```

This changes the first draft's `n=11` to `n=13` because the boundary target now uses its own fixed branch pair `{11,12}`. The change is preregistration-level only; no graph has been generated.

---

## 3. Local graph-cell predicate

For distinct vertices `a,b,u,v`, define the fixed-window local ordinary cell predicate:

```math
\operatorname{Cell}_G(a,b;u,v)=1
```

iff all of the following hold:

```math
E_G(a,u)=1,
E_G(b,u)=1,
E_G(a,v)=1,
E_G(b,v)=1,
E_G(a,b)=0,
E_G(u,v)=0.
```

Equivalently:

```math
\operatorname{Cell}_G(a,b;u,v)
=
E_{au}E_{bu}E_{av}E_{bv}(1-E_{ab})(1-E_{uv}).
```

This is intentionally a **local fixed-window cell**, not the global common-neighbor predicate. It has a static six-edge dependency set and is therefore compatible with a finite mask of size `m=10`.

---

## 4. Frozen SUN graph scaffold

The fixed centers are:

```math
(C_0,C_1,C_2,C_3,C_4)=(0,1,2,3,4).
```

The three ordinary branch pairs are:

```math
B_0=\{5,6\},\qquad B_1=\{7,8\},\qquad B_2=\{9,10\}.
```

The boundary probe pair is:

```math
B_3=\{11,12\}.
```

Define

```math
3G(G)
:=
\operatorname{Cell}_G(0,1;5,6)
\land
\operatorname{Cell}_G(1,2;7,8)
\land
\operatorname{Cell}_G(2,3;9,10).
```

Define the boundary-ordinary predicate:

```math
BOrd(G):=\operatorname{Cell}_G(3,4;11,12).
```

The target is the nonordinary boundary property:

```math
T(G)=1-BOrd(G).
```

So:

```math
T(G)=1
\iff
\text{the fourth transition is nonordinary under the frozen local-cell window.}
```

---

## 5. Truth-oracle dependency closure

The target depends exactly on the six edge bits used by `BOrd`:

```math
\Lambda_T^\star
=
\{e(3,11),e(4,11),e(3,12),e(4,12),e(3,4),e(11,12)\}.
```

This dependency set is static because the branch candidates `{11,12}` are frozen before graph generation.

The prior global predicate `Ord_G(3,4)` is explicitly **not used** in Trial 0, because its complete dependency closure would require every edge in the graph: determining the complete common-neighbor set of vertices `3` and `4` plus the edge between whichever two common neighbors occur is not compatible with `m=10`.

---

## 6. Mask-selection law

The mask is deterministic and fixed before graph generation.

Target-dependency mask:

```math
M_T=\Lambda_T^\star.
```

Four decoy masked edges:

```math
M_D=\{e(0,12),e(1,11),e(2,12),e(5,7)\}.
```

Full mask:

```math
M=M_T\cup M_D.
```

Therefore:

```math
|M|=10,
\qquad
\Lambda_T^\star\subseteq M.
```

The visible graph is:

```math
G_{vis}=\mu_T^\star(G^\star),
```

where every edge in `M` is replaced by the literal token `MASKED`, and every edge outside `M` is shown as `0` or `1`.

---

## 7. Full-graph sampler law

There is exactly one committed draw per Trial-0 instance. There is no resampling.

### 7.1 Seed custody

At instantiation time only, generate:

```text
trial_seed      = 256-bit CSPRNG value
truth_nonce     = 256-bit CSPRNG value
boundary_truth  = one fair CSPRNG bit in {0,1}
```

These values are written only into the sealed truth artifact before reveal.

### 7.2 Initial random graph

For every edge in `E_13`, draw an independent fair bit.

### 7.3 Force the visible three-generation scaffold

Overwrite the following local-cell constraints:

For `(a,b;u,v)=(0,1;5,6)`, `(1,2;7,8)`, `(2,3;9,10)` set:

```text
E(a,u)=1
E(b,u)=1
E(a,v)=1
E(b,v)=1
E(a,b)=0
E(u,v)=0
```

This makes `3G(G_star)=1` by construction. Trial 0 is a protocol shakedown, so this scaffold is permitted but cannot be treated as cross-domain empirical support.

### 7.4 Balanced boundary target generation

Let the six target-dependency edges be ordered exactly as:

```text
LAMBDA_ORDER = [e(3,11), e(4,11), e(3,12), e(4,12), e(3,4), e(11,12)]
```

The unique bit pattern making `BOrd(G)=1` is:

```text
[1,1,1,1,0,0]
```

If `boundary_truth = 0`, set the six target-dependency bits to `[1,1,1,1,0,0]`, so `T(G_star)=0`.

If `boundary_truth = 1`, sample uniformly from the other 63 six-bit strings, so `T(G_star)=1`.

Thus the sealed target truth is balanced:

```math
\Pr[T(G^\star)=0]=\Pr[T(G^\star)=1]=\frac12.
```

This prevents Trial 0 from being a trivial high-base-rate pass.

### 7.5 Decoy bits

Edges in `M_D` remain independent fair CSPRNG bits.

### 7.6 No resampling rule

After one `G_star` is produced:

```math
\boxed{\text{one committed draw = one Trial-0 instance}.}
```

If the trial terminates with any stop condition, including `NO-HEADROOM`, `NO-REALIZATION`, `NONUNIQUE`, `PREREVEAL-INCONSISTENT`, or `NONINFORMATIVE`, that result is recorded. No replacement graph is drawn.

---

## 8. Native model language versus completion states

The native model language is singleton:

```math
\mathcal L_M^{(0)}=\{M_{completion}\}.
```

The admissibility predicate is:

```math
W_D(M_{completion})=1.
```

Therefore:

```math
\mathfrak M_D^{(0)}=\{M_{completion}\}.
```

The model-induced visible state space is not the model language. It is the set of all completions of the masked bits:

```math
S_{E,M_{completion}}^{(0)}
=
\{G:\;G|_{E_{13}\setminus M}=G_{vis}|_{E_{13}\setminus M}\}.
```

Since `|M|=10`:

```math
|S_{E,M_{completion}}^{(0)}|=2^{10}=1024.
```

The native-model closure certificate is:

```math
Q_D^M=1
```

iff the verifier confirms that `L_M^(0)` contains exactly one model object, `M_completion`, and that `W_D(M_completion)=1`.

A separate completion-exhaustion certificate verifies all `1024` completion states.

---

## 9. Native target baseline and headroom

The native target set is:

```math
\mathcal C_0^{eval}
=
\{T(G):G\in S_{E,M_{completion}}^{(0)}\}.
```

Because all six target-dependency bits are masked and vary across the completion space:

```math
\mathcal C_0^{eval}=\{0,1\}.
```

Thus:

```math
H_D(T)=1.
```

The verifier must compute this by enumeration, not assume it from the formula.

---

## 10. SUN realization language and gauge

The admissible graph adapter is one unordered adapter with three ordinary branch-pair orientation gauges.

Define the unordered adapter:

```math
A_{unord}:
\begin{cases}
C_0\mapsto 0,\ C_1\mapsto 1,\ C_2\mapsto 2,\ C_3\mapsto 3,\ C_4\mapsto 4,\\
\{R_0,L_0\}\mapsto \{5,6\},\\
\{R_1,L_1\}\mapsto \{7,8\},\\
\{R_2,L_2\}\mapsto \{9,10\},\\
B_3\mapsto \{11,12\}.
\end{cases}
```

For machine enumeration, represent the oriented adapter language as:

```math
\mathcal L_A^{(0)}=\{A_\epsilon:\epsilon\in\{0,1\}^3\}.
```

Each bit `epsilon_i` chooses which member of branch pair `B_i` is named `R_i` rather than `L_i`. The boundary pair remains unordered.

The gauge group is:

```math
G_E\cong S_2^3.
```

All eight oriented representatives are prediction-equivalent:

```math
A_\epsilon\equiv_T A_{\epsilon'}\qquad\forall \epsilon,\epsilon'\in\{0,1\}^3.
```

The realization-exhaustion certificate is:

```math
Q_D^R=1
```

iff the verifier confirms that the adapter list is exactly the eight bitstrings in `{0,1}^3`, that each validates the same typed graph-cell interpretation, and that quotienting by `S_2^3` leaves one empirical prediction class.

No other adapter is admissible in Trial 0.

---

## 11. SUN-constrained state space

For every admissible oriented representative `A_epsilon`, define:

```math
S_E^{(SUN)}(A_\epsilon)
=
\{G\in S_{E,M_{completion}}^{(0)}:
3G(G)\land \neg BOrd(G)\}.
```

Since `3G(G)` is visible and forced by the sampler, and `not BOrd` is a nonempty subset of the masked boundary completions:

```math
S_E^{(SUN)}(A_\epsilon)\ne\varnothing.
```

The SUN-constrained target consequence is:

```math
\mathcal C_{SUN}^{eval}(A_\epsilon)
=
\{T(G):G\in S_E^{(SUN)}(A_\epsilon)\}
=
\{1\}.
```

Therefore:

```math
\mathcal C_{SUN}^{eval}=\{1\}.
```

The previously permitted `{0}` consequence is removed. Under this Trial-0 realization, `{0}` contradicts the mapped boundary clause and is not a licensed SUN prediction.

---

## 12. Nonvacuity

The native target set is:

```math
\mathcal C_0^{eval}=\{0,1\}.
```

The SUN-constrained target set is:

```math
\mathcal C_{SUN}^{eval}=\{1\}.
```

Hence:

```math
\mathcal C_{SUN}^{eval}\subsetneq \mathcal C_0^{eval}.
```

Therefore:

```math
\mathsf{ConstraintActive}=1.
```

---

## 13. Frozen truth oracle

The truth oracle is unique:

```math
\Gamma_T(G^\star)=T(G^\star)=1-\operatorname{Cell}_{G^\star}(3,4;11,12).
```

Truth class equivalence is Boolean equality:

```math
0\not\approx_T^{eval}1.
```

Oracle closure holds iff the verifier confirms there is exactly one oracle implementation and that it evaluates the six frozen target-dependency edges in `LAMBDA_ORDER`.

---

## 14. Frozen dependency language

The dependency language is finite edge-set dependency.

An expression may depend only on explicitly declared edge IDs. For Trial 0:

```math
\operatorname{Dep}_{\mathcal L_{dep}^{(0)}}^*(\Gamma_T)=\Lambda_T^\star.
```

The verifier `Verify_dep` accepts iff:

1. every dependency is a valid unordered edge in `E_13`;
2. the dependency set equals the six edges in `Lambda_T_star`;
3. `Lambda_T_star subset M`.

---

## 15. Frozen visible preprocessing channel

The mask operator is:

```math
\widehat\mu_T(\Lambda_T^\star)=M.
```

The preprocessing operator `O` returns exactly:

1. vertex list `V`;
2. edge list outside `M` with Boolean values;
3. edge list inside `M` with value `MASKED`;
4. fixed constants `C_i`, `B_i`, `M`, `Lambda_T_star`, `target_id`, and adapter-language ID.

`O` does not compute `T`, `BOrd`, or any hidden edge value.

---

## 16. Noninterference verifier

`Verify_NI(pi_NI, mu_T_star, O, Lambda_T_star)` accepts iff all of the following are true:

1. `Lambda_T_star subset M`;
2. for every edge in `M`, `O(mu(G))` returns `MASKED`, never its bit value;
3. for every edge outside `M`, `O(mu(G))` returns the original bit value;
4. `O` is deterministic;
5. for any two graphs `G,G'` such that `G` and `G'` agree on `E_13 \ M`,

```math
O(\mu_T^\star(G))=O(\mu_T^\star(G')).
```

Because the graph is finite, condition 5 can be certified symbolically from the code path rather than enumerating all `2^78` graphs.

---

## 17. Discovery-inference language and ledger verifier

The discovery language `L_K^(0)` consists only of deterministic finite computations over:

1. the public preregistration text;
2. visible graph `G_vis`;
3. public code hashes;
4. declared constants;
5. enumerated completion sets.

It does not allow access to:

1. `trial_seed`;
2. `truth_nonce`;
3. sealed full graph edge bits;
4. `boundary_truth`;
5. sealed truth artifact bytes;
6. unmasked target-dependency bits.

`K_seen` must contain:

1. this preregistration document and hash;
2. all public code files and hashes;
3. all reviewed drafts;
4. the candidate-election artifact hash;
5. the generated `G_vis` after instantiation;
6. every inspected completion enumeration and adapter enumeration;
7. every stop-condition or verifier output before commitment.

`Verify_K(pi_K)` accepts iff:

1. the sealed truth artifact is absent from `K_seen` before reveal;
2. `trial_seed`, `truth_nonce`, and `boundary_truth` are absent from `K_seen` before reveal;
3. `G_vis` contains `MASKED` for all edges in `M`;
4. completion enumeration from `G_vis` yields both target classes `{0,1}`;
5. no deterministic computation in `L_K^(0)` maps `K_seen_plus` to a unique target truth.

Thus:

```math
\mathsf{DiscoveryBlind}_T(K_{seen}^+)=1
```

iff `Verify_K` accepts.

---

## 18. Certificate suite

The verifier suite is:

```math
\mathcal V_0=
\{
Verify_oracle,
Verify_dep,
Verify_NI,
Verify_K,
Verify_native_model,
Verify_completion_enum,
Verify_headroom,
Verify_adapter_enum,
Verify_realization_equiv,
Verify_constraint_active,
Verify_serialization,
Verify_reveal
\}.
```

Each verifier consumes only the serialized prereveal state and declared public code. No verifier may inspect the sealed full graph before reveal, except `Verify_reveal`, which is called only after modeling stops.

---

## 19. Commitment mechanics

### 19.1 Canonical serialization

Every public prereveal object is serialized as canonical JSON using:

```text
UTF-8
LF line endings
sorted object keys
no insignificant whitespace
integers in base-10 decimal
Booleans as true/false
masked edge values as the exact string "MASKED"
edge IDs as two-element integer arrays [i,j] with i<j
```

File order in any multi-file commitment bundle is lexicographic by relative path.

### 19.2 Hash algorithm

The hash algorithm is fixed:

```text
SHA-256
```

No later replacement is permitted.

### 19.3 Public preregistration commitment

Before graph instantiation, hash:

```text
trial0_preregistration.json
trial0_verifier_manifest.json
trial0_public_code_manifest.json
```

### 19.4 Sealed truth commitment

At instantiation, create but do not reveal:

```text
sealed_truth.json
```

containing:

```text
trial_seed
truth_nonce
boundary_truth
full edge table of G_star
mask M
visible graph G_vis
sampler version hash
```

Hash `sealed_truth.json` with SHA-256 and publicly record only the digest before analysis begins. The `truth_nonce` prevents brute-force recovery of the hidden 10 masked bits from the digest.

### 19.5 Prereveal prediction commitment

If all licensing gates pass, serialize and hash:

```text
omega_0_plus.json
oracle_closure_certificate.json
discovery_closure_certificate.json
noninterference_certificate.json
native_model_certificate.json
completion_enumeration_certificate.json
realization_enumeration_certificate.json
prediction_object.json
```

At that point:

```math
\boxed{\mathbf{MODELING\ STOPS}.}
```

### 19.6 Reveal verification

After modeling stops, reveal `sealed_truth.json` once. `Verify_reveal` must:

1. recompute SHA-256 of the revealed `sealed_truth.json`;
2. confirm it matches the prereveal public digest;
3. recompute `G_vis` from `G_star` and `M`;
4. confirm it matches the analyzed visible graph;
5. evaluate `Gamma_T(G_star)` exactly once.

No target, adapter, tolerance, equivalence relation, model, or score may change after reveal.

---

## 20. Prediction object, retention, and information gain

If licensed, the prereveal SET-mode prediction is:

```math
\mathcal P_{SUN}^{(0)}=\mathcal C_{SUN}^{eval}=\{1\}.
```

After reveal:

```math
z_{true}=\Gamma_T(G^\star)=T(G^\star).
```

Retention is:

```math
\operatorname{Retain}_T
=
\mathbf 1[z_{true}\in\{1\}].
```

Since

```math
|\mathcal C_0^{eval}|=2,
\qquad
|\mathcal C_{SUN}^{eval}|=1,
```

information gain is:

```math
G_T=1-\frac{1}{2}=\frac12.
```

A licensed positive Trial-0 outcome requires:

```math
\mathsf L_{SUN}=1
\land
\operatorname{Retain}_T=1
\land
G_T>0.
```

A licensed miss is:

```math
\mathsf L_{SUN}=1
\land
\operatorname{Retain}_T=0.
```

It is recorded as a miss. No remapping is permitted.

---

## 21. Stop conditions

The implementation stops without rescue at any of:

```math
\boxed{
\begin{array}{l}
\mathbf{ORACLE\mbox{-}UNCLOSED}\\
\mathbf{DEPENDENCY\mbox{-}UNCLOSED}\\
\mathbf{DISCOVERY\mbox{-}CONTAMINATED}\\
\mathbf{NONINTERFERENCE\mbox{-}UNVERIFIED}\\
\mathbf{NATIVE\mbox{-}UNCLOSED}\\
\mathbf{COMPLETION\mbox{-}UNEXHAUSTED}\\
\mathbf{NO\mbox{-}HEADROOM}\\
\mathbf{NO\mbox{-}REALIZATION}\\
\mathbf{NONUNIQUE}\\
\mathbf{PREREVEAL\mbox{-}INCONSISTENT}\\
\mathbf{NONINFORMATIVE}\\
\mathbf{SERIALIZATION\mbox{-}UNVERIFIED}\\
\mathbf{HASH\mbox{-}MISMATCH}\\
\mathbf{REVEAL\mbox{-}MISMATCH}
\end{array}
}
```

None may be converted into a new target, adapter, or tolerance after the fact.

---

## 22. Literal sampler pseudocode

This pseudocode is specification, not execution. Do not run it until after final commitment.

```python
from secrets import token_bytes, randbits
from hashlib import sha256
from itertools import combinations, product

N = 13
V = tuple(range(N))
EDGES = tuple((i, j) for i in range(N) for j in range(i + 1, N))

CENTERS = (0, 1, 2, 3, 4)
ORDINARY_CELLS = ((0, 1, 5, 6), (1, 2, 7, 8), (2, 3, 9, 10))
BOUNDARY_CELL = (3, 4, 11, 12)

LAMBDA_ORDER = ((3, 11), (4, 11), (3, 12), (4, 12), (3, 4), (11, 12))
LAMBDA_T_STAR = frozenset(LAMBDA_ORDER)
DECOYS = frozenset(((0, 12), (1, 11), (2, 12), (5, 7)))
MASK = frozenset(LAMBDA_T_STAR | DECOYS)

TRUE_BOUNDARY_PATTERN = (1, 1, 1, 1, 0, 0)
ALL_BOUNDARY_PATTERNS = tuple(product((0, 1), repeat=6))
NONORDINARY_PATTERNS = tuple(p for p in ALL_BOUNDARY_PATTERNS if p != TRUE_BOUNDARY_PATTERN)

def norm_edge(i, j):
    assert i != j
    return (i, j) if i < j else (j, i)

def set_edge(G, i, j, value):
    G[norm_edge(i, j)] = int(value)

def get_edge(G, i, j):
    return G[norm_edge(i, j)]

def cell(G, a, b, u, v):
    return int(
        get_edge(G, a, u) == 1 and
        get_edge(G, b, u) == 1 and
        get_edge(G, a, v) == 1 and
        get_edge(G, b, v) == 1 and
        get_edge(G, a, b) == 0 and
        get_edge(G, u, v) == 0
    )

def target_T(G):
    return 1 - cell(G, 3, 4, 11, 12)

def instantiate_once():
    trial_seed = token_bytes(32)
    truth_nonce = token_bytes(32)

    # implementation must derive any PRNG stream from trial_seed using a fixed CSPRNG/KDF;
    # direct randbits below represents the specified fair-bit law, not final code.
    G = {e: randbits(1) for e in EDGES}

    for a, b, u, v in ORDINARY_CELLS:
        set_edge(G, a, u, 1)
        set_edge(G, b, u, 1)
        set_edge(G, a, v, 1)
        set_edge(G, b, v, 1)
        set_edge(G, a, b, 0)
        set_edge(G, u, v, 0)

    boundary_truth = randbits(1)
    if boundary_truth == 0:
        pattern = TRUE_BOUNDARY_PATTERN
    else:
        # final code must choose uniformly from NONORDINARY_PATTERNS
        idx = fixed_uniform_index_from_csprng(0, len(NONORDINARY_PATTERNS) - 1)
        pattern = NONORDINARY_PATTERNS[idx]

    for edge, bit in zip(LAMBDA_ORDER, pattern):
        G[edge] = bit

    G_vis = {e: ("MASKED" if e in MASK else G[e]) for e in EDGES}

    sealed_truth = {
        "trial_seed_hex": trial_seed.hex(),
        "truth_nonce_hex": truth_nonce.hex(),
        "boundary_truth": boundary_truth,
        "full_graph_edges": {f"{i}-{j}": G[(i, j)] for (i, j) in EDGES},
        "masked_edges": [list(e) for e in sorted(MASK)],
        "visible_graph_edges": {f"{i}-{j}": G_vis[(i, j)] for (i, j) in EDGES},
    }
    return sealed_truth
```

The final executable implementation must replace `fixed_uniform_index_from_csprng` with a rejection-sampling function that samples uniformly from `0..62` using the sealed CSPRNG stream. That implementation and its hash must be frozen before any graph is generated.

---

## 23. Final preregistration status

```math
\boxed{\texttt{PREREGISTRATION\_CLOSED\_DRAFT: COMMIT\mbox{-}CANDIDATE, NOT COMMITTED}}
```

```math
\boxed{\textbf{DO NOT GENERATE }G^\star\textbf{ UNTIL A COMMIT/NO-COMMIT GATE PASSES.}}
```

---

# 24. FINAL EXECUTABLE-CLOSURE ADDENDUM — CONTROLLING REVISION

**Status:** FINAL PRECOMMIT SPECIFICATION; NOT YET EXTERNALLY ATTESTED.

This addendum is controlling wherever it conflicts with Sections 7, 17, 18, 19, 22, or 23 above. It closes the final COMMIT / NO-COMMIT blockers without generating `G_star`.

## 24.1 Frozen sampler closure — supersedes Section 7 pseudocode

The authoritative sampler is the exact byte sequence of `trial0_sampler.py`. Its `SAMPLER_ID` is `SUN-TRIAL0-SAMPLER-v1`.

One independently generated 256-bit `trial_seed` determines **all graph randomness** through domain-separated HMAC-SHA256 streams:

```text
graph-bits
boundary-truth
boundary-pattern-index
```

Each stream block is

```text
HMAC-SHA256(
  key = trial_seed,
  msg = b"SUN-TRIAL0-SAMPLER-v1\x00" || domain || b"\x00" || uint64_be(counter)
)
```

with counters beginning at zero, blocks concatenated in counter order, and bits consumed MSB-first. `truth_nonce` is a separate 256-bit OS-CSPRNG value used only as commitment salt and has no causal path into the graph or target.

The 78 initial graph bits are taken from `graph-bits` in lexicographic `EDGES` order. The three ordinary cells are then overwritten exactly as already frozen. `boundary_truth` is the first bit of the `boundary-truth` stream.

If `boundary_truth=0`, assign `[1,1,1,1,0,0]`. If `boundary_truth=1`, choose uniformly among the other 63 patterns using rejection sampling from `boundary-pattern-index`: consume bytes until `x<252`, then return `x mod 63`. Because `252=4*63`, the index is exactly uniform on `0..62`.

`NONORDINARY_PATTERNS` is the lexicographic `itertools.product((0,1), repeat=6)` order with `[1,1,1,1,0,0]` removed. The sealed truth records the selected pattern, index, accepted byte, and number of rejection draws so reveal verification can deterministically reproduce them.

The four decoys retain their original `graph-bits` values. No retry, rescue, filtering, or resampling path exists.

```math
\boxed{\text{one invocation of instantiate_once() = one Trial-0 instance}.}
```

`instantiate_once()` is forbidden until the external commitment receipt in Section 24.4 exists.

## 24.2 Discovery closure — supersedes Section 17 item 5

Trial 0 does **not** attempt to prove that no program in an open-ended class can recover the target. Instead, `Verify_K` uses a finite semantic indistinguishability certificate.

The frozen public inference interface is limited to:

```text
PARSE_CANONICAL_JSON
READ_DECLARED_CONSTANT
READ_VISIBLE_EDGE
ENUMERATE_MASK_COMPLETIONS
EVALUATE_TARGET_ON_HYPOTHETICAL_COMPLETION
ENUMERATE_ADAPTERS
BOOLEAN_NOT / BOOLEAN_AND / BOOLEAN_OR
INTEGER_EQUALITY / SET_EQUALITY / SET_MEMBERSHIP
SHA256_PUBLIC_BYTES
```

No operator may read any sealed byte, seed, nonce, hidden edge, `boundary_truth`, or target truth.

`Verify_K` must exhibit two completions consistent with the **same complete public prereveal state**:

```text
all four decoy masked bits = 0 in both witnesses
T=0 witness target pattern = [1,1,1,1,0,0]
T=1 witness target pattern = [0,0,0,0,0,0]
```

Both witnesses agree with every unmasked visible edge and are compatible with `MASKED` at all ten masked positions, while their target truths differ. Therefore the actual truth is not determined by the public prereveal state. The verifier also enumerates all `2^10=1024` completions and requires the target-class set to be exactly `{0,1}`.

## 24.3 Complete V1-B object freeze — supersedes incomplete Section 18 manifest semantics

The authoritative preregistration object is exactly

```math
\omega_0^+=(D,\mathscr D,K_{seen},T,\mathcal L_\Gamma^{(0)},\mathcal L_{dep}^{(0)},\mathcal L_K^{(0)},\widehat\mu_T,O,\approx_T^{eval},\mathcal U_T,m_T,\mathcal L_M^{(0)},\mathcal L_G^{(0)},\mathcal L_A^{(0)},\Theta_0),
```

with

```math
\Theta_0=(Y_D,W_D,V_D,\mathsf{Elig}_D,\equiv_T^\Gamma,\equiv_T^0,\equiv_T,\cong_T,\mathcal V_0,\mathsf{RetainRule}_T,\Psi_T^{(0)},\ell_T).
```

Every field is bound in `trial0_v1b_manifest.json`; no field may be omitted or `null`. For SET mode only:

```text
Psi_T_0 = "N/A — SET mode"
ell_T     = "N/A — SET mode"
```

The previously implicit semantics are frozen as follows:

- `Y_D(Gamma)=1` iff `Gamma` is the unique Boolean oracle `target_T` and its dependency closure is exactly `LAMBDA_T_STAR`.
- `W_D(M)=1` iff `M=M_completion`.
- `V_D(A|M,G)=1` iff `M=M_completion`, `G=G_3B`, and `A` is one of the eight frozen branch-orientation representatives with unchanged typing and local-cell interpretation.
- `Elig_D(G)=1` iff the instance has vertices `0..12`, all 78 simple-undirected edge slots, the fixed ten-edge mask, the forced three-cell scaffold, and frozen-sampler/no-resampling provenance.
- `equiv_T^Gamma` is extensional equality of oracle outputs over all 1024 compatible completions.
- `equiv_T^0` is equality of native target baselines modulo `approx_T_eval`.
- `equiv_T` is equality of realization target-consequence sets modulo `approx_T_eval`.
- `cong_T` is equality of quotient prediction subsets of `{0,1}`.
- `RetainRule_T(P,z)=1[z in P]`.
- `mathscr_D` is the exact instance snapshot `sealed_truth.json`; prereveal identity is its SHA-256 digest.
- `L_Gamma_0={Gamma_T}`.
- `L_dep_0` is the finite explicit unordered-edge dependency language over `E_13`, with the Trial-0 oracle closure required to equal `LAMBDA_T_STAR`.
- `L_K_0` is the finite public-interface grammar in Section 24.2.
- `mu_hat_T=M`.
- `O` is the deterministic preprocessor already frozen in Section 15.
- `approx_T_eval` is Boolean equality.
- `U_T(A)=|A|` for finite SET-mode target-class sets.
- `m_T=SET`.
- `L_M_0={M_completion}`.
- `L_G_0={G_3B}`, the singleton SUN subgrammar consisting of exactly three ordinary local cells followed by the distinguished nonordinary boundary clause.
- `L_A_0={A_epsilon: epsilon in {0,1}^3}`.

`Verify_V1B_manifest` mechanically requires all 16 `omega_0_plus` fields and all 12 `Theta_0` fields to be present and bound.

## 24.4 Exact commitment root and timestamp — supersedes Section 19

Canonical JSON uses UTF-8, LF endings, sorted keys, no insignificant whitespace, decimal integers, JSON Booleans, exact string `MASKED`, normalized edge arrays `[i,j]`, and one trailing LF. Hash algorithm is SHA-256.

The precommit bundle is represented by canonical `bundle_manifest.json`:

```json
{"format":"SUN-TRIAL0-BUNDLE-v1","files":[{"bytes":123,"path":"...","sha256":"..."}]}
```

The `files` array is sorted lexicographically by relative POSIX path and contains every frozen precommit artifact. The single root commitment is:

```text
BUNDLE_ROOT_SHA256 = SHA256(canonical bytes of bundle_manifest.json)
```

The external timestamp mechanism is **OpenTimestamps over Bitcoin**. Execute:

```text
ots stamp -a https://alice.btc.calendar.opentimestamps.org \
          -a https://bob.btc.calendar.opentimestamps.org \
          bundle_manifest.json
```

Preserve the returned `bundle_manifest.json.ots` byte-for-byte. The existence of that receipt marks the transition to `COMMITTED_AWAITING_BITCOIN_UPGRADE`; only then may `instantiate_once()` execute.

After anchoring is available:

```text
ots upgrade bundle_manifest.json.ots
ots verify bundle_manifest.json.ots
```

The proof must verify against the exact bundle-manifest digest and a valid Bitcoin attestation. If no `.ots` receipt exists, commitment has not occurred.

## 24.5 Strengthened reveal verification — supersedes Section 19.6

`Verify_reveal` must:

1. match the revealed `sealed_truth.json` SHA-256 to the prereveal digest;
2. validate sampler ID and seed/nonce lengths;
3. regenerate the complete graph from revealed `trial_seed` using the frozen sampler;
4. require exact equality between regenerated graph and revealed `G_star` on all 78 edges;
5. recompute `G_vis` and require equality with both the sealed and actually analyzed visible graph;
6. reproduce the rejection-sampled nonordinary pattern, index, accepted byte, and draw count;
7. require `boundary_truth = T(G_star)` exactly;
8. evaluate `Gamma_T(G_star)` exactly once.

Any failure is terminal `REVEAL-MISMATCH`.

## 24.6 Final machine precommit gate

The machine report must contain:

```text
SAMPLER_CLOSED
DISCOVERY_LANGUAGE_CLOSED
V1B_MANIFEST_COMPLETE
COMMITMENT_MECHANISM_CLOSED
NO_GSTAR_EXISTS
```

and

```math
\boxed{\texttt{COMMIT_AUTHORIZED}=1\iff
\texttt{SAMPLER_CLOSED}\land
\texttt{DISCOVERY_LANGUAGE_CLOSED}\land
\texttt{V1B_MANIFEST_COMPLETE}\land
\texttt{COMMITMENT_MECHANISM_CLOSED}\land
\texttt{NO_GSTAR_EXISTS}.}
```

`NO_GSTAR_EXISTS=1` requires absence of runtime truth artifacts, generated seed records, generated visible graphs, sealed-truth digests, and Trial-0 instance markers.

A passing report authorizes commitment but does not itself constitute external commitment. The state changes to `COMMITTED` only when `bundle_manifest.json.ots` exists for the exact frozen manifest.

```math
\boxed{\texttt{FINAL_PRECOMMIT_SPECIFICATION: COMMIT-CANDIDATE, NOT YET ATTESTED}}
```

```math
\boxed{\textbf{DO NOT GENERATE }G^\star\textbf{ UNTIL EXTERNAL COMMITMENT ATTESTATION EXISTS.}}
```
