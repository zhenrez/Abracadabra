"""Copy an explicitly reviewed, SHA-bound publication snapshot without overwrites.

No network, Git operations, deletions, source edits, or implicit selection occur.
The destination is a strict workspace descendant. Controls are local inputs;
only the portable included-file manifest belongs to the publication snapshot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
from typing import Any

MANIFEST = "PUBLICATION_MANIFEST.json"
VAULT = ".publication-source-vault"
CHUNK = 1024 * 1024
HEX = re.compile(r"[0-9a-fA-F]{64}\Z")
DEVICES = {"con", "prn", "aux", "nul"} | {f"{p}{i}" for p in ("com", "lpt") for i in range(1, 10)}


def safe_relative(value: str) -> str:
    """Require one portable relative file address, rejecting Windows aliases."""
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("Candidate address must be a nonempty slash-separated relative path")
    parts = value.split("/")
    if any(not p or p in (".", "..") for p in parts):
        raise ValueError("Empty, dot, and parent path components are forbidden")
    if any(any(ord(c) < 32 or c in ':*?<>|"' for c in p) or p.endswith((".", " ")) for p in parts):
        raise ValueError("Nonportable or alternate-stream path component")
    if any(p.casefold() == ".git" or p.split(".")[0].casefold() in DEVICES for p in parts):
        raise ValueError("Git metadata and device paths are forbidden")
    lower = [p.casefold() for p in parts]
    if len(lower) > 1 and lower[0] == "work" and (lower[1].startswith("github-delivery") or lower[1].startswith("publication")):
        raise ValueError("Publication self-scope cannot be a source candidate")
    if lower[0] == VAULT.casefold() or lower[0] == MANIFEST.casefold():
        raise ValueError("Reserved publication output address")
    return str(PurePosixPath(*parts))


def is_reparse(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def _checked_path(base: Path, path: Path) -> Path:
    path = Path(os.path.abspath(path))
    try:
        relative = path.relative_to(base)
    except ValueError as error:
        raise ValueError("Path is outside the workspace") from error
    current = base
    if is_reparse(current):
        raise ValueError("Workspace reparse points are forbidden")
    for part in relative.parts:
        if current.exists() and not current.is_dir():
            raise ValueError("A destination or source parent is already a file")
        current = current / part
        if is_reparse(current):
            raise ValueError("Reparse points and symbolic links are forbidden")
    return path


def _digest(path: Path) -> str:
    hashed = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK), b""):
            hashed.update(block)
    return hashed.hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _read_control(workspace: Path, path: Path, *, lines: bool = False) -> tuple[Any, str]:
    path = _checked_path(workspace, Path(path))
    if not path.is_file():
        raise ValueError("Control input must be an existing regular file")
    raw = path.read_bytes()
    if b"\x00" in raw:
        raise ValueError("Control input contains NUL bytes")
    content = raw.decode("utf-8-sig")
    value = [json.loads(line) for line in content.splitlines() if line.strip()] if lines else json.loads(content)
    return value, hashlib.sha256(raw).hexdigest()


def _file_map(value: Any, role: str) -> dict[str, dict[str, Any]]:
    if not isinstance(value, dict) or not isinstance(value.get("files"), list):
        raise ValueError(f"{role} must contain a files list")
    result: dict[str, dict[str, Any]] = {}
    for row in value["files"]:
        if not isinstance(row, dict):
            raise ValueError(f"Invalid {role} row")
        path = safe_relative(row.get("path"))
        key = path.casefold()
        if key in result:
            raise ValueError(f"Duplicate {role} path")
        result[key] = {**row, "path": path}
    return result


def _reason(row: dict[str, Any]) -> str:
    reason = row.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("An explicit nonempty reason is required")
    return reason


def _sha(value: Any) -> str:
    if not isinstance(value, str) or not HEX.fullmatch(value):
        raise ValueError("Expected a complete SHA-256 digest")
    return value.lower()


def _immutable_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as output:
        output.write(raw)
        output.flush()
        os.fsync(output.fileno())
    if path.read_bytes() != raw:
        raise ValueError("Written artifact failed exact readback")


def _copy_verified(workspace: Path, source: Path, target: Path, expected: str) -> tuple[int, str]:
    _checked_path(workspace, source)
    _checked_path(workspace, target)
    if _digest(source) != expected:
        raise ValueError("Source changed after approval")
    target.parent.mkdir(parents=True, exist_ok=True)
    _checked_path(workspace, target)
    hashed = hashlib.sha256()
    copied = 0
    with source.open("rb") as incoming, target.open("xb") as outgoing:
        for block in iter(lambda: incoming.read(CHUNK), b""):
            outgoing.write(block)
            hashed.update(block)
            copied += len(block)
        outgoing.flush()
        os.fsync(outgoing.fileno())
    if hashed.hexdigest() != expected or _digest(source) != expected or _digest(target) != expected:
        raise ValueError("Source or copied bytes changed during snapshot; no completion manifest was written")
    return copied, expected


def snapshot_copy(workspace: Path, destination: Path, candidates: Path, preflight: Path,
                  *, exclusions: Path | None = None, promotions: Path | None = None,
                  adaptations: Path | None = None, manifest: Path | None = None) -> dict[str, Any]:
    """Validate every selection before copying; return the immutable portable receipt.

    Preconditions: no concurrent writer to the source/destination trees; content
    approvals supplied by the caller. This is not a privacy classifier. Unexpected
    I/O failure may leave new partial files; it never removes or overwrites them.
    """
    workspace = Path(os.path.abspath(workspace))
    if not workspace.is_dir() or is_reparse(workspace):
        raise ValueError("Workspace must be a real directory")
    destination = _checked_path(workspace, Path(destination))
    if destination == workspace or ".git" in (p.casefold() for p in destination.relative_to(workspace).parts):
        raise ValueError("Destination must be a strict workspace child outside Git metadata")
    manifest_path = _checked_path(workspace, Path(manifest) if manifest else destination / MANIFEST)
    try:
        manifest_relative = manifest_path.relative_to(destination).as_posix()
    except ValueError as error:
        raise ValueError("Portable manifest must be inside destination") from error
    if manifest_relative != MANIFEST:
        safe_relative(manifest_relative)
    if manifest_path.exists():
        raise ValueError("An existing publication manifest cannot be overwritten")

    rows, candidate_sha = _read_control(workspace, candidates, lines=True)
    approved_value, approval_sha = _read_control(workspace, preflight)
    approved = _file_map(approved_value, "preflight")
    selected = _file_map({"files": rows}, "candidate")
    control_hashes = {"candidates_sha256": candidate_sha, "preflight_sha256": approval_sha}

    exclusions_map: dict[str, dict[str, Any]] = {}
    adaptations_map: dict[str, dict[str, Any]] = {}
    for role, path in (("exclusions", exclusions), ("promotions", promotions), ("adaptations", adaptations)):
        if path is None:
            continue
        value, digest = _read_control(workspace, path)
        control_hashes[f"{role}_sha256"] = digest
        entries = _file_map(value, role)
        for row in entries.values():
            _reason(row)
        if role == "promotions":
            for key, row in entries.items():
                if key in selected:
                    raise ValueError("Promotion duplicates an existing selected path")
                selected[key] = row
        elif role == "exclusions":
            exclusions_map = entries
        else:
            adaptations_map = entries
    if not selected:
        raise ValueError("An empty snapshot cannot be certified")
    if any(key not in selected for key in exclusions_map | adaptations_map):
        raise ValueError("Exclusion or adaptation has no selected source")
    if exclusions_map.keys() & adaptations_map.keys():
        raise ValueError("One source cannot be excluded and adapted")

    excluded_local = [{"path": row["path"], "reason": _reason(row)} for row in exclusions_map.values()]
    local_path = None
    local_bytes = None
    if excluded_local:
        local_bytes = _json_bytes({"status": "LOCAL_ONLY", "excluded": excluded_local,
                                   "control_hashes": control_hashes})
        local_hash = hashlib.sha256(local_bytes).hexdigest()
        local_path = _checked_path(workspace, Path(preflight).parent / f"exclusion-updates.{local_hash}.LOCAL-ONLY.json")
        if local_path.is_relative_to(destination):
            raise ValueError("Private exclusion updates must remain outside destination")
        if local_path.exists() and local_path.read_bytes() != local_bytes:
            raise ValueError("Existing local exclusion receipt cannot be overwritten")

    pending: list[tuple[Path, Path, dict[str, Any]]] = []
    included: list[dict[str, Any]] = []
    for key, row in selected.items():
        if key in exclusions_map:
            continue
        relative = row["path"]
        if key == manifest_relative.casefold():
            raise ValueError("Candidate collides with manifest")
        approval = approved.get(key)
        if approval is None or approval.get("status") != "APPROVED":
            raise ValueError("Each included source needs explicit content approval")
        expected = _sha(approval.get("sha256"))
        source = _checked_path(workspace, workspace / relative)
        target = _checked_path(workspace, destination / relative)
        if not source.is_file() or not stat.S_ISREG(source.stat().st_mode):
            raise ValueError("Candidate is not a regular source file")
        if source == target or source.is_relative_to(destination):
            raise ValueError("Destination cannot contain a selected source")
        if _digest(source) != expected:
            raise ValueError("Source does not match its reviewed SHA-256")
        category = row.get("category")
        if not isinstance(category, str) or not category:
            raise ValueError("Included sources require a classification")
        record: dict[str, Any] = {"path": relative, "bytes": source.stat().st_size,
                                  "source_sha256": expected, "sha256": expected, "category": category}
        if key in adaptations_map:
            adaptation = adaptations_map[key]
            if relative not in ("README.md", ".gitignore") or adaptation.get("mode") != "KEEP_APPROVED_DESTINATION":
                raise ValueError("Only root README.md/.gitignore may retain an explicitly reviewed destination adaptation")
            destination_sha = _sha(adaptation.get("destination_sha256"))
            if not target.is_file() or _digest(target) != destination_sha:
                raise ValueError("Destination adaptation does not match its explicit approval")
            vault_relative = f"{VAULT}/by-sha/{expected}/content"
            vault = _checked_path(workspace, destination / vault_relative)
            if vault.exists() or any(item[1] == vault for item in pending):
                raise ValueError("Source snapshot vault collision")
            pending.append((source, vault, record))
            record.update({"source_snapshot_path": vault_relative, "destination_sha256": destination_sha,
                           "destination_bytes": target.stat().st_size, "adaptation": "KEEP_APPROVED_DESTINATION",
                           "adaptation_reason": _reason(adaptation)})
        else:
            if target.exists():
                raise ValueError("Existing destination file collision")
            pending.append((source, target, record))
            record["destination_sha256"] = expected
        included.append(record)
    if not included:
        raise ValueError("All selected sources were excluded")

    # Reject file/directory collisions among all planned writes, including a
    # custom manifest location, before writing the first included file.
    planned_paths = [manifest_path, *(target for _, target, _ in pending)]
    planned_keys = [path.relative_to(destination).as_posix().casefold() for path in planned_paths]
    planned_set = set(planned_keys)
    if len(planned_set) != len(planned_keys):
        raise ValueError("Planned destination files have a duplicate collision")
    for key in planned_keys:
        parts = key.split("/")
        if any("/".join(parts[:length]) in planned_set for length in range(1, len(parts))):
            raise ValueError("Planned destination files have a parent-file collision")

    # All logical validation above precedes creation of destination content.
    for source, target, record in pending:
        size, digest = _copy_verified(workspace, source, target, record["source_sha256"])
        if size != record["bytes"] or digest != record["source_sha256"]:
            raise ValueError("Copy byte accounting failed")
    for record in included:
        if "adaptation" in record and _digest(destination / record["path"]) != record["destination_sha256"]:
            raise ValueError("Reviewed destination adaptation changed during snapshot")
    if local_path is not None and local_bytes is not None:
        if local_path.exists():
            if local_path.read_bytes() != local_bytes:
                raise ValueError("Local exclusion receipt changed during snapshot")
        else:
            _immutable_write(local_path, local_bytes)
    result = {"schema": "source-preserving-publication-snapshot-v1", "status": "COMPLETE",
              "files": included, "included_count": len(included),
              "source_bytes": sum(row["bytes"] for row in included), "control_hashes": control_hashes,
              "excluded_count": len(excluded_local),
              "excluded_path_ids": [hashlib.sha256(row["path"].encode("utf-8")).hexdigest() for row in excluded_local],
              "assurance_boundary": "SHA-bound byte conservation; content review supplied externally; no historical truth or publication claim"}
    _immutable_write(manifest_path, _json_bytes(result))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("workspace", "destination", "candidates", "preflight"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    for name in ("exclusions", "promotions", "adaptations", "manifest"):
        parser.add_argument(f"--{name}", type=Path)
    result = snapshot_copy(**vars(parser.parse_args()))
    print(json.dumps({"status": result["status"], "included_count": result["included_count"],
                      "source_bytes": result["source_bytes"], "excluded_count": result["excluded_count"]}))


if __name__ == "__main__":
    main()
