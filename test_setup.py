

import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if api_key and api_key.startswith("gsk_"):
    print("✅ Setup is working! API key loaded successfully.")
    print(f"Key starts with: {api_key[:10]}...")
else:
    print("❌ Something's wrong. Check your .env file.")