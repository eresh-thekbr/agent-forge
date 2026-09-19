import time
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware

load_dotenv()


class HooksDemo(AgentMiddleware):
    def __init__(self):
        super().__init__()
        self.start_time = 0.0

    def before_agent(self, state, runtime):
        self.start_time = time.perf_counter()
        print("before_agent triggered")

    def before_model(self, state, runtime):
        print("before_model triggered")

    def after_model(self, state, runtime):
        print("after_model triggered")

    def after_agent(self, state, runtime):
        elapsed = time.perf_counter() - self.start_time
        print(f"after_agent triggered: {elapsed:.2f} seconds")


agent = create_agent(
    model="claude-haiku-4-5-20251001",
    middleware=[HooksDemo()],
)

response = agent.invoke(
    {"messages": [{"role": "user", "content": "Explain PCA."}]}
)

print()
print(response["messages"][-1].content)