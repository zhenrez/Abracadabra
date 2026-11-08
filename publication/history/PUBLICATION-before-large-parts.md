# Publication and reproduction boundaries

This handoff preserves working code, standalone interfaces, canonical evidence, source-qualified research outputs and verification records. The public inventory accounts for observed omissions without exposing exact private archive paths. The detailed private inventory remains in the original local workspace.

## Start without installation

Open [the ARIADNE dashboard](work/final-day-2026-11-07/dashboard/SUN_ARIADNE_Workbench.html) or [the SUNNY guide](web/delivery-2026-11-07/system-guide.html) from a downloaded checkout. Both are existing deliverables, not newly inferred historical correspondences. Archived reports may contain original absolute Windows locators; preserve those as provenance and use these relative entrypoints.

## Portable source and numerical validation

Install the two direct analysis dependencies in `requirements-ariadne.txt`. Run `python scripts/verify_abracadabra.py --output verification/portable-receipt.json`. A fresh invocation validates canonical payload hashes, reimports the exact user-supplied source and rederives the numeric arrays with the unchanged builder. The only declared relocation is the `source.path` locator. All other logical sidecar fields, raw cells and numerical arrays must agree. The archived vectors and original receipts remain unchanged.

The verifier also conserves all 106 original requirement rows and checks repository-local engineering evidence references. Two exact legacy parent-directory locators are explicitly adapted to canonical repository paths only when their original-census hashes agree; the original strings remain in the ledger and new receipt. Other escaping paths are rejected. Unretrieved external evidence is reported as not verified. This does not rerun original-host plugin contracts, certify completion of the research mission, or turn missing historical evidence into a passing result.

The original runtime and full test record remain at [FINAL_CHECKS.md](work/final-day-2026-11-07/FINAL_CHECKS.md). Their exact input and dependency conditions matter. Selected broader tests require held source material or live services. A fresh local check must report missing prerequisites instead of substituting fixtures or inheriting the original pass.

## Optional native and browser checks

Install `requirements-ariadne-native.txt` in the analysis environment for the frozen Sefer and common-contract checks, then run:

```powershell
python -B -m unittest discover -s work/unit001 -p test_g0.py -v
python -B -m unittest discover -s work/unit001 -p test_g1.py -v
python -B -m unittest discover -s work/unit001/frozen/sefer -p test_harmonic_verifier.py -v
```

For the separately pinned browser smoke check, run these commands from `verification-tools`:

```powershell
npm ci --ignore-scripts
npx playwright install chromium
node check-workbenches.mjs ../verification/browser-receipt.json
```

This checks three page startups at desktop and phone sizes, interactive-control presence and JavaScript errors. It is narrower than the preserved original interaction suites. Use a new output filename. The separate package leaves the original project dependency bindings unchanged.

## Retained sources and rights

Private account-wide databases, mixed account backup containers, installed model weights, dependency caches and earlier private-target transfer parts are retained locally. Unreviewed third-party books, downloaded pages and images are separately held. Source locators and derived observations can remain represented without publishing entire source containers. An absent public file is not an absent historical source.

No blanket project licence is asserted for imported evidence. Preserve upstream notices and source-specific conditions. The absence of a new licence does not grant rights to third-party materials. The publication inventory is an accounting artifact, not an authenticity or legal certification.

## Current and historical decisions

The initial Abracadabra README and the preceding SUNNY README are preserved under `publication/history/`. The latter describes an older private SUNNY publication plan and its large-source restorer. That plan's private parts are not supplied by this public handoff. Current public scope and fresh verification are recorded separately under `publication/`.

The original matrix and frozen SUN/Sefer sources are preserved byte for byte. No Western, Chinese or Indian output is used to force a Sefer assignment. Mathematical possibility, model-internal uniqueness and historical support remain separate.
