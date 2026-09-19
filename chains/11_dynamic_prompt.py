from dataclasses import dataclass
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest

load_dotenv()


@dataclass
class Context:
    user_role: str


@dynamic_prompt
def user_role_prompt(request: ModelRequest) -> str:
    base_prompt = "You are a helpful and very concise assistant."
    user_role = request.runtime.context.user_role

    match user_role:
        case "expert":
            return base_prompt + " Provide detailed technical responses."
        case "beginner":
            return base_prompt + " Keep your explanations simple and basic."
        case "child":
            return base_prompt + " Explain everything as if you were talking to a 5 year old."
        case _:
            return base_prompt


agent = create_agent(
    model="claude-haiku-4-5-20251001",
    middleware=[user_role_prompt],
    context_schema=Context,
)

response = agent.invoke(
    {"messages": [{"role": "user", "content": "Explain PCA."}]},
    context=Context(user_role="beginner"),
)

print(response["messages"][-1].content)