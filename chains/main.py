import requests
from dotenv import load_dotenv
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()  # Load environment variables from .env file

@dataclass
class Context:
    user_id: str

@dataclass
class ResponseFormat:
    city: str
    summary: str
    temperature_celcius: float
    temperature_fahrenheit: float
    humidity: float

@tool("locate_user", description="Locate the user based on context.", return_direct=False)
def locate_user(runtime: ToolRuntime[Context]) -> str:
    match runtime.context.user_id:
        case "user_1":
            return "User 1 is located in New York City."
        case "user_2":
            return "User 2 is located in Los Angeles."
        case "user_3":
            return "User 3 is located in Chicago."
        case _:
            return "User location is unknown."

model = init_chat_model(
    model="claude-haiku-4-5-20251001",
    temperature=0.3
    )

checkpointer = InMemorySaver()


# How to create simple agent 
@tool('get_weather', description="Get weather for a given city.", return_direct=False)
def get_weather(city: str) -> str:
    response = requests.get(f"https://wttr.in/{city}?format=%C+%t+%h", timeout=10)
    response.raise_for_status()
    return response.text.strip()

# agent = create_agent(
#     model="claude-haiku-4-5-20251001",
#     tools=[get_weather],
#     system_prompt="""
#     You are a helpful weather assistant, who always cracks jokes and is humorous while remain helpful.
#     """,
# )

agent = create_agent(
    model=model,
    tools=[get_weather, locate_user],
    system_prompt="""
    You are a helpful weather assistant, who always cracks jokes and is humorous while remain helpful.
    """,
    context_schema=Context,
    response_format = ResponseFormat,
    checkpointer=checkpointer
)

config = {'configurable': {'thread_id': "1"}}

response = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather like?"}]},
    config = config,
    context=Context(user_id="user_1")

)
# print(response["messages"][-1].content)
print(f"City: {response['structured_response'].city}")
print(response['structured_response'].summary)
print(f"Temperature in Celsius: {response['structured_response'].temperature_celcius}")
print(f"Temperature in Fahrenheit: {response['structured_response'].temperature_fahrenheit}")
print(f"Humidity: {response['structured_response'].humidity}")


# How to use standalone models 

'''
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage, AIMessage

model = init_chat_model(
    model="claude-haiku-4-5-20251001",
    temperature=0.7,
    max_tokens=1000,
)

conversation = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="What is LangChain?"),
    AIMessage(content="Langchain is Python framework for building applications with LLMs."),
    HumanMessage(content="when was it released?")
]

response = model.invoke(conversation)
print(response.content)

'''

