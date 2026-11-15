import anyio
import hmac
import hashlib
from fastapi import Request, HTTPException
from app.auth import verify_signature


class DummyRequest:
    def __init__(self, headers: dict, body_bytes: bytes):
        self.headers = headers
        self._body = body_bytes

    async def body(self):
        return self._body


def test_t1_valid_signature():
    async def run():
        secret = "test-secret-key"
        payload = b'{"action": "opened", "pull_request": {"number": 1}}'
        expected_hash = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

        req = DummyRequest(headers={"X-Hub-Signature-256": expected_hash}, body_bytes=payload)
        result = await verify_signature(req, secret)
        assert result == payload

    anyio.run(run)


def test_t2_tampered_payload_rejected():
    async def run():
        secret = "test-secret-key"
        original_payload = b'{"action": "opened"}'
        expected_hash = "sha256=" + hmac.new(secret.encode(), original_payload, hashlib.sha256).hexdigest()

        tampered_payload = b'{"action": "tampered"}'
        req = DummyRequest(headers={"X-Hub-Signature-256": expected_hash}, body_bytes=tampered_payload)

        try:
            await verify_signature(req, secret)
            assert False, "Should have raised HTTPException"
        except HTTPException as exc:
            assert exc.status_code == 401
            assert "Signature mismatch" in exc.detail

    anyio.run(run)


def test_t3_missing_signature_header_rejected():
    async def run():
        secret = "test-secret-key"
        req = DummyRequest(headers={}, body_bytes=b"{}")

        try:
            await verify_signature(req, secret)
            assert False, "Should have raised HTTPException"
        except HTTPException as exc:
            assert exc.status_code == 401
            assert "Missing X-Hub-Signature-256" in exc.detail

    anyio.run(run)
