"""Standard-library pack/restore for three explicitly public project outputs.

Original full files are never deleted or overwritten. This tool cannot package
or reconstruct arbitrary account archives, databases, credentials, or paths.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Any

PUBLIC_LARGE_PATHS = (
    "web/delivery-2026-11-07/data.js",
    "web/delivery-2026-11-07/data.json",
    "state/reconstruction/model.json",
)
PART_SIZE = 8 * 1024 * 1024
ARCHIVE = "archives/public-large"
MANIFEST = f"{ARCHIVE}/manifest.json"
SCHEMA = "public-large-project-files-v1"
SHA = re.compile(r"[0-9a-f]{64}\Z")


def is_reparse(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def _root(path: Path) -> Path:
    root = Path(os.path.abspath(path))
    if not root.is_dir() or is_reparse(root):
        raise ValueError("Repository root must be a real existing directory")
    return root


def _path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or "\\" in relative:
        raise ValueError("Expected a portable relative address")
    parts = relative.split("/")
    if any(not part or part in (".", "..") or ":" in part or part.casefold() == ".git" for part in parts):
        raise ValueError("Unsafe path component")
    current = root
    for part in parts:
        if current.exists() and not current.is_dir():
            raise ValueError("An output parent is already a file")
        current = current / part
        if is_reparse(current):
            raise ValueError("Reparse points and symbolic links are forbidden")
    return current


def _sha(value: Any) -> str:
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise ValueError("Expected a lowercase complete SHA-256")
    return value


def _bytes(value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError("Byte counts must be nonnegative integers")
    return value


def _canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(PART_SIZE), b""):
            digest.update(block)
    return digest.hexdigest()


def _same_or_absent(path: Path, raw: bytes) -> None:
    if path.exists() and (not path.is_file() or path.read_bytes() != raw):
        raise ValueError("Existing manifest or part differs; overwrite is forbidden")


def _write_once(path: Path, raw: bytes) -> None:
    if path.exists():
        _same_or_absent(path, raw)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    if path.read_bytes() != raw:
        raise ValueError("Exact written-byte readback failed")


def _part_path(full_sha: str, index: int) -> str:
    return f"{ARCHIVE}/{full_sha}/part-{index:06d}.bin"


def _scan(source: Path, relative: str, part_size: int) -> dict[str, Any]:
    if not source.is_file() or not stat.S_ISREG(source.stat().st_mode):
        raise ValueError("Explicit project source is not a regular file")
    full = hashlib.sha256()
    total = 0
    chunks = []
    with source.open("rb") as incoming:
        for index, block in enumerate(iter(lambda: incoming.read(part_size), b""), start=1):
            full.update(block)
            total += len(block)
            chunks.append({"bytes": len(block), "sha256": hashlib.sha256(block).hexdigest(), "index": index})
    digest = full.hexdigest()
    parts = [{"path": _part_path(digest, part["index"]), "bytes": part["bytes"], "sha256": part["sha256"]} for part in chunks]
    return {"path": relative, "bytes": total, "sha256": digest, "parts": parts}


def _content_manifest(record: dict[str, Any]) -> dict[str, Any]:
    return {"schema": "public-large-content-v1", "bytes": record["bytes"],
            "sha256": record["sha256"], "parts": record["parts"]}


def pack_sources(repository_root: Path, *, paths=PUBLIC_LARGE_PATHS,
                 part_size: int = PART_SIZE, expected_hashes: dict[str, str] | None = None) -> dict[str, Any]:
    """Split only the explicit allowlist, retaining complete source files.

    Supply expected_hashes from the current approval receipt for production.
    All source scans, approval matches, and existing-output collisions are
    checked before the first part is written. No compression or LFS is used.
    """
    root = _root(repository_root)
    if not isinstance(part_size, int) or isinstance(part_size, bool) or not 0 < part_size <= PART_SIZE:
        raise ValueError("Part size must be 1 through 8 MiB")
    paths = tuple(paths)
    if not paths or len(paths) != len(set(paths)) or any(path not in PUBLIC_LARGE_PATHS for path in paths):
        raise ValueError("Only distinct explicitly public project paths may be packaged")
    records = []
    for relative in paths:
        source = _path(root, relative)
        record = _scan(source, relative, part_size)
        if expected_hashes is not None:
            if relative not in expected_hashes or record["sha256"] != _sha(expected_hashes[relative]):
                raise ValueError("Project source does not match its approved current SHA-256")
        records.append(record)
    manifest = {"schema": SCHEMA, "part_size_bytes": part_size, "files": records,
                "scope": "Only the three named public project outputs; full sources retained locally"}
    manifest_path = _path(root, MANIFEST)
    _same_or_absent(manifest_path, _canonical(manifest))
    for record in records:
        _same_or_absent(_path(root, f"{ARCHIVE}/{record['sha256']}/manifest.json"), _canonical(_content_manifest(record)))
        for part in record["parts"]:
            target = _path(root, part["path"])
            if target.exists() and (not target.is_file() or target.stat().st_size != part["bytes"] or _digest(target) != part["sha256"]):
                raise ValueError("Existing part differs; overwrite is forbidden")
    for record in records:
        source = _path(root, record["path"])
        full = hashlib.sha256()
        copied = 0
        with source.open("rb") as incoming:
            for part in record["parts"]:
                block = incoming.read(part["bytes"])
                if len(block) != part["bytes"] or hashlib.sha256(block).hexdigest() != part["sha256"]:
                    raise ValueError("Source changed during split; no new completion manifest issued")
                full.update(block)
                copied += len(block)
                _write_once(_path(root, part["path"]), block)
            if incoming.read(1):
                raise ValueError("Source grew during split")
        if copied != record["bytes"] or full.hexdigest() != record["sha256"] or _digest(source) != record["sha256"]:
            raise ValueError("Full source verification failed during split")
    for record in records:
        _write_once(_path(root, f"{ARCHIVE}/{record['sha256']}/manifest.json"), _canonical(_content_manifest(record)))
    _write_once(manifest_path, _canonical(manifest))
    return manifest


def _read_manifest(root: Path) -> dict[str, Any]:
    raw = _path(root, MANIFEST).read_bytes()
    if b"\x00" in raw:
        raise ValueError("Manifest contains NUL bytes")
    manifest = json.loads(raw.decode("utf-8"))
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        raise ValueError("Unsupported public project manifest")
    size = manifest.get("part_size_bytes")
    if not isinstance(size, int) or isinstance(size, bool) or not 0 < size <= PART_SIZE:
        raise ValueError("Invalid public part size")
    records = manifest.get("files")
    if not isinstance(records, list) or not records or len(records) > len(PUBLIC_LARGE_PATHS):
        raise ValueError("Invalid explicit source list")
    seen = set()
    for record in records:
        if not isinstance(record, dict) or record.get("path") not in PUBLIC_LARGE_PATHS or record["path"] in seen:
            raise ValueError("Restore target is not one distinct explicitly public project path")
        seen.add(record["path"])
        digest = _sha(record.get("sha256"))
        total = _bytes(record.get("bytes"))
        parts = record.get("parts")
        if not isinstance(parts, list) or len(parts) != (total + size - 1) // size:
            raise ValueError("Part count does not match full byte count")
        for index, part in enumerate(parts, start=1):
            if not isinstance(part, dict) or part.get("path") != _part_path(digest, index):
                raise ValueError("Part must have the exact approved repository-relative address")
            expected_size = size if index < len(parts) else total - size * (len(parts) - 1)
            if _bytes(part.get("bytes")) != expected_size:
                raise ValueError("Part byte count does not match its sequence")
            _sha(part.get("sha256"))
    return manifest


def restore_sources(repository_root: Path) -> dict[str, Any]:
    """Verify all chunks/full hashes before restoring absent allowlisted files.

    Existing exact full files are left untouched; differing existing files cause
    rejection. Private archives and arbitrary manifest target paths cannot be
    restored through this interface. No deletion or in-place overwrite occurs.
    """
    root = _root(repository_root)
    manifest = _read_manifest(root)
    targets = []
    for record in manifest["files"]:
        target = _path(root, record["path"])
        if target.exists() and (not target.is_file() or target.stat().st_size != record["bytes"] or _digest(target) != record["sha256"]):
            raise ValueError("Existing restored target differs; overwrite is forbidden")
        targets.append((record, target, target.exists()))
        full = hashlib.sha256()
        total = 0
        for part in record["parts"]:
            path = _path(root, part["path"])
            if not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
                raise ValueError("Required part is missing or not a regular file")
            raw = path.read_bytes()
            if len(raw) != part["bytes"] or hashlib.sha256(raw).hexdigest() != part["sha256"]:
                raise ValueError("Part size or SHA-256 does not match")
            full.update(raw)
            total += len(raw)
        if total != record["bytes"] or full.hexdigest() != record["sha256"]:
            raise ValueError("Reassembled full byte count or SHA-256 does not match")
    receipts = []
    for record, target, existed in targets:
        if existed:
            if _digest(target) != record["sha256"]:
                raise ValueError("Existing exact target changed during verification")
            status = "ALREADY_EXACT"
        else:
            _path(root, record["path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            full = hashlib.sha256()
            with target.open("xb") as outgoing:
                for part in record["parts"]:
                    raw = _path(root, part["path"]).read_bytes()
                    if len(raw) != part["bytes"] or hashlib.sha256(raw).hexdigest() != part["sha256"]:
                        raise ValueError("Part changed during restoration; no success receipt issued")
                    outgoing.write(raw)
                    full.update(raw)
                outgoing.flush()
                os.fsync(outgoing.fileno())
            if full.hexdigest() != record["sha256"] or target.stat().st_size != record["bytes"] or _digest(target) != record["sha256"]:
                raise ValueError("Restored full file failed verification")
            status = "RESTORED"
        receipts.append({"path": record["path"], "bytes": record["bytes"], "sha256": record["sha256"], "status": status})
    return {"status": "VERIFIED", "schema": "public-large-restore-receipt-v1", "files": receipts}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("pack", "restore"))
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--expected-hashes", type=Path, help="JSON mapping of explicit source path to approved current SHA-256; required for production pack")
    args = parser.parse_args()
    if args.operation == "pack":
        if args.expected_hashes is None:
            parser.error("pack requires --expected-hashes to bind approved current bytes")
        expected = json.loads(args.expected_hashes.read_text(encoding="utf-8"))
        result = pack_sources(args.repository_root, expected_hashes=expected)
        print(json.dumps({"status": "PACKED_AND_VERIFIED", "files": len(result["files"]), "manifest": MANIFEST}))
    else:
        if args.expected_hashes is not None:
            parser.error("restore uses the portable manifest, not an external approval mapping")
        print(json.dumps(restore_sources(args.repository_root)))


if __name__ == "__main__":
    main()
