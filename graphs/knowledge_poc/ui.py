"""Run from the repo root: python -m streamlit run graphs/knowledge_poc/ui.py."""

import streamlit as st

from graphs.knowledge_poc.knowledge import ENTITIES, FACTS, describe, to_dot
from graphs.knowledge_poc.workflow import build_workflow

st.set_page_config(page_title="Knowledge graph playground", layout="wide")
st.title("Your first knowledge graph")
st.write("A knowledge graph connects things with named relationships. This fictional dataset has people, projects, and technologies.")
st.subheader("1. Explore the facts")
st.graphviz_chart(to_dot())
with st.expander("See the stored triples"):
    st.code("\n".join(describe(fact) for fact in FACTS))
st.subheader("2. Follow two connections")
technology = st.selectbox("Who works on projects that use…?", [e.name for e in ENTITIES.values() if e.kind == "Technology"])
st.caption("Person → WORKS_ON → Project → USES → Technology. Rust has no project relationships; try it to see a missing answer.")
result = build_workflow().invoke({"technology": technology})
st.info(result["answer"])
st.write("Evidence paths:")
for evidence in result["evidence"]:
    st.code(evidence)
st.subheader("3. See LangGraph run the workflow")
st.graphviz_chart('digraph workflow { rankdir=LR; START -> resolve_technology -> retrieve_facts -> format_answer -> END; }')
st.write("These boxes are Python functions. The graph above stores knowledge; this graph controls the order of the work.")
with st.expander("Inspect the final workflow state"):
    st.json(result)
