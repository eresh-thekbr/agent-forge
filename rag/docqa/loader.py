from langchain_community.document_loaders import PyPDFLoader

from rag.docqa.config import PDF_PATH


def load_pdf() -> list:
    # PyPDFLoader turns a PDF into one LangChain Document per page,
    # each with page_content (the text) and metadata (like page number).
    loader = PyPDFLoader(PDF_PATH)
    return loader.load()


if __name__ == "__main__":
    documents = load_pdf()

    # Just prove the load worked: how many pages, and what's on the first one.
    print(f"Loaded {len(documents)} page(s) from {PDF_PATH}")
    print("\n--- Preview of page 1 ---")
    print(documents[0].page_content[:500])
