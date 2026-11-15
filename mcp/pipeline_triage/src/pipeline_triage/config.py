"""Runtime configuration, sourced from the environment.

Only the database is configurable. ``PIPELINE_TRIAGE_DATABASE_DSN`` is a libpq connection
string; anything it omits (host, port, user, password) falls back to the standard
``PG*`` environment variables, so credentials never appear in code or in this repo.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from psycopg.conninfo import conninfo_to_dict

DATABASE_DSN_ENV_VAR = "PIPELINE_TRIAGE_DATABASE_DSN"
DEFAULT_DATABASE_DSN = "dbname=pipeline_triage_demo"


@dataclass(frozen=True, slots=True)
class Settings:
    database_dsn: str

    @classmethod
    def from_env(cls) -> Settings:
        return cls(database_dsn=os.environ.get(DATABASE_DSN_ENV_VAR, DEFAULT_DATABASE_DSN))

    @property
    def database_name(self) -> str:
        return conninfo_to_dict(self.database_dsn).get("dbname") or os.environ.get("PGDATABASE", "")
