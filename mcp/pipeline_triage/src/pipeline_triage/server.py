"""MCP server exposing two read-only pipeline triage tools.

During discovery (``tools/list``) the AI host receives each tool's name, docstring and
input/output JSON schemas, all derived from the signatures below. The docstrings are
therefore written for the model: they say when to use the tool and what to do next.
"""

from datetime import date
from typing import Annotated

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

from pipeline_triage.config import Settings
from pipeline_triage.models import FailedRunsReport, PipelineRun
from pipeline_triage.repository import PipelineRunRepository

SERVER_NAME = "pipeline-triage"
SERVER_INSTRUCTIONS = (
    "Read-only access to ETL pipeline run audit records. To explain failures for a date, "
    "call list_failed_runs, then get_run_details for each run_id it returns."
)

BusinessDate = Annotated[date, Field(description="Business date the runs processed (YYYY-MM-DD).")]
RunId = Annotated[int, Field(description="run_id from list_failed_runs.")]


def build_server(repository: PipelineRunRepository) -> MCPServer:
    server = MCPServer(SERVER_NAME, instructions=SERVER_INSTRUCTIONS)

    @server.tool()
    def list_failed_runs(business_date: BusinessDate) -> FailedRunsReport:
        """List pipeline runs that FAILED for a business date.

        Returns run ids and pipeline names only. Call get_run_details for each run
        to see the error message, source system and target table.
        """
        failed_runs = repository.find_failed_runs(business_date)
        return FailedRunsReport(
            business_date=business_date,
            failed_run_count=len(failed_runs),
            failed_runs=failed_runs,
        )

    @server.tool()
    def get_run_details(run_id: RunId) -> PipelineRun:
        """Get the full audit record of one pipeline run, including its error message."""
        run = repository.get_run(run_id)
        if run is None:
            # ToolError text is returned to the model so it can correct itself;
            # any other exception is reported as an opaque server crash.
            raise ToolError(f"No pipeline run exists with run_id={run_id}.")
        return run

    return server


def main() -> None:
    settings = Settings.from_env()
    build_server(PipelineRunRepository(settings.database_dsn)).run(transport="stdio")


if __name__ == "__main__":
    main()
