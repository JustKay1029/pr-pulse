import requests
from google import genai
from dotenv import load_dotenv
import os
load_dotenv()
gh_token = os.getenv("GITHUB_PAT")
USERNAME = "JustKay1029"
REPO = "prpulse-test"
TOKEN = gh_token
pull_number = 1
# The URL we want to request data from
url = f"https://api.github.com/repos/{USERNAME}/{REPO}/pulls/{pull_number}"

# GitHub requires us to send our token in the "headers" for authentication
headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3.diff"
}

# Make the request
response = requests.get(url, headers=headers)

# Print the result
git_diff = "Response Data:", response.text
  # This reads the .env file and loads the variables
api_key = os.getenv("GEMINI_API_KEY")


client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"You are an expert code reviewer. Review the following git diff for bugs, logic flaws, clean coding standards, and security issues. Provide constructive feedback.Here is the code: {git_diff}"
)
gemini_response = response.text
print(gemini_response)

comment_url = "https://api.github.com/repos/JustKay1029/prpulse-test/issues/1/comments" 

# 2. Package Gemini's text response into the exact JSON format GitHub expects
payload = {
    "body": gemini_response
}

# 3. Make the POST request to send it back to the cloud
post_response = requests.post(comment_url, headers=headers, json=payload)

# 4. Check if GitHub accepted it
print("GitHub Post Status:", post_response.status_code)