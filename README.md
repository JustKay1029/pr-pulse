# PR Pulse 🚀

**PR Pulse** is a lightweight, AI-powered GitHub Pull Request reviewer. It automatically fetches pull request code diffs, analyzes them for bugs, logic issues, security vulnerabilities, and code quality using Google's **Gemini 2.5 Flash** model, and posts the constructive feedback directly back to the pull request as a comment.

---

## 🌟 Features

- **Automated Diff Extraction**: Connects directly to the GitHub API to fetch PR diffs cleanly.
- **AI-Powered Analysis**: Uses `gemini-2.5-flash` via the latest `google-genai` SDK to analyze changes.
- **Constructive Code Reviews**: Scans for:
  - Security issues
  - Code design patterns and readability
  - Logical bugs or edge-case flaws
- **Automatic Feedback Loop**: Packages the AI feedback and automatically comments on the target PR thread.

---

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **AI Client**: `google-genai` (Gemini API)
- **HTTP Client**: `requests` (GitHub REST API v3)
- **Configuration**: `python-dotenv` for managing credentials securely

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/JustKay1029/pr-pulse.git
cd pr-pulse
```

### 2. Install Dependencies
Ensure you have Python installed, then install the package requirements:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a file named `.env` in the root of the project:
```ini
GEMINI_API_KEY="your-gemini-api-key"
GITHUB_PAT="your-github-personal-access-token"
```

> [!IMPORTANT]
> - **`GEMINI_API_KEY`**: Obtain from Google AI Studio.
> - **`GITHUB_PAT`**: Generate a Personal Access Token from GitHub settings with access to the repo (`repo` scopes).
> - Never commit `.env` to version control. It is already added to `.gitignore`.

---

## 🚀 How to Run

### Test Gemini Connectivity
To test that your Gemini API key is correctly configured and working:
```bash
python test_gemini.py
```

### Fetch PR Diff (Dry Run)
To verify your GitHub credentials and check if you can pull PR diffs:
```bash
python fetch_pr.py
```

### Run the Review Engine (End-to-End)
To fetch the PR diff, generate the Gemini review, and post it to the PR issues comment thread:
```bash
python review_engine.py
```

---

## 📋 Future Roadmap

- [ ] Support dynamic CLI inputs for Repo Name and PR Number.
- [ ] Implement GitHub Actions webhook integration for fully automated runs on PR opening.
- [ ] Add line-by-line review comments instead of a single top-level issue comment.
- [ ] Add support for custom system instructions to tailor review style.
