"""Read-only data access for the ``pipeline_runs`` audit table.

Knows nothing about MCP: the same repository could back a CLI, a REST API or a job.
"""

from __future__ import annotations

from datetime import date

import psycopg
from psycopg.rows import class_row

from pipeline_triage.models import FailedRunSummary, PipelineRun, RunStatus

_FAILED_RUNS_FOR_BUSINESS_DATE = """
    SELECT run_id, pipeline_name, business_date, started_at
    FROM pipeline_runs
    WHERE business_date = %(business_date)s
      AND status = %(status)s
    ORDER BY started_at, run_id
"""

_RUN_BY_ID = """
    SELECT run_id, pipeline_name, business_date, status, source_system,
           target_table, error_message, started_at
    FROM pipeline_runs
    WHERE run_id = %(run_id)s
"""


def open_read_only_connection(dsn: str) -> psycopg.Connection:
    """Every transaction is READ ONLY and timestamps come back in UTC.

    Read-only is enforced by PostgreSQL itself, not by convention in this code.
    """
    connection = psycopg.connect(dsn, options="-c TimeZone=UTC")
    connection.read_only = True
    return connection


class PipelineRunRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def find_failed_runs(self, business_date: date) -> list[FailedRunSummary]:
        with (
            open_read_only_connection(self._dsn) as connection,
            connection.cursor(row_factory=class_row(FailedRunSummary)) as cursor,
        ):
            cursor.execute(
                _FAILED_RUNS_FOR_BUSINESS_DATE,
                {"business_date": business_date, "status": RunStatus.FAILED.value},
            )
            return cursor.fetchall()

    def get_run(self, run_id: int) -> PipelineRun | None:
        with (
            open_read_only_connection(self._dsn) as connection,
            connection.cursor(row_factory=class_row(PipelineRun)) as cursor,
        ):
            cursor.execute(_RUN_BY_ID, {"run_id": run_id})
            return cursor.fetchone()
