from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from rag.docqa.config import EMBEDDING_MODEL, INDEX_DIR
from rag.docqa.loader import load_pdf
from rag.docqa.splitter import split_documents

# Loading this model does a one-time download; reused by every function below
# so we only ever load it once per process.
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def build_vectorstore(chunks: list) -> FAISS:
    # Embedding turns each text chunk into a vector (a list of numbers)
    # positioned so that similar-meaning chunks end up near each other.
    vector_store = FAISS.from_documents(chunks, embedding=embeddings)

    # Save to disk so later steps can search the PDF without re-embedding
    # it every single time — embedding is the slow, repeatable part.
    vector_store.save_local(INDEX_DIR)
    return vector_store


def load_vectorstore() -> FAISS:
    # allow_dangerous_deserialization is safe here because we only ever
    # load an index that this same code just wrote.
    return FAISS.load_local(
        INDEX_DIR, embeddings, allow_dangerous_deserialization=True
    )


if __name__ == "__main__":
    documents = load_pdf()
    chunks = split_documents(documents)
    build_vectorstore(chunks)

    print(f"Built and saved a vector index for {len(chunks)} chunk(s) to '{INDEX_DIR}'")
