#!/usr/bin/env python3
"""
Architecture Resources for KB MCP v4.

Provides architecture-level resources:
- knowledge-base://arch/components
- knowledge-base://arch/dependencies
- knowledge-base://arch/layers
- knowledge-base://arch/patterns
"""

import json
from typing import Any

from graph.export import export_ascii, export_dot, export_mermaid
from graph.models import EntityKind

from .registry import ResourceHandler, ResourceRegistry, ResourceResult


class ArchitectureResources(ResourceHandler):
    """
    Handler for architecture resources.
    
    Exposes:
    - arch/components: All components with descriptions
    - arch/dependencies: Dependency graph (JSON/DOT/Mermaid)
    - arch/layers: Architecture layers
    - arch/patterns: Detected design patterns
    """
    
    @property
    def category_prefix(self) -> str:
        return "arch"
    
    def register_resources(self, registry: ResourceRegistry) -> None:
        """Register all architecture resources."""
        registry.register_resource(
            uri="knowledge-base://arch/components",
            name="Components",
            description="All components with descriptions",
            mimetype="application/json",
        )
        
        registry.register_resource(
            uri="knowledge-base://arch/dependencies",
            name="Dependencies",
            description="Dependency graph (supports format=json|dot|mermaid|ascii)",
            mimetype="application/json",
        )
        
        registry.register_resource(
            uri="knowledge-base://arch/layers",
            name="Architecture Layers",
            description="Architecture layers with components",
            mimetype="application/json",
        )
        
        registry.register_resource(
            uri="knowledge-base://arch/patterns",
            name="Design Patterns",
            description="Detected design patterns with locations",
            mimetype="application/json",
        )
    
    def read_resource(self, path: str, query_params: dict[str, str] | None = None) -> ResourceResult:
        """
        Read an architecture resource.
        
        Args:
            path: Resource path (components, dependencies, layers, or patterns)
            query_params: Optional query parameters (format for dependencies)
            
        Returns:
            ResourceResult with content
            
        Raises:
            FileNotFoundError: If resource doesn't exist
        """
        query_params = query_params or {}
        
        if path == "components":
            return self._read_components(query_params)
        elif path == "dependencies":
            return self._read_dependencies(query_params)
        elif path == "layers":
            return self._read_layers(query_params)
        elif path == "patterns":
            return self._read_patterns(query_params)
        else:
            raise FileNotFoundError(f"Unknown architecture resource: {path}")
    
    def _read_components(self, query_params: dict[str, str]) -> ResourceResult:
        """Read all components."""
        graph = self.get_graph()
        
        if not graph:
            return ResourceResult(
                uri="knowledge-base://arch/components",
                content=json.dumps({"error": "Graph not connected"}),
                mimetype="application/json",
            )
        
        entities = graph.get_all_entities()
        components = []
        
        for entity in entities:
            # Only include classes, functions, modules (not methods)
            kind = entity.kind.value if hasattr(entity.kind, 'value') else entity.kind
            if kind in ["class", "function", "module"]:
                component = {
                    "id": entity.id,
                    "kind": kind,
                    "name": entity.name,
                    "file_path": entity.file_path,
                    "line_start": entity.line_start,
                    "line_end": entity.line_end,
                    "layer": entity.metadata.get("layer", "unknown"),
                    "patterns": entity.metadata.get("patterns", []),
                }
                
                if entity.docstring:
                    component["description"] = entity.docstring.summary
                
                components.append(component)
        
        # Sort by layer, then name
        components.sort(key=lambda x: (x["layer"], x["name"]))
        
        return ResourceResult(
            uri="knowledge-base://arch/components",
            content=json.dumps({"components": components}, indent=2),
            mimetype="application/json",
        )
    
    def _read_dependencies(self, query_params: dict[str, str]) -> ResourceResult:
        """Read dependency graph in requested format."""
        graph = self.get_graph()
        
        if not graph:
            return ResourceResult(
                uri="knowledge-base://arch/dependencies",
                content=json.dumps({"error": "Graph not connected"}),
                mimetype="application/json",
            )
        
        fmt = query_params.get("format", "json").lower()
        
        if fmt == "json":
            content = json.dumps(graph.to_dict(), indent=2)
            mimetype = "application/json"
        elif fmt == "dot":
            content = export_dot(graph, directed=True)
            mimetype = "text/vnd.graphviz"
        elif fmt == "mermaid":
            content = export_mermaid(graph)
            mimetype = "text/plain"
        elif fmt == "ascii":
            content = export_ascii(graph)
            mimetype = "text/plain"
        else:
            content = json.dumps({"error": f"Unknown format: {fmt}"})
            mimetype = "application/json"
        
        return ResourceResult(
            uri="knowledge-base://arch/dependencies",
            content=content,
            mimetype=mimetype,
        )
    
    def _read_layers(self, query_params: dict[str, str]) -> ResourceResult:
        """Read architecture layers."""
        graph = self.get_graph()
        
        if not graph:
            return ResourceResult(
                uri="knowledge-base://arch/layers",
                content=json.dumps({"error": "Graph not connected"}),
                mimetype="application/json",
            )
        
        entities = graph.get_all_entities()
        
        # Group by layer
        layers: dict[str, list[dict]] = {}
        for entity in entities:
            layer = entity.metadata.get("layer", "unknown")
            if layer not in layers:
                layers[layer] = []
            
            layers[layer].append({
                "id": entity.id,
                "name": entity.name,
                "kind": entity.kind.value if hasattr(entity.kind, 'value') else entity.kind,
                "file_path": entity.file_path,
                "patterns": entity.metadata.get("patterns", []),
            })
        
        # Sort entities within each layer
        for layer in layers:
            layers[layer].sort(key=lambda x: x["name"])
        
        # Build layer dependency map
        layer_deps: dict[str, set[str]] = {}
        relationships = graph.get_all_relationships()
        
        for rel in relationships:
            source_entity = graph.get_entity(rel.source_id)
            target_entity = graph.get_entity(rel.target_id)
            
            if source_entity and target_entity:
                source_layer = source_entity.metadata.get("layer", "unknown")
                target_layer = target_entity.metadata.get("layer", "unknown")
                
                if source_layer != target_layer:
                    if source_layer not in layer_deps:
                        layer_deps[source_layer] = set()
                    layer_deps[source_layer].add(target_layer)
        
        result = {
            "layers": {
                layer: {
                    "count": len(entities),
                    "components": entities,
                }
                for layer, entities in sorted(layers.items())
            },
            "layer_dependencies": {
                layer: list(deps)
                for layer, deps in sorted(layer_deps.items())
            },
        }
        
        return ResourceResult(
            uri="knowledge-base://arch/layers",
            content=json.dumps(result, indent=2),
            mimetype="application/json",
        )
    
    def _read_patterns(self, query_params: dict[str, str]) -> ResourceResult:
        """Read detected design patterns."""
        graph = self.get_graph()
        
        if not graph:
            return ResourceResult(
                uri="knowledge-base://arch/patterns",
                content=json.dumps({"error": "Graph not connected"}),
                mimetype="application/json",
            )
        
        entities = graph.get_all_entities()
        
        # Group patterns by type
        patterns: dict[str, list[dict]] = {}
        
        for entity in entities:
            entity_patterns = entity.metadata.get("patterns", [])
            for pattern in entity_patterns:
                if pattern not in patterns:
                    patterns[pattern] = []
                
                patterns[pattern].append({
                    "entity_id": entity.id,
                    "name": entity.name,
                    "kind": entity.kind.value if hasattr(entity.kind, 'value') else entity.kind,
                    "file_path": entity.file_path,
                    "confidence": entity.metadata.get("pattern_confidence", 0.5),
                })
        
        # Sort patterns by count
        sorted_patterns = dict(sorted(patterns.items(), key=lambda x: -len(x[1])))
        
        result = {
            "patterns": sorted_patterns,
            "total_patterns": len(patterns),
            "total_instances": sum(len(instances) for instances in patterns.values()),
        }
        
        return ResourceResult(
            uri="knowledge-base://arch/patterns",
            content=json.dumps(result, indent=2),
            mimetype="application/json",
        )