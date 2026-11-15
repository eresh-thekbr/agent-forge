"""Create the dedicated demo database and (re)seed it with fake audit records.

Only touches the database named in PIPELINE_TRIAGE_DSN (default: pipeline_triage_demo),
and refuses to run unless that name ends in "_demo".

    uv run python init_demo_db.py
"""
from __future__ import annotations

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from db import database_name, dsn

RUNS = [
    # run_id, pipeline_name, business_date, status, source_system, target_table, error_message, started_at
    (101, "customer_master_daily", "2026-11-15", "FAILED", "s3://demo/customer_raw",
     "curated.customer_master", "Spark shuffle fetch failed: missing output location for shuffle 3",
     "2026-11-15 07:10:00+00"),
    (102, "payments_ingest", "2026-11-15", "FAILED", "kafka://demo/payments",
     "bronze.payments", "Schema mismatch: column amount expected DECIMAL(18,2), received STRING",
     "2026-11-15 07:15:00+00"),
    (103, "orders_daily", "2026-11-15", "SUCCESS", "s3://demo/orders",
     "curated.orders", None, "2026-11-15 07:00:00+00"),
    (104, "fx_rates_hourly", "2026-11-15", "SUCCESS", "https://demo/fx-api",
     "bronze.fx_rates", None, "2026-11-15 08:00:00+00"),
    (105, "inventory_sync", "2026-11-14", "FAILED", "postgres://demo/inventory",
     "curated.inventory", "Source connection timeout after 300s", "2026-11-14 06:30:00+00"),
]

DDL = """
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id        INTEGER PRIMARY KEY,
    pipeline_name TEXT        NOT NULL,
    business_date DATE        NOT NULL,
    status        TEXT        NOT NULL CHECK (status IN ('SUCCESS', 'FAILED', 'RUNNING')),
    source_system TEXT        NOT NULL,
    target_table  TEXT        NOT NULL,
    error_message TEXT,
    started_at    TIMESTAMPTZ NOT NULL
)
"""


def create_database_if_missing(name: str) -> None:
    # CREATE DATABASE can't run inside a transaction, so connect to the
    # maintenance DB with autocommit. Existing databases are never dropped.
    admin = make_conninfo(dsn(), dbname="postgres")
    with psycopg.connect(admin, autocommit=True) as conn:
        exists = conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,)).fetchone()
        if not exists:
            conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))


def seed() -> None:
    name = database_name()
    if not name.endswith("_demo"):
        raise SystemExit(f"Refusing to seed '{name}': demo database names must end in _demo")
    create_database_if_missing(name)
    with psycopg.connect(dsn()) as conn:  # one transaction: all rows or none
        conn.execute(DDL)
        conn.execute("TRUNCATE pipeline_runs")
        conn.cursor().executemany(
            "INSERT INTO pipeline_runs VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", RUNS
        )
    print(f"Seeded {len(RUNS)} demo runs into database '{name}'")


if __name__ == "__main__":
    seed()
