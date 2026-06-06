#!/usr/bin/env python3
"""
Knowledge Graph Models for KB MCP v4.

Defines the core data structures for entities and relationships in the knowledge graph.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class EntityKind(str, Enum):
    """Types of code entities."""
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    MODULE = "module"
    INTERFACE = "interface"
    CONFIG = "config"
    TEST = "test"
    PACKAGE = "package"


class RelationshipKind(str, Enum):
    """Types of relationships between entities."""
    IMPORTS = "imports"           # Module A imports Module B
    EXTENDS = "extends"           # Class A extends Class B
    IMPLEMENTS = "implements"     # Class A implements Interface B
    COMPOSES = "composes"         # Class A has-a Class B
    CALLS = "calls"               # Function A calls Function B
    CREATES = "creates"           # Function A instantiates Class B
    PASSES_TO = "passes_to"       # Function A passes type to Function B
    DEFINES = "defines"           # Module defines Class/Function
    TESTS = "tests"               # Test file tests source file
    CONFIGURES = "configures"     # Config file sets value for module
    ROUTES = "routes"             # URL route maps to handler
    EMITS_EVENT = "emits_event"   # Function emits event E
    LISTENS_EVENT = "listens_event"  # Function listens for event E
    DECORATES = "decorates"       # Decorator A is applied to Class/Function B
    INSTANTIATED_BY = "instantiated_by"  # Class is instantiated by
    CALLED_BY = "called_by"       # Function is called by


@dataclass
class DocstringInfo:
    """Parsed docstring information."""
    summary: str = ""
    description: str = ""
    args: dict[str, str] = field(default_factory=dict)
    returns: Optional[str] = None
    raises: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)


@dataclass
class Entity:
    """
    Represents a code entity (class, function, method, module, etc.).
    
    Attributes:
        id: Unique identifier (format: {file_path}:{line_start}:{name})
        kind: Type of entity (class, function, method, etc.)
        name: Simple name of the entity
        file_path: Absolute path to the source file
        line_start: Starting line number (1-indexed)
        line_end: Ending line number (1-indexed)
        docstring: Parsed docstring information
        metadata: Additional metadata (layer, pattern, stability, etc.)
        created_at: Timestamp when entity was added to KB
    """
    id: str
    kind: EntityKind
    name: str
    file_path: str
    line_start: int
    line_end: int
    docstring: Optional[DocstringInfo] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "kind": self.kind.value if isinstance(self.kind, EntityKind) else self.kind,
            "name": self.name,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "docstring": {
                "summary": self.docstring.summary,
                "description": self.docstring.description,
                "args": self.docstring.args,
                "returns": self.docstring.returns,
            } if self.docstring else None,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Entity":
        """Create Entity from dictionary."""
        docstring = None
        if data.get("docstring"):
            ds = data["docstring"]
            docstring = DocstringInfo(
                summary=ds.get("summary", ""),
                description=ds.get("description", ""),
                args=ds.get("args", {}),
                returns=ds.get("returns"),
            )
        
        kind = data["kind"]
        if isinstance(kind, str):
            kind = EntityKind(kind)
        
        return cls(
            id=data["id"],
            kind=kind,
            name=data["name"],
            file_path=data["file_path"],
            line_start=data["line_start"],
            line_end=data["line_end"],
            docstring=docstring,
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
        )


@dataclass
class Relationship:
    """
    Represents a directed relationship between two entities.
    
    Attributes:
        id: Unique identifier (auto-generated)
        source_id: ID of the source entity
        target_id: ID of the target entity
        kind: Type of relationship
        metadata: Additional metadata (weight, confidence, etc.)
    """
    source_id: str
    target_id: str
    kind: RelationshipKind
    id: Optional[int] = None  # Auto-generated by database
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate relationship."""
        if self.source_id == self.target_id:
            raise ValueError("Relationship cannot have same source and target")
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "kind": self.kind.value if isinstance(self.kind, RelationshipKind) else self.kind,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Relationship":
        """Create Relationship from dictionary."""
        kind = data["kind"]
        if isinstance(kind, str):
            kind = RelationshipKind(kind)
        
        return cls(
            id=data.get("id"),
            source_id=data["source_id"],
            target_id=data["target_id"],
            kind=kind,
            metadata=data.get("metadata", {}),
        )


@dataclass
class GraphMetadata:
    """Metadata about the knowledge graph."""
    total_entities: int = 0
    total_relationships: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "4.0.0"
    project_root: Optional[str] = None
    languages: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_entities": self.total_entities,
            "total_relationships": self.total_relationships,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "project_root": self.project_root,
            "languages": self.languages,
        }


@dataclass
class ImpactResult:
    """Result of impact analysis for an entity."""
    entity_id: str
    change_type: str  # "modify", "delete", "add"
    affected_entities: list[str]
    risk_levels: dict[str, str]  # entity_id -> "high"|"medium"|"low"
    test_files: list[str]
    depth: int
    warnings: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "entity_id": self.entity_id,
            "change_type": self.change_type,
            "affected_entities": self.affected_entities,
            "risk_levels": self.risk_levels,
            "test_files": self.test_files,
            "depth": self.depth,
            "warnings": self.warnings,
        }


@dataclass
class GraphPath:
    """Represents a path through the graph."""
    entities: list[str]  # List of entity IDs in path
    relationships: list[Relationship]  # Relationships connecting them
    total_weight: float = 1.0
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "entities": self.entities,
            "relationships": [r.to_dict() for r in self.relationships],
            "total_weight": self.total_weight,
        }