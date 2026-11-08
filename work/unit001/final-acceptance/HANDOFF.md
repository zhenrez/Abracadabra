# Final G0/G1 acceptance and engineering handoff

## A. Verified baseline

The authoritative workspace is `C:\Users\Brend\Documents\ChatGPT\SUN`. No Git metadata was established. Branch, HEAD and commit SHA are unavailable; no new repository, branch, commit, PR, push or merge was created. No GitHub operation was needed for this local unit.

The original comparison table was recovered from this chat's actual local user-message event, not reconstructed from a summary. `frozen/source/matrix-message.txt` preserves the decoded message text as UTF-8; `matrix-event.jsonl` separately preserves the serialized source event. The UTF-8 table hash is `d76bee36607f67a72aad404dc98682f0ec647a9cbb0fb3f89df30230f58ca24c`. This is not a claim about bytes of an unknown external document.

The original `harmonic_verifier.py`, six-test suite, demonstration JSON and explanatory document are preserved under `frozen/sefer/`. Their hashes remain equal to the pre-migration manifest. Existing raw/derived datasets, original research context and SUN TypeScript sources also pass their preserved hash comparisons.

The two named work-state logs were clarified by the user to be duplicate copies of this same conversation. They are not independent acceptance inputs. Their original separate byte streams are not claimed as retrieved; the redundant retrieval requirement is removed. Supplied archive/review documents remain independently preserved and hashed. No missing log was reconstructed, and this dependency will not be reopened.

## B. Implemented changes and demonstrated corrections

The lossless matrix-specific importer remains in `evidence.py`. The common contracts are in `contracts.py`; the domain-independent provenance kernel is in `kernel.py`; the canonical-letter Sefer adapter is in `sefer.py`. The kernel's source, observation, claim, derivation, operator specification and experiment-receipt records are distinct. Domain records provide specialized evidence without making the matrix's witness schema a universal ontology.

The final acceptance audit demonstrated two previously untested G1 defects: duplicate source witness IDs could be reused within an encoding, and source claim references could be dropped. Both failing cases were reproduced before correction. `EncodedModel` now retains its immutable G0 evidence graph. `validate_native()` validates that graph and checks each assignment's unique witness/cell identities, claim references, exact IPA, phonetic type and profile identity against its actual witness. Altered or unbound assignments fail closed. The frozen legacy engine and its JSON output contract were not changed.

`test_final_acceptance.py` adds six focused checks: duplicate source identity, removed claim binding, readdressed source coordinates, environment-variable lock bypass, 231/462 possibility-space distinctions, and preservation of source-specific Hebrew alternatives. Existing tests remain unchanged. The two older verification runners now derive test totals from actual suite output instead of stale constants.

`final_acceptance.py` executes and records the full bounded verification. Its first full-demo comparison accidentally used carrier order where the original demonstration used category-group order. This audit-runner error was corrected to use the exact original input fixture; no model behavior or expected output was modified to obtain compatibility.

## C. G0 evidence conservation

| Requirement | Observed evidence | Result |
|---|---|---|
| Original source retained | Exact table and serialized user-message event; unchanged hash | PASS |
| Original grid structure | 46 rows, 37 fields each, 15 script groups | PASS |
| Address conservation | 36 positions per group; 540 total | PASS |
| Populated/empty distinction | 381 populated glyph positions; 159 explicit empty positions | PASS |
| All supplied field types | Glyph, literal IPA and English approximation preserved with source spans | PASS |
| Exact character representation | Unicode scalar sequences and UTF-8 source spans verified | PASS |
| Proxy distinction | Proto-Sinaitic/Paleo-Hebrew proxy classification retained | PASS |
| Unknown versus silence | Four Etruscan question marks remain UNKNOWN_VALUE | PASS |
| Heterogeneous sign values | Old Persian vowel signs and syllabic values remain different types | PASS |
| Letter names | English values remain LETTER_NAME | PASS |
| Ambiguous readings | Square Hebrew/Syriac literal alternatives retained | PASS |
| Local ordinals | Source positions do not instantiate cross-script alignments | PASS |
| Provenance | Source/observation/claim/derivation/domain records remain independently addressable | PASS |
| Genealogy | External, evidence-referenced relations; no ancestry inferred from ordinal | PASS |
| Dates | Unresolved bounds supported; no inscription dates invented by importer | PASS |
| Referential integrity | Invalid references and duplicate occupancy rejected | PASS |
| Nested state | Defensive immutable containers, mutation tests | PASS |
| Serialization | Deterministic G0/kernel round trips; source digest unchanged | PASS |
| Cross-domain representation | Synthetic T02–T12 retained; four source-identified controls added | PASS |
| Cross-orientation isolation | Empty registry; registration, evaluation, serialized and environment bypasses denied | PASS |

All original twenty G0 tests run in the current suite. `acceptance-receipt.json` includes the twenty actual conservation-invariant results. `current_G0_G1.log` lists every executed test name, not merely an asserted success flag.

The source-identified controls are an edition-specific Sefer/Gra comparison, Ruth 3:3 written/read alternatives, a scholarly Lachish uncertainty case, and two 72-name procedures preserved at their actual modern annotation layer. These are representability controls. Their detailed source metadata and limitations remain in `closeout/source-manifest.json` and `historical-controls.json`. Synthetic controls remain explicitly synthetic.

The residual accounting is fully reconciled: 136 compatible + 6 unpredicted + 234 unmapped + 4 unknown + 1 unresolved = 381 populated positions. Blank padding is not a phonological observation. Unknown pronunciation is not silence. A residual mismatch is not automatically a historical mutation.

## D. G1 acceptance and legacy compatibility

Canonical IDs use letter identities; IPA aliases remain projections. Sefer's three mothers, seven doubles and twelve simples are a stipulated letter classification. Six-switch Begadkephat and seven-double Sefer expansions remain different constructions.

| Example | Input or condition | Expected | Observed |
|---|---|---|---|
| A — Complete | All 22 configured letter assignments | Valid occupancy and partition | PASS; VALID |
| B — Missing Mem | Complete fixture with m removed | 21 occupied, unique model-specific restoration; legacy Invalid/m/null | PASS; INCOMPLETE and UNIQUE_UNDER_MODEL; legacy fields unchanged |
| C — Ambiguous sibilant | Original fixture with s eligible for two classifications | Both distinguishable assignments retained | PASS; two solutions, MULTIPLE_DISTINGUISHABLE |
| D — Resh alternative | r:1 | Tagged alternate, no invented fricative IPA | PASS; realization null |
| E — Duplicate | Two competing assignments for one exclusive slot | Contradiction with conflict record | PASS; CONTRADICTION |
| F — Overflow | 30 inputs in expanded mode | Reject excess active states | PASS; CONTRADICTION |
| G — Empty/unrelated | Empty native input or no selected assignment profile | Not evaluated, not a success | PASS; NOT_EVALUATED |
| H — Exhaustion | b constrained exclusively to Mem | No feasible assignment; premises retained | PASS; NO_FEASIBLE_SOLUTION |
| I — Multiple | b/g candidate input | Retain each distinguishable solution | PASS; two solutions |
| J — Serialization | Repeated identical candidate input | Identical canonical JSON and digest | PASS |

The original six-test suite executes from the frozen directory. The entire newly generated original demonstration JSON equals its saved reference. All three previously required demonstration checks pass. Exact original input, expected JSON, actual legacy-adapter JSON and formatting-difference field are stored in the receipt. Native typed receipts are intentionally richer than legacy JSON; legacy compatibility uses the untouched oracle through its explicit adapter.

Combinatorial counts are independently checked: 22 base letters, 29 stipulated states, 231 unordered distinct-letter possibilities, 462 ordered distinct-letter possibilities and 484 ordered pairs when self-pairs are included. Pair graphs are labeled possibility spaces, not attested historical relationships.

Each reconstruction retains structural validity, model preference, identifiability and historical support separately. Missing Mem is unique under the configured model, not historically DETERMINED. Historical support remains NOT_VERIFIED. `describe()` returns NOT_EVALUATED with no bit count because G6 is locked.

## E. Verification commands and outcomes

Primary command: `python -B work/unit001/final_acceptance.py`.

| Check | Outcome |
|---|---|
| Current G0/G1 and historical-control suite | 53 tests, exit 0 |
| Frozen original Sefer suite | 6 tests, exit 0 |
| Preserved earlier linguistic pipeline | 40 tests, exit 0 |
| Complete original demonstration comparison | Equal |
| Three original demonstration checks | PASS |
| Source, frozen oracle, prior prototype and SUN source hashes | All matched |
| Python syntax | AST parsing passed for current Unit001 modules |
| Dependency consistency | pip check, exit 0 |
| G7 denial | Registration, evaluation, serialized unlock denied; environment bypass test passed |

Suite counts describe separate executions; original tests overlap conceptually with compatibility tests and are not independent scientific confirmations. No numerical compression fitting, Western/Chinese/Indian native run, historical transmission inference or cross-orientation reconstruction was executed.

No separate static type checker or linter was executed. The unchanged TypeScript application was not rebuilt for these isolated Python adapter changes. No new dependencies were installed. No independent review or new manual Jev architectural inference is claimed. Automatic SuperJev observations do not certify completion. Existing Riqor evidence-engineering guidance was applied to red/green tests, source-bound corrections and fresh checks.

## F. Gate ledger and scope

| Gate | Verdict | Scope |
|---|---|---|
| G0 | PASSED | Bounded source-conserving architecture and evidence representability |
| G1 | PASSED | Frozen Sefer compatibility, actual native assignments and typed receipts |
| G2 | LOCKED | No Western native-model implementation or integration performed |
| G3 | LOCKED | No Chinese native-model implementation performed |
| G4 | LOCKED | No Indian native-model implementation performed |
| G5 | LOCKED | No independent phonetic/numeric control engine implemented |
| G6 | LOCKED | No historical model-preference certification or invented MDL costs |
| G7 | LOCKED | No adapters registered; no cross-orientation reconstruction |

Greek/Latin linguistic vowel mapping already completed earlier in this chat is separate from the later Western musical orientation. Older SUN musical code is preserved. Neither scope distinction authorizes new downstream work in this unit.

## G. Remaining decision-relevant uncertainty

- Historical controls are tied to retrieved editions/publications, not independently collated earliest surviving manuscripts.
- Lachish's direct PDF download returned HTML; the separately attributed inspected excerpt is not an original artifact photograph or PDF capture.
- The two 72-name descriptions are documented at the modern annotation layer; no stronger medieval attribution or W72 alignment is inferred.
- Phoneme-to-frequency identities, historical roots, genealogy and universal cross-tradition equivalence remain scientifically unverified.
- The candidate search has an explicit resource bound and raises rather than silently selecting a unique answer when it is exceeded.

These limits remain in the evidence records. They do not reopen the resolved duplicate-log dependency or require historical hypothesis proof for architectural G0/G1 acceptance.

## H. Final engineering handoff

Final-audit changes: `contracts.py`, `sefer.py`, `test_final_acceptance.py`, `verify_closeout.py`, `verify_reconciliation.py`, `final_acceptance.py`, `FINAL_ACCEPTANCE_PLAN.md` and the new final-acceptance reports/logs. Existing historical source fixtures, synthetic controls, frozen baseline and SUN core remain preserved. Earlier receipts describe their earlier states; this receipt supersedes them for the hardened implementation.

The new optional EncodedModel evidence_graph field preserves construction compatibility, but an old manually constructed encoding without source evidence is now deliberately rejected by native validation. This is a documented fail-closed provenance correction. Legacy Sefer input/output remains unchanged.

ENGINEERING UNIT 001 VERIFIED FOR THE BOUNDED G0/G1 ACCEPTANCE SCOPE. NEXT ELIGIBLE UNIT: G2 — WESTERN NATIVE MODEL. NO G2 IMPLEMENTATION PERFORMED. G2–G7 REMAIN LOCKED. WORK STOPS AT THIS CHECKPOINT.
