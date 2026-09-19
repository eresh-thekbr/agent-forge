from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from graphs.agent_poc.config import MODEL_NAME
from rag.docqa.retriever_tool import get_retriever_tool

# Reusing the exact tool built in rag/docqa instead of a toy one — this is
# the same "search_document" tool, just wired into a hand-built graph.
search_document = get_retriever_tool()

# bind_tools() is what create_agent does under the hood: it tells the model
# which tools exist so it can ask to call one instead of answering directly.
model = init_chat_model(MODEL_NAME).bind_tools([search_document])


def chatbot(state: MessagesState) -> dict:
    reply = model.invoke(state["messages"])
    return {"messages": [reply]}


# Returning the builder (not a compiled graph) lets memory.py reuse this
# exact graph shape and compile it again with a checkpointer attached.
def build_workflow() -> StateGraph:
    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node("chatbot", chatbot)

    # This node MUST be named "tools" — tools_condition below returns that
    # exact string when the model has asked to call a tool.
    graph_builder.add_node("tools", ToolNode([search_document]))

    graph_builder.add_edge(START, "chatbot")

    # tools_condition is the same conditional-edge idea from
    # conditional_routing.py, pre-written for one check: "did the model
    # just ask to call a tool?" Yes -> "tools", no -> END.
    graph_builder.add_conditional_edges("chatbot", tools_condition)

    # After the tool runs, send its result back to the model so it can
    # turn raw search results into an actual answer.
    graph_builder.add_edge("tools", "chatbot")

    return graph_builder


graph = build_workflow().compile()


if __name__ == "__main__":
    question = "What is this document about?"
    result = graph.invoke({"messages": [{"role": "user", "content": question}]})
    print(f"Q: {question}")
    print(f"A: {result['messages'][-1].content}")
