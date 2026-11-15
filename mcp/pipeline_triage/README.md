# Pipeline Triage: an MCP server for failed-ETL investigation

A read-only [Model Context Protocol](https://modelcontextprotocol.io) server that lets an on-call data engineer ask an AI assistant *"Which pipelines failed on 2026-11-15, and why?"* and get an answer grounded in the pipeline audit table, without giving the assistant database credentials or the ability to run arbitrary SQL.

## The problem

Every morning the on-call data engineer has to answer the same question before downstream consumers (dashboards, finance reports, ML features) notice stale data: **what failed overnight, and why?**

The answer is already in the orchestrator's run-audit table: status, source, target and error message for every job execution. But getting it means switching to a SQL client, remembering the schema, writing the same query again, and then reading each error and classifying it (re-run it, or escalate to the source owner).

Engineers already work alongside AI assistants, so the obvious step is to let the assistant do this lookup. The two naive ways to do that are both unacceptable:

| Option | Why not |
|---|---|
| Give the assistant a database login and let it write SQL | The model gets credentials and unrestricted query power over production data. Result quality depends on the model guessing the schema and the meaning of "failed" correctly every time. |
| Build a bespoke integration for one assistant | Tied to one vendor and rebuilt for every new tool (IDE, chat app, agent framework). |

**This POC solves a narrow version of that problem.** It exposes exactly two purpose-built, read-only operations over the audit table through MCP, an open protocol that any compatible AI host can discover and call. The assistant decides *when* to use them, but it can only ever do *what they allow*.

Scope: failure triage for a single business date. No writes, no remediation and no alerting.

## How it works

![End-to-end flow of one triage question](docs/diagrams/mcp-poc-flow.svg)

1. The engineer asks Claude Code in plain English.
2. At startup Claude Code discovered the server's tools and their schemas. Claude (the LLM) decides to call `list_failed_runs("2026-11-15")`.
3. The MCP client sends a JSON-RPC `tools/call` to this server over stdio. The server queries PostgreSQL in a read-only transaction.
4. The result (runs 202 and 203) gives Claude no cause yet, so **it decides on its own** to call `get_run_details` for each run.
5. Claude explains the failures and classifies them: run 202 is infrastructure (a lost Spark executor, so re-run it) and run 203 is a data-contract break (escalate to the payments producer).

The answer and messages in the diagram come from a real run against the seeded demo data.

<details>
<summary>Background: where MCP's host, client and server sit</summary>

![Generic MCP architecture](docs/diagrams/mcp-concept.svg)

</details>

## Design decisions

| Decision | Rationale |
|---|---|
| **Two narrow tools instead of `run_sql`** | The tool surface *is* the security boundary. Narrow tools also keep domain rules ("failed" means `status = 'FAILED'`) in code instead of in the model's guesswork. |
| **Read-only enforced by PostgreSQL** | Every connection sets `read_only = True`, so writes fail in the database (`ReadOnlySqlTransaction`) even if the code regressed. In production, add a `SELECT`-only role. |
| **Typed contracts end to end** | Tool inputs (`business_date: date`) and outputs (pydantic models) produce the JSON Schemas the model sees during discovery. Invalid input is rejected by schema validation before any SQL runs. |
| **Domain layer independent of MCP** | `PipelineRunRepository` has no MCP imports. The same queries could back a CLI, REST API or scheduled report. `server.py` is a thin adapter. |
| **`build_server(repository)` factory** | Dependency injection: tests drive the real server in-process through an MCP client, and the entry point wires in the production repository. |
| **Errors written for the model** | `ToolError` messages ("No pipeline run exists with run_id=999") reach the model so it can correct itself. Unexpected exceptions are hidden from it, so internals don't leak. |
| **stdio transport** | The host launches the server as a local subprocess: no port, no network exposure, and per-user credentials. Streamable HTTP is the path to a shared team service (see below). |
| **Configuration from the environment** | Uses a libpq DSN plus the standard `PG*` variables. No credentials in code, and the LLM never sees them. |

## Project layout

```
mcp/pipeline_triage/
├── src/pipeline_triage/
│   ├── server.py          # MCP adapter: tool definitions + entry point
│   ├── repository.py      # PipelineRunRepository: parameterized, read-only queries
│   ├── models.py          # Pydantic domain models (also the tools' output schemas)
│   ├── config.py          # Settings from environment
│   ├── demo_data.py       # Guarded demo seeder (only *_demo databases)
│   └── sql/               # schema.sql, seed_demo_data.sql
├── tests/                 # repository tests + MCP protocol tests (in-process and stdio)
└── docs/diagrams/         # animated SVGs above
```

## Running locally

Requires Python 3.11+, [uv](https://docs.astral.sh/uv/) and a reachable PostgreSQL (tested on 14).

```bash
cd mcp/pipeline_triage
uv sync
uv run pipeline-triage-seed-demo        # creates pipeline_triage_demo with 7 synthetic runs
uv run pytest                           # 14 tests
```

**Connect it to Claude Code:**

```bash
claude mcp add --scope local pipeline-triage -- \
    uv run --directory "$PWD" pipeline-triage-server
```

Then ask: *"Which pipelines failed on November 15, 2026, and why?"*

**Inspect it without an AI:**

```bash
npx @modelcontextprotocol/inspector uv run --directory "$PWD" pipeline-triage-server
```

Configuration: `PIPELINE_TRIAGE_DATABASE_DSN` (default `dbname=pipeline_triage_demo`). See `.env.example`.

## Verification

| Layer | How it was verified |
|---|---|
| Repository | Tests against real PostgreSQL: date filtering, the full audit record, unknown ids, rejected writes, seeder refusing non-demo databases |
| MCP contract | An MCP client checks that discovery lists exactly two tools with typed schemas, that results match direct SQL, that invalid dates and injection strings are rejected before the database, and that the installed entry point works over stdio |
| Protocol tooling | MCP Inspector CLI: `tools/list` and `tools/call` output compared with `psql` |
| AI host | Live Claude Code session: the model chained `list_failed_runs`, then `get_run_details` ×2, and produced the answer shown in the diagram |
| Code quality | `ruff check` and `ruff format` both pass |

## Path to production

- **Identity:** a dedicated `SELECT`-only role on the audit schema or a read replica, with credentials from a secrets manager.
- **Transport:** Streamable HTTP behind OAuth, so a whole team shares one governed server instead of local processes.
- **Observability:** structured logs of every tool call (who, which tool, arguments, latency) for audit.
- **Scale:** pagination and a date-range limit on `list_failed_runs`. Add a connection pool once traffic justifies it.
- **Next capabilities:** run history per pipeline (to tell a regression from a known flaky job), owner/runbook lookup, and only then any write action such as triggering a rerun, behind explicit human approval.

## Built with AI

This POC was built with Claude Code as an implementation partner. The problem framing, scope and constraints were set up front: read-only access, no arbitrary SQL, PostgreSQL, isolation from the rest of the repo, and verification at every layer. The output was then reviewed and iterated on. Every claim in this README is backed by the tests or by the live Claude Code run described above.
