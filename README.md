# CodeInsight

CodeInsight is a GitHub Pull Request review system for Agent and LLM engineering projects. It combines deterministic policy checks, repository context extraction, and structured review reports so later LLM reasoning can operate on traceable inputs instead of raw diffs alone.

## Capability Status

### Currently Implemented

| Area | Capability |
| --- | --- |
| API service | FastAPI application with `GET /health`, `POST /review`, `POST /webhooks/github`, `GET /github/pull-diff`, `GET /github/review-pr`, and `GET /repository/structure` |
| GitHub integration | Parse pull request webhook payloads, optionally verify webhook signatures, and fetch pull request diffs with optional `GITHUB_TOKEN` |
| Diff parsing | Parse changed files, statuses, added/deleted line counts, and added line numbers from unified diffs |
| Repository parsing | Scan local repository files, infer file roles, and skip common generated or dependency directories |
| Python AST parsing | Extract Python classes, functions, async functions, parent relationships, and imports |
| Review context | Attach changed-file roles, related imports, directly touched symbols, and import-based related files to structured review reports |
| Policy engine | Run deterministic checks before LLM reasoning |
| Rule metadata | Load implemented rule titles, severities, categories, and descriptions from `configs/rules.yaml` |
| Agent/LLM rules | Detect LLM calls without timeout, unsafe `shell=True`, and unvalidated JSON parsing of likely model output |
| Generic rules | Detect likely hardcoded secrets, debug `print()` statements, and unresolved TODO/FIXME comments |
| Output | Return structured JSON findings with rule id, severity, file, line, message, suggestion, source, and context |
| Testing and CI | Run automated tests with pytest and GitHub Actions |

### Planned

| Area | Future Capability |
| --- | --- |
| Context precision | Expand symbol matching, improve related-file ranking, and extract call-like references |
| Rule system | Add validation for malformed rule metadata and gradually support project-specific configurable policies |
| GitHub review workflow | Publish structured findings as GitHub PR comments |
| LLM reasoning | Add LLM reviewer stages after deterministic context and policy inputs are stable |
| Evaluation harness | Build review datasets, replay fixed diffs, compare expected findings, and measure hit rate, false positives, latency, and cost |
| Reliability | Add async worker execution, retries, caching, and cost/latency tracking |
| Deployment | Add production-oriented deployment docs and service packaging |

## Quick Start

Install dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run tests:

```bash
python -m pytest
```

Start the API:

```bash
uvicorn apps.api.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Review API

Example request:

```bash
curl -X POST "http://127.0.0.1:8000/review" \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "yangming2002/CodeInsight",
    "pr_number": 1,
    "diff": "diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1,1 +1,3 @@\n+password = \"super-secret-value\"\n+print(\"debug\")\n return True"
  }'
```

Example response:

```json
{
  "repository": "yangming2002/CodeInsight",
  "pr_number": 1,
  "summary": "Policy review found 2 issue(s) in the submitted diff.",
  "changed_files": [
    {
      "path": "app.py",
      "old_path": "app.py",
      "new_path": "app.py",
      "status": "modified",
      "added_lines": 2,
      "deleted_lines": 0
    }
  ],
  "changed_file_count": 1,
  "context": {
    "changed_file_roles": ["unknown"],
    "touched_symbols": [],
    "related_imports": [],
    "related_files": [],
    "files": [
      {
        "path": "app.py",
        "role": "unknown",
        "status": "modified",
        "added_lines": 2,
        "deleted_lines": 0,
        "symbols": [],
        "touched_symbols": [],
        "imports": [],
        "related_files": []
      }
    ]
  },
  "findings": [
    {
      "rule_id": "SEC001",
      "title": "Hardcoded secret",
      "severity": "critical",
      "file": "app.py",
      "line": 1,
      "message": "The added line appears to contain a hardcoded credential.",
      "suggestion": "Move secrets to environment variables or a managed secret store.",
      "source": "policy",
      "context": {
        "file_role": "unknown",
        "touched_symbols": [],
        "related_imports": [],
        "related_files": []
      }
    },
    {
      "rule_id": "DBG001",
      "title": "Debug print statement",
      "severity": "low",
      "file": "app.py",
      "line": 2,
      "message": "The added line contains a print statement that may be leftover debugging code.",
      "suggestion": "Use structured logging or remove the statement before merging.",
      "source": "policy",
      "context": {
        "file_role": "unknown",
        "touched_symbols": [],
        "related_imports": [],
        "related_files": []
      }
    }
  ],
  "finding_count": 2,
  "llm_summary": "LLM reasoning is not enabled yet."
}
```

## GitHub Webhook API

Endpoint:

```text
POST /webhooks/github
```

Required GitHub headers:

```text
X-GitHub-Event
X-GitHub-Delivery
```

Optional security header:

```text
X-Hub-Signature-256
```

If `GITHUB_WEBHOOK_SECRET` is configured, CodeInsight verifies `X-Hub-Signature-256` before parsing the payload.

CodeInsight supports `pull_request` events and returns a structured task envelope:

```json
{
  "accepted": true,
  "event": "pull_request",
  "delivery_id": "delivery-1",
  "action": "opened",
  "repository": "yangming2002/CodeInsight",
  "pr_number": 12,
  "base_sha": "base123",
  "head_sha": "head456",
  "task_id": "gh_...",
  "ignored": false,
  "ignore_reason": null
}
```

## GitHub Diff API

Endpoint:

```text
GET /github/pull-diff?repository=owner/repo&pr_number=1
```

If `GITHUB_TOKEN` is configured, CodeInsight sends it as a bearer token when calling GitHub.

Example response:

```json
{
  "repository": "owner/repo",
  "pr_number": 1,
  "diff": "diff --git a/app.py b/app.py\n...",
  "source_url": "https://api.github.com/repos/owner/repo/pulls/1"
}
```

## GitHub PR Review API

Endpoint:

```text
GET /github/review-pr?repository=owner/repo&pr_number=1
```

This endpoint fetches a GitHub PR diff, parses changed files, builds review context, runs the policy engine, and returns a structured review report.

## Repository Structure API

Endpoint:

```text
GET /repository/structure
```

This endpoint scans the local repository and returns a lightweight file inventory, inferred roles, Python symbols, and Python imports.

## Architecture

```text
HTTP Client
    |
    v
apps/api
    |
    v
core/review
    |
    v
core/context + core/policy
    |
    v
Structured JSON Report
```

## Project Structure

```text
apps/api/       FastAPI application and API schemas
core/parser/    Diff and repository structure parsing
core/context/   Review context construction
core/policy/    Deterministic rule engine and rule metadata loading
core/review/    Review orchestration service
configs/        Runtime configuration and rule metadata
tests/          API, parser, context, and policy tests
docs/           Product, architecture, and learning documents
```

## Current Policy Rules

| Rule | Severity | Purpose |
| --- | --- | --- |
| `SEC001` | critical | Detect hardcoded secrets |
| `DBG001` | low | Detect debug `print()` statements |
| `MTN001` | medium | Detect unresolved TODO/FIXME comments |
| `LLM001` | high | Detect LLM calls without explicit timeout |
| `LLM002` | medium | Detect direct JSON parsing of model output without schema validation |
| `AGT001` | critical | Detect unsafe `shell=True` execution in agent/tool code |

Rule metadata is loaded from:

```text
configs/rules.yaml
```

## Evaluation Harness Status

CodeInsight currently has normal automated tests, but it does not yet have a dedicated review evaluation harness.

| Item | Status | Notes |
| --- | --- | --- |
| Pytest unit/API tests | Implemented | Validates parser, context, policy, and API behavior |
| GitHub Actions CI | Implemented | Runs the automated test suite |
| Evaluation dataset | Planned | Should contain fixed diffs or PR fixtures with expected findings |
| Review replay harness | Planned | Should run CodeInsight against stored samples and compare structured output |
| Metrics reporting | Planned | Should track hit rate, false positives, false negatives, latency, and eventually LLM cost |

The harness should be separate from ordinary tests: tests protect implementation correctness, while the evaluation harness should measure review quality over realistic examples.

## Docker

Build:

```bash
docker build -t codeinsight .
```

Run:

```bash
docker run --rm -p 8000:8000 codeinsight
```

## Development Direction

| Principle | Direction |
| --- | --- |
| Do not duplicate mature tools | CodeInsight is not a replacement for GitHub Actions, CodeQL, Secret Scanning, Dependabot, Copilot Code Review, or Continue |
| Rule first, LLM second | Deterministic policy and context extraction should be stable before adding LLM reasoning |
| Structured output | Findings should stay machine-readable, traceable, testable, and suitable for GitHub PR comments |
| Agent/LLM focus | Prioritize review rules for LLM calls, tool execution, prompt/schema safety, evaluation coverage, and agent boundaries |
| Evaluation mindset | Future LLM review quality should be measured with datasets and metrics, not judged only by plausible prose |
