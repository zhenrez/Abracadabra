# Independent finite reading-relation review

The current compiled helper passed **87 datasets and 348 independent operation comparisons**, with structured exit **0** and no valid-input mathematical discrepancy. Tested source and compiled hashes appear in `relation-review.json`; both remained stable throughout the actual Node execution.

Independent formulations were used: pairwise row comparisons for functional dependencies; exhaustive enumeration followed by strict-set inclusion for all minimal refinements; Python selection with explicit unknown handling; and SQLite `DISTINCT` projections followed by a `NATURAL JOIN` using binary text collation. The oracle does not import helper implementations.

The admitted two-row Molin example has equal coarse inputs and different required pausal outputs. Its coarse functional dependency is contradicted. Several singleton refinements fit this small complete sample; no such field is thereby a universal law or a historical cause. Keeping only projections `[lexeme,input]` and `[input,output]` yields **four** distinct rejoined tuples from **two** original tuples, with **two** excess cross-pairs. Those cross-pairs are sample-relative join artifacts, not newly established historical forms.

The controls preserve repeated occurrence IDs while deduplicating relation tuples. Explicit nulls and missing fields retain unresolved candidates; empty strings remain known values. Greek `χ` and Latin `x` are distinct. Own keys named `__proto__`, `constructor` and `toString` do not fabricate inherited values or collapse identities.

Code inspection identified inconsistent runtime handling of malformed query-condition inputs. Root added explicit object-map validation. The final actual run confirms that null, arrays (empty and nonempty), and a string all throw rather than become query-field maps. No pre-repair execution receipt was captured by this reviewer, so the earlier observation is classified as code inspection, not a retrospectively invented failing run.

Actual Supermemory retrieval earlier in this bounded review provided continuity; it did not certify source truth. Actual local Jev receipt 62 directed the substantive source operation. No fresh Jev inference was performed by the reviewer. Only files in this assigned review directory were changed for this helper check; no source, compiled module, canonical model or interface was edited.

Reproduce with the runtime Python on `check_relations.py`. All admitted rows and actual compiled-module returns are retained in `relation-cases.json` and `relation-actual.json`. Original bowl readings, phonetic reconstruction, timing, and the identity of a historical conditioning operation remain outside this finite software validation.
