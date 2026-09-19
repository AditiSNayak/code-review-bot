import os
from google import genai
from dotenv import load_dotenv

# 1. Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# 2. Create client (the new SDK reads the API key from environment variables by default)
client = genai.Client(api_key=api_key)

# 3. Call the Interactions API
interaction = client.interactions.create(
    model="gemini-3.6-flash",  # New model name
    input="Reply with exactly this text and nothing else: Hello from Gemini"
)

# 4. Output the result (the new SDK uses .output_text)
print("--- Gemini says: ---")
print(interaction.output_text)