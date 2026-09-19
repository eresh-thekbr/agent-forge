# docqa

A tiny RAG (Retrieval-Augmented Generation) proof-of-concept: ask questions
about your own PDF and get answers grounded in its actual content.

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

## Chat with your PDF

Once the index is built (step 3 has run at least once):

```
uv run python -m rag.docqa
```

Ask anything about your document; type `exit` or `quit` to stop.
