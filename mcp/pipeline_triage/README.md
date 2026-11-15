# MCP POC 1 — Data Pipeline Triage

Small, hands-on MCP example for a data engineering interview. We use **Python, SQLite and the official MCP Python SDK v2**. It costs no LLM tokens to try the tools in MCP Inspector.

## The problem

An on-call data engineer asks, "Which pipelines failed on November 15, 2026, and why?" Instead of giving an AI direct SQL or credentials, expose a small, read-only set of useful operations.

~~~text
User -> AI host (later) -> MCP client -> MCP server -> SQLite audit DB
                                        |
                                        +-- list_failed_runs(business_date)
                                        +-- get_run_details(run_id)
~~~

The MCP **server does not contain an LLM**; it offers tools. An AI host can discover and call them later. For now, MCP Inspector acts as a test client.

## Step 1 — Install and seed the sample data

From your local clone of agent-forge:

~~~bash
cd mcp/pipeline_triage
uv sync
uv run python init_demo_db.py
~~~

This seeds 4 **fictional** audit records: two failures and one success on 2026-11-15, and one failure on the previous day. It creates a local database that is ignored by Git.

## Step 2 — Run the real MCP server in Inspector

~~~bash
uv run mcp dev server.py
~~~

In the Inspector's **Tools** tab:

1. List the tools. Notice their names, descriptions, and input schemas were derived from the Python functions.
2. Call **list_failed_runs** with business_date set to **2026-11-15**. Expect run IDs **101** and **102**.
3. Call **get_run_details** with run_id set to **101**. Expect a Spark shuffle failure, source, destination and row counts.
4. Call **get_run_details** with run_id set to **102**. Expect a schema mismatch.

No API key, paid LLM, Snowflake connection, or PostgreSQL setup is required.

## Step 3 — Test the database logic separately

~~~bash
uv run python -m unittest discover -s tests -v
~~~

This demonstrates separation of concerns: database access works independently of the MCP protocol.

## What to understand for an interview

- **Host:** a chat or coding app with an LLM (not part of this initial test).
- **Client:** the MCP-speaking component inside the host, or Inspector during this exercise.
- **Server:** server.py, which advertises tools with names, descriptions and schemas.
- **Tool call:** the client invokes a named operation with validated arguments.
- **Data access:** audit_store.py uses parameterized read-only SQLite queries.
- **Where MCP adds value:** different LLM hosts can reuse these tools without hard-coding each database access operation in every host.
- **Trade-off:** a normal API works perfectly if the caller already knows exactly which function to call; MCP helps with AI-driven tool discovery and orchestration, at some complexity and token cost.

## Next exercise

Connect this server to an AI host (such as Claude Desktop or a coding-agent MCP client) and ask: "Which pipelines failed on 2026-11-15, and what evidence explains each failure?" Then replace SQLite with PostgreSQL or Snowflake, add metadata resources and use narrowly scoped service credentials.

**Security:** this is read-only by design. Do not expose arbitrary SQL execution or production credentials in an introductory agent POC.

SDK: https://github.com/modelcontextprotocol/python-sdk
