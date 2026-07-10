from google import genai
from dotenv import load_dotenv
import os

load_dotenv()  # This reads the .env file and loads the variables
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hi! I am setting up a code review bot."
)
print(response.text)