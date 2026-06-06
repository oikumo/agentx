#!/usr/bin/env python3
"""
Knowledge Graph package for KB MCP v4.

Provides graph-based knowledge representation with NetworkX + SQLite.
"""

from .builder import GraphBuilder
from .engine import KnowledgeGraph
from .export import (
    export_ascii,
    export_dot,
    export_entity_details,
    export_json,
    export_mermaid,
    export_summary,
)
from .models import (
    DocstringInfo,
    Entity,
    EntityKind,
    GraphMetadata,
    GraphPath,
    ImpactResult,
    Relationship,
    RelationshipKind,
)
from .queries import GraphQueries
from .store import GraphStore
from .sync import GraphSync

__all__ = [
    # Core
    "KnowledgeGraph",
    "GraphBuilder",
    "GraphStore",
    "GraphQueries",
    "GraphSync",
    # Models
    "Entity",
    "EntityKind",
    "Relationship",
    "RelationshipKind",
    "DocstringInfo",
    "GraphMetadata",
    "GraphPath",
    "ImpactResult",
    # Export functions
    "export_json",
    "export_mermaid",
    "export_dot",
    "export_ascii",
    "export_entity_details",
    "export_summary",
]

__version__ = "4.0.0"