# CodeInsight Development Handoff

Last updated: 2026-06-30

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

Rule metadata is now loaded through `core/policy/config.py` from:

```text
configs/rules.yaml
```

Current scope:

- Detection logic still lives in Python code.
- YAML controls implemented rule metadata such as title, severity, category, status, and description.
- This is intentionally not a full rule DSL yet.

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
  - review context
  - findings
  - finding count
  - LLM placeholder summary

### Review Context

Implemented in `core/context/`:

- Builds lightweight PR review context from changed files and repository snapshots.
- Adds changed-file role summaries.
- Adds touched Python symbols for changed files.
- Adds related imports for changed files.
- Attaches file-level context metadata to each finding.

### Testing / CI

Current test command:

```bash
python -m pytest
```

Last known result:

```text
24 passed, 1 warning
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

Completed next step:

```text
Attach context metadata to findings.
```

Implemented shape:

1. `/review` parses changed files from the diff.
2. `RepositoryStructureParser` produces roles, symbols, and imports.
3. `core/context/` builds a lightweight review context.
4. Review output includes a top-level context summary.
5. Each finding includes file-level context metadata.

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

Completed next step:

```text
Move deterministic rules toward YAML-backed configuration.
```

Implemented as YAML-backed rule metadata while keeping detection logic deterministic and code-owned.

Best next step now:

```text
Make context extraction more precise.
```

This would use changed line ranges to distinguish symbols that are directly touched from symbols that merely live in changed files.

## Near-Term Backlog

High-value next tasks:

- Use changed line ranges to identify directly touched symbols.
- Add import-based related-file lookup.
- Add config validation errors for malformed rule metadata.
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

> Continue by making context extraction more precise with changed line ranges and directly touched symbols.
