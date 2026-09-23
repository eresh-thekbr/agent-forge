from graphs.agent_poc.cycles import graph

# invoke() blocks until the whole graph finishes and gives you only the
# final state. stream() yields one event per node as it completes — same
# graph, same execution, just observed step by step instead of at the end.
if __name__ == "__main__":
    for event in graph.stream({"count": 0}):
        print(event)
