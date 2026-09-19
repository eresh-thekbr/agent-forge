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

## Run it, one tiny step at a time

Each module below builds on the last. Run them in this order the first
time to see how the graph comes together:

```
uv run python -m graphs.agent_poc.hello_graph          # 1. State, one node, compile, invoke
uv run python -m graphs.agent_poc.sequential_nodes      # 2. two nodes chained into a pipeline
uv run python -m graphs.agent_poc.conditional_routing   # 3. branching with add_conditional_edges
uv run python -m graphs.agent_poc.chat_node             # 4. a node that calls a real Claude model
uv run python -m graphs.agent_poc.agent                 # 5. a tool-calling agent loop over your PDF
uv run python -m graphs.agent_poc.memory                # 6. the same agent, remembering across turns
```

## Chat with memory

Once the FAISS index exists:

```
uv run python -m graphs.agent_poc
```

Ask anything about your document, including follow-up questions that rely
on earlier turns — the checkpointer keeps the whole conversation in
memory. Type `exit` or `quit` to stop.
