"""Create the demo database and load synthetic pipeline runs.

Guarded to databases whose name ends in ``_demo`` so it can never truncate real data.
Run with: ``uv run pipeline-triage-seed-demo``
"""

from __future__ import annotations

from importlib.resources import files

import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo

from pipeline_triage.config import Settings

DEMO_DATABASE_SUFFIX = "_demo"
MAINTENANCE_DATABASE = "postgres"


class UnsafeSeedTargetError(RuntimeError):
    pass


def seed_demo_database(settings: Settings) -> int:
    """(Re)create the schema and demo rows; returns the number of runs loaded."""
    database_name = settings.database_name
    if not database_name.endswith(DEMO_DATABASE_SUFFIX):
        raise UnsafeSeedTargetError(
            f"Refusing to seed {database_name!r}: name must end in {DEMO_DATABASE_SUFFIX!r}."
        )
    _create_database_if_missing(settings.database_dsn, database_name)

    with psycopg.connect(settings.database_dsn) as connection:  # single transaction
        connection.execute("DROP TABLE IF EXISTS pipeline_runs")
        connection.execute(_read_sql("schema.sql"))
        connection.execute(_read_sql("seed_demo_data.sql"))
        (run_count,) = connection.execute("SELECT count(*) FROM pipeline_runs").fetchone()
    return run_count


def _create_database_if_missing(dsn: str, database_name: str) -> None:
    # CREATE DATABASE cannot run inside a transaction, hence autocommit on the
    # maintenance database. Existing databases are never dropped or altered.
    maintenance_dsn = make_conninfo(dsn, dbname=MAINTENANCE_DATABASE)
    with psycopg.connect(maintenance_dsn, autocommit=True) as connection:
        exists = connection.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (database_name,)
        ).fetchone()
        if not exists:
            connection.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))


def _read_sql(filename: str) -> str:
    return (files("pipeline_triage") / "sql" / filename).read_text(encoding="utf-8")


def main() -> None:
    settings = Settings.from_env()
    run_count = seed_demo_database(settings)
    print(f"Loaded {run_count} demo pipeline runs into {settings.database_name!r}.")


if __name__ == "__main__":
    main()
