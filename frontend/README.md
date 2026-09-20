# frontend

Ways to actually talk to the `docqa` RAG backend (see
[`rag/docqa/README.md`](../rag/docqa/README.md) for building the index
first). This package only *consumes* `rag.docqa.agent` — it has no RAG
pipeline logic of its own, so any interface added here can be swapped out
without touching ingestion, embedding, or retrieval code.

## Terminal chat

```
uv run python -m frontend
```

Ask anything about your document; type `exit` or `quit` to stop.

## Browser chat UI

```
uv run streamlit run frontend/ui.py
```

Note the different run form — Streamlit apps use `streamlit run <file>`,
not `python -m`. It opens automatically at `http://localhost:8501`.
