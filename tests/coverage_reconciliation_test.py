"""Isolated census regressions: no live SUNNY database or receipts are touched."""
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/reconcile_current_coverage.py"
spec = importlib.util.spec_from_file_location("coverage_reconciliation", SCRIPT)
coverage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coverage)


def write(root, path, value):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(coverage.encoded(value))


class CoverageReconciliationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sunny-coverage-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "data").mkdir()
        native = self.root / "data/native.txt"
        derived = self.root / "data/derived.txt"
        native.write_text("native source", encoding="utf-8")
        derived.write_text("derived model", encoding="utf-8")
        database = sqlite3.connect(self.root / "data/sunny.sqlite")
        database.executescript("""
            CREATE TABLE sources(id TEXT PRIMARY KEY,path TEXT,sha256 TEXT,kind TEXT,status TEXT);
            CREATE TABLE conversations(id TEXT PRIMARY KEY);
            CREATE TABLE messages(id TEXT PRIMARY KEY,source_id TEXT,role TEXT,content_sha256 TEXT);
            CREATE TABLE documents(id TEXT PRIMARY KEY,source_id TEXT);
            CREATE TABLE nodes(id TEXT PRIMARY KEY);
            CREATE TABLE refs(id TEXT PRIMARY KEY);
            CREATE TABLE decisions(id TEXT PRIMARY KEY);
            CREATE TABLE search_index(id TEXT PRIMARY KEY);
            CREATE TABLE coverage(source_id TEXT,status TEXT);
        """)
        database.executemany("INSERT INTO sources VALUES(?,?,?,?,?)", [
            ("native", str(native), coverage.digest(native.read_bytes()), "native_export", "available"),
            ("derived", str(derived), coverage.digest(derived.read_bytes()), "derived_current_model_reconstruction", "available"),
        ])
        database.execute("INSERT INTO conversations VALUES('chat')")
        database.executemany("INSERT INTO messages VALUES(?,?,?,?)", [
            ("m1", "native", "user", "hash1"), ("m2", "native", "assistant", "hash2"),
            ("m3", "native", "user", "hash3"),
        ])
        database.executemany("INSERT INTO documents VALUES(?,?)", [("d1", "native"), ("d2", "derived")])
        database.executemany("INSERT INTO search_index VALUES(?)", [(name,) for name in ["m1", "m2", "m3", "d1", "d2"]])
        database.commit()
        database.close()
        prior_counts = {"sources": 1, "conversations": 1, "messages": 3, "nodes": 0,
                        "documents": 1, "refs": 0, "decisions": 0, "search_index": 4}
        self.prior = {"schema": "test", "counts": prior_counts,
                      "sources": [{"id": "native", "path": str(native)}],
                      "checkpoint_comparisons": [{"historical": "must remain exact"}],
                      "explicit_gaps": ["Missing images stay missing, not nonexistent."],
                      "exact_reconciliation": {"reported_initial": 59894, "current": 3},
                      "reconstruction_module_references": {},
                      "recursive_inventory_only": "m3"}
        write(self.root, coverage.COVERAGE_PATH, self.prior)
        (self.root / coverage.DOC_PATH).parent.mkdir(parents=True)
        (self.root / coverage.DOC_PATH).write_text("previous coverage\n", encoding="utf-8")
        write(self.root, coverage.INPUT_RECEIPT, {"literal": "protected original receipt"})
        for name in coverage.BASE_MODULES:
            write(self.root, f"state/reconstruction/{name}.json", {"message_id": "m1", "source_id": "native"})
        write(self.root, "state/reconstruction/native-execution.json",
              {"status": "conditional execution", "message_id": "m2", "source_id": "native", "canonicalPromotion": False})
        # A recursive inventory must not inflate the contact count to all3messages.
        write(self.root, "state/reconstruction/model.json", {"inventory": ["m1", "m2", "m3", "native", "derived"]})
        self.receipt_before = (self.root / coverage.INPUT_RECEIPT).read_bytes()
        self.database_before = (self.root / "data/sunny.sqlite").read_bytes()

    def assert_protected_inputs_unchanged(self):
        self.assertEqual((self.root / coverage.INPUT_RECEIPT).read_bytes(), self.receipt_before)
        self.assertEqual((self.root / "data/sunny.sqlite").read_bytes(), self.database_before)

    def test_preview_is_read_only_and_excludes_recursive_inventories(self):
        old = (self.root / coverage.COVERAGE_PATH).read_bytes()
        plan = coverage.plan_reconciliation(self.root)
        self.assertEqual(plan["receipt"]["message_contacts"], 2)
        self.assertEqual(plan["receipt"]["source_contacts"], 1)
        self.assertEqual(plan["receipt"]["module_count"], 6)
        self.assertEqual(len(plan["receipt"]["pending_math_units"]), 11)
        self.assertIn("state/reconstruction/hierarchy-atlas-combined.json", plan["receipt"]["pending_math_units"])
        self.assertIsNone(plan["receipt"]["semantic_completion"])
        self.assertEqual((self.root / coverage.COVERAGE_PATH).read_bytes(), old)
        self.assertFalse((self.root / "state/checkpoint-history").exists())
        self.assertFalse((self.root / coverage.RECEIPT_PATH).exists())
        self.assert_protected_inputs_unchanged()

    def test_apply_retains_old_outputs_and_counts_derived_addition_separately(self):
        old_json = (self.root / coverage.COVERAGE_PATH).read_bytes()
        old_doc = (self.root / coverage.DOC_PATH).read_bytes()
        plan = coverage.plan_reconciliation(self.root)
        receipt = coverage.apply_reconciliation(plan, self.root)
        result = json.loads((self.root / coverage.COVERAGE_PATH).read_text(encoding="utf-8"))
        self.assertEqual(result["counts"]["sources"], 2)
        self.assertEqual(result["counts"]["documents"], 2)
        self.assertEqual(result["counts"]["search_index"], 5)
        self.assertEqual(result["current_reconciliation"]["count_delta"]["messages"], 0)
        self.assertEqual(result["current_reconciliation"]["count_delta"]["sources"], 1)
        self.assertTrue(result["current_reconciliation"]["added_source_occurrences"][0]["is_derived_reconstruction"])
        self.assertEqual(result["checkpoint_comparisons"], self.prior["checkpoint_comparisons"])
        self.assertEqual(result["explicit_gaps"], self.prior["explicit_gaps"])
        self.assertIsNone(result["semantic_coverage"]["fully_semantically_processed_messages"])
        self.assertEqual((self.root / receipt["prior_outputs"][0]["path"]).read_bytes(), old_json)
        self.assertEqual((self.root / receipt["prior_outputs"][1]["path"]).read_bytes(), old_doc)
        for output in receipt["outputs"]:
            self.assertEqual(coverage.digest((self.root / output["path"]).read_bytes()), output["sha256"])
        doc = (self.root / coverage.DOC_PATH).read_text(encoding="utf-8")
        self.assertIn("5 projections: 3 messages/events plus 2 documents", doc)
        self.assertIn("not native user messages", doc)
        self.assertNotIn("62,339", doc)
        self.assert_protected_inputs_unchanged()

    def test_rejects_changed_module_before_touching_coverage(self):
        before = (self.root / coverage.COVERAGE_PATH).read_bytes()
        plan = coverage.plan_reconciliation(self.root)
        write(self.root, "state/reconstruction/native-execution.json", {"changed": True})
        with self.assertRaisesRegex(ValueError, "Referenced module changed"):
            coverage.apply_reconciliation(plan, self.root)
        self.assertEqual((self.root / coverage.COVERAGE_PATH).read_bytes(), before)
        self.assertFalse((self.root / "state/checkpoint-history").exists())
        self.assert_protected_inputs_unchanged()

    def test_rejects_changed_input_receipt_without_overwriting_it(self):
        before = (self.root / coverage.COVERAGE_PATH).read_bytes()
        plan = coverage.plan_reconciliation(self.root)
        changed = b'{"new authorized input":true}\n'
        (self.root / coverage.INPUT_RECEIPT).write_bytes(changed)
        with self.assertRaisesRegex(ValueError, "Input-preservation receipt changed"):
            coverage.apply_reconciliation(plan, self.root)
        self.assertEqual((self.root / coverage.INPUT_RECEIPT).read_bytes(), changed)
        self.assertEqual((self.root / coverage.COVERAGE_PATH).read_bytes(), before)
        self.assertFalse((self.root / coverage.RECEIPT_PATH).exists())

    def test_rejects_newly_appeared_math_module_before_writing_a_stale_census(self):
        before = (self.root / coverage.COVERAGE_PATH).read_bytes()
        plan = coverage.plan_reconciliation(self.root)
        write(self.root, "state/reconstruction/master-score.json", {"source_id": "native", "message_id": "m3"})
        with self.assertRaisesRegex(ValueError, "Pending mathematical module appeared"):
            coverage.apply_reconciliation(plan, self.root)
        self.assertEqual((self.root / coverage.COVERAGE_PATH).read_bytes(), before)
        self.assertFalse((self.root / "state/checkpoint-history").exists())
        self.assert_protected_inputs_unchanged()


if __name__ == "__main__":
    unittest.main()
