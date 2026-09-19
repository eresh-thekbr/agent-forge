from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware, ModelCallLimitMiddleware
from langchain.chat_models import init_chat_model

load_dotenv()

model = init_chat_model(model="claude-haiku-4-5-20251001")

agent = create_agent(
    model=model,
    middleware=[
        SummarizationMiddleware(
            model=model,
            max_tokens_before_summary=4000,
            messages_to_keep=20,
        ),
        ModelCallLimitMiddleware(
            thread_limit=10,
            run_limit=5,
        ),
    ],
)

response = agent.invoke(
    {"messages": [{"role": "user", "content": "Explain PCA in two sentences."}]}
)

print(response["messages"][-1].content)