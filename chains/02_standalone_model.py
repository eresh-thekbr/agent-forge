from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

model = init_chat_model(
    model="claude-haiku-4-5-20251001",
    temperature=0.1,
)

response = model.invoke("Hello, what is Python?")

print(response.content)