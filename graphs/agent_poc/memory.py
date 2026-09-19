from langgraph.checkpoint.memory import InMemorySaver

from graphs.agent_poc.agent import build_workflow

# Same graph shape as agent.py — the only difference is the checkpointer,
# which saves state after every step so a conversation can be resumed by
# passing the same thread_id back in.
graph = build_workflow().compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    # The same thread_id on both calls is what makes these one continuous
    # conversation instead of two unrelated ones.
    config = {"configurable": {"thread_id": "demo-1"}}

    first = graph.invoke(
        {"messages": [{"role": "user", "content": "My name is Eresh."}]}, config
    )
    print(f"Bot: {first['messages'][-1].content}")

    second = graph.invoke(
        {"messages": [{"role": "user", "content": "What's my name?"}]}, config
    )
    print(f"Bot: {second['messages'][-1].content}")
