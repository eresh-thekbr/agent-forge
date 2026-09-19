from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    name: str
    greeting: str


# First node builds the base greeting...
def build_greeting(state: State) -> dict:
    return {"greeting": f"Hello, {state['name']}"}


# ...the second node only adds to what's already in state — this is the
# point of a pipeline: each node does one small job and hands off.
def add_emphasis(state: State) -> dict:
    return {"greeting": f"{state['greeting']}!!!"}


graph_builder = StateGraph(State)
graph_builder.add_node("build_greeting", build_greeting)
graph_builder.add_node("add_emphasis", add_emphasis)

# Two edges instead of one: state now flows through both nodes in order.
graph_builder.add_edge(START, "build_greeting")
graph_builder.add_edge("build_greeting", "add_emphasis")
graph_builder.add_edge("add_emphasis", END)

graph = graph_builder.compile()


if __name__ == "__main__":
    result = graph.invoke({"name": "Eresh"})
    print(result["greeting"])
