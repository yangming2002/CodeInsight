import json
import os

from fastapi import FastAPI, Header, HTTPException, Request, status

from apps.api.schemas import (
    GitHubWebhookResponse,
    HealthResponse,
    ReviewRequest,
    ReviewResponse,
)
from core.github import parse_webhook, verify_signature
from core.review.service import review_diff


app = FastAPI(
    title="CodeInsight API",
    description="PR code review API for deterministic policies and LLM-assisted reasoning.",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="codeinsight-api")


@app.post("/review", response_model=ReviewResponse)
def review(request: ReviewRequest) -> ReviewResponse:
    report = review_diff(diff=request.diff, repository=request.repository, pr_number=request.pr_number)
    return ReviewResponse(**report)


@app.post(
    "/webhooks/github",
    response_model=GitHubWebhookResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def github_webhook(
    request: Request,
    x_github_event: str | None = Header(default=None),
    x_github_delivery: str | None = Header(default=None),
    x_hub_signature_256: str | None = Header(default=None),
) -> GitHubWebhookResponse:
    if not x_github_event:
        raise HTTPException(status_code=400, detail="Missing X-GitHub-Event header.")
    if not x_github_delivery:
        raise HTTPException(status_code=400, detail="Missing X-GitHub-Delivery header.")

    payload = await request.body()
    secret = os.getenv("GITHUB_WEBHOOK_SECRET")

    if not verify_signature(payload, x_hub_signature_256, secret):
        raise HTTPException(status_code=401, detail="Invalid GitHub webhook signature.")

    try:
        event = parse_webhook(
            event=x_github_event,
            delivery_id=x_github_delivery,
            payload=payload,
        )
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.") from exc

    return GitHubWebhookResponse(**event.to_dict())
