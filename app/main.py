import os
import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from dotenv import load_dotenv

from app.auth import verify_signature
from app.diff_parser import parse_diff
from app.rule_engine import run_all_rules
from app.github_client import fetch_pr_diff, post_pr_review

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pr-pulse")

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("PR-Pulse gateway initialized and listening.")
    yield
    logger.info("PR-Pulse gateway shutting down.")


app = FastAPI(
    title="PR-Pulse Webhook Gatekeeper",
    description="Automated Git Pull Request Security & Quality Analysis Service",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "pr-pulse",
        "version": "1.0.0",
    }


@app.post("/webhook")
async def github_webhook(request: Request):
    secret = os.getenv("WEBHOOK_SECRET", "")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: WEBHOOK_SECRET not set.",
        )

    # 1. Verify HMAC Signature
    body_bytes = await verify_signature(request, secret)

    event_type = request.headers.get("X-GitHub-Event", "")
    if event_type != "pull_request":
        return {"status": "ignored", "reason": f"Event '{event_type}' is not handled."}

    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    action = payload.get("action")
    if action not in ["opened", "synchronize", "reopened"]:
        return {"status": "ignored", "reason": f"PR action '{action}' does not trigger review."}

    pr_data = payload.get("pull_request", {})
    repo_data = payload.get("repository", {})
    pull_number = pr_data.get("number")
    diff_url = pr_data.get("diff_url")
    owner = repo_data.get("owner", {}).get("login")
    repo_name = repo_data.get("name")

    if not diff_url or not pull_number or not owner or not repo_name:
        raise HTTPException(status_code=400, detail="Incomplete pull request metadata.")

    logger.info(f"Processing PR #{pull_number} for {owner}/{repo_name}")

    # 2. Fetch unified diff
    token = os.getenv("GITHUB_TOKEN", "")
    try:
        raw_diff = await fetch_pr_diff(diff_url, token)
    except Exception as exc:
        logger.error(f"Failed to fetch diff: {exc}")
        raise HTTPException(status_code=502, detail=f"Could not fetch diff: {exc}")

    # 3. Parse changed lines
    changed_lines = parse_diff(raw_diff)

    # 4. Run deterministic security & syntax rules
    violations = run_all_rules(changed_lines)

    # 5. Optional Gemini AI Review
    ai_review = None
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if gemini_key and not any(v.severity == "CRITICAL" for v in violations):
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            prompt = (
                "You are an expert code reviewer. Review the following git diff additions "
                "for potential edge cases, logic flaws, and readability. Keep it concise, structured in bullet points:\n\n"
                f"{raw_diff[:4000]}"
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            ai_review = response.text
        except Exception as exc:
            logger.warning(f"Gemini AI review step skipped/failed: {exc}")

    # 6. Post review to GitHub
    try:
        review_result = await post_pr_review(
            owner=owner,
            repo=repo_name,
            pull_number=pull_number,
            violations=violations,
            token=token,
            ai_review=ai_review,
        )
    except Exception as exc:
        logger.error(f"Failed to post GitHub review: {exc}")
        raise HTTPException(status_code=502, detail=f"Failed to dispatch review to GitHub: {exc}")

    return {
        "status": "success",
        "pull_request": pull_number,
        "violations_found": len(violations),
        "review_id": review_result.get("id"),
    }
