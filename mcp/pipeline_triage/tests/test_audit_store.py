"""Database layer tests: real PostgreSQL, no MCP and no AI model involved."""
import psycopg
import pytest

import audit_store
from db import connect_read_only
from init_demo_db import seed


@pytest.fixture(scope="module", autouse=True)
def seeded_db():
    seed()  # resets the dedicated *_demo database to known rows


def test_failed_runs_filtered_by_date():
    rows = audit_store.list_failed_runs("2026-11-15")
    assert [r["run_id"] for r in rows] == [101, 102]
    assert all(r["status"] == "FAILED" for r in rows)


def test_run_details_include_failure_evidence():
    run = audit_store.get_run_details(102)
    assert run["pipeline_name"] == "payments_ingest"
    assert "schema mismatch" in run["error_message"].lower()
    assert run["started_at"].startswith("2026-11-15T07:15:00")


def test_unknown_run_returns_none():
    assert audit_store.get_run_details(999) is None


@pytest.mark.parametrize("bad", ["2026-99-99", "15/11/2026", "2026-11-15'; DROP TABLE pipeline_runs;--"])
def test_invalid_date_rejected_before_sql(bad):
    with pytest.raises(ValueError):
        audit_store.list_failed_runs(bad)


def test_connection_is_read_only():
    with connect_read_only() as conn, pytest.raises(psycopg.errors.ReadOnlySqlTransaction):
        conn.execute("DELETE FROM pipeline_runs")
