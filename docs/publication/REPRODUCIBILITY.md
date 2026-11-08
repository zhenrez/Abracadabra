# Reproducing the published SUNNY workspace

The Git repository carries source, research records and evidence manifests. A fresh clone is not the original Python environment, model cache or complete large-file archive. Restore the required large research inputs from the publication's release/archive manifest **before** running data-backed checks. Missing input bytes must remain a failed or unavailable check, not a silent skipped source.

## Research dependencies

From the repository root in PowerShell:

```powershell
./scripts/bootstrap-research.ps1
./.venv-research/Scripts/python.exe -X utf8 -B scripts/verify_reconstruction.py
```

The bootstrap creates an isolated `.venv-research` without inherited system packages, installs `requirements-research.txt`, runs `pip check`, and verifies six direct package versions and imports. It performs small memory-only checks for Pillow, SymPy, openpyxl and pypdf when available. PDF extraction packages receive import/native-library checks; no unseen manuscript page is claimed inspected. This is a pinned direct-dependency list, not a complete transitive lockfile or a whole-project acceptance run.

To inspect an existing environment without installing, cloning or downloading:

```powershell
./scripts/bootstrap-research.ps1 -VerifyOnly -Python ./runtime/.venv/Scripts/python.exe -CheckJevSource
```

`-VerifyOnly` writes a result report and returns nonzero if a required package is missing, differs from its pin, or fails import. Its default Python command is `python`; pass the intended interpreter explicitly. It never loads model weights or runs a live Jev inference.

| Dependency | Pin | Initial runtime/global observation |
| --- | --- | --- |
| Pillow | 11.3.0 | Installed |
| SymPy | 1.14.0 | Installed |
| pdfplumber | 0.11.7 | Installed |
| pypdfium2 | 4.30.0 | Installed |
| openpyxl | 3.1.5 | Declared in existing `requirements.txt`; missing in both inspected Python environments |
| pypdf | 6.1.1 | Declared in existing `requirements.txt`; missing in both inspected Python environments |

The initially inspected interpreters were Python 3.13.0. The existing runtime environment inherits system packages and is not a portable dependency bundle. The original `bootstrap-verification.json` preserves that initial four-of-six result and remains unchanged. The manifest's observation fields likewise describe that initial inspection, before the separate clean bootstrap below.

### Actual clean-environment check

The authorized bootstrap was subsequently run in a new, isolated `.venv-research` using:

```powershell
./scripts/bootstrap-research.ps1 -CheckJevSource -ReportPath docs/publication/bootstrap-clean-environment.json
```

It exited **0**. All six pinned distributions imported and passed their stated memory/import checks, `pip check` reported **“No broken requirements found,”** and all six public Jev source-file hashes plus the pinned Git commit passed. The environment has `include-system-site-packages = false`; user-site packages are disabled. The global Python and existing Jev environment were not changed. Only the six direct requirements and their necessary transitive dependencies were installed; no model weights or Jev runtime packages were downloaded.

The existing independent phase oracle was then executed with `.venv-research/Scripts/python.exe`. It checked **10,296 probe pairs**, reproduced **4,608 sufficient / 5,688 insufficient pairs**, and found **zero criterion mismatches**. Its output directory was explicitly redirected to `docs/publication/clean-environment-oracle`, preserving the earlier review. Execution metadata is in `bootstrap-clean-oracle.json`; dependency/source checks are in `bootstrap-clean-environment.json`. The core model and delivery data hashes stayed unchanged.

These are actual clean-environment dependency checks and one independent calculation, **not a new-environment full-suite pass**, model inference, archive-restoration certificate or scientific-completion claim. Keep `.venv-research` out of the source publication; publish the requirements and evidence reports.

Node/TypeScript work uses the checked-in `package.json` and lockfile. Install those dependencies separately with the repository's normal package-manager workflow. Research bootstrap does not install browser drivers, optional plugins, CUDA or PyTorch.

## Pinned Jev source and model

`bootstrap-manifest.json` records the public [AgentJev source repository](https://github.com/malevrigns/agent-jev), independently checked local commit **`fbe1bc97c76873d08f0820adf0dead55e95d5fc6`**, source-critical file hashes, optional runtime versions, configuration/tokenizer identities, and all seven release-file hashes. The source `LICENSE` is Apache-2.0. The [model card at the pinned release revision](https://huggingface.co/aimeigaoshou/agent-jev/blob/7d433994fbde17a3f0993c2f2b02fe8ca1370db1/README.md) also declares `apache-2.0`; the actual connector rendering is preserved separately. This is a recorded license declaration, not a legal compatibility opinion or endorsement of the card's performance claims.

If the public source was not included in the clone, restore it explicitly:

```powershell
./scripts/bootstrap-research.ps1 -RestoreJevSource
```

This clones only when `runtime/agent-jev` is absent and checks out the pinned commit. It does not reset an existing checkout, install the Jev runtime or download weights. `-CheckJevSource` checks exact critical files and, when Git metadata exists, the commit. A vendored checkout without `.git` supports critical-file checks but not an independently verified Git identity.

The optional model release is `aimeigaoshou/agent-jev`, revision **`7d433994fbde17a3f0993c2f2b02fe8ca1370db1`**, variant **v1**. Its weight file is **1,196,881,242 bytes**, SHA-256 **`8166e46dc6019ae13f0d8fc97d603cdbcc2d20eb1882c7350c8deb9fc6bae215`**. Virtual environments and model weights are reproducible dependencies and are excluded from normal source publication. Do not substitute the model repository's moving default branch: the pinned fetcher explicitly distinguishes another, later checkpoint.

A separate `runtime/.venv` is required by `scripts/start-jev.ps1`. For CPU restoration, install the appropriate Python 3.13/PyTorch 2.9.1 CPU build from the official PyTorch wheel source, then the exact optional Jev package versions in the manifest. The observed workspace build `torch 2.9.1+cu128` is hardware-specific and is not imposed on every clone. After reviewing the pinned public fetcher, download model assets explicitly:

```powershell
Push-Location runtime/agent-jev
../.venv/Scripts/python.exe fetch_v1_weights.py --variant v1
Pop-Location
./scripts/start-jev.ps1 -Device cpu
```

The upstream fetcher checks sizes and SHA-256 for the weights, `temperatures.json`, `config.json`, `tokenizer.json`, `tokenizer_config.json`, `vocab.json` and `merges.txt`. Configuration is Qwen3, BF16, with a Qwen tokenizer release captured alongside the checkpoint. The publication verification does not rehash the 1.2 GB weight file; its pinned digest comes from the previously verified runtime manifest and the inspected pinned fetcher.

Service startup is a separate action, bound to loopback. Historical upstream README examples are not current credentials or instructions to contact remote hosts. A live inference is only claimed after an actual request and its model/hash-bound receipt. Model preferences are not mathematical proof or calibrated historical probabilities.

## Research artifacts versus disposable dependencies

`workspace-metadata-inventory.json` lists only explicit `runtime` and `work` directory-entry metadata. No credential stores or content-pattern scan was used. The inventory deliberately does not descend into `work/publication`, virtual environments, caches, or Git internals, and performs no copying.

Keep research code, source/evidence manifests, receipts, derived tables, plots, tests, checkpoints and handoffs under `work`. In particular, `work/final-day-2026-11-07`, `unit001`, `unit002`, `w72-witness`, `ariadne-inverse`, and the `sunny-native` subtree of the upstream worktree contain unique SUNNY artifacts. The worktree's nested public upstream code is a dependency; its SUNNY-specific additions are not disposable. Other work folders remain preserved candidates unless their contents have been separately reviewed.

Exclude `.venv`/`.venv-research`, `node_modules`, `__pycache__`, `.git` internals, model weights and the active `work/publication` staging area from normal source packaging. Preserve original large research inputs through the publication's explicit large-file archive/manifest rather than pretending they are dependencies that can be regenerated. Do not copy `work/publication` into itself or treat an inventory as proof of source authenticity or full scientific completion.

All sixteen SUNNY goals and eight outputs remain incomplete. The reproducibility package documents source/code/receipt continuity and scoped checks; it does not establish recovered ancient sounds, a unique historical orientation, full archive semantics or uninterrupted execution.
