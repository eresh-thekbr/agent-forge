from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage

load_dotenv()

basic_model = init_chat_model(model="claude-haiku-4-5-20251001")
advanced_model = init_chat_model(model="claude-sonnet-4-6")


@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
    message_count = len(request.state["messages"])

    if message_count > 3:
        model = advanced_model
    else:
        model = basic_model

    request.model = model
    return handler(request)


agent = create_agent(
    model=basic_model,
    middleware=[dynamic_model_selection],
)

response = agent.invoke(
    {
        "messages": [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="What is 1 + 1?"),
        ]
    }
)

print(response["messages"][-1].content)
print("Model used:", response["messages"][-1].response_metadata["model_name"])