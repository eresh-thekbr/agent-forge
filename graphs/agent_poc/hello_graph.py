from typing import TypedDict

from langgraph.graph import END, START, StateGraph


# State is the shape of data passed between nodes — every node reads from
# it and returns a partial update that gets merged back in.
class State(TypedDict):
    name: str
    greeting: str


# A node is just a plain function: state in, partial state update out.
def say_hello(state: State) -> dict:
    return {"greeting": f"Hello, {state['name']}!"}


# Wiring START -> say_hello -> END is the smallest possible graph.
graph_builder = StateGraph(State)
graph_builder.add_node("say_hello", say_hello)
graph_builder.add_edge(START, "say_hello")
graph_builder.add_edge("say_hello", END)

# Compiling turns the builder into something you can actually run.
graph = graph_builder.compile()


if __name__ == "__main__":
    # invoke() runs the whole graph once, start to finish, on this input.
    result = graph.invoke({"name": "Eresh"})
    print(result["greeting"])
