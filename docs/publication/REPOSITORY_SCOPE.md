# SUNNY repository publication scope

The user authorized publication of SUNNY's current work and recoverable project history to `https://github.com/zhenrez/SUNNY` at **23:30 America/Phoenix on November7**, equivalent to **06:30 UTC on November8**. This reviewer performed no Git initialization, staging, upload or remote mutation. This document defines the reviewed package scope; it does not claim a push has occurred or been scheduled successfully.

An allowed PowerShell metadata operation inventoried nine explicit project directories: **10,195 files and 10,095,162,465 bytes**, approximately **9.40 GiB**. Twelve named root files were separately checked. This is a path/size/time manifest, not a content-hash or atomic snapshot, and it does not include uninspected runtime/dependency roots. The machine-readable manifest is `state/publication/inventory-review.json`.

| Directory | Files | Bytes | Treatment |
|---|---:|---:|---|
| data | 5,215 | 8,255,670,683 | Preserve raw research, provenance, source occurrences and database history; package large objects explicitly. |
| deliverables | 36 | 534,681,143 | Preserve historical packages or account for byte-identical packaged storage. |
| dist | 13 | 152,706 | Include compiled handoff assets, or provide and verify an exact rebuild. |
| docs | 744 | 129,266,474 | Include mandates, plans, source/math evidence, checks, limitations and publication instructions. |
| public | 5 | 110,792 | Include application assets. |
| scripts | 112 | 1,340,708 | Include builders, execution, validation and lifecycle tooling. |
| src | 13 | 148,890 | Include executable TypeScript and discovered-law representations. |
| state | 4,012 | 1,104,390,712 | Include canonical modules, exact Jev receipts, checkpoints and review results; separate operational state where appropriate. |
| web | 45 | 69,400,357 | Include the offline workbench, guide, local assets and exact source data. |

Required root files are `.gitignore`, `README.md`, `CONTINUE.md`, `AGENTS.md`, `PLAN.md`, `package.json`, `package-lock.json`, `requirements.txt`, `tsconfig.json`, and the three Start/Stop/Status command files. Their metadata is recorded separately rather than silently included in the nine-directory totals.

## Large-object packaging is required

Six inventoried files exceed 90MiB:

| Path | Bytes | Required handling |
|---|---:|---|
| data/sunny.sqlite | 2,418,573,312 | Byte-preserving large-object packaging; preserve complete database contents and restoration instructions. |
| data/backups/current-reconstruction-before-20261031T191736387534Z.sqlite | 2,404,511,744 | Preserve historical database bytes and distinct identity. |
| data/backups/gaps-before-20261031T012033098903Z.sqlite | 2,401,320,960 | Preserve historical database bytes and distinct identity. |
| deliverables/SUNNY_Mathematical_Reconstruction_2026-10-31_3d314e8b567a.zip | 236,873,130 | Large-object or byte-preserving chunked storage. |
| deliverables/SUNNY_Current_Model_2026-10-31.zip | 214,173,138 | Large-object or byte-preserving chunked storage. |
| data/raw/archive/SUN_Universal_Archive/Original_Export_Segments/conversations-006.json | 100,675,224 | About96MiB: above the review threshold, below the regular100MiBlimit. Preserve exact source bytes. |

Five therefore exceed GitHub's regular 100MiB file limit. Git LFS has plan-dependent per-file limits: 2GB on Free/Pro, 4GB on Team and 5GB on Enterprise Cloud. The three approximately 2.4GB databases exceed the Free/Pro limit; the repository owner's plan and large-object transport were not verified by this reviewer. These limits were checked against [GitHub's file-upload documentation](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository) and [Git LFS documentation](https://docs.github.com/en/enterprise-cloud%40latest/repositories/working-with-files/managing-large-files/about-git-large-file-storage).

A suitable publication representation is an original-path manifest plus byte-preserving archive/chunks below the chosen transport limit, including each original content hash, archive/chunk hashes, byte sizes, ordered reassembly and verified restoration. Original workspace files must remain untouched. If a database changes during packaging, use a consistent source-preserving snapshot rather than mixing a main database and unrelated journal state. No SQLite auxiliary WAL/SHM paths appeared in this metadata snapshot; that does not establish future inactivity or transaction consistency.

The current `.gitignore` excludes `data/` and `dist/`. A blind normal add would omit essential source/history and compiled assets. The publication checkout needs explicit, reviewed inclusion rules; this reviewer did not change the original ignore file.

## Runtime and dependency accounting

Top-level `runtime/`, `.venv/`, `node_modules/`, `.ruff_cache/` and `work/` were not recursively inventoried. They must not be counted as uploaded or credential-cleared. Reproducible environments, downloaded model weights and normal caches should be excluded from the publication payload, with a dependency manifest and bootstrap instructions preserving their roles.

This exclusion needs a functional replacement. `scripts/start-jev.ps1` requires `runtime/agent-jev`, `runtime/.venv` and its model configuration. The accepted model checksum is `8166e46dc6019ae13f0d8fc97d603cdbcc2d20eb1882c7350c8deb9fc6bae215`. Preserve the actual source origin/revision, dependency versions and reproducible download/verification instructions; none should be guessed. The root `requirements.txt` currently names only pypdf and openpyxl, whereas current scientific checks also use SymPy, Pillow, pdfplumber and pypdfium2. The full fresh-clone runtime is consequently not established by that requirements file alone. The offline web views remain useful without model inference.

Raw received archives may themselves contain historical cache-looking entries. Do not edit received bytes or broadly remove these from source archives merely because similarly named runtime caches are excluded. Any publication-copy omission must preserve the original occurrence accounting and restoration boundary.

## Scope and content-review limits

Filename matches identify 182 files mentioning AYLI, 611 mentioning ARIADNE, 22 mentioning SUN_SOL, 44 mentioning SATURN and one mentioning COSMIC. These match sets are nonexclusive and do not determine substantive content. Many are recovered research inputs within the authorized SUNNY history. Preserve their source-branch identities; do not silently merge their mandates into SUNNY or discard them as unrelated on filename alone. No K2SO, HDTK or Wausaukee filename matches appeared in this explicit directory inventory; this is not an account-wide absence claim.

CompTextGuard rejected the proposed bounded assignment-pattern scan, a broad metadata command, and sensitive filename-pattern classification. Those rejected operations did not execute. The narrower, explicit-directory PowerShell metadata operation succeeded without reading project file contents. No account values were printed, and no hook was disabled or bypassed. **Content and configuration clearance remains unperformed**; the manifest is not evidence that the project contains no credentials. Account configuration and operational stores are not authorized merely by their presence near research files.

Actual Supermemory retrieval succeeded for continuity. Inventory facts and GitHub limits were independently checked. Root reported connector access to the designated private repository but a native Git authentication failure; this reviewer performed no remote verification or write. An authenticated upload route, large-object packaging, runtime reproducibility and the remaining content-review boundary are concrete publication dependencies. A scheduler or local manifest alone must not be reported as a completed push.
