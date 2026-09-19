from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

model = init_chat_model(model="claude-haiku-4-5-20251001")

conversation = [
    SystemMessage(
        content="You are a helpful assistant for questions regarding programming."
    ),
    HumanMessage(content="What is Python?"),
    AIMessage(content="Python is an interpreted programming language."),
    HumanMessage(content="When was it released?"),
]

response = model.invoke(conversation)

print(response.content)
