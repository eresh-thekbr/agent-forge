from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.tools import create_retriever_tool
from langchain.agents import create_agent

load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

texts = [
    "I love apples.",
    "I enjoy oranges.",
    "I think pears taste very good.",
    "I hate bananas.",
    "I dislike raspberries.",
    "I despise mangoes.",
    "I love Linux.",
    "I hate Windows.",
]

vector_store = FAISS.from_texts(texts, embedding=embeddings)

retriever = vector_store.as_retriever(search_kwargs={"k": 3})

retriever_tool = create_retriever_tool(
    retriever,
    name="kb_search",
    description="Search the knowledge base for information about what the person likes and dislikes.",
)

agent = create_agent(
    model="claude-haiku-4-5-20251001",
    tools=[retriever_tool],
    system_prompt=(
        "You are a helpful assistant. For any question about the person's preferences, "
        "use the kb_search tool first to retrieve context, then answer concisely. "
        "You may need to use the tool more than once to gather all the information."
    ),
)

response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "What three fruits does the person like and what three fruits does the person dislike?",
            }
        ]
    }
)

print(response["messages"][-1].content)