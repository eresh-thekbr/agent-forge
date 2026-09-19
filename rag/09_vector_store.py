from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

texts = [
    "Apple makes very good computers.",
    "I believe Apple is innovative.",
    "I love apples.",
    "I am a fan of MacBooks.",
    "I enjoy oranges.",
    "I like Dell laptops.",
    "I think pears taste very good.",
]

vector_store = FAISS.from_texts(texts, embedding=embeddings)

print("--- apples are my favorite food ---")
for doc in vector_store.similarity_search("apples are my favorite food", k=7):
    print(doc.page_content)

print()
print("--- Linux is a great operating system ---")
for doc in vector_store.similarity_search("Linux is a great operating system", k=7):
    print(doc.page_content)