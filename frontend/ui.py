import logging
import sys
from pathlib import Path

# streamlit run executes this file directly (unlike `python -m frontend`
# elsewhere in this project), so the project root isn't automatically on
# sys.path — add it explicitly, based on this file's own location, so the
# import below works no matter how or from where `streamlit run` is invoked.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Streamlit's file watcher walks every loaded module (including
# transformers' unused vision submodules) to find files to auto-reload on.
# Those submodules import torchvision, which this text-only project never
# needs, so the watcher logs a harmless warning. This only raises the log
# level for that one specific logger — the watcher itself keeps running.
logging.getLogger("streamlit.watcher.local_sources_watcher").setLevel(logging.ERROR)

import streamlit as st

from rag.docqa.agent import ask, build_agent


st.title("docqa")


# @st.cache_resource means this only really runs once (not on every rerun),
# so the retriever/agent isn't rebuilt on every single message.
@st.cache_resource
def get_agent():
    return build_agent()


agent = get_agent()

# Streamlit reruns this whole script on every interaction, so chat history
# has to live in session_state — a normal Python list would reset every time.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Redraw everything said so far, since the script reruns from the top.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question := st.chat_input("Ask a question about your PDF"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    answer = ask(agent, question)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
