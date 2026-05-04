import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load the API key from .env file
load_dotenv()

# Initialize the LLM
# llama-3.3-70b is Groq's strong free model — perfect for SQL generation
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,  # 0 = deterministic, no creativity (we want exact SQL, not poetry)
    api_key=os.getenv("GROQ_API_KEY")
)

# Send a test message
print("🤖 Sending test message to Groq...")
response = llm.invoke("Say 'Hello InsightBot!' in exactly 5 words.")

print("\n📨 LLM Response:")
print(response.content)