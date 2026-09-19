import requests
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()


@tool("get_weather", description="Return weather information for a given city.")
def get_weather(city: str):
    response = requests.get(f"https://wttr.in/{city}?format=j1")
    return response.json()


checkpointer = InMemorySaver()

agent = create_agent(
    model="claude-haiku-4-5-20251001",
    tools=[get_weather],
    system_prompt="You are a helpful weather assistant.",
    checkpointer=checkpointer,
)

config = {"configurable": {"thread_id": "1"}}

first = agent.invoke(
    {"messages": [{"role": "user", "content": "What is the weather like in Dallas?"}]},
    config=config,
)
print(first["messages"][-1].content)

print("---")

second = agent.invoke(
    {"messages": [{"role": "user", "content": "And is that usual?"}]},
    config=config,
)
print(second["messages"][-1].content)