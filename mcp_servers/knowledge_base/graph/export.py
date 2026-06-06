#!/usr/bin/env python3
"""
Graph export utilities for KB MCP v4.

Exports knowledge graph to various formats: JSON, Mermaid, DOT, ASCII.
"""

import json
from typing import Any, Optional

from .engine import KnowledgeGraph
from .models import Entity, Relationship


def export_json(graph: KnowledgeGraph, pretty: bool = True) -> str:
    """
    Export graph to JSON format.
    
    Args:
        graph: The KnowledgeGraph to export
        pretty: Whether to pretty-print JSON
        
    Returns:
        JSON string
    """
    data = graph.to_dict()
    if pretty:
        return json.dumps(data, indent=2, default=str)
    return json.dumps(data, default=str)


def export_mermaid(
    graph: KnowledgeGraph,
    root_entity_id: Optional[str] = None,
    max_depth: int = 3,
    show_labels: bool = True,
) -> str:
    """
    Export graph to Mermaid.js format.
    
    Args:
        graph: The KnowledgeGraph to export
        root_entity_id: Optional root entity to center diagram around
        max_depth: Maximum depth from root (if root specified)
        show_labels: Whether to show relationship labels
        
    Returns:
        Mermaid diagram string
    """
    lines = ["graph TD"]
    
    if root_entity_id:
        # Export subgraph around root
        entities = graph.traverse(root_entity_id, depth=max_depth)
        entity_ids = {root_entity_id} | {e.id for e in entities}
        relationships = [
            rel for rel in graph.get_all_relationships()
            if rel.source_id in entity_ids and rel.target_id in entity_ids
        ]
    else:
        # Export full graph (limit to first 50 entities for readability)
        all_entities = graph.get_all_entities()[:50]
        entity_ids = {e.id for e in all_entities}
        relationships = [
            rel for rel in graph.get_all_relationships()
            if rel.source_id in entity_ids and rel.target_id in entity_ids
        ]
    
    # Add nodes
    for entity in graph.get_all_entities():
        if entity.id in entity_ids:
            label = f"{entity.name}\\n({entity.kind.value})"
            lines.append(f'    {entity.id.replace(":", "_").replace(".", "_")}["{label}"]')
    
    # Add edges
    for rel in relationships:
        source_id = rel.source_id.replace(":", "_").replace(".", "_")
        target_id = rel.target_id.replace(":", "_").replace(".", "_")
        
        if show_labels:
            lines.append(f"    {source_id} -->|{rel.kind.value}| {target_id}")
        else:
            lines.append(f"    {source_id} --> {target_id}")
    
    return "\n".join(lines)


def export_dot(
    graph: KnowledgeGraph,
    root_entity_id: Optional[str] = None,
    max_depth: int = 3,
    layout: str = "dot",
) -> str:
    """
    Export graph to Graphviz DOT format.
    
    Args:
        graph: The KnowledgeGraph to export
        root_entity_id: Optional root entity
        max_depth: Maximum depth from root
        layout: Layout algorithm (dot, neato, fdp, sfdp, circo)
        
    Returns:
        DOT format string
    """
    lines = [f'digraph KnowledgeGraph {{', f'    layout={layout};']
    
    if root_entity_id:
        entities = graph.traverse(root_entity_id, depth=max_depth)
        entity_ids = {root_entity_id} | {e.id for e in entities}
        relationships = [
            rel for rel in graph.get_all_relationships()
            if rel.source_id in entity_ids and rel.target_id in entity_ids
        ]
    else:
        all_entities = graph.get_all_entities()[:50]
        entity_ids = {e.id for e in all_entities}
        relationships = [
            rel for rel in graph.get_all_relationships()
            if rel.source_id in entity_ids and rel.target_id in entity_ids
        ]
    
    # Add nodes with styling
    for entity in graph.get_all_entities():
        if entity.id not in entity_ids:
            continue
        
        node_id = entity.id.replace(":", "_").replace(".", "_")
        kind = entity.kind.value if hasattr(entity.kind, 'value') else entity.kind
        
        # Color by kind
        colors = {
            "class": "#FFD700",
            "function": "#87CEEB",
            "method": "#98FB98",
            "module": "#DDA0DD",
            "interface": "#FFA07A",
            "config": "#D3D3D3",
            "test": "#FF6347",
        }
        color = colors.get(kind, "#FFFFFF")
        
        label = f"{entity.name}\\n({kind})"
        lines.append(f'    {node_id} [label="{label}", style=filled, fillcolor="{color}"];')
    
    # Add edges with styling
    for rel in relationships:
        source_id = rel.source_id.replace(":", "_").replace(".", "_")
        target_id = rel.target_id.replace(":", "_").replace(".", "_")
        kind = rel.kind.value if hasattr(rel.kind, 'value') else rel.kind
        
        lines.append(f'    {source_id} -> {target_id} [label="{kind}"];')
    
    lines.append("}")
    return "\n".join(lines)


def export_ascii(
    graph: KnowledgeGraph,
    root_entity_id: Optional[str] = None,
    max_depth: int = 2,
    max_width: int = 80,
) -> str:
    """
    Export graph to ASCII tree format.
    
    Args:
        graph: The KnowledgeGraph to export
        root_entity_id: Root entity for tree view
        max_depth: Maximum depth to display
        max_width: Maximum line width
        
    Returns:
        ASCII tree string
    """
    if not root_entity_id:
        # If no root, show top-level modules only
        modules = [e for e in graph.get_all_entities() if e.kind.value == "module"]
        if not modules:
            return "No entities to display"
        
        lines = ["Knowledge Graph (Top-Level Modules)", "=" * 40]
        for module in modules[:10]:  # Limit to 10 modules
            lines.append(f"📦 {module.name}")
            lines.append(f"   └── {module.file_path}")
        return "\n".join(lines)
    
    # Build tree from root
    root = graph.get_entity(root_entity_id)
    if not root:
        return f"Entity {root_entity_id} not found"
    
    lines = [f"Knowledge Graph (Root: {root.name})", "=" * 60]
    
    def format_entity(entity: Entity) -> str:
        """Format entity for display."""
        icons = {
            "class": "🏛️",
            "function": "⚙️",
            "method": "🔧",
            "module": "📦",
            "interface": "🔌",
            "config": "⚙️",
            "test": "🧪",
        }
        icon = icons.get(entity.kind.value if hasattr(entity.kind, 'value') else entity.kind, "📄")
        return f"{icon} {entity.name}"
    
    def add_tree(entity_id: str, prefix: str = "", depth: int = 0):
        """Recursively add tree nodes."""
        if depth > max_depth:
            return
        
        entity = graph.get_entity(entity_id)
        if not entity:
            return
        
        # Get outgoing relationships
        rels = graph.get_relationships(entity_id, direction="outgoing")
        
        if depth == 0:
            lines.append(format_entity(entity))
        else:
            lines.append(f"{prefix}├── {format_entity(entity)}")
        
        # Add children
        for i, rel in enumerate(rels[:5]):  # Limit to 5 relationships per node
            is_last = (i == len(rels[:5]) - 1)
            child_prefix = prefix + ("    " if is_last else "│   ")
            
            # Show relationship type
            rel_line = f"{prefix}│   └── [{rel.kind.value}]"
            lines.append(rel_line)
            
            # Add child entity
            add_tree(rel.target_id, child_prefix, depth + 1)
    
    add_tree(root_entity_id)
    
    # Truncate long lines
    lines = [line[:max_width] for line in lines]
    
    return "\n".join(lines)


def export_entity_details(entity: Entity, relationships: list[Relationship]) -> str:
    """
    Export detailed information about a single entity.
    
    Args:
        entity: The entity to describe
        relationships: All relationships involving this entity
        
    Returns:
        Formatted details string
    """
    lines = []
    
    # Header
    lines.append(f"{'=' * 60}")
    lines.append(f"Entity: {entity.name}")
    lines.append(f"{'=' * 60}")
    
    # Basic info
    lines.append(f"Kind: {entity.kind.value if hasattr(entity.kind, 'value') else entity.kind}")
    lines.append(f"File: {entity.file_path}")
    lines.append(f"Lines: {entity.line_start}-{entity.line_end}")
    
    # Docstring
    if entity.docstring and entity.docstring.summary:
        lines.append(f"\nSummary: {entity.docstring.summary}")
    
    # Metadata
    if entity.metadata:
        lines.append("\nMetadata:")
        for key, value in entity.metadata.items():
            lines.append(f"  • {key}: {value}")
    
    # Relationships
    incoming = [r for r in relationships if r.target_id == entity.id]
    outgoing = [r for r in relationships if r.source_id == entity.id]
    
    if incoming:
        lines.append("\nIncoming Relationships:")
        for rel in incoming[:10]:  # Limit display
            lines.append(f"  ← [{rel.kind.value}] {rel.source_id}")
    
    if outgoing:
        lines.append("\nOutgoing Relationships:")
        for rel in outgoing[:10]:
            lines.append(f"  → [{rel.kind.value}] {rel.target_id}")
    
    return "\n".join(lines)


def export_summary(graph: KnowledgeGraph) -> str:
    """
    Export a summary of the graph.
    
    Args:
        graph: The KnowledgeGraph
        
    Returns:
        Summary string
    """
    stats = graph.get_all_entities()
    
    lines = [
        "Knowledge Graph Summary",
        "=" * 40,
        f"Total Entities: {graph.num_entities}",
        f"Total Relationships: {graph.num_relationships}",
        f"Average Relationships per Entity: {graph.num_relationships / graph.num_entities:.2f}" if graph.num_entities > 0 else "N/A",
        "",
    ]
    
    # Count by kind
    by_kind = {}
    for entity in graph.get_all_entities():
        kind = entity.kind.value if hasattr(entity.kind, 'value') else entity.kind
        by_kind[kind] = by_kind.get(kind, 0) + 1
    
    lines.append("Entities by Kind:")
    for kind, count in sorted(by_kind.items()):
        lines.append(f"  • {kind}: {count}")
    
    # Count by relationship kind
    by_rel = {}
    for rel in graph.get_all_relationships():
        kind = rel.kind.value if hasattr(rel.kind, 'value') else rel.kind
        by_rel[kind] = by_rel.get(kind, 0) + 1
    
    lines.append("\nRelationships by Kind:")
    for kind, count in sorted(by_rel.items()):
        lines.append(f"  • {kind}: {count}")
    
    # Cycles
    cycles = graph.find_cycles()
    if cycles:
        lines.append(f"\n⚠️  Circular Dependencies Detected: {len(cycles)}")
    else:
        lines.append("\n✅ No circular dependencies detected")
    
    return "\n".join(lines)