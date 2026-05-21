#!/usr/bin/env python3
"""
RAG Ingestion Tool using ChromaDB
"""

import sys
import ast
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent))

from rag_tool import get_chroma_collection


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
class KBEntry:
    entry_type: EntryType
    category: Category
    title: str
    finding: str
    solution: str
    context: str
    confidence: float
    example: str = ""


class PythonCodeAnalyzer:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = ""
        self.tree = None
        self.elements: List[CodeElement] = []
    
    def analyze(self) -> List[CodeElement]:
        try:
            self.content = self.file_path.read_text(encoding='utf-8', errors='ignore')
            self.tree = ast.parse(self.content, filename=str(self.file_path))
            self._extract_elements()
            return self.elements
        except Exception as e:
            print(f"Error analyzing {self.file_path}: {e}")
            return []
    
    def _extract_elements(self):
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                self._extract_class(node)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(self.tree)):
                    self._extract_function(node)
    
    def _extract_class(self, node: ast.ClassDef):
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item.name)
        
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
        
        docstring = ast.get_docstring(node)
        
        element = CodeElement(
            name=node.name,
            type="class",
            file_path=str(self.file_path),
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', None),
            docstring=docstring,
            methods=methods,
            base_classes=base_classes,
            confidence=0.98
        )
        self.elements.append(element)
        
        for method_name in methods:
            method_node = next((item for item in node.body
                              if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                              and item.name == method_name), None)
            if method_node:
                method_doc = ast.get_docstring(method_node)
                self.elements.append(CodeElement(
                    name=f"{node.name}.{method_name}",
                    type="method",
                    file_path=str(self.file_path),
                    line_start=method_node.lineno,
                    line_end=getattr(method_node, 'end_lineno', None),
                    docstring=method_doc,
                    confidence=0.95
                ))
    
    def _extract_function(self, node: ast.FunctionDef):
        docstring = ast.get_docstring(node)
        element = CodeElement(
            name=node.name,
            type="function",
            file_path=str(self.file_path),
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', None),
            docstring=docstring,
            confidence=0.95
        )
        self.elements.append(element)


class ChromaDBIngestion:
    def __init__(self):
        self.collection = get_chroma_collection()
    
    def ingest_file(self, file_path: Path, verbose: bool = True) -> List[str]:
        entry_ids = []
        
        if file_path.suffix == '.py':
            analyzer = PythonCodeAnalyzer(file_path)
            elements = analyzer.analyze()
            
            for element in elements:
                if element.type == "imports":
                    continue
                
                kb_entry = self._create_kb_entry(element, file_path)
                entry_id = self._add_entry(kb_entry)
                if entry_id:
                    entry_ids.append(entry_id)
                    if verbose:
                        print(f" ✓ Added: {kb_entry.title}")
        
        elif file_path.suffix == '.md':
            kb_entry = self._process_markdown(file_path)
            if kb_entry:
                entry_id = self._add_entry(kb_entry)
                if entry_id:
                    entry_ids.append(entry_id)
                    if verbose:
                        print(f" ✓ Added: {kb_entry.title}")
        
        return entry_ids
    
    def _create_kb_entry(self, element: CodeElement, file_path: Path) -> KBEntry:
        rel_path = self._get_relative_path(file_path)
        
        if element.type == "class":
            methods_str = ", ".join(element.methods) if element.methods else "No methods"
            return KBEntry(
                entry_type=EntryType.PATTERN,
                category=Category.CLASS,
                title=f"Class: {element.name}",
                finding=f"Class {element.name} defined in {file_path.name}",
                solution=f"Class {element.name} with methods: {methods_str}. Base classes: {', '.join(element.base_classes) or 'None'}.",
                context=f"Source: {rel_path} | Lines: {element.line_start}-{element.line_end or 'N/A'}",
                confidence=element.confidence,
                example=f"from {Path(str(rel_path)).parent} import {element.name}"
            )
        elif element.type == "method":
            return KBEntry(
                entry_type=EntryType.FINDING,
                category=Category.METHOD,
                title=f"Method: {element.name}",
                finding=f"Method {element.name} in class",
                solution=f"Method defined in {file_path.name} at line {element.line_start}.",
                context=f"Source: {rel_path}",
                confidence=element.confidence,
                example=f"obj.{element.name}()"
            )
        elif element.type == "function":
            return KBEntry(
                entry_type=EntryType.FINDING,
                category=Category.FUNCTION,
                title=f"Function: {element.name}",
                finding=f"Standalone function {element.name} in {file_path.name}",
                solution=f"Function defined at line {element.line_start}.",
                context=f"Source: {rel_path}",
                confidence=element.confidence,
                example=f"from {Path(str(rel_path)).parent} import {element.name}"
            )
        
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
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
        
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
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
            hash_input = f"{kb_entry.entry_type.value}{kb_entry.category.value}{kb_entry.title}{timestamp}"
            hash_val = hashlib.md5(hash_input.encode()).hexdigest()[:4].upper()
            
            prefix_map = {'pattern': 'PAT', 'finding': 'FIND', 'decision': 'DEC', 'correction': 'COR'}
            entry_id = f"{prefix_map.get(kb_entry.entry_type.value, 'KB')}-{hash_val}"
            
            document_text = f"{kb_entry.title} {kb_entry.finding} {kb_entry.solution} {kb_entry.context} {kb_entry.example}"
            
            metadata = {
                "entry_id": entry_id,
                "type": kb_entry.entry_type.value,
                "category": kb_entry.category.value,
                "title": kb_entry.title,
                "finding": kb_entry.finding,
                "solution": kb_entry.solution,
                "context": kb_entry.context,
                "example": kb_entry.example,
                "confidence": kb_entry.confidence,
                "created_at": datetime.now().isoformat(),
            }
            
            self.collection.add(
                documents=[document_text],
                metadatas=[metadata],
                ids=[entry_id]
            )
            
            return entry_id
        except Exception as e:
            print(f"Error adding entry: {e}")
            return None
    
    def _get_relative_path(self, file_path: Path) -> Path:
        try:
            return file_path.relative_to(Path(__file__).parent.parent.parent.parent)
        except:
            return Path(str(file_path))
    
    def ingest_directory(self, dir_path: Path, pattern: str = "*.py", verbose: bool = True) -> int:
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
    import argparse
    
    parser = argparse.ArgumentParser(description="ChromaDB RAG Ingestion Tool")
    parser.add_argument("--source", type=Path, help="Source directory or file")
    parser.add_argument("--file", type=Path, help="Single file to ingest")
    parser.add_argument("--pattern", default="*.py", help="Glob pattern")
    parser.add_argument("--verbose", action="store_true", default=True)
    
    args = parser.parse_args()
    
    ingestion = ChromaDBIngestion()
    
    try:
        if args.file:
            ingestion.ingest_file(args.file, verbose=args.verbose)
        elif args.source:
            ingestion.ingest_directory(args.source, args.pattern, verbose=args.verbose)
        else:
            parser.print_help()
    finally:
        pass


if __name__ == "__main__":
    main()
