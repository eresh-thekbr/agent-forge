from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    name: str
    mood: str
    greeting: str


def formal_greeting(state: State) -> dict:
    return {"greeting": f"Good day, {state['name']}."}


def casual_greeting(state: State) -> dict:
    return {"greeting": f"Hey {state['name']}!"}


# A router function doesn't touch state — it just inspects it and returns
# the name of whichever node should run next.
def route_by_mood(state: State) -> Literal["formal_greeting", "casual_greeting"]:
    if state["mood"] == "formal":
        return "formal_greeting"
    return "casual_greeting"


graph_builder = StateGraph(State)
graph_builder.add_node("formal_greeting", formal_greeting)
graph_builder.add_node("casual_greeting", casual_greeting)

# add_conditional_edges is what turns this into a real graph instead of a
# straight line: the router picks the branch at invoke time, not up front.
graph_builder.add_conditional_edges(START, route_by_mood)
graph_builder.add_edge("formal_greeting", END)
graph_builder.add_edge("casual_greeting", END)

graph = graph_builder.compile()


if __name__ == "__main__":
    # Same graph, two different paths through it.
    for mood in ("formal", "casual"):
        result = graph.invoke({"name": "Eresh", "mood": mood})
        print(f"[{mood}] {result['greeting']}")
