# Public project files above the repository file-size limit

`large_sources.py` is a separate standard-library packer/restorer for exactly these three project outputs:

- `web/delivery-2026-11-07/data.js`
- `web/delivery-2026-11-07/data.json`
- `state/reconstruction/model.json`

It cannot select a private account export, an arbitrary database, a credential file, or another path. It does not modify the earlier private-archive packaging tools.

The packer reads approved complete files from the checkout and divides their exact bytes into parts of at most 8 MiB. Each content address is `archives/public-large/<full-file-sha256>/`, containing numbered `part-000001.bin` files and a content manifest. The master `archives/public-large/manifest.json` records each original repository-relative path, full byte count, full SHA-256, and every part's repository-relative address, byte count, and SHA-256. There is no compression or Git LFS dependency.

Production packing requires a separate JSON mapping whose keys are the three exact paths and whose values are their approved current SHA-256 digests:

```powershell
python large_sources.py pack --repository-root <checkout> --expected-hashes <approved-hashes.json>
```

The coordinating publisher adds the three complete-file paths to the public checkout's `.gitignore` and includes their parts, manifests, and this standalone restorer. The packer leaves all complete local files in place; it does not edit `.gitignore`, delete files, commit, push, or contact a remote service.

After obtaining the complete published parts, restore the three files with:

```powershell
python large_sources.py restore --repository-root <checkout>
```

The restorer verifies every part's address, size, and SHA-256, then recomputes each complete file's size and SHA-256 before creating any absent full file. Existing exact full files remain untouched. Existing differing files cause rejection and are never overwritten. Part paths and restored targets are restricted to this fixed public-project layout; symbolic links and reparse points are rejected.

The caller must prevent simultaneous writes during packing or restoration. An unexpected I/O error or detected concurrent change may leave newly created partial outputs; the tool never deletes them or reports success for that failed operation. Portable hashes establish byte consistency with the manifest; they do not independently authenticate its origin or certify the contents as public, licensed, or scientifically correct. Current content approval remains a separate publication requirement.

Focused validation uses only tiny synthetic files at the three permitted relative paths:

```powershell
python -B -m unittest discover -s work/github-delivery-2026-11-07/export -p test_large_sources.py -v
```
