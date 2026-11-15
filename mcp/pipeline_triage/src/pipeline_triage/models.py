"""Domain models returned by the MCP tools.

These are published to the AI host as each tool's output schema, so field descriptions
double as documentation the model reads before deciding how to use a result.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class RunStatus(StrEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RUNNING = "RUNNING"


class FailedRunSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: int = Field(description="Pass to get_run_details for the failure cause.")
    pipeline_name: str
    business_date: date
    started_at: datetime


class FailedRunsReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    business_date: date
    failed_run_count: int
    failed_runs: list[FailedRunSummary]


class PipelineRun(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: int
    pipeline_name: str
    business_date: date
    status: RunStatus
    source_system: str = Field(description="Where the job reads from.")
    target_table: str = Field(description="Where the job writes to.")
    error_message: str | None = Field(description="Error raised by the job; null if it succeeded.")
    started_at: datetime
