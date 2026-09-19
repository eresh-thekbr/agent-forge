from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

model = init_chat_model(model="claude-haiku-4-5-20251001")

for chunk in model.stream("Explain what Python is in about 200 words."):
    print(chunk.text, end="", flush=True)

print()