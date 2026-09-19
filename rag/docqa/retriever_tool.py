from langchain_core.tools import create_retriever_tool

from rag.docqa.vectorstore import load_vectorstore


def get_retriever_tool():
    vector_store = load_vectorstore()

    # k=3 means "give me the 3 most relevant chunks" — enough context
    # for an answer without overwhelming the model with noise.
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # Wrapping the retriever as a tool is what lets an agent decide
    # *when* to search the document, instead of us forcing it every time.
    return create_retriever_tool(
        retriever,
        name="search_document",
        description="Search the uploaded PDF for information relevant to the user's question.",
    )


if __name__ == "__main__":
    tool = get_retriever_tool()

    # .invoke() runs the tool directly, the same way an agent would call it.
    sample_query = "What is this document about?"
    result = tool.invoke(sample_query)

    print(f"--- Chunks retrieved for: {sample_query!r} ---")
    print(result)
