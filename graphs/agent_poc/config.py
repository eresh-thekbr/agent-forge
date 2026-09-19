from dotenv import load_dotenv

# Every other module in this package reads its model name from here,
# so switching models only means editing one file.
load_dotenv()

# Same chat model used across the rest of the agent-forge lessons.
MODEL_NAME = "claude-haiku-4-5-20251001"
