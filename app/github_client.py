import httpx
from app.rule_engine import Violation


def format_review_body(violations: list[Violation], ai_review: str | None = None) -> str:
    has_critical = any(v.severity == "CRITICAL" for v in violations)
    verdict = "CHANGES REQUESTED" if has_critical or len(violations) > 0 else "APPROVED"
    verdict_emoji = "🔴" if has_critical else ("🟡" if violations else "🟢")

    lines = [
        "### 🛡️ PR-Pulse Automated Security & Quality Analysis",
        "",
        f"**Verdict:** {verdict_emoji} **{verdict}**",
        "",
    ]

    if violations:
        lines.append("| Severity | File | Line | Finding |")
        lines.append("| :--- | :--- | :--- | :--- |")
        for v in violations:
            icon = "🔴" if v.severity == "CRITICAL" else "🟡"
            lines.append(f"| {icon} {v.severity} | `{v.filename}` | Line {v.line_number} | {v.message} |")
        lines.append("")
    else:
        lines.append("✅ No security leaks or immediate syntax violations detected by deterministic rules.")
        lines.append("")

    if ai_review:
        lines.extend([
            "---",
            "### 🤖 Gemini AI Code Review Summary",
            "",
            ai_review,
            "",
        ])

    lines.append("---")
    lines.append("*Automated review powered by PR-Pulse • HMAC-SHA256 Verified*")
    return "\n".join(lines)


async def fetch_pr_diff(diff_url: str, token: str) -> str:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff",
    }
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(diff_url, headers=headers)
        response.raise_for_status()
        return response.text


async def post_pr_review(
    owner: str,
    repo: str,
    pull_number: int,
    violations: list[Violation],
    token: str,
    ai_review: str | None = None,
) -> dict:
    has_critical = any(v.severity == "CRITICAL" for v in violations)
    event = "REQUEST_CHANGES" if has_critical else "COMMENT"

    body_text = format_review_body(violations, ai_review=ai_review)
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    payload = {
        "body": body_text,
        "event": event,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
