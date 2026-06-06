#!/usr/bin/env python3
"""
Flow Resources for KB MCP v4.

Provides flow-level resources:
- knowledge-base://flows/data
- knowledge-base://flows/control
- knowledge-base://flows/imports
- knowledge-base://flows/events
"""

import json
from typing import Any

from graph.models import RelationshipKind

from .registry import ResourceHandler, ResourceRegistry, ResourceResult


class FlowResources(ResourceHandler):
    """
    Handler for flow resources.
    
    Exposes:
    - flows/data: End-to-end data flow descriptions
    - flows/control: Main call chains
    - flows/imports: Import hierarchy
    - flows/events: Event/pub-sub channels
    """
    
    @property
    def category_prefix(self) -> str:
        return "flows"
    
    def register_resources(self, registry: ResourceRegistry) -> None:
        """Register all flow resources."""
        registry.register_resource(
            uri="knowledge-base://flows/data",
            name="Data Flow",
            description="End-to-end data flow paths",
            mimetype="application/json",
        )
        
        registry.register_resource(
            uri="knowledge-base://flows/control",
            name="Control Flow",
            description="Main call chains and control flow",
            mimetype="application/json",
        )
        
        registry.register_resource(
            uri="knowledge-base://flows/imports",
            name="Import Flow",
            description="Import/export dependency chains",
            mimetype="application/json",
        )
        
        registry.register_resource(
            uri="knowledge-base://flows/events",
            name="Event Flow",
            description="Event/pub-sub channels and handlers",
            mimetype="application/json",
        )
    
    def read_resource(self, path: str, query_params: dict[str, str] | None = None) -> ResourceResult:
        """
        Read a flow resource.
        
        Args:
            path: Resource path (data, control, imports, or events)
            query_params: Optional query parameters
            
        Returns:
            ResourceResult with content
            
        Raises:
            FileNotFoundError: If resource doesn't exist
        """
        query_params = query_params or {}
        
        if path == "data":
            return self._read_data_flow(query_params)
        elif path == "control":
            return self._read_control_flow(query_params)
        elif path == "imports":
            return self._read_imports(query_params)
        elif path == "events":
            return self._read_events(query_params)
        else:
            raise FileNotFoundError(f"Unknown flow resource: {path}")
    
    def _read_data_flow(self, query_params: dict[str, str]) -> ResourceResult:
        """Read data flow paths."""
        graph = self.get_graph()
        
        if not graph:
            return ResourceResult(
                uri="knowledge-base://flows/data",
                content=json.dumps({"error": "Graph not connected"}),
                mimetype="application/json",
            )
        
        # Find data flow paths (entities with 'passes_to' relationships)
        relationships = graph.get_all_relationships()
        data_flows = []
        
        for rel in relationships:
            if rel.kind == RelationshipKind.PASSES_TO or rel.kind.value == "passes_to":
                source = graph.get_entity(rel.source_id)
                target = graph.get_entity(rel.target_id)
                
                if source and target:
                    data_flows.append({
                        "source": {
                            "id": source.id,
                            "name": source.name,
                            "file_path": source.file_path,
                        },
                        "target": {
                            "id": target.id,
                            "name": target.name,
                            "file_path": target.file_path,
                        },
                        "metadata": rel.metadata,
                    })
        
        # Also trace call chains as data flow
        depth = int(query_params.get("depth", 3))
        entry_points = self._find_entry_points(graph)
        
        flow_chains = []
        for entry in entry_points[:5]:  # Limit to 5 entry points
            chain = self._trace_call_chain(graph, entry["id"], depth, visited=set())
            if len(chain) > 1:
                flow_chains.append({
                    "entry_point": entry,
                    "chain": chain,
                })
        
        return ResourceResult(
            uri="knowledge-base://flows/data",
            content=json.dumps({
                "data_flows": data_flows,
                "flow_chains": flow_chains,
                "total_flows": len(data_flows),
                "total_chains": len(flow_chains),
            }, indent=2),
            mimetype="application/json",
        )
    
    def _read_control_flow(self, query_params: dict[str, str]) -> ResourceResult:
        """Read control flow (call graphs)."""
        graph = self.get_graph()
        
        if not graph:
            return ResourceResult(
                uri="knowledge-base://flows/control",
                content=json.dumps({"error": "Graph not connected"}),
                mimetype="application/json",
            )
        
        # Find all 'calls' relationships
        relationships = graph.get_all_relationships()
        call_graph = []
        
        for rel in relationships:
            if rel.kind == RelationshipKind.CALLS or rel.kind.value == "calls":
                source = graph.get_entity(rel.source_id)
                target = graph.get_entity(rel.target_id)
                
                if source and target:
                    call_graph.append({
                        "caller": {
                            "id": source.id,
                            "name": source.name,
                            "kind": source.kind.value if hasattr(source.kind, 'value') else source.kind,
                            "file_path": source.file_path,
                        },
                        "callee": {
                            "id": target.id,
                            "name": target.name,
                            "kind": target.kind.value if hasattr(target.kind, 'value') else target.kind,
                            "file_path": target.file_path,
                        },
                    })
        
        # Group by caller
        grouped: dict[str, list] = {}
        for call in call_graph:
            caller_id = call["caller"]["id"]
            if caller_id not in grouped:
                grouped[caller_id] = {
                    "caller": call["caller"],
                    "calls": [],
                }
            grouped[caller_id]["calls"].append(call["callee"])
        
        return ResourceResult(
            uri="knowledge-base://flows/control",
            content=json.dumps({
                "call_graph": list(grouped.values()),
                "total_calls": len(call_graph),
                "total_callers": len(grouped),
            }, indent=2),
            mimetype="application/json",
        )
    
    def _read_imports(self, query_params: dict[str, str]) -> ResourceResult:
        """Read import dependency chains."""
        graph = self.get_graph()
        
        if not graph:
            return ResourceResult(
                uri="knowledge-base://flows/imports",
                content=json.dumps({"error": "Graph not connected"}),
                mimetype="application/json",
            )
        
        # Find all 'imports' relationships
        relationships = graph.get_all_relationships()
        imports = []
        
        for rel in relationships:
            if rel.kind == RelationshipKind.IMPORTS or rel.kind.value == "imports":
                source = graph.get_entity(rel.source_id)
                target = graph.get_entity(rel.target_id)
                
                if source and target:
                    imports.append({
                        "importer": {
                            "id": source.id,
                            "name": source.name,
                            "file_path": source.file_path,
                        },
                        "imported": {
                            "id": target.id,
                            "name": target.name,
                            "file_path": target.file_path,
                        },
                    })
        
        # Group by file
        by_file: dict[str, list] = {}
        for imp in imports:
            file_path = imp["importer"]["file_path"]
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(imp["imported"])
        
        return ResourceResult(
            uri="knowledge-base://flows/imports",
            content=json.dumps({
                "imports_by_file": {
                    file_path: {
                        "importer": imp[0]["importer"] if imp else None,
                        "imports": imp,
                    }
                    for file_path, imp in by_file.items()
                },
                "total_imports": len(imports),
            }, indent=2),
            mimetype="application/json",
        )
    
    def _read_events(self, query_params: dict[str, str]) -> ResourceResult:
        """Read event/pub-sub channels."""
        graph = self.get_graph()
        
        if not graph:
            return ResourceResult(
                uri="knowledge-base://flows/events",
                content=json.dumps({"error": "Graph not connected"}),
                mimetype="application/json",
            )
        
        # Find event-related relationships
        relationships = graph.get_all_relationships()
        events = {
            "emitters": [],
            "listeners": [],
            "channels": {},
        }
        
        for rel in relationships:
            kind = rel.kind if isinstance(rel.kind, str) else rel.kind.value
            
            source = graph.get_entity(rel.source_id)
            target = graph.get_entity(rel.target_id)
            
            if kind == "emits_event" and source and target:
                events["emitters"].append({
                    "emitter": {
                        "id": source.id,
                        "name": source.name,
                        "file_path": source.file_path,
                    },
                    "event": target.name if target else "unknown",
                })
                # Track channel
                event_name = target.name if target else "unknown"
                if event_name not in events["channels"]:
                    events["channels"][event_name] = {"emitters": [], "listeners": []}
                events["channels"][event_name]["emitters"].append(source.id)
            
            elif kind == "listens_event" and source and target:
                events["listeners"].append({
                    "listener": {
                        "id": source.id,
                        "name": source.name,
                        "file_path": source.file_path,
                    },
                    "event": target.name if target else "unknown",
                })
                # Track channel
                event_name = target.name if target else "unknown"
                if event_name not in events["channels"]:
                    events["channels"][event_name] = {"emitters": [], "listeners": []}
                events["channels"][event_name]["listeners"].append(source.id)
        
        return ResourceResult(
            uri="knowledge-base://flows/events",
            content=json.dumps({
                "events": events,
                "total_emitters": len(events["emitters"]),
                "total_listeners": len(events["listeners"]),
                "total_channels": len(events["channels"]),
            }, indent=2),
            mimetype="application/json",
        )
    
    def _find_entry_points(self, graph) -> list[dict]:
        """Find entry points in the graph."""
        entities = graph.get_all_entities()
        entry_points = []
        
        for entity in entities:
            # Look for main functions, CLI entry points, etc.
            name = entity.name.lower()
            kind = entity.kind.value if hasattr(entity.kind, 'value') else entity.kind
            
            if kind == "function" and name in ["main", "run", "start", "execute"]:
                entry_points.append({
                    "id": entity.id,
                    "name": entity.name,
                    "file_path": entity.file_path,
                    "type": "function",
                })
        
        return entry_points
    
    def _trace_call_chain(self, graph, entity_id: str, depth: int, visited: set) -> list[dict]:
        """Trace a call chain from an entity."""
        if depth <= 0 or entity_id in visited:
            return []
        
        visited.add(entity_id)
        entity = graph.get_entity(entity_id)
        
        if not entity:
            return []
        
        chain = [{
            "id": entity.id,
            "name": entity.name,
            "file_path": entity.file_path,
        }]
        
        # Find outgoing calls
        relationships = graph.get_relationships(entity_id, direction="outgoing", relationship_kind="calls")
        
        for rel in relationships[:3]:  # Limit branching
            target_id = rel.target_id if rel.source_id == entity_id else rel.source_id
            sub_chain = self._trace_call_chain(graph, target_id, depth - 1, visited)
            if sub_chain:
                chain.extend(sub_chain)
                break  # Take first path
        
        return chain