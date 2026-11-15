import anyio
import hmac
import hashlib
import json
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport
from app.main import app


def test_health_endpoint():
    async def run():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "healthy"
            assert data["service"] == "pr-pulse"

    anyio.run(run)


def test_webhook_non_pr_event_ignored():
    async def run():
        secret = "justkay's-pr-pulse"
        payload = json.dumps({"zen": "Keep it logically awesome."}).encode("utf-8")
        sig = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = {
                "X-Hub-Signature-256": sig,
                "X-GitHub-Event": "ping",
                "Content-Type": "application/json",
            }
            resp = await client.post("/webhook", content=payload, headers=headers)
            assert resp.status_code == 200
            assert resp.json().get("status") == "ignored"

    anyio.run(run)


def test_webhook_pr_synchronize_processed():
    async def run():
        secret = "justkay's-pr-pulse"
        payload_data = {
            "action": "synchronize",
            "pull_request": {
                "number": 42,
                "diff_url": "https://api.github.com/repos/JustKay1029/prpulse-test/pulls/42",
            },
            "repository": {
                "name": "prpulse-test",
                "owner": {"login": "JustKay1029"},
            },
        }
        payload = json.dumps(payload_data).encode("utf-8")
        sig = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

        # Using an obvious dummy string that won't trip GitHub's secret scanner
        fake_diff = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1,1 +1,2 @@
+SECRET = "dummy_fake_token_value_for_testing"
"""

        with patch("app.main.fetch_pr_diff", new_callable=AsyncMock) as mock_fetch, \
             patch("app.main.post_pr_review", new_callable=AsyncMock) as mock_post:
            
            mock_fetch.return_value = fake_diff
            mock_post.return_value = {"id": 99999, "state": "COMMENT"}

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                headers = {
                    "X-Hub-Signature-256": sig,
                    "X-GitHub-Event": "pull_request",
                    "Content-Type": "application/json",
                }
                resp = await client.post("/webhook", content=payload, headers=headers)
                assert resp.status_code == 200
                data = resp.json()
                assert data["status"] == "success"
                assert data["pull_request"] == 42
                assert data["review_id"] == 99999

    anyio.run(run)
