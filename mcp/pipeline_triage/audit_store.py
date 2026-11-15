"""Read-only access to synthetic data pipeline audit records.

This is plain Python database code. The MCP layer is in server.py.
"""
from __future__ import annotations

from contextlib import closing
from datetime import date
from pathlib import Path
import re
import sqlite3

DB_PATH = Path(__file__).with_name("demo_pipeline_audit.sqlite3")


def _read_only_connection(db_path: Path) -> sqlite3.Connection:
    if not db_path.is_file():
        raise FileNotFoundError(
            "Demo database not found. Run: uv run python init_demo_db.py"
        )
    connection = sqlite3.connect(f"{db_path.resolve().as_uri()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def list_failed_runs(business_date: str, db_path: Path = DB_PATH) -> list[dict]:
    """Return failed runs for an ISO date, ordered by run_id."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", business_date):
        raise ValueError("business_date must be YYYY-MM-DD")
    date.fromisoformat(business_date)  # Reject impossible dates.

    with closing(_read_only_connection(db_path)) as connection:
        rows = connection.execute(
            """
            SELECT run_id, business_date, pipeline_name, status
            FROM pipeline_runs
            WHERE business_date = ? AND status = 'FAILED'
            ORDER BY run_id
            """,
            (business_date,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_run_details(run_id: int, db_path: Path = DB_PATH) -> dict | None:
    """Return a run's audit metadata and error, or None if not found."""
    with closing(_read_only_connection(db_path)) as connection:
        row = connection.execute(
            """
            SELECT run_id, business_date, pipeline_name, status, source_system,
                   target_table, input_rows, output_rows, error_message, started_at
            FROM pipeline_runs WHERE run_id = ?
            """,
            (run_id,),
        ).fetchone()
    return dict(row) if row else None
