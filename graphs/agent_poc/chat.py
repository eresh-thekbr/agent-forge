from langgraph.checkpoint.memory import InMemorySaver

from graphs.agent_poc.agent import build_workflow

# A fresh checkpointer per run, one thread_id for the whole session — that
# combination is what makes this an actual back-and-forth conversation
# instead of the one-question-at-a-time behavior of rag/docqa/chat.py.
graph = build_workflow().compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "chat-session"}}


def main():
    print("Chat about your PDF. Type 'exit' or 'quit' to stop.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not question:
            continue

        result = graph.invoke(
            {"messages": [{"role": "user", "content": question}]}, config
        )
        print(f"Bot: {result['messages'][-1].content}\n")


if __name__ == "__main__":
    main()
