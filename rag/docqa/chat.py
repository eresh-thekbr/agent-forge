from rag.docqa.agent import ask, build_agent


def main():
    # Build the agent once up front — re-embedding or reconnecting per
    # question would be slow and pointless.
    agent = build_agent()
    print("Ask questions about your PDF. Type 'exit' or 'quit' to stop.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not question:
            continue

        answer = ask(agent, question)
        print(f"Bot: {answer}\n")


if __name__ == "__main__":
    main()
