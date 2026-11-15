# 🛡️ PR-Pulse

> Automated Git Pull Request Security & Quality Analysis Service using GitHub Webhooks.

PR-Pulse is a self-hostable FastAPI microservice that acts as an automated gatekeeper for version control repositories. It listens for GitHub `pull_request` webhook events, cryptographically verifies payloads using HMAC-SHA256, parses unified git diffs, executes deterministic regex & AST syntax checks, optionally triggers Google Gemini 2.5 Flash for code reasoning, and dispatches review comments back into GitHub PR threads.

---

## 🚀 Key Features

- **Cryptographic Ingestion Gateway:** Validates incoming payloads via constant-time HMAC-SHA256 comparison against `X-Hub-Signature-256`.
- **Zero-Token Deterministic Scanner:** Flags leaked AWS keys, Stripe secret keys, GitHub tokens, and private SSH/RSA blocks before branch merge.
- **Python AST Syntax Validator:** Groups patch additions and checks for fatal syntax errors (`ast.parse`) before runtime failure.
- **Gemini 2.5 Flash Integration:** Provides contextual semantic code quality and edge-case feedback directly on clean diffs.
- **GitHub REST API Review Dispatcher:** Automatically posts structured markdown feedback and review verdicts (`REQUEST_CHANGES` vs `COMMENT`).

---

## 📁 Repository Structure

```
pr-pulse/
├── app/
│   ├── __init__.py
│   ├── auth.py           # HMAC-SHA256 validation
│   ├── diff_parser.py    # Unified diff parser (hunk extraction)
│   ├── rule_engine.py    # Deterministic secret scanner & AST linting
│   ├── github_client.py  # Upstream GitHub REST API client
│   └── main.py           # FastAPI entrypoint (/webhook, /health)
├── tests/
│   ├── test_auth.py
│   ├── test_diff_parser.py
│   ├── test_rule_engine.py
│   └── test_integration.py
├── .env.example
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🛠️ Local Setup & Execution

### 1. Clone & Install
```bash
git clone https://github.com/JustKay1029/pr-pulse.git
cd pr-pulse
python -m venv venv
venv\Scripts\activate   # On Windows
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```env
GITHUB_TOKEN=ghp_your_personal_access_token
WEBHOOK_SECRET=your_custom_webhook_secret
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Run the Server
```bash
uvicorn app.main:app --reload --port 8000
```
- Interactive API Docs: `http://localhost:8000/docs`
- Health Endpoint: `http://localhost:8000/health`

### 4. Run Automated Tests
```bash
pytest tests/ -v
```

---

## 🐳 Docker Deployment
```bash
docker build -t pr-pulse .
docker run -p 8000:8000 --env-file .env pr-pulse
```

---

## 📜 License
MIT License. Developed for Version Control Systems (CSE25302).
