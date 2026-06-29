import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from apps.api.main import app


client = TestClient(app)


def test_github_pull_request_webhook_is_accepted(monkeypatch) -> None:
    monkeypatch.delenv("GITHUB_WEBHOOK_SECRET", raising=False)
    payload = {
        "action": "opened",
        "repository": {"full_name": "yangming2002/CodeInsight"},
        "number": 12,
        "pull_request": {
            "number": 12,
            "base": {"sha": "base123"},
            "head": {"sha": "head456"},
        },
    }

    response = client.post(
        "/webhooks/github",
        json=payload,
        headers={
            "X-GitHub-Event": "pull_request",
            "X-GitHub-Delivery": "delivery-1",
        },
    )

    body = response.json()

    assert response.status_code == 202
    assert body["accepted"] is True
    assert body["event"] == "pull_request"
    assert body["action"] == "opened"
    assert body["repository"] == "yangming2002/CodeInsight"
    assert body["pr_number"] == 12
    assert body["base_sha"] == "base123"
    assert body["head_sha"] == "head456"
    assert body["task_id"].startswith("gh_")


def test_github_webhook_rejects_invalid_signature(monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "secret")

    response = client.post(
        "/webhooks/github",
        json={"action": "opened"},
        headers={
            "X-GitHub-Event": "pull_request",
            "X-GitHub-Delivery": "delivery-2",
            "X-Hub-Signature-256": "sha256=wrong",
        },
    )

    assert response.status_code == 401


def test_github_webhook_accepts_valid_signature(monkeypatch) -> None:
    secret = "secret"
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", secret)
    payload = json.dumps({"action": "ping", "repository": {"full_name": "owner/repo"}}).encode()
    signature = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    response = client.post(
        "/webhooks/github",
        content=payload,
        headers={
            "Content-Type": "application/json",
            "X-GitHub-Event": "ping",
            "X-GitHub-Delivery": "delivery-3",
            "X-Hub-Signature-256": signature,
        },
    )

    body = response.json()

    assert response.status_code == 202
    assert body["accepted"] is False
    assert body["ignored"] is True
    assert body["ignore_reason"] == "Only pull_request events are supported in MVP v0."


def test_github_webhook_requires_headers() -> None:
    response = client.post("/webhooks/github", json={})

    assert response.status_code == 400
