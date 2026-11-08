# Portable ARIADNE source and catalog verification

This additive checker works from a relocated repository. It uses the existing canonical builder and preserves every archived input. It performs fresh checks; it does not replay the historical Windows SuperJev contract, invoke Jev, run a browser, or certify a historical reconstruction.

Use Python with NumPy2.2.5 and SciPy1.16.3. These were inspected on the execution host. Install the direct dependencies in a separate environment:

```powershell
python -m venv .venv-ariadne
./.venv-ariadne/Scripts/python.exe -m pip install -r work/github-delivery-2026-11-07/portable/requirements-portable.txt
./.venv-ariadne/Scripts/python.exe -m pip check
```

Replace python with the appropriate installed Python command if it is not on PATH. On platforms using bin/python instead of Scripts/python.exe, select that interpreter. A cross-platform source checker does not establish cross-platform support for the separate Windows worker lifecycle.

From the repository root, run the implementation in its current source location:

```powershell
./.venv-ariadne/Scripts/python.exe -B work/github-delivery-2026-11-07/portable/verify_abracadabra.py --repo-root . --output portable-receipts/check-001.json
```

The publication process may copy this unchanged single-file implementation to scripts/verify_abracadabra.py. It locates the repository from its own location or accepts --repo-root explicitly:

```powershell
./.venv-ariadne/Scripts/python.exe -B scripts/verify_abracadabra.py --output portable-receipts/check-002.json
```

Choose a new JSON output filename. Existing files are never overwritten. Output under preserved source, test, archive and final-day evidence areas is rejected. A failure exits1 and prints a structured error; it does not modify an old receipt. A pass exits0 and writes then reads back the new receipt. An otherwise conserved catalog with unavailable evidence writes a PARTIAL receipt and exits2; its missing/external references remain NOT_VERIFIED.

## What is checked

- Every canonical-v2 payload digest and byte count, including the original source bytes.
- The unchanged canonical builder, binding manifest and three imported implementations.
- A fresh15×36×20 derivation, exact dtype/value equality for vector, mask and normalized arrays, scripts, columns, cell_ids and value_state, and the entire logical sidecar.
- One explicit adaptation: the archived source.path locator is replaced in an in-memory comparison copy by the current checkout path. The manifest and archived sidecar must first agree on the old locator. Exact source bytes and every other logical field must remain equal. vectors.json is never rewritten.
- All106 original requirement dictionaries, their ordering and statuses, current assessment fields and safe existing repository-relative evidence references.
- Two exact legacy catalog locators containing an internal parent segment have explicit adapters to their canonical repository paths. Both target hashes must match uniquely identified original census evidence. The original locator strings and per-requirement links remain in the new receipt; generic escaping paths remain rejected. External locators are never read or fetched, and unavailable evidence is reported separately from catalog conservation.
- Input hashes at read time and again before a successful result, plus the current interpreter and dependency versions.

Original contracts and receipts remain classified HISTORICAL_WINDOWS_SCOPE. The new receipt explicitly records that no original proof was reexecuted or rewritten. Geometry remains unavailable in this strict profile. Broader PCA, graphical extraction, browser, worker, plugin and model execution have separate requirements; scikit-learn was not installed in the inspected host and is not claimed by this dependency profile.

## Focused acceptance tests

```powershell
./.venv-ariadne/Scripts/python.exe -B -m unittest discover -s work/github-delivery-2026-11-07/portable -p test_portable_verifier.py -v
```

The ten tests relocate the actual canonical source and artifacts into a temporary checkout. They preserve all106 original rows, use explicitly synthetic engineering links to avoid copying unrelated private research, and test altered payloads, rehashed numerical values, raw sidecars, source locators, escaping references, changed original statuses, protected output areas and the intended scripts/ copy location. Additional actual-catalog cases test the two legacy locators against their original byte hashes and an unavailable external locator. These are engineering controls, not independent historical evidence.

Publishing this helper requires the relative research trees and canonical inputs listed by its binding manifest. It does not reconstruct an omitted source, fetch a model or grant publication rights over third-party material.
