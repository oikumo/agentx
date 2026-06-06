#!/usr/bin/env python3
"""
Consolidated Graph Exporters for KB MCP v4.

Provides export functions for different formats with format negotiation
and proper error handling.
"""

import json
from pathlib import Path
from typing import Any, Literal, Optional, Union

from .engine import KnowledgeGraph
from .models import Entity, Relationship


ExportFormat = Literal["json", "mermaid", "dot", "ascii"]


class ExportError(Exception):
    """Exception raised when export fails."""
    pass


def export_json(
    graph: KnowledgeGraph,
    pretty: bool = True,
    include_metadata: bool = True,
) -> str:
    """
    Export graph to JSON format.
    
    Args:
        graph: The KnowledgeGraph to export
        pretty: Whether to pretty-print JSON with indentation
        include_metadata: Whether to include graph metadata
        
    Returns:
        JSON string representation of the graph
        
    Raises:
        ExportError: If export fails
    """
    try:
        data = graph.to_dict()
        
        if not include_metadata:
            data.pop("metadata", None)
        
        if pretty:
            return json.dumps(data, indent=2, default=str, ensure_ascii=False)
        return json.dumps(data, default=str, ensure_ascii=False)
    
    except Exception as e:
        raise ExportError(f"Failed to export graph to JSON: {e}") from e


def export_mermaid(
    graph: KnowledgeGraph,
    root_entity_id: Optional[str] = None,
    max_depth: int = 3,
    show_labels: bool = True,
    direction: str = "TD",
) -> str:
    """
    Export graph to Mermaid.js diagram format.
    
    Args:
        graph: The KnowledgeGraph to export
        root_entity_id: Optional root entity to center diagram around
        max_depth: Maximum depth from root (if root specified)
        show_labels: Whether to show relationship labels on edges
        direction: Diagram direction (TD, LR, RL, BT)
        
    Returns:
        Mermaid diagram string
        
    Raises:
        ExportError: If export fails
    """
    try:
        lines = [f"graph {direction}"]
        
        entity_ids: set[str] = set()
        relationships: list[Relationship] = []
        
        if root_entity_id:
            root_entity = graph.get_entity(root_entity_id)
            if not root_entity:
                raise ExportError(f"Root entity not found: {root_entity_id}")
            
            entities = graph.traverse(root_entity_id, depth=max_depth)
            entity_ids = {root_entity_id} | {e.id for e in entities}
            
            for rel in graph.get_all_relationships():
                if rel.source_id in entity_ids and rel.target_id in entity_ids:
                    relationships.append(rel)
        else:
            all_entities = graph.get_all_entities()[:50]
            entity_ids = {e.id for e in all_entities}
            
            for rel in graph.get_all_relationships():
                if rel.source_id in entity_ids and rel.target_id in entity_ids:
                    relationships.append(rel)
        
        for entity in graph.get_all_entities():
            if entity.id not in entity_ids:
                continue
            
            safe_id = _sanitize_mermaid_id(entity.id)
            kind = entity.kind.value if hasattr(entity.kind, "value") else entity.kind
            label = f"{entity.name}\\n({kind})"
            lines.append(f'    {safe_id}["{label}"]')
        
        for rel in relationships:
            source_id = _sanitize_mermaid_id(rel.source_id)
            target_id = _sanitize_mermaid_id(rel.target_id)
            kind = rel.kind.value if hasattr(rel.kind, "value") else rel.kind
            
            if show_labels:
                lines.append(f"    {source_id} -->|{kind}| {target_id}")
            else:
                lines.append(f"    {source_id} --> {target_id}")
        
        return "\n".join(lines)
    
    except ExportError:
        raise
    except Exception as e:
        raise ExportError(f"Failed to export graph to Mermaid: {e}") from e


def export_dot(
    graph: KnowledgeGraph,
    root_entity_id: Optional[str] = None,
    max_depth: int = 3,
    layout: str = "dot",
    rankdir: str = "TB",
) -> str:
    """
    Export graph to Graphviz DOT format.
    
    Args:
        graph: The KnowledgeGraph to export
        root_entity_id: Optional root entity for subgraph
        max_depth: Maximum depth from root
        layout: Layout algorithm (dot, neato, fdp, sfdp, circo)
        rankdir: Direction of graph ranking (TB, LR, RL, BT)
        
    Returns:
        DOT format string
        
    Raises:
        ExportError: If export fails
    """
    try:
        lines = [
            "digraph KnowledgeGraph {",
            f"    layout={layout};",
            f"    rankdir={rankdir};",
            "    node [shape=box, style=rounded];",
        ]
        
        entity_ids: set[str] = set()
        relationships: list[Relationship] = []
        
        if root_entity_id:
            root_entity = graph.get_entity(root_entity_id)
            if not root_entity:
                raise ExportError(f"Root entity not found: {root_entity_id}")
            
            entities = graph.traverse(root_entity_id, depth=max_depth)
            entity_ids = {root_entity_id} | {e.id for e in entities}
            
            for rel in graph.get_all_relationships():
                if rel.source_id in entity_ids and rel.target_id in entity_ids:
                    relationships.append(rel)
        else:
            all_entities = graph.get_all_entities()[:50]
            entity_ids = {e.id for e in all_entities}
            
            for rel in graph.get_all_relationships():
                if rel.source_id in entity_ids and rel.target_id in entity_ids:
                    relationships.append(rel)
        
        colors = {
            "class": "#FFD700",
            "function": "#87CEEB",
            "method": "#98FB98",
            "module": "#DDA0DD",
            "interface": "#FFA07A",
            "config": "#D3D3D3",
            "test": "#FF6347",
            "package": "#90EE90",
        }
        
        for entity in graph.get_all_entities():
            if entity.id not in entity_ids:
                continue
            
            node_id = _sanitize_dot_id(entity.id)
            kind = entity.kind.value if hasattr(entity.kind, "value") else entity.kind
            
            color = colors.get(kind, "#FFFFFF")
            label = f"{entity.name}\\n({kind})"
            lines.append(f'    {node_id} [label="{label}", style=filled, fillcolor="{color}"];')
        
        for rel in relationships:
            source_id = _sanitize_dot_id(rel.source_id)
            target_id = _sanitize_dot_id(rel.target_id)
            kind = rel.kind.value if hasattr(rel.kind, "value") else rel.kind
            
            lines.append(f'    {source_id} -> {target_id} [label="{kind}"];')
        
        lines.append("}")
        return "\n".join(lines)
    
    except ExportError:
        raise
    except Exception as e:
        raise ExportError(f"Failed to export graph to DOT: {e}") from e


def export_ascii(
    graph: KnowledgeGraph,
    root_entity_id: Optional[str] = None,
    max_depth: int = 2,
    max_width: int = 80,
    use_unicode: bool = True,
) -> str:
    """
    Export graph to ASCII tree format.
    
    Args:
        graph: The KnowledgeGraph to export
        root_entity_id: Root entity for tree view
        max_depth: Maximum depth to display
        max_width: Maximum line width
        use_unicode: Whether to use Unicode box-drawing characters
        
    Returns:
        ASCII tree string
        
    Raises:
        ExportError: If export fails
    """
    try:
        if not root_entity_id:
            modules = [e for e in graph.get_all_entities() if _get_entity_kind(e) == "module"]
            
            if not modules:
                return "No entities to display"
            
            lines = ["Knowledge Graph (Top-Level Modules)", "=" * 40]
            for module in modules[:10]:
                lines.append(f"📦 {module.name}" if use_unicode else f"[PKG] {module.name}")
                lines.append(f"   └── {module.file_path}" if use_unicode else f"    -> {module.file_path}")
            return "\n".join(lines)
        
        root = graph.get_entity(root_entity_id)
        if not root:
            return f"Entity {root_entity_id} not found"
        
        title = f"Knowledge Graph (Root: {root.name})"
        lines = [title, "=" * min(len(title), max_width)]
        
        icons = {
            "class": "🏛️",
            "function": "⚙️",
            "method": "🔧",
            "module": "📦",
            "interface": "🔌",
            "config": "⚙️",
            "test": "🧪",
            "package": "📦",
        } if use_unicode else {
            "class": "[CLS]",
            "function": "[FUNC]",
            "method": "[METH]",
            "module": "[MOD]",
            "interface": "[IFACE]",
            "config": "[CFG]",
            "test": "[TEST]",
            "package": "[PKG]",
        }
        
        def format_entity(entity: Entity) -> str:
            kind = _get_entity_kind(entity)
            icon = icons.get(kind, "📄" if use_unicode else "[ENT]")
            return f"{icon} {entity.name}"
        
        def add_tree(entity_id: str, prefix: str = "", depth: int = 0):
            if depth > max_depth:
                return
            
            entity = graph.get_entity(entity_id)
            if not entity:
                return
            
            rels = graph.get_relationships(entity_id, direction="outgoing")
            
            if depth == 0:
                lines.append(format_entity(entity)[:max_width])
            else:
                lines.append(f"{prefix}├── {format_entity(entity)}"[:max_width] if use_unicode else f"{prefix}+-- {format_entity(entity)}"[:max_width])
            
            for i, rel in enumerate(rels[:5]):
                is_last = i == len(rels[:5]) - 1
                child_prefix = prefix + ("    " if is_last else "│   ") if use_unicode else prefix + ("    " if is_last else "|   ")
                
                rel_line = f"{prefix}│   └── [{rel.kind.value}]" if use_unicode else f"{prefix}    +-- [{rel.kind.value}]"
                lines.append(rel_line[:max_width])
                
                add_tree(rel.target_id, child_prefix, depth + 1)
        
        add_tree(root_entity_id)
        
        lines = [line[:max_width] for line in lines]
        return "\n".join(lines)
    
    except Exception as e:
        raise ExportError(f"Failed to export graph to ASCII: {e}") from e


def export(
    graph: KnowledgeGraph,
    format: ExportFormat = "json",
    **kwargs: Any,
) -> str:
    """
    Export graph with format negotiation.
    
    Args:
        graph: The KnowledgeGraph to export
        format: Export format (json, mermaid, dot, ascii)
        **kwargs: Format-specific keyword arguments
        
    Returns:
        Exported graph string in specified format
        
    Raises:
        ExportError: If format is unknown or export fails
    """
    exporters: dict[ExportFormat, Any] = {
        "json": export_json,
        "mermaid": export_mermaid,
        "dot": export_dot,
        "ascii": export_ascii,
    }
    
    if format not in exporters:
        raise ExportError(f"Unknown export format: {format}. Supported: {list(exporters.keys())}")
    
    exporter = exporters[format]
    return exporter(graph, **kwargs)


def export_to_file(
    graph: KnowledgeGraph,
    path: Union[str, Path],
    format: Optional[ExportFormat] = None,
    **kwargs: Any,
) -> Path:
    """
    Export graph to a file.
    
    Args:
        graph: The KnowledgeGraph to export
        path: Output file path
        format: Export format (auto-detected from extension if not provided)
        **kwargs: Format-specific keyword arguments
        
    Returns:
        Path to the created file
        
    Raises:
        ExportError: If format cannot be determined or export fails
    """
    path = Path(path)
    
    if format is None:
        format = _detect_format_from_extension(path.suffix)
        if format is None:
            raise ExportError(f"Cannot determine export format from extension: {path.suffix}")
    
    content = export(graph, format, **kwargs)
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return path


def _detect_format_from_extension(extension: str) -> Optional[ExportFormat]:
    """
    Detect export format from file extension.
    
    Args:
        extension: File extension (e.g., ".json", ".mmd")
        
    Returns:
        ExportFormat or None if unknown
    """
    mapping = {
        ".json": "json",
        ".mmd": "mermaid",
        ".mermaid": "mermaid",
        ".dot": "dot",
        ".gv": "dot",
        ".txt": "ascii",
        ".text": "ascii",
        ".ascii": "ascii",
    }
    return mapping.get(extension.lower())


def _sanitize_mermaid_id(entity_id: str) -> str:
    """Sanitize entity ID for Mermaid diagram."""
    return entity_id.replace(":", "_").replace(".", "_").replace("-", "_")


def _sanitize_dot_id(entity_id: str) -> str:
    """Sanitize entity ID for DOT format."""
    return entity_id.replace(":", "_").replace(".", "_").replace("-", "_")


def _get_entity_kind(entity: Entity) -> str:
    """Get entity kind as string."""
    return entity.kind.value if hasattr(entity.kind, "value") else entity.kind