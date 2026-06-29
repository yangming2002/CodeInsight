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
