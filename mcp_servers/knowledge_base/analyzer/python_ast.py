#!/usr/bin/env python3
"""
Python AST semantic analyzer for KB MCP v4.

Performs two-pass analysis:
1. Structure extraction (classes, functions, imports, relationships)
2. Cross-file symbol resolution
"""

import ast
import re
from pathlib import Path
from typing import Any, Optional

from .base import LanguageBackend
from graph.models import (
    DocstringInfo,
    Entity,
    EntityKind,
    Relationship,
    RelationshipKind,
)


class PythonASTAnalyzer(LanguageBackend):
    """
    Semantic analyzer for Python code using AST.
    
    Extracts:
    - Classes, functions, methods with docstrings
    - Import relationships
    - Inheritance hierarchies
    - Composition relationships
    - Call graphs (static analysis)
    - Design pattern hints
    """
    
    @property
    def supported_extensions(self) -> set[str]:
        return {'.py', '.pyi'}
    
    @property
    def language_name(self) -> str:
        return 'python'
    
    @property
    def confidence(self) -> float:
        return 0.95  # High confidence for AST-based analysis
    
    def analyze_file(self, path: Path) -> tuple[list[Entity], list[Relationship]]:
        """
        Analyze a Python file using AST.
        
        Args:
            path: Path to Python file
            
        Returns:
            Tuple of (entities, relationships)
        """
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        try:
            source = path.read_text(encoding='utf-8')
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in {path}: {e}")
        
        entities = []
        relationships = []
        
        # Pass 1: Extract structure
        self._pass1_extract(tree, path, source, entities, relationships)
        
        return entities, relationships
    
    def _pass1_extract(
        self,
        tree: ast.AST,
        path: Path,
        source: str,
        entities: list[Entity],
        relationships: list[Relationship],
    ) -> None:
        """
        First pass: Extract all entities and relationships from AST.
        
        Args:
            tree: Parsed AST
            path: File path
            source: Source code string
            entities: List to append entities to
            relationships: List to append relationships to
        """
        lines = source.split('\n')
        
        # Extract module-level entities
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                entity = self._extract_class(node, path, lines)
                entities.append(entity)
                
                # Extract inheritance
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        rel = Relationship(
                            source_id=entity.id,
                            target_id=f"{path}:{node.lineno}:{base.id}",
                            kind=RelationshipKind.EXTENDS,
                        )
                        relationships.append(rel)
                
                # Extract decorators
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        rel = Relationship(
                            source_id=f"{path}:{node.lineno}:{decorator.id}",
                            target_id=entity.id,
                            kind=RelationshipKind.DECORATES,
                        )
                        relationships.append(rel)
            
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                entity = self._extract_function(node, path, lines)
                entities.append(entity)
                
                # Extract decorators
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        rel = Relationship(
                            source_id=f"{path}:{node.lineno}:{decorator.id}",
                            target_id=entity.id,
                            kind=RelationshipKind.DECORATES,
                        )
                        relationships.append(rel)
            
            elif isinstance(node, ast.Import):
                # Handle: import module
                for alias in node.names:
                    entities.append(Entity(
                        id=f"{path}:{node.lineno}:import_{alias.name}",
                        kind=EntityKind.MODULE,
                        name=alias.name,
                        file_path=str(path),
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        metadata={"import_type": "import"},
                    ))
            
            elif isinstance(node, ast.ImportFrom):
                # Handle: from module import name
                if node.module:
                    for alias in node.names:
                        entities.append(Entity(
                            id=f"{path}:{node.lineno}:from_{node.module}_{alias.name}",
                            kind=EntityKind.MODULE,
                            name=alias.name,
                            file_path=str(path),
                            line_start=node.lineno,
                            line_end=node.end_lineno or node.lineno,
                            metadata={"import_type": "from", "module": node.module},
                        ))
        
        # Extract method-level entities and call relationships
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method = self._extract_function(item, path, lines, class_name=node.name)
                        entities.append(method)
                        
                        # Extract method calls within this method
                        self._extract_calls(item, method, entities, relationships)
            
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Module-level functions
                if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) if parent != node):
                    self._extract_calls(node, entities[-1] if entities and entities[-1].name == node.name else None, entities, relationships)
    
    def _extract_class(self, node: ast.ClassDef, path: Path, lines: list[str]) -> Entity:
        """Extract class entity from AST node."""
        docstring = self._parse_docstring(node)
        
        # Detect patterns
        patterns = self._detect_class_patterns(node)
        
        return Entity(
            id=f"{path}:{node.lineno}:{node.name}",
            kind=EntityKind.CLASS,
            name=node.name,
            file_path=str(path),
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=docstring,
            metadata={
                "layer": self._infer_layer(node.name, path),
                "pattern": patterns,
                "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
            },
        )
    
    def _extract_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        path: Path,
        lines: list[str],
        class_name: Optional[str] = None,
    ) -> Entity:
        """Extract function/method entity from AST node."""
        docstring = self._parse_docstring(node)
        
        kind = EntityKind.METHOD if class_name else EntityKind.FUNCTION
        
        # Extract parameters
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        
        patterns = self._detect_function_patterns(node)
        
        metadata = {
            "layer": self._infer_layer(node.name, path),
            "pattern": patterns,
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
            "args": args,
            "is_async": isinstance(node, ast.AsyncFunctionDef),
        }
        
        if class_name:
            metadata["class"] = class_name
        
        return Entity(
            id=f"{path}:{node.lineno}:{node.name}",
            kind=kind,
            name=node.name,
            file_path=str(path),
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=docstring,
            metadata=metadata,
        )
    
    def _extract_calls(
        self,
        func_node: ast.FunctionDef | ast.AsyncFunctionDef,
        method_entity: Optional[Entity],
        entities: list[Entity],
        relationships: list[Relationship],
    ) -> None:
        """Extract function calls within a function body."""
        if not method_entity:
            return
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                # Handle simple calls: func()
                if isinstance(node.func, ast.Name):
                    rel = Relationship(
                        source_id=method_entity.id,
                        target_id=f"{method_entity.file_path}:{func_node.lineno}:{node.func.id}",
                        kind=RelationshipKind.CALLS,
                    )
                    relationships.append(rel)
                
                # Handle attribute calls: obj.method()
                elif isinstance(node.func, ast.Attribute):
                    rel = Relationship(
                        source_id=method_entity.id,
                        target_id=f"{method_entity.file_path}:{func_node.lineno}:{node.func.attr}",
                        kind=RelationshipKind.CALLS,
                    )
                    relationships.append(rel)
    
    def _parse_docstring(self, node: ast.AST) -> Optional[DocstringInfo]:
        """Parse docstring from AST node."""
        if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            return None
        
        docstring = ast.get_docstring(node)
        if not docstring:
            return None
        
        # Simple docstring parsing
        lines = docstring.strip().split('\n')
        summary = lines[0] if lines else ""
        description = '\n'.join(lines[1:]) if len(lines) > 1 else ""
        
        # Extract args, returns (very basic parsing)
        args = {}
        returns = None
        
        for line in lines:
            if line.startswith(':param ') or line.startswith('@param '):
                match = re.match(r':param\s+(\w+)\s*:\s*(.+)', line)
                if match:
                    args[match.group(1)] = match.group(2)
            elif line.startswith(':returns:') or line.startswith('@returns'):
                match = re.match(r':returns?:\s*(.+)', line)
                if match:
                    returns = match.group(1)
        
        return DocstringInfo(
            summary=summary,
            description=description,
            args=args,
            returns=returns,
        )
    
    def _detect_class_patterns(self, node: ast.ClassDef) -> list[str]:
        """Detect design patterns in class."""
        patterns = []
        
        # Check for common pattern indicators
        name_lower = node.name.lower()
        
        if 'singleton' in name_lower:
            patterns.append('singleton')
        if 'factory' in name_lower:
            patterns.append('factory')
        if 'observer' in name_lower or 'listener' in name_lower:
            patterns.append('observer')
        if 'strategy' in name_lower:
            patterns.append('strategy')
        if 'adapter' in name_lower:
            patterns.append('adapter')
        if 'decorator' in name_lower and node.decorator_list:
            patterns.append('decorator')
        if 'facade' in name_lower:
            patterns.append('facade')
        if 'builder' in name_lower:
            patterns.append('builder')
        
        # Check for ABC (Abstract Base Class)
        for base in node.bases:
            if isinstance(base, ast.Name) and 'ABC' in base.id:
                patterns.append('abstract_base')
        
        return patterns
    
    def _detect_function_patterns(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
        """Detect patterns in function."""
        patterns = []
        
        name_lower = node.name.lower()
        
        # Check for common patterns
        if name_lower.startswith('get_') or name_lower.startswith('fetch_'):
            patterns.append('getter')
        if name_lower.startswith('set_') or name_lower.startswith('update_'):
            patterns.append('setter')
        if name_lower.startswith('create_') or name_lower.startswith('make_'):
            patterns.append('factory')
        if name_lower.startswith('validate_') or name_lower.startswith('check_'):
            patterns.append('validator')
        if name_lower.startswith('handle_') or name_lower.startswith('on_'):
            patterns.append('handler')
        
        # Check for async
        if isinstance(node, ast.AsyncFunctionDef):
            patterns.append('async')
        
        # Check for decorators
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                if dec.id in ('property', 'staticmethod', 'classmethod'):
                    patterns.append(dec.id)
                elif dec.id == 'abstractmethod':
                    patterns.append('abstract')
        
        return patterns
    
    def _infer_layer(self, name: str, path: Path) -> str:
        """Infer architecture layer from name and path."""
        path_str = str(path).lower()
        name_lower = name.lower()
        
        if 'model' in path_str or name_lower.endswith('model'):
            return 'model'
        if 'view' in path_str or name_lower.endswith('view'):
            return 'view'
        if 'controller' in path_str or name_lower.endswith('controller'):
            return 'controller'
        if 'service' in path_str or name_lower.endswith('service'):
            return 'service'
        if 'repository' in path_str or name_lower.endswith('repository'):
            return 'repository'
        if 'test' in path_str:
            return 'test'
        
        return 'unknown'
    
    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Get decorator name from AST node."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        elif isinstance(decorator, ast.Call):
            return self._get_decorator_name(decorator.func)
        return 'unknown'
    
    def analyze_project(self, root: Path, exclude_dirs: set[str] | None = None) -> tuple[list[Entity], list[Relationship]]:
        """
        Analyze all Python files in a project.
        
        Args:
            root: Project root directory
            exclude_dirs: Directories to exclude
            
        Returns:
            Tuple of (all_entities, all_relationships)
        """
        if exclude_dirs is None:
            exclude_dirs = {'venv', '.venv', '.git', '__pycache__', 'node_modules', '.tox', '.eggs'}
        
        all_entities = []
        all_relationships = []
        
        for py_file in root.rglob('*.py'):
            # Check if file is in excluded directory
            if any(excl in py_file.parts for excl in exclude_dirs):
                continue
            
            try:
                entities, relationships = self.analyze_file(py_file)
                all_entities.extend(entities)
                all_relationships.extend(relationships)
            except (SyntaxError, FileNotFoundError) as e:
                # Skip files with errors
                continue
        
        return all_entities, all_relationships
    
    def get_config_files(self, root: Path) -> list[Path]:
        """Get Python project config files."""
        config_files = []
        
        for config_name in ['setup.py', 'setup.cfg', 'pyproject.toml', 'requirements.txt', 'Pipfile', 'poetry.lock']:
            config_path = root / config_name
            if config_path.exists():
                config_files.append(config_path)
        
        return config_files


# Export as default Python analyzer
__all__ = ['PythonASTAnalyzer']
