"""The MCP layer: publishes two read-only audit queries as MCP tools.

The function names, docstrings and type hints below become what the client sees
during discovery (tools/list): tool name, description and JSON input schema.

    uv run mcp dev server.py      # open in MCP Inspector
    uv run python server.py       # stdio server (what Claude Code launches)
"""
from __future__ import annotations

from typing import TypedDict

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

import audit_store

mcp = MCPServer(
    "pipeline-triage",
    instructions="Read-only access to ETL pipeline audit records in PostgreSQL. "
    "Use list_failed_runs to find failures for a date, then get_run_details for the cause.",
)


class RunDetails(TypedDict):
    """Typed return value -> the SDK advertises it as the tool's output schema."""

    run_id: int
    pipeline_name: str
    business_date: str
    status: str
    source_system: str
    target_table: str
    error_message: str | None
    started_at: str


@mcp.tool()
def list_failed_runs(business_date: str) -> list[dict]:
    """List FAILED pipeline runs for a business date given as YYYY-MM-DD.

    Returns run_id, pipeline_name, business_date and status (no error text).
    Call get_run_details with a run_id to see why it failed. Read-only.
    """
    try:
        return audit_store.list_failed_runs(business_date)
    except ValueError:
        # ToolError text is sent to the AI; other exceptions are hidden as crashes.
        raise ToolError(f"business_date must be YYYY-MM-DD, got {business_date!r}")


@mcp.tool()
def get_run_details(run_id: int) -> RunDetails:
    """Get the full audit record for one pipeline run: source system, target table,
    start time and error_message. Read-only.
    """
    run = audit_store.get_run_details(run_id)
    if run is None:
        raise ToolError(f"No pipeline run found for run_id={run_id}")
    return run


if __name__ == "__main__":
    mcp.run()  # stdio transport: JSON-RPC messages over stdin/stdout
