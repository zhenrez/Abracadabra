# Reviewed-work publication inventory

This inventory supports the separately authorized public `zhenrez/Abracadabra` delivery. It makes no GitHub call, commit, push or old-SUNNY-repository change. Root owns repository operations and the final content, secret and rights preflight.

The corrected SUN metadata observation accounts for **34,156 accessible files** and **23,447,451,622 logical bytes**. Logical byte sums count separate file copies; they are not deduplicated disk usage. Ignored files were included. No reparse point was followed; none was observed. One existing directory could not be enumerated because of an access denial. Its unknown child count and byte size remain unknown. This is a live-tree observation with an explicit gap, not an atomic or complete filesystem snapshot.

## Publication scope

| Classification | Files | Logical bytes | Recommendation |
|---|---:|---:|---|
| Project authored product | 5,992 | 1,449,429,577 | Include after root content/secret/rights preflight |
| Private account archive | 62 | 7,728,904,761 | Retain locally; publish only separately reviewed project-specific extracts |
| Dependency/model/install | 21,979 | 5,984,181,603 | Exclude installed copies; preserve reproducible source and acquisition manifests |
| Duplicate publication parts | 831 | 7,119,325,642 | Retain locally; exclude old packets/chunks/checkout copies |
| Third-party source review | 5,292 | 1,165,610,039 | Hold until source-role, privacy and licence review |

Canonical G0 fixtures, frozen Sefer/SUN scientific sources and every initial/current mathematical evidence version are explicit include candidates. A duplicate fixture's identity and provenance are preserved; identical bytes alone do not make a canonical control disposable. Missing historical certainty does not erase useful work.

`include-candidates.public.jsonl` and `include-paths.public.txt` provide one actual include-candidate path per line for the root staging process. Their projection retains the frozen public-plan input hash and removes all `work/github-delivery*` and `work/publication*` paths to prevent recursive publication copies. This leaves **5,988 paths and 1,449,415,198 logical bytes** before root content preflight and any separately reviewed additions. `include-candidates-summary.public.json` records the four self-scope exclusions and output hashes. No checkout is modified by producing these lists.

The whole metadata observation found **18 files at least 100,000,000 bytes** and **17 at least 104,857,600 bytes**. Those are review thresholds, not a newly verified statement of GitHub policy. None of the include candidates exceeds 100 MiB. Large installed models, raw account databases, mixed archives and private-target chunks remain local or held rather than being blindly uploaded.

## Public-safe and local-only artifacts

`publication-plan.public-redacted.jsonl` accounts for every observed file. Include candidates retain their project-relative path. Every held/excluded item exposes only an opaque path hash, byte count, category and generic reason. `publication-summary.public.json` reconciles counts and bytes, records boundaries and names the supported artifacts.

**Do not publish** `publication-plan.LOCAL-ONLY.jsonl`, the full metadata JSONL files, `summary.json`, the local gap observation or diagnostic directories. They retain exact local paths and may identify private account material. Keep them locally for traceability. The public summary and public-redacted manifest, this README and the three reusable scripts are appropriate source-review candidates; they do not contain file-content secrets from the scanned corpus.

`diagnostics-invalid-scope` preserves an initial metadata-only helper run that selected the parent directory by an incorrect relative-depth calculation. It is outside the authorized publication scope and is not publication material. The helper now uses and asserts the explicit SUN workspace. `diagnostics-metadata-format` preserves a scoped intermediate run whose extension aggregation had an empty key and whose token-like filename pattern over-redacted ordinary task hashes. Both issues were corrected before the final inventory. No original source content was changed, and no secret values were read or printed.

## Reproduction and verification

```powershell
& 'work/github-delivery-2026-11-07/inventory/verify_inventory.ps1'
```

The verifier checks artifact hashes, all **34,156 source/local/public record correspondences**, per-file reasons, withheld-path redaction and category/file/byte totals. It does not inspect source contents or approve redistribution. The captured outcome is in `publication-verification.public.json`.

The capture and classification scripts are `inventory_workspace.ps1` and `classify_public_scope.ps1`. They should be run in a separately identified output scope for a later observation; preserve earlier observations. The current generated inventory scope is deliberately excluded from its own growing output stream. These new audit artifacts remain separately reviewable work products.

Installed host-workspace-operator guidance was read and applied to explicit scope, read-only metadata discovery, bounded new artifacts and fresh checks. Actual native PowerShell enumeration, hashing and verification ran. No new model inference, remote guardrail runtime, account export, dependency download or original-source rewrite is claimed.
