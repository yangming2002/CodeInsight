from fastapi import FastAPI

from apps.api.schemas import HealthResponse, ReviewRequest, ReviewResponse
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
