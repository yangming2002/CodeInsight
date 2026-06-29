from pathlib import Path

from core.parser import PythonAstParser, RepositoryStructureParser, parse_changed_files


def test_parse_changed_files_tracks_modified_added_deleted_and_renamed_files() -> None:
    diff = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1,2 +1,3 @@
 import os
+print("debug")
-OLD = True
diff --git a/new.py b/new.py
new file mode 100644
--- /dev/null
+++ b/new.py
@@ -0,0 +1,2 @@
+VALUE = 1
+VALUE = 2
diff --git a/old.py b/old.py
deleted file mode 100644
--- a/old.py
+++ /dev/null
@@ -1,1 +0,0 @@
-VALUE = 1
diff --git a/before.py b/after.py
similarity index 90%
rename from before.py
rename to after.py
--- a/before.py
+++ b/after.py
@@ -1,1 +1,1 @@
-name = "old"
+name = "new"
"""

    files = parse_changed_files(diff)

    assert [file.status for file in files] == ["modified", "added", "deleted", "renamed"]
    assert files[0].path == "app.py"
    assert files[0].added_lines == 1
    assert files[0].deleted_lines == 1
    assert files[1].path == "new.py"
    assert files[1].added_lines == 2
    assert files[2].path == "old.py"
    assert files[2].deleted_lines == 1
    assert files[3].old_path == "before.py"
    assert files[3].new_path == "after.py"


def test_repository_structure_parser_skips_excluded_dirs_and_infers_roles(tmp_path: Path) -> None:
    _write(tmp_path / "apps" / "api" / "main.py", "app = object()\n")
    _write(tmp_path / "core" / "review" / "service.py", "def review(): pass\n")
    _write(tmp_path / "tests" / "test_service.py", "def test_ok(): pass\n")
    _write(tmp_path / "docs" / "guide.md", "# Guide\n")
    _write(tmp_path / ".venv" / "ignored.py", "ignored\n")

    snapshot = RepositoryStructureParser().parse(tmp_path)
    files_by_path = {file.path: file for file in snapshot.files}

    assert snapshot.file_count == 4
    assert snapshot.symbol_count == 2
    assert files_by_path["apps/api/main.py"].role == "api"
    assert files_by_path["core/review/service.py"].role == "core"
    assert files_by_path["tests/test_service.py"].role == "test"
    assert files_by_path["docs/guide.md"].role == "docs"
    assert ".venv/ignored.py" not in files_by_path
    assert {symbol.name for symbol in snapshot.symbols} == {"review", "test_ok"}


def test_python_ast_parser_extracts_symbols_and_imports() -> None:
    source = """import os
from core.review import service as review_service

class Reviewer:
    def review(self):
        return review_service.review()

async def run_review():
    return Reviewer()
"""

    summary = PythonAstParser().parse_source(source, file="core/reasoning/reviewer.py")

    symbols = {(symbol.kind, symbol.name, symbol.parent) for symbol in summary.symbols}
    imports = {(import_.module, import_.name, import_.alias) for import_ in summary.imports}

    assert symbols == {
        ("class", "Reviewer", None),
        ("function", "review", "Reviewer"),
        ("async_function", "run_review", None),
    }
    assert imports == {
        ("os", None, None),
        ("core.review", "service", "review_service"),
    }


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
