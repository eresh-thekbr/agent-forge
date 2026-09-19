### agent-forge. It covers all four topics honestly since LangChain, RAG, MCP, and LangGraph are all agent plumbing.


```
mkdir agent-forge
cd agent-forge
uv init
uv add langchain langchain-anthropic python-dotenv
mkdir core chains rag graphs mcp data
touch core/__init__.py
```

### How to run modules 
```
uv run python -m rag.docqa.loader
uv run python -m rag.docqa.splitter
uv run python -m rag.docqa.vectorstore
uv run python -m rag.docqa.retriever_tool
uv run python -m rag.docqa.agent
uv run python -m rag.docqa          # interactive chat
```