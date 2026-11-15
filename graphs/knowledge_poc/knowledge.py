"""The DATA graph: entities and directed, named relationships."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Entity:
    id: str
    name: str
    kind: str


@dataclass(frozen=True)
class Fact:
    source: str
    relation: str
    target: str


ENTITIES = {
    entity.id: entity
    for entity in (
        Entity("alice", "Alice", "Person"),
        Entity("bob", "Bob", "Person"),
        Entity("carol", "Carol", "Person"),
        Entity("atlas", "Atlas", "Project"),
        Entity("beacon", "Beacon", "Project"),
        Entity("python", "Python", "Technology"),
        Entity("typescript", "TypeScript", "Technology"),
        Entity("rust", "Rust", "Technology"),
    )
}

# Each fact is a triple: (subject, relationship, object).
FACTS = (
    Fact("alice", "WORKS_ON", "atlas"),
    Fact("bob", "WORKS_ON", "atlas"),
    Fact("carol", "WORKS_ON", "beacon"),
    Fact("atlas", "USES", "python"),
    Fact("beacon", "USES", "typescript"),
)


def describe(fact: Fact) -> str:
    return f"{ENTITIES[fact.source].name} --{fact.relation}--> {ENTITIES[fact.target].name}"


def find_paths(technology: str, facts: tuple[Fact, ...] = FACTS) -> list[tuple[Fact, Fact]]:
    """Match Person -WORKS_ON-> Project -USES-> Technology.

    Start at the technology and walk incoming edges twice. This is a
    two-hop query, not keyword similarity or a prediction about expertise.
    """
    paths = []
    for uses in facts:
        if uses.relation != "USES" or uses.target != technology:
            continue
        for works_on in facts:
            if works_on.relation == "WORKS_ON" and works_on.target == uses.source:
                paths.append((works_on, uses))
    return paths


def to_dot() -> str:
    """Render the fixed teaching dataset in Streamlit."""
    lines = ["digraph knowledge {", "rankdir=LR;"]
    colors = {"Person": "lightblue", "Project": "palegreen", "Technology": "khaki"}
    for entity in ENTITIES.values():
        lines.append(
            f'{entity.id} [label="{entity.name}\\n({entity.kind})", '
            f'style=filled, fillcolor="{colors[entity.kind]}"];'
        )
    for fact in FACTS:
        lines.append(f'{fact.source} -> {fact.target} [label="{fact.relation}"];')
    return "\n".join([*lines, "}"])
