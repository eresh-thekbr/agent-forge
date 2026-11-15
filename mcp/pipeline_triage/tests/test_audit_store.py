"""Database tests run without an AI model or MCP host."""
import tempfile
import unittest
from pathlib import Path

from audit_store import get_run_details, list_failed_runs
from init_demo_db import create_demo_db


class PipelineAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "demo.sqlite3"
        create_demo_db(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_failed_runs_are_filtered_by_date(self):
        rows = list_failed_runs("2026-11-15", self.db_path)
        self.assertEqual([row["run_id"] for row in rows], [101, 102])

    def test_run_details_include_failure_evidence(self):
        run = get_run_details(101, self.db_path)
        self.assertEqual(run["pipeline_name"], "customer_master_daily")
        self.assertIn("shuffle", run["error_message"].lower())

    def test_no_match(self):
        self.assertIsNone(get_run_details(999, self.db_path))

    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            list_failed_runs("2026-99-99", self.db_path)


if __name__ == "__main__":
    unittest.main()
