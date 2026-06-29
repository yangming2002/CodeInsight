# Roadmap

CodeInsight is being built as a production-style AI engineering project, not a prompt-only demo.

## Completed

- FastAPI MVP service.
- Structured `/review` API.
- Deterministic policy engine.
- GitHub webhook receiver.
- GitHub PR diff fetcher.
- Changed-file parser.
- Local repository structure parser.
- One-call GitHub PR review API.
- Agent / LLM deterministic review rules.
- Pytest test suite.
- GitHub Actions CI.
- Dockerfile.
- Project positioning and learning docs.

## Near-Term

### Repository Context

- Add Python AST parsing.
- Extract functions, classes, imports, and call-like references.
- Attach repository role context to review findings.
- Improve changed-file summaries for multi-file PRs.

### Policy Engine

- Move deterministic rules toward YAML-backed configuration.
- Add project-specific architecture rules.
- Distinguish production code from tests.
- Add rule categories and confidence fields.

### LLM Reasoning

- Add a model client abstraction.
- Add structured output schemas for LLM review.
- Add timeout, retry, and fallback handling.
- Add a rule-first, LLM-second review pipeline.

## Mid-Term

- GitHub PR comment publishing.
- Async API + worker pipeline.
- Review task status endpoint.
- Evaluation datasets and metrics.
- Latency and cost tracking.
- Docker Compose for API, worker, Redis, and optional database.

## Later

- Symbol-based retrieval.
- AST-aware context builder.
- Optional vector retrieval.
- Dashboard or lightweight report viewer.
- Multi-language parsing.
