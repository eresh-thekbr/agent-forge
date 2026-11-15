"""Read-only queries over synthetic pipeline audit records.

Plain Python + SQL, with no MCP here. server.py exposes these functions as MCP tools.
"""
from __future__ import annotations

from datetime import date, datetime

from db import connect_read_only


def _jsonable(row: dict) -> dict:
    """Dates and timestamps become ISO strings so the row serializes to JSON."""
    return {k: v.isoformat() if isinstance(v, (date, datetime)) else v for k, v in row.items()}


def list_failed_runs(business_date: str) -> list[dict]:
    """Failed runs for one YYYY-MM-DD business date, ordered by run_id."""
    day = date.fromisoformat(business_date)  # ValueError for bad input, before any SQL
    with connect_read_only() as conn:
        rows = conn.execute(
            """
            SELECT run_id, pipeline_name, business_date, status
            FROM pipeline_runs
            WHERE business_date = %s AND status = 'FAILED'
            ORDER BY run_id
            """,
            (day,),  # parameterized: the value never becomes SQL text
        ).fetchall()
    return [_jsonable(r) for r in rows]


def get_run_details(run_id: int) -> dict | None:
    """All audit columns for one run, or None if the run_id does not exist."""
    with connect_read_only() as conn:
        row = conn.execute(
            """
            SELECT run_id, pipeline_name, business_date, status, source_system,
                   target_table, error_message, started_at
            FROM pipeline_runs
            WHERE run_id = %s
            """,
            (run_id,),
        ).fetchone()
    return _jsonable(row) if row else None
