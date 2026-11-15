"""PostgreSQL connection settings, read from the environment.

PIPELINE_TRIAGE_DSN is an optional libpq connection string. Anything it leaves out
(host, port, user, password) comes from the standard PG* variables (PGHOST, PGUSER,
PGPASSWORD, ...) or libpq defaults. Credentials never live in code.
"""
from __future__ import annotations

import os

import psycopg
from psycopg.conninfo import conninfo_to_dict
from psycopg.rows import dict_row

DEFAULT_DSN = "dbname=pipeline_triage_demo"


def dsn() -> str:
    return os.environ.get("PIPELINE_TRIAGE_DSN", DEFAULT_DSN)


def database_name() -> str:
    return conninfo_to_dict(dsn()).get("dbname") or os.environ.get("PGDATABASE", "")


def connect_read_only() -> psycopg.Connection:
    """Connection whose transactions are READ ONLY: Postgres itself rejects writes."""
    conn = psycopg.connect(dsn(), row_factory=dict_row, options="-c TimeZone=UTC")
    conn.read_only = True
    return conn
