from pathlib import Path

from core.context import ReviewContextBuilder
from core.parser import RepositoryStructureParser, parse_added_line_numbers, parse_changed_files
from core.review.service import review_diff


def test_review_context_builder_attaches_roles_symbols_and_imports(tmp_path: Path) -> None:
    _write(
        tmp_path / "core" / "review" / "service.py",
        """from core.policy import PolicyEngine

class Reviewer:
    def review(self):
        return PolicyEngine()

def unrelated():
    return None
""",
    )
    diff = """diff --git a/core/review/service.py b/core/review/service.py
--- a/core/review/service.py
+++ b/core/review/service.py
@@ -4,2 +4,3 @@
+        print("debug")
         return PolicyEngine()
"""

    changed_files = parse_changed_files(diff)
    added_line_numbers = parse_added_line_numbers(diff)
    snapshot = RepositoryStructureParser().parse(tmp_path)
    context = ReviewContextBuilder().build(
        changed_files=changed_files,
        snapshot=snapshot,
        added_line_numbers=added_line_numbers,
    )

    assert context.changed_file_roles == ["core"]
    assert context.touched_symbols == ["Reviewer", "Reviewer.review"]
    assert context.related_imports == ["core.policy.PolicyEngine"]
    assert context.files[0].role == "core"
    assert [symbol.name for symbol in context.files[0].symbols] == [
        "Reviewer",
        "review",
        "unrelated",
    ]
    assert [symbol.name for symbol in context.files[0].touched_symbols] == [
        "Reviewer",
        "review",
    ]


def test_review_diff_includes_context_in_report_and_findings(tmp_path: Path) -> None:
    _write(
        tmp_path / "apps" / "api" / "main.py",
        "def route():\n    return True\n\ndef untouched():\n    return False\n",
    )
    diff = """diff --git a/apps/api/main.py b/apps/api/main.py
--- a/apps/api/main.py
+++ b/apps/api/main.py
@@ -1,2 +1,3 @@
 def route():
+    print("debug")
     return True
"""

    report = review_diff(diff=diff, repository_root=tmp_path)

    assert report["context"]["changed_file_roles"] == ["api"]
    assert report["context"]["touched_symbols"] == ["route"]
    assert [symbol["name"] for symbol in report["context"]["files"][0]["symbols"]] == [
        "route",
        "untouched",
    ]
    assert [
        symbol["name"] for symbol in report["context"]["files"][0]["touched_symbols"]
    ] == ["route"]
    assert report["findings"][0]["context"]["file_role"] == "api"
    assert report["findings"][0]["context"]["touched_symbols"] == ["route"]


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
