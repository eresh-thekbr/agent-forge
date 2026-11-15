from datetime import UTC, date, datetime

import psycopg
import pytest

from pipeline_triage.config import Settings
from pipeline_triage.demo_data import UnsafeSeedTargetError, seed_demo_database
from pipeline_triage.models import RunStatus
from pipeline_triage.repository import PipelineRunRepository, open_read_only_connection


def test_find_failed_runs_returns_only_failures_for_the_requested_date(
    repository: PipelineRunRepository,
) -> None:
    failed_runs = repository.find_failed_runs(date(2026, 11, 15))

    assert [run.run_id for run in failed_runs] == [202, 203]
    assert {run.business_date for run in failed_runs} == {date(2026, 11, 15)}


def test_find_failed_runs_returns_empty_list_for_a_clean_day(
    repository: PipelineRunRepository,
) -> None:
    assert repository.find_failed_runs(date(2026, 11, 1)) == []


def test_get_run_returns_the_full_audit_record(repository: PipelineRunRepository) -> None:
    run = repository.get_run(203)

    assert run is not None
    assert run.status is RunStatus.FAILED
    assert run.target_table == "bronze.payments"
    assert "Schema mismatch" in run.error_message
    assert run.started_at == datetime(2026, 11, 15, 7, 15, tzinfo=UTC)


def test_get_run_returns_none_for_an_unknown_run_id(repository: PipelineRunRepository) -> None:
    assert repository.get_run(999) is None


def test_connections_reject_writes(settings: Settings) -> None:
    with (
        open_read_only_connection(settings.database_dsn) as connection,
        pytest.raises(psycopg.errors.ReadOnlySqlTransaction),
    ):
        connection.execute("DELETE FROM pipeline_runs")


def test_seeding_refuses_databases_not_named_as_demo() -> None:
    with pytest.raises(UnsafeSeedTargetError):
        seed_demo_database(Settings(database_dsn="dbname=analytics_prod"))
