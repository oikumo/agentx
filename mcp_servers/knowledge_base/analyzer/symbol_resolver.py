#!/usr/bin/env python3
"""
Cross-file symbol resolution for KB MCP v4.

Resolves symbols across files using import tracking and builds a global symbol index.
"""

import ast
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from graph.models import Entity, Relationship, RelationshipKind


@dataclass
class ImportInfo:
    """Information about an import statement."""
    module: str
    names: list[str]
    alias: dict[str, str]
    line_start: int
    is_relative: bool
    level: int = 0


@dataclass
class SymbolInfo:
    """Information about a resolved symbol."""
    name: str
    entity: Entity
    imported_as: Optional[str] = None
    import_chain: list[str] = field(default_factory=list)


class SymbolResolver:
    """
    Cross-file symbol resolver.
    
    Resolves symbols across files by:
    - Tracking import statements
    - Building a global symbol index
    - Resolving relative and absolute imports
    - Following import chains
    
    Usage:
        resolver = SymbolResolver(project_root)
        resolver.build_symbol_index(all_entities)
        resolved = resolver.resolve_cross_file(symbol_name, current_file)
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize symbol resolver.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root
        self.symbol_index: dict[str, SymbolInfo] = {}
        self.import_map: dict[str, list[ImportInfo]] = {}
        self.module_to_file: dict[str, str] = {}
    
    def build_symbol_index(self, entities: list[Entity]) -> None:
        """
        Build a global index of all symbols from entities.
        
        Args:
            entities: List of all entities from analysis
        """
        self.symbol_index.clear()
        
        for entity in entities:
            key = f"{entity.file_path}:{entity.name}"
            self.symbol_index[key] = SymbolInfo(
                name=entity.name,
                entity=entity,
            )
            
            # Also index by simple name for quick lookup
            simple_key = entity.name
            if simple_key not in self.symbol_index:
                self.symbol_index[simple_key] = SymbolInfo(
                    name=entity.name,
                    entity=entity,
                )
            
            # Map module names to files
            if entity.kind.value == 'module':
                module_name = entity.name
                self.module_to_file[module_name] = entity.file_path
    
    def resolve_imports(self, file_path: Path, source: str) -> list[ImportInfo]:
        """
        Parse and resolve all imports in a file.
        
        Args:
            file_path: Path to the Python file
            source: Source code string
            
        Returns:
            List of ImportInfo objects
        """
        try:
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError:
            return []
        
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                import_info = ImportInfo(
                    module='',
                    names=[alias.name for alias in node.names],
                    alias={alias.name: alias.asname or alias.name for alias in node.names},
                    line_start=node.lineno,
                    is_relative=False,
                )
                imports.append(import_info)
                
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                import_info = ImportInfo(
                    module=module,
                    names=[alias.name for alias in node.names],
                    alias={alias.name: alias.asname or alias.name for alias in node.names},
                    line_start=node.lineno,
                    is_relative=node.level > 0,
                    level=node.level,
                )
                imports.append(import_info)
        
        return imports
    
    def resolve_cross_file(
        self,
        symbol_name: str,
        current_file: Path,
        imports: Optional[list[ImportInfo]] = None,
    ) -> Optional[SymbolInfo]:
        """
        Resolve a symbol across files.
        
        Args:
            symbol_name: Name of the symbol to resolve
            current_file: Path to the file where the symbol is referenced
            imports: Optional pre-parsed imports (if not provided, will parse file)
            
        Returns:
            SymbolInfo if resolved, None otherwise
        """
        # First, try direct lookup
        if symbol_name in self.symbol_index:
            return self.symbol_index[symbol_name]
        
        # If imports provided, use them to resolve
        if imports:
            for imp in imports:
                resolved = self._resolve_from_import(symbol_name, imp, current_file)
                if resolved:
                    return resolved
        
        # Try to find in same directory
        current_dir = current_file.parent
        for key, info in self.symbol_index.items():
            if info.name == symbol_name:
                entity_file = Path(info.entity.file_path)
                if entity_file.parent == current_dir:
                    return info
        
        return None
    
    def _resolve_from_import(
        self,
        symbol_name: str,
        import_info: ImportInfo,
        current_file: Path,
    ) -> Optional[SymbolInfo]:
        """
        Resolve a symbol from an import statement.
        
        Args:
            symbol_name: Symbol to resolve
            import_info: Import information
            current_file: Current file path
            
        Returns:
            SymbolInfo if resolved
        """
        # Check if symbol is imported with alias
        for name, alias in import_info.alias.items():
            if alias == symbol_name or name == symbol_name:
                # Try to find the actual symbol
                if import_info.module:
                    # Absolute or relative import
                    module_path = self._resolve_module_path(
                        import_info.module,
                        current_file,
                        import_info.level,
                    )
                    
                    if module_path:
                        key = f"{module_path}:{name}"
                        if key in self.symbol_index:
                            symbol_info = self.symbol_index[key]
                            symbol_info.imported_as = alias
                            symbol_info.import_chain = [import_info.module]
                            return symbol_info
                
                # Direct import (from x import name)
                if name in self.symbol_index:
                    symbol_info = self.symbol_index[name]
                    symbol_info.imported_as = alias
                    return symbol_info
        
        return None
    
    def _resolve_module_path(
        self,
        module: str,
        current_file: Path,
        level: int = 0,
    ) -> Optional[str]:
        """
        Resolve a module name to a file path.
        
        Args:
            module: Module name (e.g., 'package.subpackage.module')
            current_file: Current file path (for relative imports)
            level: Relative import level (0 = absolute, 1 = ., 2 = ..)
            
        Returns:
            Absolute path to module file, or None if not found
        """
        # Handle relative imports
        if level > 0:
            current_dir = current_file.parent
            for _ in range(level - 1):
                current_dir = current_dir.parent
            
            module_parts = module.split('.') if module else []
            module_path = current_dir
            for part in module_parts:
                module_path = module_path / part
            
            # Try as package (dir with __init__.py)
            if (module_path / '__init__.py').exists():
                return str(module_path / '__init__.py')
            
            # Try as module
            module_file = module_path.with_suffix('.py')
            if module_file.exists():
                return str(module_file)
        else:
            # Absolute import
            module_parts = module.split('.')
            
            # Try from project root
            module_path = self.project_root
            for part in module_parts:
                module_path = module_path / part
            
            # Try as package
            if (module_path / '__init__.py').exists():
                return str(module_path / '__init__.py')
            
            # Try as module
            module_file = self.project_root / f"{module.replace('.', '/')}.py"
            if module_file.exists():
                return str(module_file)
        
        # Check if in module_to_file map
        if module in self.module_to_file:
            return self.module_to_file[module]
        
        return None
    
    def get_import_dependencies(self, file_path: Path, source: str) -> list[Relationship]:
        """
        Extract import relationships from a file.
        
        Args:
            file_path: Path to the Python file
            source: Source code string
            
        Returns:
            List of IMPORTS relationships
        """
        relationships = []
        imports = self.resolve_imports(file_path, source)
        
        for imp in imports:
            if imp.module:
                target_path = self._resolve_module_path(imp.module, file_path, imp.level)
                
                if target_path:
                    # Create relationship for each imported name
                    for name in imp.names:
                        rel = Relationship(
                            source_id=f"{file_path}:{imp.line_start}:import_{name}",
                            target_id=target_path,
                            kind=RelationshipKind.IMPORTS,
                            metadata={
                                'import_name': name,
                                'alias': imp.alias.get(name),
                                'is_relative': imp.is_relative,
                            }
                        )
                        relationships.append(rel)
        
        return relationships
    
    def resolve_all_symbols(self, entities: list[Entity]) -> dict[str, list[SymbolInfo]]:
        """
        Resolve all symbols and group by file.
        
        Args:
            entities: List of all entities
            
        Returns:
            Dictionary mapping file paths to their resolved symbols
        """
        self.build_symbol_index(entities)
        
        result: dict[str, list[SymbolInfo]] = {}
        
        for entity in entities:
            file_path = entity.file_path
            if file_path not in result:
                result[file_path] = []
            
            # Find symbols referenced by this entity
            if entity.metadata.get('pattern'):
                for pattern in entity.metadata['pattern']:
                    if pattern in self.symbol_index:
                        result[file_path].append(self.symbol_index[pattern])
        
        return result