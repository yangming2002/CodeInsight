from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChangedFile:
    old_path: str | None
    new_path: str | None
    status: str
    added_lines: int = 0
    deleted_lines: int = 0

    @property
    def path(self) -> str:
        return self.new_path or self.old_path or "unknown"

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "old_path": self.old_path,
            "new_path": self.new_path,
            "status": self.status,
            "added_lines": self.added_lines,
            "deleted_lines": self.deleted_lines,
        }


def parse_changed_files(diff: str) -> list[ChangedFile]:
    files: list[ChangedFile] = []
    current = _MutableChangedFile()

    for raw_line in diff.splitlines():
        if raw_line.startswith("diff --git "):
            _append_current(files, current)
            current = _MutableChangedFile()
            parts = raw_line.split()
            if len(parts) >= 4:
                current.old_path = _clean_git_path(parts[2])
                current.new_path = _clean_git_path(parts[3])
            continue

        if raw_line.startswith("rename from "):
            current.old_path = raw_line.removeprefix("rename from ").strip()
            current.status = "renamed"
            continue

        if raw_line.startswith("rename to "):
            current.new_path = raw_line.removeprefix("rename to ").strip()
            current.status = "renamed"
            continue

        if raw_line.startswith("new file mode"):
            current.status = "added"
            continue

        if raw_line.startswith("deleted file mode"):
            current.status = "deleted"
            continue

        if raw_line.startswith("--- "):
            old_path = _clean_diff_path(raw_line[4:].strip())
            if old_path is None:
                current.status = "added"
            else:
                current.old_path = old_path
            continue

        if raw_line.startswith("+++ "):
            new_path = _clean_diff_path(raw_line[4:].strip())
            if new_path is None:
                current.status = "deleted"
            else:
                current.new_path = new_path
            continue

        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            current.added_lines += 1
            continue

        if raw_line.startswith("-") and not raw_line.startswith("---"):
            current.deleted_lines += 1

    _append_current(files, current)
    return files


class _MutableChangedFile:
    def __init__(self) -> None:
        self.old_path: str | None = None
        self.new_path: str | None = None
        self.status = "modified"
        self.added_lines = 0
        self.deleted_lines = 0


def _append_current(files: list[ChangedFile], current: _MutableChangedFile) -> None:
    if not current.old_path and not current.new_path:
        return

    status = current.status
    if current.old_path is None and current.new_path is not None:
        status = "added"
    elif current.new_path is None and current.old_path is not None:
        status = "deleted"

    files.append(
        ChangedFile(
            old_path=current.old_path,
            new_path=current.new_path,
            status=status,
            added_lines=current.added_lines,
            deleted_lines=current.deleted_lines,
        )
    )


def _clean_diff_path(path: str) -> str | None:
    if path == "/dev/null":
        return None
    return _clean_git_path(path)


def _clean_git_path(path: str) -> str:
    if path.startswith("a/") or path.startswith("b/"):
        return path[2:]
    return path
