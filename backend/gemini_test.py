
import os
from dotenv import load_dotenv
from google import genai


# Load API key from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. Check your .env file."
    )


# Connect to Gemini
client = genai.Client(api_key=api_key)

try:
    print("Connecting to Gemini...")

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=(
            "You are the AI assistant of CiviLens, "
            "a government policy intelligence platform. "
            "Explain in 3 simple sentences how AI can help "
            "students understand scholarship guideline changes."
        )
    )

    print("\n========== GEMINI RESPONSE ==========\n")
    print(response.text)
    print("\n=====================================")

except Exception as error:
    print("\nGemini API request failed:")
    print(error)

finally:
    client.close()
