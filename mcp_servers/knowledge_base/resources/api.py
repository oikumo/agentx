#!/usr/bin/env python3
"""
API Resources for KB MCP v4.

Provides API surface resources:
- knowledge-base://api/endpoints
- knowledge-base://api/public
- knowledge-base://api/config
"""

import json
from pathlib import Path

from .registry import ResourceHandler, ResourceRegistry, ResourceResult


class APIResources(ResourceHandler):
    """
    Handler for API surface resources.
    
    Exposes:
    - api/endpoints: All API endpoints (for web services)
    - api/public: Public API surface
    - api/config: Configuration surface & env vars
    """
    
    @property
    def category_prefix(self) -> str:
        return "api"
    
    def register_resources(self, registry: ResourceRegistry) -> None:
        """Register all API resources."""
        registry.register_resource(
            uri="knowledge-base://api/endpoints",
            name="API Endpoints",
            description="All API endpoints (for web services)",
            mimetype="application/json",
        )
        
        registry.register_resource(
            uri="knowledge-base://api/public",
            name="Public API",
            description="Public API surface (classes/functions meant for external use)",
            mimetype="application/json",
        )
        
        registry.register_resource(
            uri="knowledge-base://api/config",
            name="Configuration",
            description="Configuration surface and environment variables",
            mimetype="application/json",
        )
    
    def read_resource(self, path: str, query_params: dict[str, str] | None = None) -> ResourceResult:
        """
        Read an API resource.
        
        Args:
            path: Resource path (endpoints, public, or config)
            query_params: Optional query parameters
            
        Returns:
            ResourceResult with content
            
        Raises:
            FileNotFoundError: If resource doesn't exist
        """
        query_params = query_params or {}
        
        if path == "endpoints":
            return self._read_endpoints(query_params)
        elif path == "public":
            return self._read_public_api(query_params)
        elif path == "config":
            return self._read_config(query_params)
        else:
            raise FileNotFoundError(f"Unknown API resource: {path}")
    
    def _read_endpoints(self, query_params: dict[str, str]) -> ResourceResult:
        """Read API endpoints."""
        graph = self.get_graph()
        
        if not graph:
            return ResourceResult(
                uri="knowledge-base://api/endpoints",
                content=json.dumps({"error": "Graph not connected"}),
                mimetype="application/json",
            )
        
        # Look for route decorators, endpoint markers
        entities = graph.get_all_entities()
        endpoints = []
        
        for entity in entities:
            # Detect web framework endpoints by metadata or name patterns
            metadata = entity.metadata
            if metadata.get("is_endpoint") or self._is_endpoint(entity):
                endpoint = {
                    "id": entity.id,
                    "name": entity.name,
                    "file_path": entity.file_path,
                    "line_start": entity.line_start,
                    "line_end": entity.line_end,
                }
                
                # Try to extract route info
                route = metadata.get("route")
                if route:
                    endpoint["route"] = route
                
                method = metadata.get("method")
                if method:
                    endpoint["method"] = method
                
                endpoints.append(endpoint)
        
        # Group by file
        by_file: dict[str, list] = {}
        for ep in endpoints:
            file_path = ep["file_path"]
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(ep)
        
        return ResourceResult(
            uri="knowledge-base://api/endpoints",
            content=json.dumps({
                "endpoints": endpoints,
                "by_file": by_file,
                "total_endpoints": len(endpoints),
            }, indent=2),
            mimetype="application/json",
        )
    
    def _read_public_api(self, query_params: dict[str, str]) -> ResourceResult:
        """Read public API surface."""
        graph = self.get_graph()
        
        if not graph:
            return ResourceResult(
                uri="knowledge-base://api/public",
                content=json.dumps({"error": "Graph not connected"}),
                mimetype="application/json",
            )
        
        entities = graph.get_all_entities()
        public_api = []
        
        for entity in entities:
            # Check if entity is marked as public
            metadata = entity.metadata
            if metadata.get("is_public") or self._is_public(entity):
                api_item = {
                    "id": entity.id,
                    "name": entity.name,
                    "kind": entity.kind.value if hasattr(entity.kind, 'value') else entity.kind,
                    "file_path": entity.file_path,
                    "line_start": entity.line_start,
                    "line_end": entity.line_end,
                }
                
                if entity.docstring:
                    api_item["description"] = entity.docstring.summary
                
                public_api.append(api_item)
        
        # Sort by kind, then name
        public_api.sort(key=lambda x: (x["kind"], x["name"]))
        
        return ResourceResult(
            uri="knowledge-base://api/public",
            content=json.dumps({
                "public_api": public_api,
                "total_items": len(public_api),
            }, indent=2),
            mimetype="application/json",
        )
    
    def _read_config(self, query_params: dict[str, str]) -> ResourceResult:
        """Read configuration surface."""
        graph = self.get_graph()
        
        config = {
            "config_files": [],
            "env_vars": [],
            "settings_classes": [],
            "cli_args": [],
        }
        
        if graph:
            entities = graph.get_all_entities()
            
            for entity in entities:
                name = entity.name.lower()
                kind = entity.kind.value if hasattr(entity.kind, 'value') else entity.kind
                
                # Detect config classes
                if kind == "class" and ("config" in name or "settings" in name or "options" in name):
                    config["settings_classes"].append({
                        "id": entity.id,
                        "name": entity.name,
                        "file_path": entity.file_path,
                    })
                
                # Detect CLI argument parsers
                if "argparse" in entity.file_path.lower() or "click" in entity.file_path.lower():
                    config["cli_args"].append({
                        "id": entity.id,
                        "name": entity.name,
                        "file_path": entity.file_path,
                    })
        
        # Check project root for config files
        project_root = getattr(self, "_project_root", None)
        if project_root:
            root = Path(project_root)
            config_files = [
                "pyproject.toml", "setup.py", "requirements.txt",
                ".env", "config.json", "settings.yaml", "settings.yml",
            ]
            
            for cf in config_files:
                if (root / cf).exists():
                    config["config_files"].append({
                        "name": cf,
                        "path": str(root / cf),
                    })
        
        return ResourceResult(
            uri="knowledge-base://api/config",
            content=json.dumps(config, indent=2),
            mimetype="application/json",
        )
    
    def _is_endpoint(self, entity) -> bool:
        """Check if entity is a web endpoint."""
        # Check for common web framework patterns
        name = entity.name.lower()
        file_path = entity.file_path.lower()
        
        # Flask/FastAPI patterns
        if "route" in entity.metadata.get("decorators", []):
            return True
        
        # Common endpoint names
        endpoint_keywords = ["handler", "endpoint", "route", "view", "controller"]
        return any(kw in name for kw in endpoint_keywords)
    
    def _is_public(self, entity) -> bool:
        """Check if entity is part of public API."""
        # Check metadata
        if entity.metadata.get("is_public"):
            return True
        
        # Check if in __all__ (would need to parse module)
        # For now, use heuristics
        
        # Public classes/functions typically don't start with underscore
        name = entity.name
        if name.startswith("_"):
            return False
        
        # Check docstring quality (public APIs usually have good docs)
        if entity.docstring and entity.docstring.summary:
            return True
        
        # Check if in public module (api/, public/, __init__.py exports)
        file_path = entity.file_path.lower()
        if "/api/" in file_path or "/public/" in file_path:
            return True
        
        return False