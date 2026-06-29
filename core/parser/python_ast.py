from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PythonSymbol:
    name: str
    kind: str
    file: str
    line: int
    end_line: int | None
    parent: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "kind": self.kind,
            "file": self.file,
            "line": self.line,
            "end_line": self.end_line,
            "parent": self.parent,
        }


@dataclass(frozen=True)
class PythonImport:
    module: str
    name: str | None
    alias: str | None
    file: str
    line: int

    def to_dict(self) -> dict[str, object]:
        return {
            "module": self.module,
            "name": self.name,
            "alias": self.alias,
            "file": self.file,
            "line": self.line,
        }


@dataclass(frozen=True)
class PythonAstSummary:
    file: str
    symbols: list[PythonSymbol]
    imports: list[PythonImport]

    def to_dict(self) -> dict[str, object]:
        return {
            "file": self.file,
            "symbols": [symbol.to_dict() for symbol in self.symbols],
            "imports": [import_.to_dict() for import_ in self.imports],
        }


class PythonAstParser:
    def parse_file(self, path: str | Path, root: str | Path | None = None) -> PythonAstSummary:
        file_path = Path(path)
        root_path = Path(root).resolve() if root else file_path.parent.resolve()
        relative_path = file_path.resolve().relative_to(root_path).as_posix()
        source = file_path.read_text(encoding="utf-8")
        return self.parse_source(source=source, file=relative_path)

    def parse_source(self, source: str, file: str = "<memory>") -> PythonAstSummary:
        tree = ast.parse(source)
        visitor = _PythonAstVisitor(file=file)
        visitor.visit(tree)
        return PythonAstSummary(file=file, symbols=visitor.symbols, imports=visitor.imports)


class _PythonAstVisitor(ast.NodeVisitor):
    def __init__(self, file: str) -> None:
        self.file = file
        self.symbols: list[PythonSymbol] = []
        self.imports: list[PythonImport] = []
        self._parents: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._add_symbol(name=node.name, kind="class", node=node)
        self._parents.append(node.name)
        self.generic_visit(node)
        self._parents.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._add_symbol(name=node.name, kind="function", node=node)
        self._parents.append(node.name)
        self.generic_visit(node)
        self._parents.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._add_symbol(name=node.name, kind="async_function", node=node)
        self._parents.append(node.name)
        self.generic_visit(node)
        self._parents.pop()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(
                PythonImport(
                    module=alias.name,
                    name=None,
                    alias=alias.asname,
                    file=self.file,
                    line=node.lineno,
                )
            )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = "." * node.level + (node.module or "")
        for alias in node.names:
            self.imports.append(
                PythonImport(
                    module=module,
                    name=alias.name,
                    alias=alias.asname,
                    file=self.file,
                    line=node.lineno,
                )
            )

    def _add_symbol(self, name: str, kind: str, node: ast.AST) -> None:
        self.symbols.append(
            PythonSymbol(
                name=name,
                kind=kind,
                file=self.file,
                line=node.lineno,
                end_line=getattr(node, "end_lineno", None),
                parent=self._parents[-1] if self._parents else None,
            )
        )
