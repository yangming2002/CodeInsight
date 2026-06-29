from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.parser.python_ast import PythonAstParser, PythonImport, PythonSymbol


DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "dist",
    "htmlcov",
    "node_modules",
}


@dataclass(frozen=True)
class RepositoryFile:
    path: str
    extension: str
    role: str
    size_bytes: int

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "extension": self.extension,
            "role": self.role,
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True)
class RepositorySnapshot:
    root: str
    files: list[RepositoryFile]
    symbols: list[PythonSymbol]
    imports: list[PythonImport]

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def symbol_count(self) -> int:
        return len(self.symbols)

    def to_dict(self) -> dict[str, object]:
        return {
            "root": self.root,
            "file_count": self.file_count,
            "symbol_count": self.symbol_count,
            "files": [file.to_dict() for file in self.files],
            "symbols": [symbol.to_dict() for symbol in self.symbols],
            "imports": [import_.to_dict() for import_ in self.imports],
        }


class RepositoryStructureParser:
    def __init__(self, excluded_dirs: set[str] | None = None) -> None:
        self._excluded_dirs = excluded_dirs or DEFAULT_EXCLUDED_DIRS

    def parse(self, root: str | Path) -> RepositorySnapshot:
        root_path = Path(root).resolve()
        files: list[RepositoryFile] = []
        symbols: list[PythonSymbol] = []
        imports: list[PythonImport] = []
        ast_parser = PythonAstParser()

        for path in sorted(root_path.rglob("*")):
            if not path.is_file() or self._is_excluded(path, root_path):
                continue

            relative_path = path.relative_to(root_path).as_posix()
            files.append(
                RepositoryFile(
                    path=relative_path,
                    extension=path.suffix.lower(),
                    role=_infer_role(relative_path),
                    size_bytes=path.stat().st_size,
                )
            )
            if path.suffix == ".py":
                summary = ast_parser.parse_file(path=path, root=root_path)
                symbols.extend(summary.symbols)
                imports.extend(summary.imports)

        return RepositorySnapshot(
            root=root_path.as_posix(),
            files=files,
            symbols=symbols,
            imports=imports,
        )

    def _is_excluded(self, path: Path, root: Path) -> bool:
        relative_parts = path.relative_to(root).parts
        return any(part in self._excluded_dirs for part in relative_parts)


def _infer_role(path: str) -> str:
    first_part = path.split("/", maxsplit=1)[0]

    if path.startswith("apps/api/"):
        return "api"
    if first_part == "apps":
        return "app"
    if first_part == "core":
        return "core"
    if first_part == "tests":
        return "test"
    if first_part == "configs":
        return "config"
    if first_part == "docs":
        return "docs"
    if first_part == "prompts":
        return "prompt"
    if first_part == "evaluation":
        return "evaluation"
    if first_part == ".github":
        return "ci"
    return "project"
