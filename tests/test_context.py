from pathlib import Path

from core.context import ReviewContextBuilder
from core.parser import RepositoryStructureParser, parse_changed_files
from core.review.service import review_diff


def test_review_context_builder_attaches_roles_symbols_and_imports(tmp_path: Path) -> None:
    _write(
        tmp_path / "core" / "review" / "service.py",
        """from core.policy import PolicyEngine

class Reviewer:
    def review(self):
        return PolicyEngine()
""",
    )
    diff = """diff --git a/core/review/service.py b/core/review/service.py
--- a/core/review/service.py
+++ b/core/review/service.py
@@ -1,1 +1,2 @@
+print("debug")
 return True
"""

    changed_files = parse_changed_files(diff)
    snapshot = RepositoryStructureParser().parse(tmp_path)
    context = ReviewContextBuilder().build(changed_files=changed_files, snapshot=snapshot)

    assert context.changed_file_roles == ["core"]
    assert context.touched_symbols == ["Reviewer", "Reviewer.review"]
    assert context.related_imports == ["core.policy.PolicyEngine"]
    assert context.files[0].role == "core"


def test_review_diff_includes_context_in_report_and_findings(tmp_path: Path) -> None:
    _write(tmp_path / "apps" / "api" / "main.py", "def route():\n    return True\n")
    diff = """diff --git a/apps/api/main.py b/apps/api/main.py
--- a/apps/api/main.py
+++ b/apps/api/main.py
@@ -1,1 +1,2 @@
+print("debug")
 return True
"""

    report = review_diff(diff=diff, repository_root=tmp_path)

    assert report["context"]["changed_file_roles"] == ["api"]
    assert report["context"]["touched_symbols"] == ["route"]
    assert report["findings"][0]["context"]["file_role"] == "api"
    assert report["findings"][0]["context"]["touched_symbols"] == ["route"]


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
