from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGEngine, PGVectorStore

from rag.docqa.config import (
    EMBEDDING_DIM,
    EMBEDDING_MODEL,
    INDEX_DIR,
    PG_CONNECTION_STRING,
    PG_TABLE_NAME,
    VECTOR_BACKEND,
)
from rag.docqa.loader import load_pdf
from rag.docqa.splitter import split_documents

# Loading this model does a one-time download; reused by every function below
# so we only ever load it once per process, regardless of which backend
# stores the resulting vectors.
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


# ---- FAISS backend: default, stores the index as local files ----

def _build_faiss(chunks: list) -> FAISS:
    # Embedding turns each text chunk into a vector (a list of numbers)
    # positioned so that similar-meaning chunks end up near each other.
    vector_store = FAISS.from_documents(chunks, embedding=embeddings)

    # Save to disk so later steps can search the PDF without re-embedding
    # it every single time — embedding is the slow, repeatable part.
    vector_store.save_local(INDEX_DIR)
    return vector_store


def _load_faiss() -> FAISS:
    # allow_dangerous_deserialization is safe here because we only ever
    # load an index that this same code just wrote.
    return FAISS.load_local(
        INDEX_DIR, embeddings, allow_dangerous_deserialization=True
    )


# ---- PGVector backend: optional, stores the index in your local Postgres ----

def _pg_engine() -> PGEngine:
    return PGEngine.from_connection_string(url=PG_CONNECTION_STRING)


def _build_pgvector(chunks: list) -> PGVectorStore:
    engine = _pg_engine()

    engine.init_vectorstore_table(
        table_name=PG_TABLE_NAME,
        vector_size=EMBEDDING_DIM,
        overwrite_existing=True,
    )

    vector_store = PGVectorStore.create_sync(
        engine=engine, table_name=PG_TABLE_NAME, embedding_service=embeddings
    )

    # Postgres TEXT columns reject NUL bytes outright; some PDFs (this one
    # was produced by calibre) leak stray \x00 bytes during text extraction.
    # FAISS never hits this since it just pickles the string as-is.
    for chunk in chunks:
        chunk.page_content = chunk.page_content.replace("\x00", "")

    vector_store.add_documents(chunks)
    return vector_store


def _load_pgvector() -> PGVectorStore:
    engine = _pg_engine()
    return PGVectorStore.create_sync(
        engine=engine, table_name=PG_TABLE_NAME, embedding_service=embeddings
    )


# ---- Public API — every other module calls only these two functions, so
#      switching VECTOR_BACKEND never requires touching downstream code ----

def build_vectorstore(chunks: list):
    if VECTOR_BACKEND == "pgvector":
        return _build_pgvector(chunks)
    return _build_faiss(chunks)


def load_vectorstore():
    if VECTOR_BACKEND == "pgvector":
        return _load_pgvector()
    return _load_faiss()


if __name__ == "__main__":
    documents = load_pdf()
    chunks = split_documents(documents)
    build_vectorstore(chunks)

    print(
        f"Built a vector index for {len(chunks)} chunk(s) "
        f"using the '{VECTOR_BACKEND}' backend"
    )
