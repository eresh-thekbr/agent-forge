import requests
from dataclasses import dataclass
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime

load_dotenv()


@dataclass
class Context:
    user_id: str


@tool("get_weather", description="Return weather information for a given city.")
def get_weather(city: str):
    response = requests.get(f"https://wttr.in/{city}?format=j1")
    return response.json()


@tool("locate_user", description="Look up a user's city based on the context.")
def locate_user(runtime: ToolRuntime[Context]):
    match runtime.context.user_id:
        case "ABC123":
            return "Dallas"
        case "XYZ456":
            return "Chicago"
        case "HJKL111":
            return "Seattle"
        case _:
            return "unknown"


agent = create_agent(
    model="claude-haiku-4-5-20251001",
    tools=[get_weather, locate_user],
    system_prompt="You are a helpful weather assistant. If the location is unknown, say so.",
    context_schema=Context,
)

response = agent.invoke(
    {"messages": [{"role": "user", "content": "What is the weather like?"}]},
    context=Context(user_id="ABC123"),
)

print(response["messages"][-1].content)