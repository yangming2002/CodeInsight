# Changelog

All notable changes to CodeInsight are documented here.

## Unreleased

### Added

- FastAPI service with `/health`, `/review`, `/webhooks/github`, `/github/pull-diff`, `/github/review-pr`, and `/repository/structure`.
- Deterministic policy engine with structured JSON findings.
- GitHub webhook receiver with optional signature verification.
- GitHub PR diff fetcher using the GitHub diff media type.
- Diff changed-file parser and local repository structure parser.
- Python AST parser and repository symbol extraction.
- Agent / LLM engineering rules for missing LLM timeouts, unsafe `shell=True`, and unvalidated model JSON parsing.
- Pytest test suite and GitHub Actions CI.
- Dockerfile for containerized API startup.

### Changed

- README now tracks completed MVP capabilities with `✅️` markers.
- Project positioning docs clarify why CodeInsight is not a low-end clone of GitHub Actions, CodeQL, Copilot Code Review, or Continue.

## 0.1.0 - MVP Foundation

Initial MVP foundation for a GitHub PR review system.
