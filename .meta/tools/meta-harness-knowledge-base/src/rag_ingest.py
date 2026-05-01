#!/usr/bin/env python3
"""
RAG Ingestion Tool - Enhanced Knowledge Base Population

This tool improves the ingestion phase of the RAG system by:
1. Extracting structured knowledge from Python source code (classes, methods, functions)
2. Creating intelligent chunks for large files
3. Generating high-quality KB entries with proper categorization
4. Supporting batch processing and incremental updates

Usage:
    python -m src.rag_ingest --source src/agentx --category code
    python -m src.rag_ingest --file src/agentx/controllers/main_controller/main_controller.py
    python -m src.rag_ingest --analyze src/agentx --verbose
"""

import sys
import ast
import hashlib
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from rag_tool import get_db_connection


class EntryType(Enum):
    """Types of KB entries."""
    PATTERN = "pattern"
    FINDING = "finding"
    DECISION = "decision"
    CORRECTION = "correction"


class Category(Enum):
    """Categories for KB entries."""
    CODE = "code"
    CLASS = "class"
    METHOD = "method"
    FUNCTION = "function"
    ARCHITECTURE = "architecture"
    WORKFLOW = "workflow"
    DOCUMENTATION = "documentation"
    DIRECTIVES = "directives"
    TEST = "test"


@dataclass
class CodeElement:
    """Represents a code element (class, method, function)."""
    name: str
    type: str  # class, method, function
    file_path: str
    line_start: int
    line_end: Optional[int] = None
    docstring: Optional[str] = None
    signature: Optional[str] = None
    methods: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    confidence: float = 0.95


@dataclass
class KBEntry:
    """Represents a knowledge base entry."""
    entry_type: EntryType
    category: Category
    title: str
    finding: str
    solution: str
    context: str
    confidence: float
    example: str = ""
    entry_id: Optional[str] = None


class PythonCodeAnalyzer:
    """Analyzes Python source code to extract structured information."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = ""
        self.tree = None
        self.elements: List[CodeElement] = []

    def analyze(self) -> List[CodeElement]:
        """Analyze Python file and extract code elements."""
        try:
            self.content = self.file_path.read_text(encoding='utf-8', errors='ignore')
            self.tree = ast.parse(self.content, filename=str(self.file_path))
            self._extract_elements()
            return self.elements
        except SyntaxError as e:
            print(f"Syntax error in {self.file_path}: {e}")
            return []
        except Exception as e:
            print(f"Error analyzing {self.file_path}: {e}")
            return []

    def _extract_elements(self):
        """Extract classes, functions, and methods from AST."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                self._extract_class(node)
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Only top-level functions (not methods)
                if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(self.tree)):
                    self._extract_function(node)

        # Extract module-level imports
        imports = []
        for node in self.tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"from {module} import {alias.name}")

        # Add imports as a special element
        if imports:
            self.elements.append(CodeElement(
                name=f"{self.file_path.name} (imports)",
                type="imports",
                file_path=str(self.file_path),
                line_start=0,
                line_end=0,
                imports=imports[:20],  # Limit to 20 imports
                confidence=1.0
            ))

    def _extract_class(self, node: ast.ClassDef):
        """Extract class information."""
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item.name)

        # Get base classes
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(f"{ast.unparse(base) if hasattr(ast, 'unparse') else str(base)}")

        # Get docstring
        docstring = ast.get_docstring(node)

        # Get decorators
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    decorators.append(decorator.func.id)

        element = CodeElement(
            name=node.name,
            type="class",
            file_path=str(self.file_path),
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', None),
            docstring=docstring,
            methods=methods,
            base_classes=base_classes,
            decorators=decorators,
            confidence=0.98
        )
        self.elements.append(element)

        # Extract methods as separate elements
        for method_name in methods:
            method_node = next((item for item in node.body 
                              if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) 
                              and item.name == method_name), None)
            if method_node:
                method_doc = ast.get_docstring(method_node)
                method_decorators = []
                for dec in method_node.decorator_list:
                    if isinstance(dec, ast.Name):
                        method_decorators.append(dec.id)

                self.elements.append(CodeElement(
                    name=f"{node.name}.{method_name}",
                    type="method",
                    file_path=str(self.file_path),
                    line_start=method_node.lineno,
                    line_end=getattr(method_node, 'end_lineno', None),
                    docstring=method_doc,
                    decorators=method_decorators,
                    confidence=0.95
                ))

    def _extract_function(self, node: ast.FunctionDef):
        """Extract function information."""
        docstring = ast.get_docstring(node)
        
        # Get decorators
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)

        element = CodeElement(
            name=node.name,
            type="function",
            file_path=str(self.file_path),
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', None),
            docstring=docstring,
            decorators=decorators,
            confidence=0.95
        )
        self.elements.append(element)


class RAGIngestion:
    """Handles RAG knowledge ingestion with enhanced extraction."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path
        self.conn = None
        self._connect()

    def _connect(self):
        """Establish database connection."""
        try:
            if self.db_path:
                from sqlite3 import connect
                self.conn = connect(str(self.db_path), timeout=30.0)
            else:
                self.conn = get_db_connection()
            self.conn.row_factory = sqlite3.Row
        except Exception as e:
            print(f"DB Connection error: {e}")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def ingest_file(self, file_path: Path, verbose: bool = True) -> List[str]:
        """
        Ingest a single file and create KB entries.
        
        Args:
            file_path: Path to the file to ingest
            verbose: Print progress information
            
        Returns:
            List of created entry IDs
        """
        entry_ids = []

        if file_path.suffix == '.py':
            # Analyze Python code
            analyzer = PythonCodeAnalyzer(file_path)
            elements = analyzer.analyze()

            for element in elements:
                if element.type == "imports":
                    # Skip imports as separate entry
                    continue

                kb_entry = self._create_kb_entry(element, file_path)
                entry_id = self._add_entry(kb_entry)
                if entry_id:
                    entry_ids.append(entry_id)
                    if verbose:
                        print(f"  ✓ Added: {kb_entry.title}")

        elif file_path.suffix == '.md':
            # Process markdown file
            kb_entry = self._process_markdown(file_path)
            if kb_entry:
                entry_id = self._add_entry(kb_entry)
                if entry_id:
                    entry_ids.append(entry_id)
                    if verbose:
                        print(f"  ✓ Added: {kb_entry.title}")

        return entry_ids

    def _create_kb_entry(self, element: CodeElement, file_path: Path) -> KBEntry:
        """Create KB entry from code element."""
        rel_path = self._get_relative_path(file_path)

        if element.type == "class":
            # Class entry
            methods_str = ", ".join(element.methods) if element.methods else "No methods"
            
            return KBEntry(
                entry_type=EntryType.PATTERN,
                category=Category.CLASS,
                title=f"Class: {element.name}",
                finding=f"Class {element.name} defined in {file_path.name}",
                solution=f"Class {element.name} with methods: {methods_str}. " +
                        f"Base classes: {', '.join(element.base_classes) or 'None'}. " +
                        f"Decorators: {', '.join(element.decorators) or 'None'}.",
                context=f"Source: {rel_path} | Lines: {element.line_start}-{element.line_end or 'N/A'}",
                confidence=element.confidence,
                example=f"from {Path(str(rel_path)).parent} import {element.name}"
            )

        elif element.type == "method":
            # Method entry
            return KBEntry(
                entry_type=EntryType.FINDING,
                category=Category.METHOD,
                title=f"Method: {element.name}",
                finding=f"Method {element.name} in class",
                solution=f"Method defined in {file_path.name} at line {element.line_start}. " +
                        f"Decorators: {', '.join(element.decorators) or 'None'}.",
                context=f"Source: {rel_path}",
                confidence=element.confidence,
                example=f"obj.{element.name}()"
            )

        elif element.type == "function":
            # Function entry
            return KBEntry(
                entry_type=EntryType.FINDING,
                category=Category.FUNCTION,
                title=f"Function: {element.name}",
                finding=f"Standalone function {element.name} in {file_path.name}",
                solution=f"Function defined at line {element.line_start}. " +
                        f"Decorators: {', '.join(element.decorators) or 'None'}.",
                context=f"Source: {rel_path}",
                confidence=element.confidence,
                example=f"from {Path(str(rel_path)).parent} import {element.name}"
            )

        # Default fallback
        return KBEntry(
            entry_type=EntryType.FINDING,
            category=Category.CODE,
            title=f"Code: {element.name}",
            finding=f"Code element {element.name} in {file_path.name}",
            solution=f"Type: {element.type}",
            context=f"Source: {rel_path}",
            confidence=element.confidence,
            example=""
        )

    def _process_markdown(self, file_path: Path) -> Optional[KBEntry]:
        """Process markdown file and create KB entry."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None

        # Extract title from first heading
        title = file_path.stem
        for line in content.split('\n'):
            if line.startswith('# '):
                title = line[2:].strip()
                break

        rel_path = self._get_relative_path(file_path)

        return KBEntry(
            entry_type=EntryType.PATTERN,
            category=Category.DOCUMENTATION,
            title=f"{title} ({file_path.name})",
            finding=f"Documentation file: {file_path.name}",
            solution=content[:2000].replace('\n', ' '),
            context=f"Full path: {file_path}",
            confidence=0.95,
            example=f"Read {file_path.name} for complete information"
        )

    def _add_entry(self, kb_entry: KBEntry) -> Optional[str]:
        """Add entry to knowledge base."""
        try:
            # Generate entry ID
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
            hash_input = f"{kb_entry.entry_type.value}{kb_entry.category.value}{kb_entry.title}{timestamp}"
            hash_val = hashlib.md5(hash_input.encode()).hexdigest()[:4].upper()
            
            prefix_map = {
                'pattern': 'PAT',
                'finding': 'FIND',
                'decision': 'DEC',
                'correction': 'COR'
            }
            entry_id = f"{prefix_map.get(kb_entry.entry_type.value, 'KB')}-{hash_val}"

            now = datetime.now().isoformat()

            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO entries (id, type, category, title, confidence, context,
                finding, solution, example, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry_id,
                kb_entry.entry_type.value,
                kb_entry.category.value,
                kb_entry.title,
                kb_entry.confidence,
                kb_entry.context,
                kb_entry.finding,
                kb_entry.solution,
                kb_entry.example,
                now,
                now
            ))
            self.conn.commit()

            return entry_id
        except Exception as e:
            print(f"Error adding entry: {e}")
            return None

    def _get_relative_path(self, file_path: Path) -> Path:
        """Get relative path from project root."""
        try:
            return file_path.relative_to(Path(__file__).parent.parent.parent.parent)
        except:
            return Path(str(file_path))

    def ingest_directory(self, dir_path: Path, pattern: str = "*.py", verbose: bool = True) -> int:
        """
        Ingest all matching files in a directory.
        
        Args:
            dir_path: Directory to search
            pattern: Glob pattern (default: *.py)
            verbose: Print progress
            
        Returns:
            Number of entries created
        """
        total_entries = 0

        if verbose:
            print(f"Ingesting files from {dir_path} (pattern: {pattern})")

        for file_path in dir_path.rglob(pattern):
            if '__pycache__' in str(file_path) or '.venv' in str(file_path):
                continue

            if verbose:
                print(f"Processing: {file_path}")

            entries = self.ingest_file(file_path, verbose=False)
            total_entries += len(entries)

        if verbose:
            print(f"\n✓ Complete! Created {total_entries} entries")

        return total_entries


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="RAG Ingestion Tool - Enhanced KB population"
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="Source directory or file to ingest"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Single file to ingest"
    )
    parser.add_argument(
        "--pattern",
        default="*.py",
        help="Glob pattern for file matching (default: *.py)"
    )
    parser.add_argument(
        "--category",
        default="code",
        help="Default category for entries"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Print progress information"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be ingested without adding to KB"
    )

    args = parser.parse_args()

    ingestion = RAGIngestion()

    try:
        if args.file:
            # Single file
            if args.dry_run:
                print(f"Would ingest: {args.file}")
            else:
                ingestion.ingest_file(args.file, verbose=args.verbose)

        elif args.source:
            # Directory
            if args.dry_run:
                print(f"Would ingest all {args.pattern} files from {args.source}")
            else:
                ingestion.ingest_directory(args.source, args.pattern, verbose=args.verbose)

        else:
            parser.print_help()

    finally:
        ingestion.close()


if __name__ == "__main__":
    main()
