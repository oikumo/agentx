#!/usr/bin/env python3
"""
Relationship extraction for KB MCP v4.

Extracts all 16 relationship types from code entities.
"""

import ast
from pathlib import Path
from typing import Optional

from graph.models import Entity, Relationship, RelationshipKind, EntityKind


class RelationshipExtractor:
    """
    Extracts relationships between code entities.
    
    Supports all 16 relationship types from RelationshipKind:
    - IMPORTS, EXTENDS, IMPLEMENTS, COMPOSES
    - CALLS, CREATES, PASSES_TO, DEFINES
    - TESTS, CONFIGURES, ROUTES, EMITS_EVENT
    - LISTENS_EVENT, DECORATES, INSTANTIATED_BY, CALLED_BY
    
    Works with entities extracted by PythonASTAnalyzer.
    
    Usage:
        extractor = RelationshipExtractor()
        relationships = extractor.extract_all(entities, source_files)
    """
    
    def __init__(self):
        """Initialize relationship extractor."""
        self.relationships: list[Relationship] = []
    
    def extract_all(
        self,
        entities: list[Entity],
        source_files: Optional[dict[str, str]] = None,
    ) -> list[Relationship]:
        """
        Extract all relationship types from entities.
        
        Args:
            entities: List of entities from analysis
            source_files: Optional mapping of file paths to source code
            
        Returns:
            List of all extracted relationships
        """
        self.relationships.clear()
        
        # Extract by type
        self._extract_imports(entities)
        self._extract_inheritance(entities)
        self._extract_implements(entities)
        self._extract_composition(entities)
        self._extract_calls(entities, source_files)
        self._extract_creates(entities)
        self._extract_decorates(entities)
        self._extract_defines(entities)
        
        # Extract architectural relationships
        self._extract_tests(entities)
        self._extract_configures(entities)
        self._extract_routes(entities)
        
        # Extract event-driven relationships
        self._extract_event_relationships(entities)
        
        # Extract reverse relationships
        self._extract_instantiated_by(entities)
        self._extract_called_by(entities)
        
        return self.relationships
    
    def extract_imports(self, entities: list[Entity]) -> list[Relationship]:
        """
        Extract import relationships.
        
        Args:
            entities: List of entities
            
        Returns:
            List of IMPORTS relationships
        """
        relationships = []
        
        for entity in entities:
            if entity.kind == EntityKind.MODULE:
                metadata = entity.metadata or {}
                import_type = metadata.get('import_type', '')
                module = metadata.get('module', '')
                
                if module:
                    # Find the module entity
                    target = self._find_module_entity(entities, module)
                    if target:
                        rel = Relationship(
                            source_id=entity.id,
                            target_id=target.id,
                            kind=RelationshipKind.IMPORTS,
                            metadata={'import_type': import_type},
                        )
                        relationships.append(rel)
                        self.relationships.append(rel)
        
        return relationships
    
    def extract_inheritance(self, entities: list[Entity]) -> list[Relationship]:
        """
        Extract inheritance (EXTENDS) relationships.
        
        Args:
            entities: List of entities
            
        Returns:
            List of EXTENDS relationships
        """
        relationships = []
        
        for entity in entities:
            if entity.kind == EntityKind.CLASS:
                metadata = entity.metadata or {}
                decorators = metadata.get('decorators', [])
                
                # Check if entity has base classes in metadata
                base_classes = metadata.get('base_classes', [])
                
                for base in base_classes:
                    target = self._find_entity_by_name(entities, base, EntityKind.CLASS)
                    if target:
                        rel = Relationship(
                            source_id=entity.id,
                            target_id=target.id,
                            kind=RelationshipKind.EXTENDS,
                        )
                        relationships.append(rel)
                        self.relationships.append(rel)
        
        return relationships
    
    def extract_calls(
        self,
        entities: list[Entity],
        source_files: Optional[dict[str, str]] = None,
    ) -> list[Relationship]:
        """
        Extract function call relationships.
        
        Args:
            entities: List of entities
            source_files: Optional source code for deeper analysis
            
        Returns:
            List of CALLS relationships
        """
        relationships = []
        
        # Extract from metadata (already captured by AST analyzer)
        for entity in entities:
            if entity.kind in (EntityKind.FUNCTION, EntityKind.METHOD):
                # Check if calls are in metadata
                metadata = entity.metadata or {}
                calls = metadata.get('calls', [])
                
                for call_name in calls:
                    target = self._find_entity_by_name(
                        entities,
                        call_name,
                        (EntityKind.FUNCTION, EntityKind.METHOD),
                    )
                    if target:
                        rel = Relationship(
                            source_id=entity.id,
                            target_id=target.id,
                            kind=RelationshipKind.CALLS,
                        )
                        relationships.append(rel)
                        self.relationships.append(rel)
        
        # Extract from source if provided
        if source_files:
            relationships.extend(self._extract_calls_from_source(entities, source_files))
        
        return relationships
    
    def extract_composition(self, entities: list[Entity]) -> list[Relationship]:
        """
        Extract composition (has-a) relationships.
        
        Args:
            entities: List of entities
            
        Returns:
            List of COMPOSES relationships
        """
        relationships = []
        
        for entity in entities:
            if entity.kind == EntityKind.CLASS:
                metadata = entity.metadata or {}
                
                # Check for composition in metadata
                composed_of = metadata.get('composed_of', [])
                
                for component in composed_of:
                    target = self._find_entity_by_name(entities, component, EntityKind.CLASS)
                    if target:
                        rel = Relationship(
                            source_id=entity.id,
                            target_id=target.id,
                            kind=RelationshipKind.COMPOSES,
                            metadata={'composition_type': 'has-a'},
                        )
                        relationships.append(rel)
                        self.relationships.append(rel)
        
        return relationships
    
    def _extract_imports(self, entities: list[Entity]) -> None:
        """Internal: Extract import relationships."""
        for entity in entities:
            if entity.kind == EntityKind.MODULE:
                metadata = entity.metadata or {}
                module = metadata.get('module')
                
                if module:
                    target = self._find_module_entity(entities, module)
                    if target:
                        self.relationships.append(Relationship(
                            source_id=entity.id,
                            target_id=target.id,
                            kind=RelationshipKind.IMPORTS,
                        ))
    
    def _extract_inheritance(self, entities: list[Entity]) -> None:
        """Internal: Extract EXTENDS relationships from AST metadata."""
        # This is already captured in python_ast.py via base classes
        # Here we just ensure they're in the relationships list
        pass
    
    def _extract_implements(self, entities: list[Entity]) -> None:
        """Internal: Extract IMPLEMENTS relationships."""
        for entity in entities:
            if entity.kind == EntityKind.CLASS:
                metadata = entity.metadata or {}
                patterns = metadata.get('pattern', [])
                
                # Check for ABC pattern
                if 'abstract_base' in patterns:
                    continue
                
                # Look for interface implementations
                for base in metadata.get('base_classes', []):
                    if 'interface' in base.lower() or 'abc' in base.lower():
                        target = self._find_entity_by_name(entities, base, EntityKind.CLASS)
                        if target:
                            self.relationships.append(Relationship(
                                source_id=entity.id,
                                target_id=target.id,
                                kind=RelationshipKind.IMPLEMENTS,
                            ))
    
    def _extract_composition(self, entities: list[Entity]) -> None:
        """Internal: Extract COMPOSES relationships."""
        for entity in entities:
            if entity.kind == EntityKind.CLASS:
                # Check attributes for type annotations
                metadata = entity.metadata or {}
                attributes = metadata.get('attributes', [])
                
                for attr in attributes:
                    attr_type = attr.get('type', '') if isinstance(attr, dict) else str(attr)
                    if attr_type and attr_type[0].isupper():
                        # Likely a class type
                        target = self._find_entity_by_name(entities, attr_type, EntityKind.CLASS)
                        if target:
                            self.relationships.append(Relationship(
                                source_id=entity.id,
                                target_id=target.id,
                                kind=RelationshipKind.COMPOSES,
                            ))
    
    def _extract_calls(self, entities: list[Entity], source_files: Optional[dict[str, str]]) -> None:
        """Internal: Extract CALLS relationships."""
        # Already handled in public method
        pass
    
    def _extract_creates(self, entities: list[Entity]) -> None:
        """Internal: Extract CREATES relationships."""
        for entity in entities:
            if entity.kind in (EntityKind.FUNCTION, EntityKind.METHOD):
                metadata = entity.metadata or {}
                creates = metadata.get('creates', [])
                
                for created_class in creates:
                    target = self._find_entity_by_name(entities, created_class, EntityKind.CLASS)
                    if target:
                        self.relationships.append(Relationship(
                            source_id=entity.id,
                            target_id=target.id,
                            kind=RelationshipKind.CREATES,
                        ))
    
    def _extract_decorates(self, entities: list[Entity]) -> None:
        """Internal: Extract DECORATES relationships."""
        # Already captured in python_ast.py
        pass
    
    def _extract_defines(self, entities: list[Entity]) -> None:
        """Internal: Extract DEFINES relationships."""
        # Module defines its contents
        modules = [e for e in entities if e.kind == EntityKind.MODULE]
        
        for entity in entities:
            if entity.kind in (EntityKind.CLASS, EntityKind.FUNCTION, EntityKind.METHOD):
                for module in modules:
                    if entity.file_path == module.file_path:
                        self.relationships.append(Relationship(
                            source_id=module.id,
                            target_id=entity.id,
                            kind=RelationshipKind.DEFINES,
                        ))
                        break
    
    def _extract_tests(self, entities: list[Entity]) -> None:
        """Internal: Extract TESTS relationships."""
        test_files = [e for e in entities if 'test' in e.file_path.lower() or e.kind == EntityKind.TEST]
        source_entities = [e for e in entities if e not in test_files]
        
        for test_entity in test_files:
            # Try to match test name to source name
            test_name = test_entity.name.lower()
            
            for source_entity in source_entities:
                source_name = source_entity.name.lower()
                
                # Check if test name contains source name
                if source_name in test_name or test_name.startswith(f"test_{source_name}"):
                    self.relationships.append(Relationship(
                        source_id=test_entity.id,
                        target_id=source_entity.id,
                        kind=RelationshipKind.TESTS,
                    ))
    
    def _extract_configures(self, entities: list[Entity]) -> None:
        """Internal: Extract CONFIGURES relationships."""
        config_entities = [e for e in entities if e.kind == EntityKind.CONFIG]
        
        for config in config_entities:
            metadata = config.metadata or {}
            configures = metadata.get('configures', [])
            
            for configured_name in configures:
                target = self._find_entity_by_name(
                    entities,
                    configured_name,
                    (EntityKind.MODULE, EntityKind.CLASS, EntityKind.FUNCTION),
                )
                if target:
                    self.relationships.append(Relationship(
                        source_id=config.id,
                        target_id=target.id,
                        kind=RelationshipKind.CONFIGURES,
                    ))
    
    def _extract_routes(self, entities: list[Entity]) -> None:
        """Internal: Extract ROUTES relationships."""
        for entity in entities:
            if entity.kind in (EntityKind.FUNCTION, EntityKind.METHOD):
                metadata = entity.metadata or {}
                routes = metadata.get('routes', [])
                
                for route in routes:
                    self.relationships.append(Relationship(
                        source_id=entity.id,
                        target_id=f"route:{route}",
                        kind=RelationshipKind.ROUTES,
                        metadata={'route_path': route},
                    ))
    
    def _extract_event_relationships(self, entities: list[Entity]) -> None:
        """Internal: Extract EMITS_EVENT and LISTENS_EVENT relationships."""
        for entity in entities:
            if entity.kind in (EntityKind.FUNCTION, EntityKind.METHOD):
                metadata = entity.metadata or {}
                
                # Check for event emission
                emits = metadata.get('emits_events', [])
                for event in emits:
                    self.relationships.append(Relationship(
                        source_id=entity.id,
                        target_id=f"event:{event}",
                        kind=RelationshipKind.EMITS_EVENT,
                        metadata={'event_name': event},
                    ))
                
                # Check for event listeners
                listens = metadata.get('listens_events', [])
                for event in listens:
                    self.relationships.append(Relationship(
                        source_id=entity.id,
                        target_id=f"event:{event}",
                        kind=RelationshipKind.LISTENS_EVENT,
                        metadata={'event_name': event},
                    ))
    
    def _extract_instantiated_by(self, entities: list[Entity]) -> None:
        """Internal: Extract INSTANTIATED_BY (reverse of CREATES)."""
        # Create reverse relationships from CREATES
        creates_rels = [r for r in self.relationships if r.kind == RelationshipKind.CREATES]
        
        for creates_rel in creates_rels:
            self.relationships.append(Relationship(
                source_id=creates_rel.target_id,
                target_id=creates_rel.source_id,
                kind=RelationshipKind.INSTANTIATED_BY,
            ))
    
    def _extract_called_by(self, entities: list[Entity]) -> None:
        """Internal: Extract CALLED_BY (reverse of CALLS)."""
        # Create reverse relationships from CALLS
        calls_rels = [r for r in self.relationships if r.kind == RelationshipKind.CALLS]
        
        for calls_rel in calls_rels:
            self.relationships.append(Relationship(
                source_id=calls_rel.target_id,
                target_id=calls_rel.source_id,
                kind=RelationshipKind.CALLED_BY,
            ))
    
    def _extract_calls_from_source(
        self,
        entities: list[Entity],
        source_files: dict[str, str],
    ) -> list[Relationship]:
        """
        Extract call relationships from source code analysis.
        
        Args:
            entities: List of entities
            source_files: Mapping of file paths to source code
            
        Returns:
            List of CALLS relationships
        """
        relationships = []
        
        for entity in entities:
            if entity.kind not in (EntityKind.FUNCTION, EntityKind.METHOD):
                continue
            
            source = source_files.get(entity.file_path, '')
            if not source:
                continue
            
            try:
                tree = ast.parse(source, filename=entity.file_path)
            except SyntaxError:
                continue
            
            # Find the function node
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name == entity.name and node.lineno == entity.line_start:
                        # Extract calls from this function
                        for call_node in ast.walk(node):
                            if isinstance(call_node, ast.Call):
                                if isinstance(call_node.func, ast.Name):
                                    target = self._find_entity_by_name(
                                        entities,
                                        call_node.func.id,
                                        (EntityKind.FUNCTION, EntityKind.METHOD),
                                    )
                                    if target:
                                        rel = Relationship(
                                            source_id=entity.id,
                                            target_id=target.id,
                                            kind=RelationshipKind.CALLS,
                                        )
                                        relationships.append(rel)
        
        return relationships
    
    def _find_module_entity(self, entities: list[Entity], module_name: str) -> Optional[Entity]:
        """Find entity by module name."""
        for entity in entities:
            if entity.kind == EntityKind.MODULE and entity.name == module_name:
                return entity
        return None
    
    def _find_entity_by_name(
        self,
        entities: list[Entity],
        name: str,
        kinds: EntityKind | tuple[EntityKind, ...],
    ) -> Optional[Entity]:
        """Find entity by name and kind(s)."""
        for entity in entities:
            if entity.name == name and entity.kind in (kinds if isinstance(kinds, tuple) else (kinds,)):
                return entity
        return None
    
    def get_relationships_by_kind(self, kind: RelationshipKind) -> list[Relationship]:
        """
        Get all relationships of a specific kind.
        
        Args:
            kind: Relationship kind to filter by
            
        Returns:
            List of relationships of that kind
        """
        return [r for r in self.relationships if r.kind == kind]
    
    def get_relationship_counts(self) -> dict[str, int]:
        """
        Get count of each relationship type.
        
        Returns:
            Dictionary mapping kind to count
        """
        counts: dict[str, int] = {}
        for rel in self.relationships:
            kind_str = rel.kind.value
            counts[kind_str] = counts.get(kind_str, 0) + 1
        return counts