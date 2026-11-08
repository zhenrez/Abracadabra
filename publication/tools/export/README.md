# Reviewed byte-preserving snapshot copier

This tool prepares a reviewed local publication snapshot. It does not publish, run Git, contact a remote service, delete files, or change original source files.

`snapshot_copy.py` accepts a workspace, a destination strictly inside that workspace, an explicit candidate JSONL file, and a content-preflight JSON document. A candidate is copied only when a preflight entry explicitly says `APPROVED` and its complete SHA-256 matches the current source bytes.

```powershell
python snapshot_copy.py --workspace <SUN> --destination <SUN-child-checkout> --candidates <candidate-jsonl> --preflight <approval-json>
```

The importable function is:

```python
snapshot_copy(workspace, destination, candidates, preflight,
              exclusions=None, promotions=None, adaptations=None, manifest=None)
```

Candidate records contain `path` and `category`. Preflight is `{"files": [{"path": "src/example.py", "sha256": "<64 hex characters>", "status": "APPROVED"}]}`. Paths use forward slashes and remain relative to the workspace.

Optional exclusion and source-fixture promotion documents each contain a `files` list whose records include a `path` and a nonempty `reason`. Promotions also supply a `category` and require their own approved SHA-bound preflight entry. Excluded paths and reasons appear only in a separate local-only, content-addressed receipt beside the preflight input. The portable manifest contains their opaque path hashes and count.

The only supported destination adaptation is `KEEP_APPROVED_DESTINATION` for root `README.md` or `.gitignore`. Its record requires `destination_sha256` and a nonempty `reason`. The destination file must already match that hash. The exact original workspace source bytes are copied to `.publication-source-vault/by-sha/<source-sha>/content`; the portable manifest binds both representations. Preserving an earlier remote README before adapting the checkout remains the caller's separate responsibility.

Existing destination files, existing manifests, Git metadata paths, absolute or parent-traversing paths, Windows path aliases, symbolic links, reparse points, and publication self-scope source paths are rejected. Planned file/parent collisions and invalid private-receipt locations are checked before copying the first file. The copier also hashes each source before and after its copy and verifies the copied bytes independently.

The default create-once portable receipt is `PUBLICATION_MANIFEST.json`. It records every included source path, byte count, SHA-256, classification, control-input hashes, and any explicit adaptation. It contains no absolute workspace path. Outputs use deterministic UTF-8 JSON.

The caller must prevent concurrent writes to the source and destination trees. Unexpected I/O failure or a detected mid-copy change may leave newly created partial files; the tool never deletes or overwrites them and does not issue a completion manifest for that failure. Hash binding establishes byte conservation, not privacy clearance, historical truth, licensing clearance, successful upload, or complete account-archive coverage. Content review remains an independent required input.

Focused validation:

```powershell
python -B -m unittest discover -s work/github-delivery-2026-11-07/export -p test_snapshot_copy.py -v
```

The tests use isolated synthetic fixtures only. They exercise reparse rejection through an injected predicate; they do not claim a physical Windows junction was created or copied. Production copying is owned by the coordinating agent after its independent content preflight.
