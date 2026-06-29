# CodeInsight Development Handoff

Last updated: 2026-06-29

This document preserves the current project state so development can continue later without relying on chat history.

## Current Goal

Build CodeInsight as a production-style GitHub PR review system for Agent / LLM engineering projects.

The project should not become a generic low-end clone of GitHub Actions, CodeQL, Copilot Code Review, or Continue.

The intended direction is:

```text
GitHub PR
  -> webhook / PR number
  -> diff fetcher
  -> changed-file parser
  -> repository context
  -> deterministic policy engine
  -> later LLM reasoning
  -> structured review report
  -> later GitHub PR comments
```

## Current Repository State

Main branch:

```text
master
```

Latest important commits:

```text
d107daf feat: add Python AST symbol extraction
2ca9c6c docs: clarify pipeline progress markers
731af09 docs: refresh project maintenance files
03b300e feat: add agent LLM review rules
b3c25fe feat: add PR review pipeline context parsing
```

Working tree was clean at handoff time.

## Implemented Capabilities

### API

Implemented in `apps/api/`:

- `GET /health`
- `POST /review`
- `POST /webhooks/github`
- `GET /github/pull-diff`
- `GET /github/review-pr`
- `GET /repository/structure`

### GitHub Integration

Implemented in `core/github/`:

- GitHub webhook payload parsing.
- Optional GitHub webhook signature verification with `GITHUB_WEBHOOK_SECRET`.
- PR diff fetching from GitHub API.
- Optional GitHub API token via `GITHUB_TOKEN`.

### Parsing / Context

Implemented in `core/parser/`:

- Unified diff changed-file parsing.
- Local repository file inventory.
- File role inference such as `api`, `core`, `test`, `docs`, `config`.
- Python AST parsing using the standard library `ast`.
- Symbol extraction:
  - classes
  - functions
  - async functions
  - method parent relationship
- Import extraction:
  - `import x`
  - `from x import y`

### Policy Engine

Implemented in `core/policy/engine.py`:

Generic rules:

- `SEC001`: hardcoded secret
- `DBG001`: debug `print()`
- `MTN001`: unresolved TODO / FIXME

Agent / LLM rules:

- `LLM001`: LLM call without explicit timeout
- `LLM002`: likely model output parsed with `json.loads(...)` without schema validation
- `AGT001`: unsafe `shell=True`

### Review Pipeline

Implemented in `core/review/service.py`:

- Accepts a unified diff.
- Extracts changed files.
- Runs deterministic policy rules.
- Returns structured JSON report with:
  - repository
  - PR number
  - summary
  - changed files
  - findings
  - finding count
  - LLM placeholder summary

### Testing / CI

Current test command:

```bash
python -m pytest
```

Last known result:

```text
21 passed, 1 warning
```

The warning is from FastAPI / Starlette TestClient dependency behavior and does not currently affect project behavior.

GitHub Actions CI exists at:

```text
.github/workflows/ci.yml
```

## Real Manual Test Already Done

The user tested a real GitHub PR:

```text
GET /github/review-pr?repository=yangming2002/CodeInsight&pr_number=1
```

Observed result:

```json
{
  "repository": "yangming2002/CodeInsight",
  "pr_number": 1,
  "summary": "Policy review completed with no issues found in the submitted diff.",
  "changed_files": [
    {
      "path": "README.md",
      "old_path": "README.md",
      "new_path": "README.md",
      "status": "modified",
      "added_lines": 1,
      "deleted_lines": 1
    }
  ],
  "changed_file_count": 1,
  "findings": [],
  "finding_count": 0,
  "llm_summary": "LLM reasoning is not enabled in MVP v0."
}
```

Conclusion:

```text
Real GitHub PR diff fetch -> changed-file parse -> policy review -> structured JSON output works.
```

No findings were expected because PR #1 only changed README text.

## Git Workflow Practice Already Done

The user practiced a company-style PR flow with README:

1. Created feature branch.
2. Changed one README line.
3. Pushed branch.
4. Created PR #1.
5. Commented in `Files changed`.
6. Updated README again.
7. Pushed update to same PR.
8. Resolved comment.
9. Merged PR.
10. Deleted local feature branch.

This was useful for learning real company PR workflow.

## Documentation / Maintenance Files

Recently updated:

- `README.md`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `ROADMAP.md`
- `LICENSE`
- `CLAUDE.md`
- `configs/settings.yaml`
- `configs/rules.yaml`
- `configs/models.yaml`

License:

```text
MIT
```

`CLAUDE.md` is now an LLM handoff guide so Claude or another coding agent can continue if needed.

## Important Design Decisions

### Do Not Overbuild Yet

Avoid adding too much infrastructure too early:

- no dashboard yet
- no vector DB yet
- no multi-agent orchestration yet
- no Kubernetes yet

### Rule First, LLM Second

Current system is deterministic-first.

LLM reasoning should be added only after context and rule structure are stable.

### Context Before Prompting

Before writing prompts, improve:

- changed files
- repository roles
- symbols
- imports
- related files
- later AST references

### Structured Output Only

Do not make review output free-form only.

Every finding should remain traceable and structured:

```text
rule_id
title
severity
file
line
message
suggestion
source
```

## Recommended Next Development

Best next step:

```text
Attach context metadata to findings.
```

Concrete implementation idea:

1. When `/review` runs, it already knows changed files.
2. Repository parser can now produce roles, symbols, and imports.
3. Add a lightweight `core/context/` module that builds review context.
4. Include context summary in review output.

Possible next API/report fields:

```json
{
  "context": {
    "changed_file_roles": ["docs", "core"],
    "touched_symbols": ["PolicyEngine.review"],
    "related_imports": ["core.policy"]
  }
}
```

Alternative next step:

```text
Move deterministic rules toward YAML-backed configuration.
```

This would connect `configs/rules.yaml` to `core/policy/engine.py`.

## Near-Term Backlog

High-value next tasks:

- Add `core/context/` module.
- Attach repository role metadata to findings.
- Attach changed-file summaries to findings.
- Add import-based related-file lookup.
- Extract call-like references from Python AST.
- Add confidence/source fields for future LLM findings.
- Start an evaluation dataset under `evaluation/datasets`.
- Add GitHub PR comment publishing.
- Add async worker pipeline later.

## Things To Avoid Next Session

Avoid:

- building a dashboard before the backend review pipeline is useful
- adding Qdrant/Milvus before simple symbol/import retrieval
- making LLM calls directly from FastAPI route handlers
- creating vague natural-language-only review output
- marking README items complete before code and tests exist

## How To Resume

Recommended startup commands:

```bash
git status
git pull origin master
python -m pytest
```

Then inspect:

```text
README.md
CLAUDE.md
docs/11_Positioning_And_Tool_Comparison.md
docs/12_Agent_LLM_Review_Rules.md
core/parser/
core/policy/engine.py
core/review/service.py
```

Suggested first question next session:

> Continue by adding `core/context/` to attach repository role, symbol, and import context to review reports.

