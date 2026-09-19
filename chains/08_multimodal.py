from base64 import b64encode
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

model = init_chat_model(model="claude-haiku-4-5-20251001")

with open("data/logo.png", "rb") as f:
    image_data = b64encode(f.read()).decode("utf-8")

message = {
    "role": "user",
    "content": [
        {"type": "text", "text": "Describe the contents of this image."},
        {
            "type": "image",
            "source_type": "base64",
            "data": image_data,
            "mime_type": "image/png",
        },
    ],
}

response = model.invoke([message])

print(response.content)