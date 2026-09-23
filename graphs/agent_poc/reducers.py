import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


# No Annotated -> the default reducer is REPLACE. Whatever a node returns
# for this key overwrites what was there, same as every lesson so far.
class ReplaceState(TypedDict):
    log: list[str]


# Annotated[list, operator.add] -> the reducer is ADD (list concat).
# Same field name, same node logic below — only the type changes.
class AppendState(TypedDict):
    log: Annotated[list[str], operator.add]


def step_one(state) -> dict:
    return {"log": ["step_one ran"]}


def step_two(state) -> dict:
    return {"log": ["step_two ran"]}


def build(state_cls) -> StateGraph:
    g = StateGraph(state_cls)
    g.add_node("step_one", step_one)
    g.add_node("step_two", step_two)
    g.add_edge(START, "step_one")
    g.add_edge("step_one", "step_two")
    g.add_edge("step_two", END)
    return g.compile()


replace_graph = build(ReplaceState)
append_graph = build(AppendState)


if __name__ == "__main__":
    print("ReplaceState:", replace_graph.invoke({"log": []}))
    print("AppendState: ", append_graph.invoke({"log": []}))
