from dotenv import load_dotenv

# Every other module in this package reads its settings from here,
# so changing a PDF or a model only means editing one file.
load_dotenv()

# Path to the PDF you want to ask questions about.
PDF_PATH = "data/Atomic-Habits.pdf"

# Where the built vector index gets saved, so we don't re-embed every run.
INDEX_DIR = "data/faiss_index"

# Same chat model used across the rest of the agent-forge lessons.
CHAT_MODEL = "claude-haiku-4-5-20251001"

# Same embedding model used in rag/09_vector_store.py and rag/10_retriever_tool.py.
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
