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
    context: dict[str, object] | None = None


class ChangedFile(BaseModel):
    path: str
    old_path: str | None
    new_path: str | None
    status: str
    added_lines: int
    deleted_lines: int


class ReviewContextFile(BaseModel):
    path: str
    role: str
    status: str
    added_lines: int
    deleted_lines: int
    symbols: list[dict[str, object]]
    imports: list[dict[str, object]]


class ReviewContext(BaseModel):
    changed_file_roles: list[str]
    touched_symbols: list[str]
    related_imports: list[str]
    files: list[ReviewContextFile]


class ReviewResponse(BaseModel):
    repository: str | None
    pr_number: int | None
    summary: str
    changed_files: list[ChangedFile]
    changed_file_count: int
    context: ReviewContext
    findings: list[Finding]
    finding_count: int
    llm_summary: str | None = None


class GitHubWebhookResponse(BaseModel):
    accepted: bool
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


class PullRequestDiffResponse(BaseModel):
    repository: str
    pr_number: int
    diff: str
    source_url: str


class RepositoryFileResponse(BaseModel):
    path: str
    extension: str
    role: str
    size_bytes: int


class RepositorySymbolResponse(BaseModel):
    name: str
    kind: str
    file: str
    line: int
    end_line: int | None
    parent: str | None = None


class RepositoryImportResponse(BaseModel):
    module: str
    name: str | None
    alias: str | None
    file: str
    line: int


class RepositoryStructureResponse(BaseModel):
    root: str
    file_count: int
    symbol_count: int
    files: list[RepositoryFileResponse]
    symbols: list[RepositorySymbolResponse]
    imports: list[RepositoryImportResponse]
