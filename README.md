# CodeInsight

CodeInsight is a GitHub Pull Request code review system built with FastAPI, deterministic policy checks, and an LLM-ready review pipeline for hands-on production-style AI engineering practice.

MVP v0 can:

- start a FastAPI service ✅️
- expose `GET /health` ✅️
- expose `POST /review` ✅️
- accept a unified diff ✅️
- run deterministic policy checks before LLM reasoning ✅️
- return structured JSON findings ✅️
- run automated tests with pytest ✅️
- run CI with GitHub Actions ✅️
- receive GitHub webhook events ✅️
- parse pull request webhook payloads ✅️
- verify GitHub webhook signatures when `GITHUB_WEBHOOK_SECRET` is configured ✅️
- fetch GitHub pull request diffs ✅️
- parse changed files from unified diffs ✅️
- scan local repository structure ✅️
- review a GitHub PR through one API call ✅️

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
  "findings": [
    {
      "rule_id": "SEC001",
      "title": "Hardcoded secret",
      "severity": "critical",
      "file": "app.py",
      "line": 1,
      "message": "The added line appears to contain a hardcoded credential.",
      "suggestion": "Move secrets to environment variables or a managed secret store.",
      "source": "policy"
    },
    {
      "rule_id": "DBG001",
      "title": "Debug print statement",
      "severity": "low",
      "file": "app.py",
      "line": 2,
      "message": "The added line contains a print statement that may be leftover debugging code.",
      "suggestion": "Use structured logging or remove the statement before merging.",
      "source": "policy"
    }
  ],
  "finding_count": 2,
  "llm_summary": "LLM reasoning is not enabled in MVP v0."
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

MVP v0 supports `pull_request` events and returns a structured task envelope:

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

This endpoint fetches a GitHub PR diff, parses changed files, runs the policy engine, and returns a structured review report.

## Repository Structure API

Endpoint:

```text
GET /repository/structure
```

This endpoint scans the local repository and returns a lightweight file inventory with inferred roles such as `api`, `core`, `test`, `docs`, and `config`.

## MVP Architecture

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
core/policy
    |
    v
Structured JSON Report
```

## Project Structure

```text
apps/api/       FastAPI application and API schemas
core/parser/    Diff and repository structure parsing
core/policy/    Deterministic rule engine
core/review/    Review orchestration service
tests/          API and policy tests
docs/           Product, architecture, and learning documents
```

## Current Policy Rules

| Rule | Severity | Purpose |
| --- | --- | --- |
| `SEC001` | critical | Detect hardcoded secrets |
| `DBG001` | low | Detect debug `print()` statements |
| `MTN001` | medium | Detect unresolved TODO/FIXME comments |

## Docker

Build:

```bash
docker build -t codeinsight .
```

Run:

```bash
docker run --rm -p 8000:8000 codeinsight
```

## 30 Day Vibe Coding Plan

Goal:
Build a production-ready Code Intelligence Platform starting from zero.

Primary Feature:
GitHub PR Code Review System

### Week 1 - Foundation

- Day 1: Initialize repo structure and FastAPI backend. ✅️
- Day 2: Implement GitHub webhook receiver. ✅️
- Day 3: Implement diff fetcher. ✅️
- Day 4: Build basic repository parser. ✅️
- Day 5: Integrate basic AST parsing.
- Day 6: Build symbol extraction.
- Day 7: End-to-end pipeline v0: PR -> diff -> simple review -> output. ✅️

### Week 2 - Context Engine

- Add embedding-based retrieval.
- Add symbol-based retrieval.
- Build AST-based context extraction.
- Add hybrid ranking.
- Build context builder.

### Week 3 - Reasoning Layer

- Build single reviewer.
- Add bug, security, architecture, and performance analysis.
- Merge reasoning outputs.
- Generate structured reports.

### Week 4 - Productization

- Build YAML rule engine.
- Add policy validation before LLM.
- Integrate GitHub PR comments.
- Add evaluation dataset.
- Optimize latency and caching.
- Release v1.0 MVP.
