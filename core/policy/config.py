from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class RuleMetadata:
    rule_id: str
    title: str
    severity: str
    category: str | None = None
    status: str | None = None
    description: str | None = None


DEFAULT_RULE_METADATA = {
    "SEC001": RuleMetadata(
        rule_id="SEC001",
        title="Hardcoded secret",
        severity="critical",
        category="security",
    ),
    "DBG001": RuleMetadata(
        rule_id="DBG001",
        title="Debug print statement",
        severity="low",
        category="maintainability",
    ),
    "MTN001": RuleMetadata(
        rule_id="MTN001",
        title="Unresolved TODO or FIXME",
        severity="medium",
        category="maintainability",
    ),
    "LLM001": RuleMetadata(
        rule_id="LLM001",
        title="LLM call without timeout",
        severity="high",
        category="llm-reliability",
    ),
    "LLM002": RuleMetadata(
        rule_id="LLM002",
        title="Unvalidated LLM JSON parsing",
        severity="medium",
        category="llm-safety",
    ),
    "AGT001": RuleMetadata(
        rule_id="AGT001",
        title="Unsafe shell execution",
        severity="critical",
        category="agent-safety",
    ),
}


class RuleConfig:
    def __init__(self, rules: dict[str, RuleMetadata] | None = None) -> None:
        self._rules = rules or DEFAULT_RULE_METADATA

    @classmethod
    def load(cls, path: str | Path | None = None) -> RuleConfig:
        config_path = Path(path) if path else Path("configs/rules.yaml")
        if not config_path.exists():
            return cls()

        payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        rules = dict(DEFAULT_RULE_METADATA)
        for item in payload.get("rules", []):
            metadata = _parse_rule_metadata(item)
            rules[metadata.rule_id] = metadata

        return cls(rules=rules)

    def get(self, rule_id: str) -> RuleMetadata:
        return self._rules.get(
            rule_id,
            RuleMetadata(rule_id=rule_id, title=rule_id, severity="medium"),
        )


def _parse_rule_metadata(item: dict[str, Any]) -> RuleMetadata:
    rule_id = str(item["id"])
    fallback = DEFAULT_RULE_METADATA.get(rule_id)
    return RuleMetadata(
        rule_id=rule_id,
        title=str(item.get("title") or (fallback.title if fallback else rule_id)),
        severity=str(item.get("severity") or (fallback.severity if fallback else "medium")),
        category=item.get("category") or (fallback.category if fallback else None),
        status=item.get("status") or (fallback.status if fallback else None),
        description=item.get("description") or (fallback.description if fallback else None),
    )
