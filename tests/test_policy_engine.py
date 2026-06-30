import yaml

from core.policy import RuleConfig
from core.policy.engine import PolicyEngine, parse_added_lines


def test_parse_added_lines_tracks_file_and_line_number() -> None:
    diff = """diff --git a/service.py b/service.py
--- a/service.py
+++ b/service.py
@@ -10,2 +10,3 @@
 context = {}
+print("debug")
 return context
"""

    lines = parse_added_lines(diff)

    assert len(lines) == 1
    assert lines[0].file == "service.py"
    assert lines[0].line_number == 11
    assert lines[0].content == 'print("debug")'


def test_policy_engine_detects_mvp_rules() -> None:
    diff = """diff --git a/settings.py b/settings.py
--- a/settings.py
+++ b/settings.py
@@ -1,1 +1,4 @@
+api_key = "abcdef123456"
+print("temporary")
+# FIXME: replace mock
 DEBUG = False
"""

    findings = PolicyEngine().review(diff)
    rule_ids = [finding.rule_id for finding in findings]

    assert rule_ids == ["SEC001", "DBG001", "MTN001"]


def test_policy_engine_detects_agent_llm_risks() -> None:
    diff = """diff --git a/core/reasoning/reviewer.py b/core/reasoning/reviewer.py
--- a/core/reasoning/reviewer.py
+++ b/core/reasoning/reviewer.py
@@ -1,1 +1,4 @@
+response = client.responses.create(model="gpt-5", input=prompt)
+subprocess.run(command, shell=True)
+payload = json.loads(response.output_text)
 REVIEWER = "code"
"""

    findings = PolicyEngine().review(diff)
    rule_ids = [finding.rule_id for finding in findings]

    assert rule_ids == ["LLM001", "AGT001", "LLM002"]


def test_policy_engine_allows_llm_call_with_timeout() -> None:
    diff = """diff --git a/core/reasoning/reviewer.py b/core/reasoning/reviewer.py
--- a/core/reasoning/reviewer.py
+++ b/core/reasoning/reviewer.py
@@ -1,1 +1,2 @@
+response = client.responses.create(model="gpt-5", input=prompt, timeout=30)
 REVIEWER = "code"
"""

    findings = PolicyEngine().review(diff)

    assert [finding.rule_id for finding in findings] == []


def test_policy_engine_uses_rule_metadata_from_yaml(tmp_path) -> None:
    config_path = tmp_path / "rules.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "rules": [
                    {
                        "id": "DBG001",
                        "title": "Temporary stdout debug",
                        "severity": "medium",
                        "category": "maintainability",
                        "status": "implemented",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    diff = """diff --git a/service.py b/service.py
--- a/service.py
+++ b/service.py
@@ -1,1 +1,2 @@
+print("debug")
 return True
"""

    findings = PolicyEngine(rule_config=RuleConfig.load(config_path)).review(diff)

    assert findings[0].rule_id == "DBG001"
    assert findings[0].title == "Temporary stdout debug"
    assert findings[0].severity == "medium"
