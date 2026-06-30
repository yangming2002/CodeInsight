from __future__ import annotations

from dataclasses import dataclass

from core.parser import ChangedFile, PythonImport, PythonSymbol, RepositorySnapshot


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
        }


@dataclass(frozen=True)
class FindingContext:
    file_role: str
    touched_symbols: list[str]
    related_imports: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "file_role": self.file_role,
            "touched_symbols": self.touched_symbols,
            "related_imports": self.related_imports,
        }


@dataclass(frozen=True)
class ReviewContext:
    changed_file_roles: list[str]
    touched_symbols: list[str]
    related_imports: list[str]
    files: list[ReviewFileContext]

    def for_file(self, path: str) -> FindingContext:
        file_context = next((file for file in self.files if file.path == path), None)
        if file_context is None:
            return FindingContext(file_role="unknown", touched_symbols=[], related_imports=[])

        return FindingContext(
            file_role=file_context.role,
            touched_symbols=[_format_symbol(symbol) for symbol in file_context.touched_symbols],
            related_imports=[_format_import(import_) for import_ in file_context.imports],
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "changed_file_roles": self.changed_file_roles,
            "touched_symbols": self.touched_symbols,
            "related_imports": self.related_imports,
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
        added_line_numbers = added_line_numbers or {}

        file_contexts: list[ReviewFileContext] = []
        for changed_file in changed_files:
            path = changed_file.path
            repository_file = files_by_path.get(path)
            symbols = symbols_by_file.get(path, [])
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
                    imports=imports_by_file.get(path, []),
                )
            )

        changed_file_roles = sorted({file.role for file in file_contexts})
        touched_symbols = sorted(
            {_format_symbol(symbol) for file in file_contexts for symbol in file.touched_symbols}
        )
        related_imports = sorted(
            {_format_import(import_) for file in file_contexts for import_ in file.imports}
        )

        return ReviewContext(
            changed_file_roles=changed_file_roles,
            touched_symbols=touched_symbols,
            related_imports=related_imports,
            files=file_contexts,
        )


def _group_by_file(items: list[PythonSymbol] | list[PythonImport]) -> dict[str, list]:
    grouped: dict[str, list] = {}
    for item in items:
        grouped.setdefault(item.file, []).append(item)
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
