from collections.abc import Iterator

import psycopg
import pytest

from pipeline_triage.config import Settings
from pipeline_triage.demo_data import seed_demo_database
from pipeline_triage.repository import PipelineRunRepository


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings.from_env()


@pytest.fixture(scope="session", autouse=True)
def demo_database(settings: Settings) -> Iterator[None]:
    try:
        seed_demo_database(settings)
    except psycopg.OperationalError as error:
        pytest.skip(f"PostgreSQL is not reachable: {error}")
    yield


@pytest.fixture
def repository(settings: Settings) -> PipelineRunRepository:
    return PipelineRunRepository(settings.database_dsn)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
