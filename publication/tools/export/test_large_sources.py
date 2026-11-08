from pathlib import Path
import hashlib
import json
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
FIRST = "web/delivery-2026-11-07/data.js"
SECOND = "web/delivery-2026-11-07/data.json"
THIRD = "state/reconstruction/model.json"
FOURTH = "state/checkpoint-history/before-math-model.json-0cd76aa39f015b3f4f2b1b400510461214a5a79084ba036d3e5b19c7bd7d377b.snapshot"
FIFTH = "state/checkpoint-history/before-math-model.json-2e0677402fcdb160e600da54b38f05da1d5d83794fd6f797d2f6cd5c5a585bbc.snapshot"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class PublicLargeSourceTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((HERE / "large_sources.py").exists(), "Public large-source packer/restorer is absent")
        import large_sources
        self.api = large_sources
        self.temporary = tempfile.TemporaryDirectory(dir=HERE)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "checkout"
        self.root.mkdir()

    def source(self, path=FIRST, raw=b"source\r\n\x00\xff bytes exactly"):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        return target

    def pack(self, paths=(FIRST,), **options):
        return self.api.pack_sources(self.root, paths=paths, part_size=7, **options)

    def test_binary_round_trip_and_existing_exact_preservation(self):
        source = self.source()
        original = source.read_bytes()
        manifest = self.pack()
        self.assertEqual(source.read_bytes(), original)
        record = manifest["files"][0]
        self.assertEqual(record["sha256"], sha(original))
        self.assertEqual(sum(part["bytes"] for part in record["parts"]), len(original))
        self.assertTrue(all(part["bytes"] <= 7 for part in record["parts"]))
        before = source.stat().st_mtime_ns
        existing = self.api.restore_sources(self.root)
        self.assertEqual(existing["files"][0]["status"], "ALREADY_EXACT")
        self.assertEqual(source.stat().st_mtime_ns, before)
        source.unlink()  # Only isolated test data is removed.
        restored = self.api.restore_sources(self.root)
        self.assertEqual(restored["files"][0]["status"], "RESTORED")
        self.assertEqual(source.read_bytes(), original)

    def test_exact_five_path_allowlist(self):
        for path in (FIRST, SECOND, THIRD, FOURTH, FIFTH):
            self.source(path, path.encode())
        manifest = self.api.pack_sources(self.root, part_size=7)
        self.assertEqual({row["path"] for row in manifest["files"]}, {FIRST, SECOND, THIRD, FOURTH, FIFTH})
        for path in ("private/account.db", "../escape", ".git/config", ".env", "/absolute"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.api.pack_sources(self.root, paths=(path,), part_size=7)

    def test_named_checkpoint_snapshots_require_current_approved_hash(self):
        for path in (FOURTH, FIFTH):
            self.source(path, b"exact public scientific checkpoint")
        with self.assertRaises(ValueError):
            self.pack(paths=(FOURTH, FIFTH), expected_hashes={FOURTH: sha(b"old"), FIFTH: sha(b"old")})
        self.assertFalse((self.root / "archives/public-large").exists())
        manifest = self.pack(paths=(FOURTH, FIFTH), expected_hashes={FOURTH: sha(b"exact public scientific checkpoint"), FIFTH: sha(b"exact public scientific checkpoint")})
        self.assertEqual({record["path"] for record in manifest["files"]}, {FOURTH, FIFTH})

    def test_cli_can_select_one_explicit_allowed_path(self):
        import subprocess
        import sys
        self.source(FOURTH, b"approved checkpoint")
        approval = self.root / "approved.json"
        approval.write_text(json.dumps({FOURTH: sha(b"approved checkpoint")}), encoding="utf-8")
        result = subprocess.run([sys.executable, str(HERE / "large_sources.py"), "pack", "--repository-root", str(self.root),
                                 "--expected-hashes", str(approval), "--path", FOURTH], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((self.root / "archives/public-large/manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([row["path"] for row in manifest["files"]], [FOURTH])

    def test_approved_hash_binding_rejects_changed_source_before_parts(self):
        self.source(raw=b"changed")
        with self.assertRaises(ValueError):
            self.pack(expected_hashes={FIRST: sha(b"old reviewed version")})
        self.assertFalse((self.root / "archives/public-large").exists())

    def test_part_and_full_digest_present_with_portable_addresses(self):
        original = self.source().read_bytes()
        manifest = self.pack()
        self.assertNotIn(str(self.root), json.dumps(manifest))
        record = manifest["files"][0]
        for index, part in enumerate(record["parts"], start=1):
            self.assertEqual(part["path"], f"archives/public-large/{sha(original)}/part-{index:06d}.bin")
            self.assertEqual(sha((self.root / part["path"]).read_bytes()), part["sha256"])
        self.assertTrue((self.root / f"archives/public-large/{sha(original)}/manifest.json").is_file())

    def test_corrupt_part_rejected_without_creating_restored_file(self):
        source = self.source()
        manifest = self.pack()
        source.unlink()
        part = self.root / manifest["files"][0]["parts"][0]["path"]
        part.write_bytes(b"corrupt")
        with self.assertRaises(ValueError):
            self.api.restore_sources(self.root)
        self.assertFalse(source.exists())

    def test_incorrect_full_digest_rejected_after_part_verification(self):
        source = self.source()
        manifest = self.pack()
        source.unlink()
        record = manifest["files"][0]
        record["sha256"] = "0" * 64
        for index, part in enumerate(record["parts"], start=1):
            old = self.root / part["path"]
            part["path"] = f"archives/public-large/{'0' * 64}/part-{index:06d}.bin"
            new = self.root / part["path"]
            new.parent.mkdir(parents=True, exist_ok=True)
            new.write_bytes(old.read_bytes())
        path = self.root / "archives/public-large/manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.api.restore_sources(self.root)
        self.assertFalse(source.exists())

    def test_existing_mismatch_never_overwritten(self):
        source = self.source()
        self.pack()
        source.write_bytes(b"a user modification")
        with self.assertRaises(ValueError):
            self.api.restore_sources(self.root)
        self.assertEqual(source.read_bytes(), b"a user modification")

    def test_tampered_restore_target_and_part_escape_rejected(self):
        self.source()
        original = self.pack()
        path = self.root / "archives/public-large/manifest.json"
        for kind in ("target", "part"):
            changed = json.loads(json.dumps(original))
            if kind == "target":
                changed["files"][0]["path"] = "private/account.db"
            else:
                changed["files"][0]["parts"][0]["path"] = "../../outside"
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.api.restore_sources(self.root)

    def test_reparse_guard_blocks_source_and_output(self):
        from unittest.mock import patch
        self.source()
        original = self.api.is_reparse
        def source_link(path):
            return Path(path).name == "web" or original(path)
        with patch.object(self.api, "is_reparse", side_effect=source_link), self.assertRaises(ValueError):
            self.pack()
        def output_link(path):
            return Path(path).name == "archives" or original(path)
        with patch.object(self.api, "is_reparse", side_effect=output_link), self.assertRaises(ValueError):
            self.pack()

    def test_existing_manifest_and_parts_are_preserved_exactly(self):
        self.source()
        manifest = self.pack()
        path = self.root / "archives/public-large/manifest.json"
        before = path.read_bytes()
        self.assertEqual(self.pack(), manifest)
        self.assertEqual(path.read_bytes(), before)
        part = self.root / manifest["files"][0]["parts"][0]["path"]
        part.write_bytes(b"collision")
        with self.assertRaises(ValueError):
            self.pack()
        self.assertEqual(part.read_bytes(), b"collision")


if __name__ == "__main__":
    unittest.main()
