from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from core.parser import (
    ChangedFile,
    PythonImport,
    PythonSymbol,
    RepositoryFile,
    RepositorySnapshot,
)


@dataclass(frozen=True)
class RelatedFile:
    path: str
    role: str
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "role": self.role,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ReviewFileContext:
    path: str
    role: str
    status: str
    added_lines: int
    deleted_lines: int
    symbols: list[PythonSymbol]
    touched_symbols: list[PythonSymbol]
    imports: list[PythonImport]
    related_files: list[RelatedFile]

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "role": self.role,
            "status": self.status,
            "added_lines": self.added_lines,
            "deleted_lines": self.deleted_lines,
            "symbols": [symbol.to_dict() for symbol in self.symbols],
            "touched_symbols": [symbol.to_dict() for symbol in self.touched_symbols],
            "imports": [import_.to_dict() for import_ in self.imports],
            "related_files": [file.to_dict() for file in self.related_files],
        }


@dataclass(frozen=True)
class FindingContext:
    file_role: str
    touched_symbols: list[str]
    related_imports: list[str]
    related_files: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "file_role": self.file_role,
            "touched_symbols": self.touched_symbols,
            "related_imports": self.related_imports,
            "related_files": self.related_files,
        }


@dataclass(frozen=True)
class ReviewContext:
    changed_file_roles: list[str]
    touched_symbols: list[str]
    related_imports: list[str]
    related_files: list[RelatedFile]
    files: list[ReviewFileContext]

    def for_file(self, path: str) -> FindingContext:
        file_context = next((file for file in self.files if file.path == path), None)
        if file_context is None:
            return FindingContext(
                file_role="unknown",
                touched_symbols=[],
                related_imports=[],
                related_files=[],
            )

        return FindingContext(
            file_role=file_context.role,
            touched_symbols=[_format_symbol(symbol) for symbol in file_context.touched_symbols],
            related_imports=[_format_import(import_) for import_ in file_context.imports],
            related_files=[file.path for file in file_context.related_files],
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "changed_file_roles": self.changed_file_roles,
            "touched_symbols": self.touched_symbols,
            "related_imports": self.related_imports,
            "related_files": [file.to_dict() for file in self.related_files],
            "files": [file.to_dict() for file in self.files],
        }


class ReviewContextBuilder:
    def build(
        self,
        changed_files: list[ChangedFile],
        snapshot: RepositorySnapshot,
        added_line_numbers: dict[str, set[int]] | None = None,
    ) -> ReviewContext:
        files_by_path = {file.path: file for file in snapshot.files}
        symbols_by_file = _group_by_file(snapshot.symbols)
        imports_by_file = _group_by_file(snapshot.imports)
        symbols_by_name = _group_symbols_by_name(snapshot.symbols)
        added_line_numbers = added_line_numbers or {}

        file_contexts: list[ReviewFileContext] = []
        for changed_file in changed_files:
            path = changed_file.path
            repository_file = files_by_path.get(path)
            symbols = symbols_by_file.get(path, [])
            imports = imports_by_file.get(path, [])
            file_contexts.append(
                ReviewFileContext(
                    path=path,
                    role=repository_file.role if repository_file else "unknown",
                    status=changed_file.status,
                    added_lines=changed_file.added_lines,
                    deleted_lines=changed_file.deleted_lines,
                    symbols=symbols,
                    touched_symbols=_filter_touched_symbols(
                        symbols=symbols,
                        added_lines=added_line_numbers.get(path, set()),
                    ),
                    imports=imports,
                    related_files=_find_related_files(
                        imports=imports,
                        files_by_path=files_by_path,
                        symbols_by_name=symbols_by_name,
                        current_path=path,
                    ),
                )
            )

        changed_file_roles = sorted({file.role for file in file_contexts})
        touched_symbols = sorted(
            {_format_symbol(symbol) for file in file_contexts for symbol in file.touched_symbols}
        )
        related_imports = sorted(
            {_format_import(import_) for file in file_contexts for import_ in file.imports}
        )
        related_files = _dedupe_related_files(
            file for file_context in file_contexts for file in file_context.related_files
        )

        return ReviewContext(
            changed_file_roles=changed_file_roles,
            touched_symbols=touched_symbols,
            related_imports=related_imports,
            related_files=related_files,
            files=file_contexts,
        )


def _group_by_file(items: list[PythonSymbol] | list[PythonImport]) -> dict[str, list]:
    grouped: dict[str, list] = {}
    for item in items:
        grouped.setdefault(item.file, []).append(item)
    return grouped


def _group_symbols_by_name(symbols: list[PythonSymbol]) -> dict[str, list[PythonSymbol]]:
    grouped: dict[str, list[PythonSymbol]] = {}
    for symbol in symbols:
        grouped.setdefault(symbol.name, []).append(symbol)
    return grouped


def _format_symbol(symbol: PythonSymbol) -> str:
    if symbol.parent:
        return f"{symbol.parent}.{symbol.name}"
    return symbol.name


def _format_import(import_: PythonImport) -> str:
    if import_.name:
        return f"{import_.module}.{import_.name}"
    return import_.module


def _filter_touched_symbols(
    symbols: list[PythonSymbol],
    added_lines: set[int],
) -> list[PythonSymbol]:
    if not added_lines:
        return []
    return [
        symbol
        for symbol in symbols
        if any(_symbol_contains_line(symbol=symbol, line=line) for line in added_lines)
    ]


def _symbol_contains_line(symbol: PythonSymbol, line: int) -> bool:
    end_line = symbol.end_line or symbol.line
    return symbol.line <= line <= end_line


def _find_related_files(
    imports: list[PythonImport],
    files_by_path: dict[str, RepositoryFile],
    symbols_by_name: dict[str, list[PythonSymbol]],
    current_path: str,
) -> list[RelatedFile]:
    related: list[RelatedFile] = []
    for import_ in imports:
        for path in _candidate_paths_for_import(import_):
            _append_related_file(
                related=related,
                path=path,
                files_by_path=files_by_path,
                current_path=current_path,
                reason=f"import:{_format_import(import_)}",
            )

        if import_.name:
            for symbol in symbols_by_name.get(import_.name, []):
                _append_related_file(
                    related=related,
                    path=symbol.file,
                    files_by_path=files_by_path,
                    current_path=current_path,
                    reason=f"symbol:{import_.name}",
                )

    return _dedupe_related_files(related)


def _candidate_paths_for_import(import_: PythonImport) -> list[str]:
    module = import_.module.lstrip(".")
    candidates: list[str] = []

    if module:
        module_path = module.replace(".", "/")
        candidates.append(f"{module_path}.py")
        candidates.append(f"{module_path}/__init__.py")
        if import_.name:
            candidates.append(f"{module_path}/{import_.name}.py")

    return candidates


def _append_related_file(
    related: list[RelatedFile],
    path: str,
    files_by_path: dict[str, RepositoryFile],
    current_path: str,
    reason: str,
) -> None:
    if path == current_path or path not in files_by_path:
        return
    repository_file = files_by_path[path]
    related.append(RelatedFile(path=path, role=repository_file.role, reason=reason))


def _dedupe_related_files(files: Iterable[RelatedFile]) -> list[RelatedFile]:
    deduped: dict[str, RelatedFile] = {}
    for file in files:
        deduped.setdefault(file.path, file)
    return sorted(deduped.values(), key=lambda file: file.path)
