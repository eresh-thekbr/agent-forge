import requests
from dataclasses import dataclass
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()


@dataclass
class ResponseFormat:
    summary: str
    temperature_celsius: float
    temperature_fahrenheit: float
    humidity: float


@tool("get_weather", description="Return weather information for a given city.")
def get_weather(city: str):
    response = requests.get(f"https://wttr.in/{city}?format=j1")
    return response.json()


agent = create_agent(
    model="claude-haiku-4-5-20251001",
    tools=[get_weather],
    system_prompt="You are a helpful weather assistant.",
    response_format=ResponseFormat,
)

response = agent.invoke(
    {"messages": [{"role": "user", "content": "What is the weather like in Dallas?"}]}
)

result = response["structured_response"]

print(result.summary)
print(f"Celsius: {result.temperature_celsius}")
print(f"Fahrenheit: {result.temperature_fahrenheit}")
print(f"Humidity: {result.humidity}")