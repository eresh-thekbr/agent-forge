from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, MessagesState, StateGraph

from graphs.agent_poc.config import MODEL_NAME

# One model instance shared by every invoke — creating it fresh per call
# would be slow and pointless (same reasoning as rag/docqa/vectorstore.py).
model = init_chat_model(MODEL_NAME)


# MessagesState is a prebuilt state with one field, "messages", that
# already knows how to append new messages instead of overwriting them.
def chatbot(state: MessagesState) -> dict:
    reply = model.invoke(state["messages"])
    return {"messages": [reply]}


graph_builder = StateGraph(MessagesState)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()


if __name__ == "__main__":
    question = "Say hi in one short sentence."
    result = graph.invoke({"messages": [{"role": "user", "content": question}]})
    print(result["messages"])
    print(result["messages"][-1].content)
