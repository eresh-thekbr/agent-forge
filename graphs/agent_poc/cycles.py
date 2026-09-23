from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    count: int


def increment(state: State) -> dict:
    return {"count": state["count"] + 1}


# Router points back to "increment" itself instead of always going
# forward — that's what turns this into a loop instead of a pipeline.
def keep_going(state: State) -> Literal["increment", "__end__"]:
    if state["count"] < 5:
        return "increment"
    return END


graph_builder = StateGraph(State)
graph_builder.add_node("increment", increment)
graph_builder.add_edge(START, "increment")
graph_builder.add_conditional_edges("increment", keep_going)

graph = graph_builder.compile()


if __name__ == "__main__":
    result = graph.invoke({"count": 0})
    print(result)
