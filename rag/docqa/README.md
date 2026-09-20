# docqa

A tiny RAG (Retrieval-Augmented Generation) backend: loads a PDF, chunks it,
embeds it into a searchable vector index, and answers questions grounded in
its actual content. This package is UI-agnostic — it has no terminal or
browser code of its own. For ways to actually talk to it, see
[`frontend/README.md`](../../frontend/README.md).

## Setup

1. Save a PDF as `data/document.pdf` (relative to the repo root).
2. Make sure `ANTHROPIC_API_KEY` is set in your `.env` file.

## Run it, one tiny step at a time

Each module below builds on the last. Run them in this order the first time
to see how the pipeline comes together:

```
uv run python -m rag.docqa.loader           # 1. load the PDF into text
uv run python -m rag.docqa.splitter         # 2. split the text into small chunks
uv run python -m rag.docqa.vectorstore      # 3. embed the chunks + save a searchable index
uv run python -m rag.docqa.retriever_tool   # 4. search the index for relevant chunks
uv run python -m rag.docqa.agent            # 5. ask one question, get a grounded answer
```

Once the index is built (step 3 has run at least once), see
[`frontend/README.md`](../../frontend/README.md) for the terminal chat and
browser UI that actually let you talk to it.

## Optional: use Postgres instead of FAISS

By default the vector index is saved to local files via FAISS — no extra
setup needed. If you'd rather store it in your own local Postgres (using
the `pgvector` extension), you can opt in without changing any code:

1. Make sure the `pgvector` extension is installed on your local Postgres
   server (this is a one-time install on the server itself, e.g. via
   `brew install pgvector` — enabling it *inside* a database happens
   automatically the first time you build the index).
2. Add to your `.env` file:
   ```
   VECTOR_BACKEND=pgvector
   PG_CONNECTION_STRING=postgresql+psycopg://<user>:<password>@localhost:5432/<dbname>
   ```
   (defaults to `postgresql+psycopg://postgres:postgres@localhost:5432/postgres`
   if you don't set one).
3. Run the pipeline exactly as above — `vectorstore.py`, `retriever_tool.py`,
   `agent.py`, and the chat loop all work unchanged, just backed by a
   `docqa_chunks` table in Postgres instead of `data/faiss_index/`.

Remove or unset `VECTOR_BACKEND` to switch back to FAISS at any time.
