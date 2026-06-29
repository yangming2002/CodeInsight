# CLAUDE.md - CodeInsight LLM Handoff Guide

This file is for Claude or any other coding agent that may continue the project.

The goal is not to generate random features. The goal is to keep building CodeInsight as a production-style GitHub PR review system.

## 1. Project Identity

CodeInsight is:

> a deterministic + probabilistic PR review system for Agent / LLM engineering projects.

It is not:

> a chatbot, IDE assistant, low-end GitHub Actions clone, or prompt-only demo.

The project should combine:

- GitHub PR events
- PR diff fetching
- changed-file parsing
- repository context
- deterministic policy rules
- later LLM reasoning
- structured review output
- tests, CI, and deployable service boundaries

## 2. Current Architecture

Current code layout:

```text
apps/api/       FastAPI routes and API schemas
core/github/    GitHub webhook parsing and PR diff fetching
core/parser/    Diff parsing and repository structure parsing
core/policy/    Deterministic review rules
core/review/    Review orchestration
configs/        Planned runtime configuration
tests/          Unit and API tests
docs/           Product, architecture, and learning docs
```

Keep responsibilities separated.

Do not put GitHub API calls inside `core/policy`.
Do not put FastAPI route logic inside `core/review`.
Do not put LLM calls directly into route handlers.
Do not mix retrieval, policy, and reasoning in one large function.

## 3. Current Capabilities

Implemented:

- `GET /health`
- `POST /review`
- `POST /webhooks/github`
- `GET /github/pull-diff`
- `GET /github/review-pr`
- `GET /repository/structure`
- policy findings as structured JSON
- GitHub webhook signature verification
- PR diff fetching
- changed-file parsing
- repository structure scanning
- Agent / LLM deterministic rules
- pytest and GitHub Actions CI

Run tests with:

```bash
python -m pytest
```

## 4. Development Principles

### 4.1 Keep Changes Small

Prefer one focused PR or commit per capability.

Good:

- add one parser
- add one endpoint
- add one policy rule group
- add one test file

Bad:

- add parser, vector DB, LLM client, dashboard, and deployment in one change

### 4.2 Rule First, LLM Second

Deterministic checks should run before LLM reasoning when possible.

Reasons:

- cheaper
- faster
- easier to test
- easier to explain
- less likely to hallucinate

### 4.3 Context Before Prompting

Before improving prompts, improve what context is supplied.

Priority:

1. changed files
2. repository roles
3. AST symbols
4. imports and references
5. related files
6. embeddings, only when needed

### 4.4 Structured Output Only

Review output must stay structured.

Findings should include:

- `rule_id`
- `title`
- `severity`
- `file`
- `line`
- `message`
- `suggestion`
- `source`

Do not return free-form review paragraphs as the only output.

## 5. Current Policy Rules

Implemented:

```text
SEC001  Hardcoded secret
DBG001  Debug print statement
MTN001  Unresolved TODO or FIXME
LLM001  LLM call without timeout
LLM002  Unvalidated LLM JSON parsing
AGT001  Unsafe shell execution
```

When adding rules:

- add tests
- update README rule table
- update `configs/rules.yaml`
- document non-obvious rules in `docs/`

## 6. Recommended Next Work

Best next steps:

1. Add Python AST parsing.
2. Extract functions, classes, and imports from changed files.
3. Attach repository role and changed-file metadata to findings.
4. Move policy rule definitions closer to YAML-backed configuration.
5. Add LLM client abstraction only after context and deterministic policy are stable.

Avoid:

- adding a dashboard too early
- adding vector DB before symbol/context retrieval
- adding multi-agent orchestration before a single reviewer is reliable
- calling an LLM directly from FastAPI route handlers

## 7. Git Workflow

Use feature branches for non-trivial changes:

```bash
git checkout master
git pull origin master
git checkout -b feature/short-description
```

Before committing:

```bash
git status
git diff
python -m pytest
```

Commit messages:

```text
feat: add capability
fix: correct behavior
docs: update documentation
test: add coverage
refactor: restructure without behavior change
```

## 8. README Progress Markers

When a capability is actually completed and tested, update README with `✅️`.

Do not mark planned work as complete.

## 9. Handoff Notes

If another LLM continues from here:

1. Read README first.
2. Read `docs/11_Positioning_And_Tool_Comparison.md`.
3. Read `docs/12_Agent_LLM_Review_Rules.md`.
4. Inspect `core/policy/engine.py`, `core/parser/`, and `core/review/service.py`.
5. Run tests before editing.

The project should keep moving toward a custom PR reviewer for Agent / LLM systems, not a generic lint wrapper.
