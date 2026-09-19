from langchain.agents import create_agent

from rag.docqa.config import CHAT_MODEL
from rag.docqa.retriever_tool import get_retriever_tool


def build_agent():
    retriever_tool = get_retriever_tool()

    # This is the "RAG" part: the agent is told to retrieve before
    # answering, and to admit when the document doesn't have the answer
    # instead of guessing — that's what keeps it grounded.
    return create_agent(
        model=CHAT_MODEL,
        tools=[retriever_tool],
        system_prompt=(
            "You are a helpful assistant that answers questions about an uploaded "
            "document. Always use the search_document tool first to find relevant "
            "context before answering. If the document does not contain the answer, "
            "say so honestly instead of guessing."
        ),
    )


def ask(agent, question: str) -> str:
    response = agent.invoke({"messages": [{"role": "user", "content": question}]})
    return response["messages"][-1].content


if __name__ == "__main__":
    agent = build_agent()

    sample_question = "What is this document about?"
    answer = ask(agent, sample_question)

    print(f"Q: {sample_question}")
    print(f"A: {answer}")
