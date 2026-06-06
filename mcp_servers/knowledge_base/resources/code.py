#!/usr/bin/env python3
"""
Code Resources for KB MCP v4.

Provides code-level resources:
- knowledge-base://code/entity/{id}
- knowledge-base://code/search/{query}
- knowledge-base://code/file/{path}
"""

import json
import re
from urllib.parse import unquote

from .registry import ResourceHandler, ResourceRegistry, ResourceResult


class CodeResources(ResourceHandler):
    """
    Handler for code-level resources.
    
    Exposes:
    - code/entity/{id}: Full entity details with relationships
    - code/search/{query}: Semantic code search results
    - code/file/{path}: Annotated file view
    """
    
    @property
    def category_prefix(self) -> str:
        return "code"
    
    def register_resources(self, registry: ResourceRegistry) -> None:
        """Register all code resources."""
        registry.register_template(
            uri_pattern=r"entity/(?P<entity_id>.+)",
            name="Entity Details",
            description="Full entity details with relationships",
            mimetype="application/json",
        )
        
        registry.register_template(
            uri_pattern=r"search/(?P<query>.+)",
            name="Code Search",
            description="Semantic code search results",
            mimetype="application/json",
        )
        
        registry.register_template(
            uri_pattern=r"file/(?P<file_path>.+)",
            name="File View",
            description="Annotated file view with entities",
            mimetype="application/json",
        )
    
    def read_resource(self, path: str, query_params: dict[str, str] | None = None) -> ResourceResult:
        """
        Read a code resource.
        
        Args:
            path: Resource path (entity/{id}, search/{query}, or file/{path})
            query_params: Optional query parameters
            
        Returns:
            ResourceResult with content
            
        Raises:
            FileNotFoundError: If resource doesn't exist
        """
        query_params = query_params or {}
        
        # Match entity/{id}
        entity_match = re.match(r"entity/(?P<entity_id>.+)", path)
        if entity_match:
            entity_id = unquote(entity_match.group("entity_id"))
            return self._read_entity(entity_id, query_params)
        
        # Match search/{query}
        search_match = re.match(r"search/(?P<query>.+)", path)
        if search_match:
            query = unquote(search_match.group("query"))
            return self._read_search(query, query_params)
        
        # Match file/{path}
        file_match = re.match(r"file/(?P<file_path>.+)", path)
        if file_match:
            file_path = unquote(file_match.group("file_path"))
            return self._read_file(file_path, query_params)
        
        raise FileNotFoundError(f"Unknown code resource path: {path}")
    
    def _read_entity(self, entity_id: str, query_params: dict[str, str]) -> ResourceResult:
        """Read entity details."""
        graph = self.get_graph()
        
        if not graph:
            return ResourceResult(
                uri=f"knowledge-base://code/entity/{entity_id}",
                content=json.dumps({"error": "Graph not connected"}),
                mimetype="application/json",
            )
        
        entity = graph.get_entity(entity_id)
        
        if not entity:
            return ResourceResult(
                uri=f"knowledge-base://code/entity/{entity_id}",
                content=json.dumps({"error": "Entity not found", "entity_id": entity_id}),
                mimetype="application/json",
                metadata={"status": 404},
            )
        
        # Get relationships
        relationships = graph.get_relationships(entity_id, direction="both")
        
        incoming = []
        outgoing = []
        
        for rel in relationships:
            rel_data = rel.to_dict()
            if rel.source_id == entity_id:
                # Outgoing
                target = graph.get_entity(rel.target_id)
                rel_data["target"] = {
                    "id": target.id if target else rel.target_id,
                    "name": target.name if target else "unknown",
                    "kind": target.kind.value if target and hasattr(target.kind, 'value') else (target.kind if target else "unknown"),
                } if target else {"id": rel.target_id}
                outgoing.append(rel_data)
            else:
                # Incoming
                source = graph.get_entity(rel.source_id)
                rel_data["source"] = {
                    "id": source.id if source else rel.source_id,
                    "name": source.name if source else "unknown",
                    "kind": source.kind.value if source and hasattr(source.kind, 'value') else (source.kind if source else "unknown"),
                } if source else {"id": rel.source_id}
                incoming.append(rel_data)
        
        result = {
            "entity": entity.to_dict(),
            "relationships": {
                "incoming": incoming,
                "outgoing": outgoing,
                "total_incoming": len(incoming),
                "total_outgoing": len(outgoing),
            },
        }
        
        # Include code snippet if requested
        if query_params.get("include_code") == "true":
            context_lines = int(query_params.get("context_lines", 5))
            code_snippet = self._extract_code_snippet(entity.file_path, entity.line_start, entity.line_end, context_lines)
            result["code_snippet"] = code_snippet
        
        return ResourceResult(
            uri=f"knowledge-base://code/entity/{entity_id}",
            content=json.dumps(result, indent=2),
            mimetype="application/json",
        )
    
    def _read_search(self, query: str, query_params: dict[str, str]) -> ResourceResult:
        """Search for entities."""
        graph = self.get_graph()
        
        if not graph:
            return ResourceResult(
                uri=f"knowledge-base://code/search/{query}",
                content=json.dumps({"error": "Graph not connected"}),
                mimetype="application/json",
            )
        
        entities = graph.get_all_entities()
        results = []
        
        # Simple name-based search
        query_lower = query.lower()
        
        for entity in entities:
            score = 0.0
            
            # Exact name match
            if entity.name.lower() == query_lower:
                score = 1.0
            # Contains query
            elif query_lower in entity.name.lower():
                score = 0.7
            # Query in docstring
            elif entity.docstring and query_lower in entity.docstring.summary.lower():
                score = 0.5
            # Query in file path
            elif query_lower in entity.file_path.lower():
                score = 0.3
            
            if score > 0.3:  # Threshold
                results.append({
                    "entity": entity.to_dict(),
                    "score": score,
                    "match_type": self._get_match_type(score),
                })
        
        # Sort by score
        results.sort(key=lambda x: -x["score"])
        
        # Limit results
        limit = int(query_params.get("limit", 20))
        results = results[:limit]
        
        return ResourceResult(
            uri=f"knowledge-base://code/search/{query}",
            content=json.dumps({
                "query": query,
                "results": results,
                "total_results": len(results),
                "limit": limit,
            }, indent=2),
            mimetype="application/json",
        )
    
    def _read_file(self, file_path: str, query_params: dict[str, str]) -> ResourceResult:
        """Read annotated file view."""
        graph = self.get_graph()
        
        if not graph:
            return ResourceResult(
                uri=f"knowledge-base://code/file/{file_path}",
                content=json.dumps({"error": "Graph not connected"}),
                mimetype="application/json",
            )
        
        # Find all entities in this file
        entities = graph.get_all_entities()
        file_entities = [e for e in entities if e.file_path == file_path]
        
        if not file_entities:
            return ResourceResult(
                uri=f"knowledge-base://code/file/{file_path}",
                content=json.dumps({
                    "error": "No entities found in file",
                    "file_path": file_path,
                }),
                mimetype="application/json",
                metadata={"status": 404},
            )
        
        # Sort by line number
        file_entities.sort(key=lambda e: e.line_start)
        
        # Build annotated view
        annotations = []
        for entity in file_entities:
            annotations.append({
                "line_start": entity.line_start,
                "line_end": entity.line_end,
                "kind": entity.kind.value if hasattr(entity.kind, 'value') else entity.kind,
                "name": entity.name,
                "docstring": entity.docstring.summary if entity.docstring else None,
            })
        
        # Try to read file content if path exists
        content_lines = []
        try:
            from pathlib import Path
            if Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content_lines = f.readlines()
        except Exception:
            pass
        
        result = {
            "file_path": file_path,
            "total_lines": len(content_lines),
            "entities": file_entities,
            "annotations": annotations,
            "content": "".join(content_lines) if query_params.get("include_content") == "true" else None,
        }
        
        return ResourceResult(
            uri=f"knowledge-base://code/file/{file_path}",
            content=json.dumps(result, indent=2),
            mimetype="application/json",
        )
    
    def _get_match_type(self, score: float) -> str:
        """Get match type description from score."""
        if score >= 1.0:
            return "exact_name"
        elif score >= 0.7:
            return "contains_name"
        elif score >= 0.5:
            return "docstring"
        else:
            return "file_path"
    
    def _extract_code_snippet(self, file_path: str, line_start: int, line_end: int, context_lines: int) -> dict:
        """Extract code snippet from file."""
        try:
            from pathlib import Path
            if not Path(file_path).exists():
                return {"error": "File not found"}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Add context
            start = max(0, line_start - 1 - context_lines)
            end = min(len(lines), line_end + context_lines)
            
            snippet_lines = lines[start:end]
            
            return {
                "file_path": file_path,
                "start_line": start + 1,
                "end_line": end,
                "content": "".join(snippet_lines),
            }
        except Exception as e:
            return {"error": str(e)}