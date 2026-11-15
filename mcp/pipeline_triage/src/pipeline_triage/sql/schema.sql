-- Audit trail written by the orchestrator: one row per ETL job execution.
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id         INTEGER     PRIMARY KEY,
    pipeline_name  TEXT        NOT NULL,
    business_date  DATE        NOT NULL,
    status         TEXT        NOT NULL CHECK (status IN ('SUCCESS', 'FAILED', 'RUNNING')),
    source_system  TEXT        NOT NULL,
    target_table   TEXT        NOT NULL,
    error_message  TEXT,
    started_at     TIMESTAMPTZ NOT NULL,
    CONSTRAINT failed_runs_have_error CHECK (status <> 'FAILED' OR error_message IS NOT NULL)
);

-- Serves the triage access path: failures for one business date.
CREATE INDEX IF NOT EXISTS pipeline_runs_business_date_status_idx
    ON pipeline_runs (business_date, status);
