"""The MCP layer: publishes existing Python operations as callable tools.

Start in MCP Inspector: uv run mcp dev server.py
"""
from __future__ import annotations

import json

from mcp.server import MCPServer

from audit_store import get_run_details as query_run_details
from audit_store import list_failed_runs as query_failed_runs

mcp = MCPServer("data-pipeline-triage")


@mcp.tool()
def list_failed_runs(business_date: str) -> str:
    """List failed data pipeline runs for a YYYY-MM-DD business date.

    Returns run IDs, pipeline names and statuses. Read-only.
    """
    return json.dumps(query_failed_runs(business_date), indent=2)


@mcp.tool()
def get_run_details(run_id: int) -> str:
    """Get audit metadata, row counts, source/target and error for one run ID.

    Use a run ID discovered through list_failed_runs. Read-only.
    """
    run = query_run_details(run_id)
    if run is None:
        return json.dumps({"error": f"No pipeline run found for run_id={run_id}"})
    return json.dumps(run, indent=2)
