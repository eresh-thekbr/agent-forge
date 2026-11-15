"""Create and seed the local SQLite database with fake audit records."""
from __future__ import annotations

from pathlib import Path
import sqlite3

from audit_store import DB_PATH

RUNS = [
    (101, "2026-11-15", "customer_master_daily", "FAILED",
     "s3://demo/customer_raw", "curated.customer_master", 1500000, 0,
     "Spark shuffle fetch failed: missing output location", "2026-11-15T07:10:00Z"),
    (102, "2026-11-15", "payments_ingest", "FAILED",
     "kafka://demo/payments", "bronze.payments", 80000, 0,
     "Schema mismatch: amount expected DECIMAL, received STRING", "2026-11-15T07:15:00Z"),
    (103, "2026-11-15", "orders_daily", "SUCCESS",
     "s3://demo/orders", "curated.orders", 500000, 499998,
     None, "2026-11-15T07:00:00Z"),
    (104, "2026-11-14", "inventory_sync", "FAILED",
     "postgres://demo/inventory", "curated.inventory", 34000, 0,
     "Source connection timeout", "2026-11-14T06:30:00Z"),
]


def create_demo_db(db_path: Path = DB_PATH) -> None:
    """Reset this dedicated demo database to a known, repeatable state."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id INTEGER PRIMARY KEY,
                business_date TEXT NOT NULL,
                pipeline_name TEXT NOT NULL,
                status TEXT NOT NULL,
                source_system TEXT NOT NULL,
                target_table TEXT NOT NULL,
                input_rows INTEGER NOT NULL,
                output_rows INTEGER NOT NULL,
                error_message TEXT,
                started_at TEXT NOT NULL
            )
            """
        )
        connection.execute("DELETE FROM pipeline_runs")
        connection.executemany(
            """
            INSERT INTO pipeline_runs
            (run_id, business_date, pipeline_name, status, source_system,
             target_table, input_rows, output_rows, error_message, started_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            RUNS,
        )


if __name__ == "__main__":
    create_demo_db()
    print(f"Seeded {len(RUNS)} demo pipeline runs in {DB_PATH}")
