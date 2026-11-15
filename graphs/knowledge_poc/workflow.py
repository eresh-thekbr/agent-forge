"""The WORKFLOW graph: resolve input -> retrieve facts -> format answer."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from .knowledge import ENTITIES, describe, find_paths


class State(TypedDict, total=False):
    technology: str
    technology_id: str | None
    people: list[str]
    evidence: list[str]
    answer: str


def resolve_technology(state: State) -> dict:
    requested = state["technology"].strip().casefold()
    match = next(
        (entity.id for entity in ENTITIES.values()
         if entity.kind == "Technology" and entity.name.casefold() == requested),
        None,
    )
    return {"technology_id": match}


def retrieve_facts(state: State) -> dict:
    paths = find_paths(state["technology_id"]) if state["technology_id"] else []
    return {
        "people": sorted({ENTITIES[path[0].source].name for path in paths}),
        "evidence": ["; ".join(describe(fact) for fact in path) for path in paths],
    }


def format_answer(state: State) -> dict:
    if state["technology_id"] is None:
        answer = f"Unknown technology: {state['technology']!r}. Try Python, TypeScript, or Rust."
    elif not state["people"]:
        answer = f"No matching facts for {ENTITIES[state['technology_id']].name} in this dataset."
    else:
        name = ENTITIES[state["technology_id"]].name
        answer = f"{', '.join(state['people'])} work on projects that use {name}."
    return {"answer": answer}


def build_workflow():
    builder = StateGraph(State)
    builder.add_node("resolve_technology", resolve_technology)
    builder.add_node("retrieve_facts", retrieve_facts)
    builder.add_node("format_answer", format_answer)
    builder.add_edge(START, "resolve_technology")
    builder.add_edge("resolve_technology", "retrieve_facts")
    builder.add_edge("retrieve_facts", "format_answer")
    builder.add_edge("format_answer", END)
    return builder.compile()
