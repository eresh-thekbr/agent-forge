# agent_poc

A tiny LangGraph proof-of-concept: build a graph-based agent from scratch,
one small concept at a time, ending with the same PDF Q&A agent from
`rag/docqa` — but hand-built with `StateGraph` and given real multi-turn
memory.

## Setup

1. Make sure `ANTHROPIC_API_KEY` is set in your `.env` file.
2. Make sure the FAISS index exists at `data/faiss_index` (built by
   `rag/docqa` — run `uv run python -m rag.docqa.vectorstore` first if it's
   missing).

## The course, one concept at a time

Nine concepts in order. Each one builds on the last, so don't skip — the
later files look like magic until the earlier ones are boring.

**Part A — mechanics.** Pure Python, no API key, runs instantly.

| # | Concept | Run it | Status |
|---|---------|--------|--------|
| 1 | **State** — the shared dict every node reads and writes | `uv run python -m graphs.agent_poc.hello_graph` | done |
| 2 | **Nodes & edges** — chaining, and how updates accumulate | `uv run python -m graphs.agent_poc.sequential_nodes` | done |
| 3 | **Reducers** — the merge-vs-append rule | `uv run python -m graphs.agent_poc.reducers` | done |
| 4 | **Conditional edges** — picking the next node at runtime | `uv run python -m graphs.agent_poc.conditional_routing` | done |
| 5 | **Cycles** — an edge pointing backwards, and `recursion_limit` | `uv run python -m graphs.agent_poc.cycles` | done |
| 6 | **Streaming** — watching each node fire, for debugging | `uv run python -m graphs.agent_poc.streaming` | next |

**Part B — the real agent.** Calls Claude, needs the FAISS index.

| # | Concept | Run it | Status |
|---|---------|--------|--------|
| 7 | **A model inside a node** — `MessagesState` | `uv run python -m graphs.agent_poc.chat_node` | done |
| 8 | **Tools & the agent loop** — `ToolNode`, `tools_condition` | `uv run python -m graphs.agent_poc.agent` | done |
| 9 | **Checkpointer & `thread_id`** — multi-turn memory | `uv run python -m graphs.agent_poc.memory` | done |

Lessons 3, 5 and 6 don't have files yet — they get written when you reach
them. Part B is just Part A applied, with an LLM in the box.

## Chat with memory

Once the FAISS index exists:

```
uv run python -m graphs.agent_poc
```

Ask anything about your document, including follow-up questions that rely
on earlier turns — the checkpointer keeps the whole conversation in
memory. Type `exit` or `quit` to stop.
