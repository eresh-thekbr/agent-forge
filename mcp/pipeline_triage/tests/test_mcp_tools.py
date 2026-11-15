"""Exercise the tools through a real MCP client, the same protocol an AI host uses."""

import sys

import psycopg
import pytest
from mcp import Client, StdioServerParameters

from pipeline_triage.config import Settings
from pipeline_triage.repository import PipelineRunRepository
from pipeline_triage.server import build_server

pytestmark = pytest.mark.anyio


@pytest.fixture
def server(repository: PipelineRunRepository):
    return build_server(repository)


async def test_discovery_advertises_exactly_two_typed_tools(server) -> None:
    async with Client(server) as client:
        tools = {tool.name: tool for tool in (await client.list_tools()).tools}

    assert set(tools) == {"list_failed_runs", "get_run_details"}
    date_param = tools["list_failed_runs"].input_schema["properties"]["business_date"]
    assert date_param["format"] == "date"
    assert tools["get_run_details"].input_schema["properties"]["run_id"]["type"] == "integer"
    assert "error_message" in tools["get_run_details"].output_schema["properties"]


async def test_list_failed_runs_matches_the_audit_table(server, settings: Settings) -> None:
    async with Client(server) as client:
        result = await client.call_tool("list_failed_runs", {"business_date": "2026-11-15"})

    with psycopg.connect(settings.database_dsn) as connection:
        expected_run_ids = [
            run_id
            for (run_id,) in connection.execute(
                "SELECT run_id FROM pipeline_runs "
                "WHERE business_date = '2026-11-15' AND status = 'FAILED' ORDER BY run_id"
            )
        ]

    assert not result.is_error
    report = result.structured_content
    assert report["failed_run_count"] == len(expected_run_ids)
    assert [run["run_id"] for run in report["failed_runs"]] == expected_run_ids


async def test_get_run_details_returns_the_failure_cause(server) -> None:
    async with Client(server) as client:
        result = await client.call_tool("get_run_details", {"run_id": 202})

    assert not result.is_error
    assert result.structured_content["error_message"].startswith("Spark shuffle fetch failed")


@pytest.mark.parametrize("invalid_date", ["2026-13-01", "15/11/2026", "'; DROP TABLE x;--"])
async def test_invalid_business_date_is_rejected_before_reaching_the_database(
    server, invalid_date: str
) -> None:
    async with Client(server) as client:
        result = await client.call_tool("list_failed_runs", {"business_date": invalid_date})

    assert result.is_error
    assert "business_date" in result.content[0].text


async def test_unknown_run_id_returns_an_actionable_error(server) -> None:
    async with Client(server) as client:
        result = await client.call_tool("get_run_details", {"run_id": 999})

    assert result.is_error
    assert "run_id=999" in result.content[0].text


async def test_installed_entry_point_serves_tools_over_stdio() -> None:
    process = StdioServerParameters(command=sys.executable, args=["-m", "pipeline_triage"])
    async with Client(process) as client:
        result = await client.call_tool("list_failed_runs", {"business_date": "2026-11-15"})

    assert result.structured_content["failed_run_count"] == 2
