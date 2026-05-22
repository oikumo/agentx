"""Workspace ingestion: walk a directory, analyse files, write entries.

Python files are analysed with `ast` to produce one entry per class, method,
and top-level function. Markdown files become a single documentation entry.

This module only depends on `kb.store`, `kb.ids`, `kb.logging` — it does not
import anything from the legacy `meta_harness_knowledge_base` package.
"""

import ast
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from .ids import make_entry_id
from .logging import get_logger
from .store import KBStore, get_default_store


class EntryType(Enum):
    PATTERN = "pattern"
    FINDING = "finding"
    DECISION = "decision"
    CORRECTION = "correction"


class Category(Enum):
    CODE = "code"
    CLASS = "class"
    METHOD = "method"
    FUNCTION = "function"
    ARCHITECTURE = "architecture"
    WORKFLOW = "workflow"
    DOCUMENTATION = "documentation"


@dataclass
class CodeElement:
    name: str
    type: str
    file_path: str
    line_start: int
    line_end: Optional[int] = None
    docstring: Optional[str] = None
    methods: List[str] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    confidence: float = 0.95


@dataclass
class _IngestEntry:
    """Internal pre-write record (mirrors a future ChromaDB row)."""
    entry_type: EntryType
    category: Category
    title: str
    finding: str
    solution: str
    context: str
    confidence: float
    example: str = ""


# ---------------------------------------------------------------------------
# Python AST analysis
# ---------------------------------------------------------------------------

class PythonCodeAnalyzer:
    """Extracts classes, methods and top-level functions from a .py file."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = ""
        self.tree: Optional[ast.AST] = None
        self.elements: List[CodeElement] = []

    def analyze(self) -> List[CodeElement]:
        logger = get_logger()
        try:
            self.content = self.file_path.read_text(encoding="utf-8", errors="ignore")
            self.tree = ast.parse(self.content, filename=str(self.file_path))
            self._extract_elements()
            return self.elements
        except Exception as exc:
            logger.warning("Error analyzing %s: %s", self.file_path, exc)
            return []

    def _extract_elements(self) -> None:
        assert self.tree is not None
        seen_funcs: set = set()

        # Top-level classes (and their methods).
        for node in self.tree.body:
            if isinstance(node, ast.ClassDef):
                self._extract_class(node)

        # Top-level functions only.
        for node in self.tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name in seen_funcs:
                    continue
                seen_funcs.add(node.name)
                self._extract_function(node)

    def _extract_class(self, node: ast.ClassDef) -> None:
        methods: List[str] = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item.name)

        base_classes = [b.id for b in node.bases if isinstance(b, ast.Name)]

        self.elements.append(CodeElement(
            name=node.name,
            type="class",
            file_path=str(self.file_path),
            line_start=node.lineno,
            line_end=getattr(node, "end_lineno", None),
            docstring=ast.get_docstring(node),
            methods=methods,
            base_classes=base_classes,
            confidence=0.98,
        ))

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.elements.append(CodeElement(
                    name=f"{node.name}.{item.name}",
                    type="method",
                    file_path=str(self.file_path),
                    line_start=item.lineno,
                    line_end=getattr(item, "end_lineno", None),
                    docstring=ast.get_docstring(item),
                    confidence=0.95,
                ))

    def _extract_function(self, node: ast.FunctionDef) -> None:
        self.elements.append(CodeElement(
            name=node.name,
            type="function",
            file_path=str(self.file_path),
            line_start=node.lineno,
            line_end=getattr(node, "end_lineno", None),
            docstring=ast.get_docstring(node),
            confidence=0.95,
        ))


# ---------------------------------------------------------------------------
# Ingestion pipeline
# ---------------------------------------------------------------------------

class WorkspaceIngestor:
    """Walks files, converts them to entries, writes them through `KBStore`."""

    def __init__(self, store: Optional[KBStore] = None,
                 workspace_root: Optional[Path] = None):
        self.store = store if store is not None else get_default_store()
        self.workspace_root = workspace_root

    # ---- single-file dispatch -----------------------------------------

    def ingest_file(self, file_path: Path) -> List[str]:
        if file_path.suffix == ".py":
            return self._ingest_python(file_path)
        if file_path.suffix == ".md":
            return self._ingest_markdown(file_path)
        return []

    def _ingest_python(self, file_path: Path) -> List[str]:
        ids_out: List[str] = []
        for element in PythonCodeAnalyzer(file_path).analyze():
            entry = self._element_to_entry(element, file_path)
            entry_id = self._write(entry)
            if entry_id:
                ids_out.append(entry_id)
        return ids_out

    def _ingest_markdown(self, file_path: Path) -> List[str]:
        logger = get_logger()
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception as exc:
            logger.warning("Error reading %s: %s", file_path, exc)
            return []

        title = file_path.stem
        for line in content.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break

        rel_path = self._relative_path(file_path)
        entry = _IngestEntry(
            entry_type=EntryType.PATTERN,
            category=Category.DOCUMENTATION,
            title=f"{title} ({file_path.name})",
            finding=f"Documentation file: {file_path.name}",
            solution=content[:2000].replace("\n", " "),
            context=f"Full path: {file_path}",
            confidence=0.95,
            example=f"Read {file_path.name} for complete information",
        )
        entry_id = self._write(entry)
        return [entry_id] if entry_id else []

    # ---- element -> entry mapping -------------------------------------

    def _element_to_entry(self, element: CodeElement, file_path: Path) -> _IngestEntry:
        rel_path = self._relative_path(file_path)

        if element.type == "class":
            methods_str = ", ".join(element.methods) if element.methods else "No methods"
            bases_str = ", ".join(element.base_classes) or "None"
            return _IngestEntry(
                entry_type=EntryType.PATTERN,
                category=Category.CLASS,
                title=f"Class: {element.name}",
                finding=f"Class {element.name} defined in {file_path.name}",
                solution=f"Class {element.name} with methods: {methods_str}. Base classes: {bases_str}.",
                context=f"Source: {rel_path} | Lines: {element.line_start}-{element.line_end or 'N/A'}",
                confidence=element.confidence,
                example=f"from {Path(str(rel_path)).parent} import {element.name}",
            )
        if element.type == "method":
            return _IngestEntry(
                entry_type=EntryType.FINDING,
                category=Category.METHOD,
                title=f"Method: {element.name}",
                finding=f"Method {element.name} in class",
                solution=f"Method defined in {file_path.name} at line {element.line_start}.",
                context=f"Source: {rel_path}",
                confidence=element.confidence,
                example=f"obj.{element.name}()",
            )
        if element.type == "function":
            return _IngestEntry(
                entry_type=EntryType.FINDING,
                category=Category.FUNCTION,
                title=f"Function: {element.name}",
                finding=f"Standalone function {element.name} in {file_path.name}",
                solution=f"Function defined at line {element.line_start}.",
                context=f"Source: {rel_path}",
                confidence=element.confidence,
                example=f"from {Path(str(rel_path)).parent} import {element.name}",
            )
        return _IngestEntry(
            entry_type=EntryType.FINDING,
            category=Category.CODE,
            title=f"Code: {element.name}",
            finding=f"Code element {element.name} in {file_path.name}",
            solution=f"Type: {element.type}",
            context=f"Source: {rel_path}",
            confidence=element.confidence,
        )

    # ---- write through the store --------------------------------------

    def _write(self, entry: _IngestEntry) -> Optional[str]:
        logger = get_logger()
        try:
            entry_id = make_entry_id(
                entry_type=entry.entry_type.value,
                category=entry.category.value,
                title=entry.title,
            )
            document_text = " ".join([
                entry.title, entry.finding, entry.solution,
                entry.context, entry.example,
            ])
            metadata: Dict[str, object] = {
                "entry_id": entry_id,
                "type": entry.entry_type.value,
                "category": entry.category.value,
                "title": entry.title,
                "finding": entry.finding,
                "solution": entry.solution,
                "context": entry.context,
                "example": entry.example,
                "confidence": entry.confidence,
                "created_at": datetime.now().isoformat(),
            }
            self.store.add(entry_id=entry_id, document_text=document_text, metadata=metadata)
            return entry_id
        except Exception as exc:
            logger.warning("Error adding entry: %s", exc)
            return None

    # ---- helpers ------------------------------------------------------

    def _relative_path(self, file_path: Path) -> Path:
        root = self.workspace_root
        if root is None:
            # Fall back to repo root: 4 levels up from this file
            #   kb/ingest.py -> kb -> mcp_servers/knowledge_base -> mcp_servers -> <repo>
            root = Path(__file__).resolve().parent.parent.parent.parent
        try:
            return file_path.relative_to(root)
        except ValueError:
            return Path(str(file_path))
