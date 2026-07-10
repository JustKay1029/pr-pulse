import os
import requests
from dotenv import load_dotenv
load_dotenv()

USERNAME = "JustKay1029"
REPO = "prpulse-test"
TOKEN = os.getenv("GITHUB_PAT")
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
print("Status Code:", response.status_code)
print("Response Data:", response.text)