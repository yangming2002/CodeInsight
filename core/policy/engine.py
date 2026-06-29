from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class DiffLine:
    file: str
    line_number: int | None
    content: str


@dataclass(frozen=True)
class PolicyFinding:
    rule_id: str
    title: str
    severity: str
    file: str
    line: int | None
    message: str
    suggestion: str
    source: str = "policy"

    def to_dict(self) -> dict[str, object]:
        return {
            "rule_id": self.rule_id,
            "title": self.title,
            "severity": self.severity,
            "file": self.file,
            "line": self.line,
            "message": self.message,
            "suggestion": self.suggestion,
            "source": self.source,
        }


class PolicyEngine:
    """Deterministic checks that run before expensive LLM review."""

    _SECRET_PATTERN = re.compile(
        r"(?i)\b(password|passwd|token|secret|api[_-]?key|access[_-]?key)\b\s*[:=]\s*['\"][^'\"]{6,}['\"]"
    )
    _LLM_CALL_PATTERN = re.compile(
        r"\b(client\.)?(responses\.create|chat\.completions\.create|messages\.create)\s*\("
    )
    _LLM_JSON_LOADS_PATTERN = re.compile(
        r"\bjson\.loads\s*\(\s*[^)]*(response|content|completion|model_output|llm_output)"
    )

    def review(self, diff: str) -> list[PolicyFinding]:
        findings: list[PolicyFinding] = []

        for line in parse_added_lines(diff):
            findings.extend(self._review_line(line))

        return findings

    def _review_line(self, line: DiffLine) -> Iterable[PolicyFinding]:
        content = line.content.strip()

        if self._SECRET_PATTERN.search(content):
            yield PolicyFinding(
                rule_id="SEC001",
                title="Hardcoded secret",
                severity="critical",
                file=line.file,
                line=line.line_number,
                message="The added line appears to contain a hardcoded credential.",
                suggestion="Move secrets to environment variables or a managed secret store.",
            )

        if "print(" in content:
            yield PolicyFinding(
                rule_id="DBG001",
                title="Debug print statement",
                severity="low",
                file=line.file,
                line=line.line_number,
                message="The added line contains a print statement that may be leftover debugging code.",
                suggestion="Use structured logging or remove the statement before merging.",
            )

        if "TODO" in content.upper() or "FIXME" in content.upper():
            yield PolicyFinding(
                rule_id="MTN001",
                title="Unresolved TODO or FIXME",
                severity="medium",
                file=line.file,
                line=line.line_number,
                message="The added line contains an unresolved TODO or FIXME marker.",
                suggestion="Resolve it now or link it to a tracked issue with an owner.",
            )

        if self._LLM_CALL_PATTERN.search(content) and "timeout" not in content:
            yield PolicyFinding(
                rule_id="LLM001",
                title="LLM call without timeout",
                severity="high",
                file=line.file,
                line=line.line_number,
                message="The added line appears to call an LLM API without an explicit timeout.",
                suggestion="Set a request timeout and handle timeout failures before merging.",
            )

        if "shell=True" in content:
            yield PolicyFinding(
                rule_id="AGT001",
                title="Unsafe shell execution",
                severity="critical",
                file=line.file,
                line=line.line_number,
                message="The added line enables shell execution, which is risky for agent tools.",
                suggestion="Use argument-list subprocess calls and enforce an allowlist for tool commands.",
            )

        if self._LLM_JSON_LOADS_PATTERN.search(content):
            yield PolicyFinding(
                rule_id="LLM002",
                title="Unvalidated LLM JSON parsing",
                severity="medium",
                file=line.file,
                line=line.line_number,
                message="The added line appears to parse model output as JSON without schema validation.",
                suggestion="Validate LLM output with a typed schema before using it in application logic.",
            )


def parse_added_lines(diff: str) -> list[DiffLine]:
    added_lines: list[DiffLine] = []
    current_file = "unknown"
    new_line_number: int | None = None

    for raw_line in diff.splitlines():
        if raw_line.startswith("+++ "):
            current_file = raw_line[4:].strip()
            if current_file.startswith("b/"):
                current_file = current_file[2:]
            continue

        if raw_line.startswith("@@"):
            new_line_number = _parse_hunk_new_start(raw_line)
            continue

        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            added_lines.append(
                DiffLine(file=current_file, line_number=new_line_number, content=raw_line[1:])
            )
            if new_line_number is not None:
                new_line_number += 1
            continue

        if raw_line.startswith("-") and not raw_line.startswith("---"):
            continue

        if new_line_number is not None:
            new_line_number += 1

    return added_lines


def _parse_hunk_new_start(hunk_header: str) -> int | None:
    match = re.search(r"\+(\d+)(?:,\d+)?", hunk_header)
    if not match:
        return None
    return int(match.group(1))
