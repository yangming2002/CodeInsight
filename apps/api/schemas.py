from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str


class ReviewRequest(BaseModel):
    diff: str = Field(..., min_length=1, description="Unified diff content to review.")
    repository: str | None = Field(default=None, description="Repository full name, if available.")
    pr_number: int | None = Field(default=None, ge=1, description="Pull request number, if available.")


class Finding(BaseModel):
    rule_id: str
    title: str
    severity: str
    file: str
    line: int | None = None
    message: str
    suggestion: str
    source: str = "policy"


class ReviewResponse(BaseModel):
    repository: str | None
    pr_number: int | None
    summary: str
    findings: list[Finding]
    finding_count: int
    llm_summary: str | None = None
