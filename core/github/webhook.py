from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GitHubWebhookEvent:
    event: str
    delivery_id: str
    action: str | None
    repository: str | None
    pr_number: int | None
    base_sha: str | None
    head_sha: str | None
    task_id: str
    ignored: bool = False
    ignore_reason: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "accepted": not self.ignored,
            "event": self.event,
            "delivery_id": self.delivery_id,
            "action": self.action,
            "repository": self.repository,
            "pr_number": self.pr_number,
            "base_sha": self.base_sha,
            "head_sha": self.head_sha,
            "task_id": self.task_id,
            "ignored": self.ignored,
            "ignore_reason": self.ignore_reason,
        }


def verify_signature(payload: bytes, signature_header: str | None, secret: str | None) -> bool:
    if not secret:
        return True

    if not signature_header or not signature_header.startswith("sha256="):
        return False

    expected = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def parse_webhook(event: str, delivery_id: str, payload: bytes) -> GitHubWebhookEvent:
    data = json.loads(payload.decode("utf-8"))
    task_id = _build_task_id(delivery_id)

    if event != "pull_request":
        return GitHubWebhookEvent(
            event=event,
            delivery_id=delivery_id,
            action=data.get("action"),
            repository=_repository_name(data),
            pr_number=None,
            base_sha=None,
            head_sha=None,
            task_id=task_id,
            ignored=True,
            ignore_reason="Only pull_request events are supported in MVP v0.",
        )

    pull_request = data.get("pull_request") or {}
    base = pull_request.get("base") or {}
    head = pull_request.get("head") or {}

    return GitHubWebhookEvent(
        event=event,
        delivery_id=delivery_id,
        action=data.get("action"),
        repository=_repository_name(data),
        pr_number=pull_request.get("number") or data.get("number"),
        base_sha=base.get("sha"),
        head_sha=head.get("sha"),
        task_id=task_id,
    )


def _repository_name(data: dict[str, Any]) -> str | None:
    repository = data.get("repository") or {}
    return repository.get("full_name")


def _build_task_id(delivery_id: str) -> str:
    digest = hashlib.sha256(delivery_id.encode("utf-8")).hexdigest()[:16]
    return f"gh_{digest}"
