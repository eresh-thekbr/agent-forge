"""End-to-end MCP tests: a real MCP client launches server.py over stdio,
discovers its tools, calls them, and checks the answers against PostgreSQL directly.
"""
import sys
from pathlib import Path

import anyio
import psycopg
import pytest
from mcp import Client, StdioServerParameters

from db import dsn
from init_demo_db import seed

SERVER = StdioServerParameters(
    command=sys.executable, args=[str(Path(__file__).parents[1] / "server.py")]
)


@pytest.fixture(scope="module", autouse=True)
def seeded_db():
    seed()


def run(coro_fn):
    return anyio.run(coro_fn)


def test_discovery_lists_exactly_two_tools():
    async def go():
        async with Client(SERVER) as client:
            return (await client.list_tools()).tools

    tools = {t.name: t for t in run(go)}
    assert set(tools) == {"list_failed_runs", "get_run_details"}
    assert tools["list_failed_runs"].input_schema["properties"]["business_date"]["type"] == "string"
    assert tools["get_run_details"].input_schema["properties"]["run_id"]["type"] == "integer"


def test_tool_results_match_postgres():
    async def go():
        async with Client(SERVER) as client:
            failed = await client.call_tool("list_failed_runs", {"business_date": "2026-11-15"})
            detail = await client.call_tool("get_run_details", {"run_id": 101})
            return failed, detail

    failed, detail = run(go)
    assert not failed.is_error and not detail.is_error

    with psycopg.connect(dsn()) as conn:
        expected_ids = [r[0] for r in conn.execute(
            "SELECT run_id FROM pipeline_runs WHERE business_date='2026-11-15' "
            "AND status='FAILED' ORDER BY run_id")]
        expected_error = conn.execute(
            "SELECT error_message FROM pipeline_runs WHERE run_id=101").fetchone()[0]

    assert [r["run_id"] for r in failed.structured_content["result"]] == expected_ids
    assert detail.structured_content["error_message"] == expected_error


def test_expected_errors_reach_the_client():
    async def go():
        async with Client(SERVER) as client:
            bad_date = await client.call_tool("list_failed_runs", {"business_date": "nope"})
            missing = await client.call_tool("get_run_details", {"run_id": 999})
            return bad_date, missing

    bad_date, missing = run(go)
    assert bad_date.is_error and "YYYY-MM-DD" in bad_date.content[0].text
    assert missing.is_error and "run_id=999" in missing.content[0].text
