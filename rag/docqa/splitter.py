from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.docqa.loader import load_pdf


def split_documents(documents: list) -> list:
    # A whole page is too big and unfocused to hand an LLM as "context".
    # Splitting into small overlapping chunks means each chunk is one
    # self-contained idea, and the overlap avoids cutting a sentence in half.
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_documents(documents)


if __name__ == "__main__":
    documents = load_pdf()
    chunks = split_documents(documents)

    print(f"Split {len(documents)} page(s) into {len(chunks)} chunk(s)")
    print("\n--- Sample chunk ---")
    print(chunks[0].page_content)
    print("\nmetadata:", chunks[0].metadata)
