#!/usr/bin/env python3
"""
Project Resources for KB MCP v4.

Provides project-level resources:
- knowledge-base://project/tree
- knowledge-base://project/summary
- knowledge-base://project/metadata
"""

import json
from pathlib import Path
from typing import Any

from .registry import ResourceHandler, ResourceRegistry, ResourceResult


class ProjectResources(ResourceHandler):
    """
    Handler for project-level resources.
    
    Exposes:
    - project/tree: Full directory tree with entity annotations
    - project/summary: One-paragraph project summary
    - project/metadata: Language, framework, package info
    """
    
    def __init__(self, project_root: str | None = None):
        """
        Initialize project resources.
        
        Args:
            project_root: Root directory of the project (optional)
        """
        self._project_root = Path(project_root) if project_root else None
    
    @property
    def category_prefix(self) -> str:
        return "project"
    
    def register_resources(self, registry: ResourceRegistry) -> None:
        """Register all project resources."""
        registry.register_resource(
            uri="knowledge-base://project/tree",
            name="Project Tree",
            description="Full directory tree with entity annotations",
            mimetype="application/json",
        )
        
        registry.register_resource(
            uri="knowledge-base://project/summary",
            name="Project Summary",
            description="One-paragraph project summary",
            mimetype="text/plain",
        )
        
        registry.register_resource(
            uri="knowledge-base://project/metadata",
            name="Project Metadata",
            description="Language, framework, package manager, dependencies",
            mimetype="application/json",
        )
    
    def read_resource(self, path: str, query_params: dict[str, str] | None = None) -> ResourceResult:
        """
        Read a project resource.
        
        Args:
            path: Resource path (tree, summary, or metadata)
            query_params: Optional query parameters
            
        Returns:
            ResourceResult with content
            
        Raises:
            FileNotFoundError: If resource doesn't exist
        """
        query_params = query_params or {}
        
        if path == "tree":
            return self._read_tree(query_params)
        elif path == "summary":
            return self._read_summary(query_params)
        elif path == "metadata":
            return self._read_metadata(query_params)
        else:
            raise FileNotFoundError(f"Unknown project resource: {path}")
    
    def _read_tree(self, query_params: dict[str, str]) -> ResourceResult:
        """Read the project tree."""
        graph = self.get_graph()
        if not graph:
            return ResourceResult(
                uri="knowledge-base://project/tree",
                content=json.dumps({"error": "Graph not connected", "tree": []}),
                mimetype="application/json",
            )
        
        # Build tree from entities
        entities = graph.get_all_entities()
        tree = self._build_tree(entities, query_params)
        
        return ResourceResult(
            uri="knowledge-base://project/tree",
            content=json.dumps(tree, indent=2),
            mimetype="application/json",
        )
    
    def _build_tree(self, entities: list[Any], query_params: dict[str, str]) -> dict[str, Any]:
        """Build a tree structure from entities."""
        if not entities:
            return {"root": self._project_root or ".", "children": []}
        
        # Group entities by directory
        tree_structure: dict[str, dict] = {}
        
        for entity in entities:
            # Get relative path
            file_path = Path(entity.file_path)
            try:
                if self._project_root:
                    rel_path = file_path.relative_to(Path(self._project_root))
                else:
                    rel_path = file_path
            except ValueError:
                rel_path = file_path
            
            # Build directory structure
            parts = rel_path.parts
            current = tree_structure
            
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {"_type": "directory", "_children": {}}
                current = current[part]["_children"]
            
            # Add file with entity
            filename = parts[-1]
            if filename not in current:
                current[filename] = {
                    "_type": "file",
                    "_path": str(file_path),
                    "entities": [],
                }
            
            current[filename]["entities"].append({
                "id": entity.id,
                "kind": entity.kind.value if hasattr(entity.kind, 'value') else entity.kind,
                "name": entity.name,
                "line_start": entity.line_start,
                "line_end": entity.line_end,
            })
        
        # Convert to serializable format
        def convert(node: dict, depth: int = 0) -> dict | None:
            if depth > int(query_params.get("max_depth", 10)):
                return None
            
            if "_type" not in node:
                return None
            
            result = {
                "name": node.get("_name", ""),
                "type": node["_type"],
            }
            
            if node["_type"] == "directory":
                children = []
                for child_name, child_data in node.get("_children", {}).items():
                    child_data["_name"] = child_name
                    converted = convert(child_data, depth + 1)
                    if converted:
                        children.append(converted)
                result["children"] = sorted(children, key=lambda x: (x["type"] != "directory", x["name"]))
            
            if node["_type"] == "file":
                result["path"] = node.get("_path", "")
                result["entities"] = node.get("entities", [])
            
            return result
        
        # Build root
        root_path = str(self._project_root) if self._project_root else "."
        root = {
            "root": root_path,
            "children": [],
        }
        
        for dir_name, dir_data in tree_structure.items():
            dir_data["_name"] = dir_name
            converted = convert(dir_data)
            if converted:
                root["children"].append(converted)
        
        root["children"].sort(key=lambda x: (x["type"] != "directory", x["name"]))
        
        return root
    
    def _read_summary(self, query_params: dict[str, str]) -> ResourceResult:
        """Read the project summary."""
        graph = self.get_graph()
        
        if not graph or graph.num_entities == 0:
            return ResourceResult(
                uri="knowledge-base://project/summary",
                content="This project has not been analyzed yet. Run kb_populate_workspace_tool to index the codebase.",
                mimetype="text/plain",
            )
        
        # Generate summary from graph metadata
        metadata = graph.metadata
        entities = graph.get_all_entities()
        
        # Count by kind
        kind_counts: dict[str, int] = {}
        for entity in entities:
            kind = entity.kind.value if hasattr(entity.kind, 'value') else entity.kind
            kind_counts[kind] = kind_counts.get(kind, 0) + 1
        
        # Count by layer
        layer_counts: dict[str, int] = {}
        for entity in entities:
            layer = entity.metadata.get("layer", "unknown")
            layer_counts[layer] = layer_counts.get(layer, 0) + 1
        
        # Build summary
        summary_lines = [
            f"This project contains {metadata.total_entities} code entities with {metadata.total_relationships} relationships.",
            "",
            "Entity breakdown:",
        ]
        
        for kind, count in sorted(kind_counts.items()):
            summary_lines.append(f"  - {count} {kind}(s)")
        
        if any(layer != "unknown" for layer in layer_counts):
            summary_lines.append("")
            summary_lines.append("Architecture layers:")
            for layer, count in sorted(layer_counts.items()):
                if layer != "unknown":
                    summary_lines.append(f"  - {layer}: {count} entities")
        
        summary_lines.append("")
        summary_lines.append(f"Languages: {', '.join(metadata.languages) if metadata.languages else 'Python'}")
        summary_lines.append(f"Last updated: {metadata.updated_at.strftime('%Y-%m-%d %H:%M')}")
        
        return ResourceResult(
            uri="knowledge-base://project/summary",
            content="\n".join(summary_lines),
            mimetype="text/plain",
        )
    
    def _read_metadata(self, query_params: dict[str, str]) -> ResourceResult:
        """Read the project metadata."""
        graph = self.get_graph()
        
        metadata = {
            "project_root": str(self._project_root) if self._project_root else None,
            "languages": [],
            "framework": None,
            "package_manager": None,
            "dependencies": [],
            "config_files": [],
            "analysis_info": {},
        }
        
        if graph:
            metadata["analysis_info"] = graph.metadata.to_dict()
            metadata["languages"] = graph.metadata.languages or ["python"]
        
        # Detect from project root
        if self._project_root:
            root = Path(self._project_root)
            
            # Check for Python
            if (root / "pyproject.toml").exists():
                metadata["package_manager"] = "pip (pyproject.toml)"
                metadata["config_files"].append("pyproject.toml")
            elif (root / "setup.py").exists():
                metadata["package_manager"] = "pip (setup.py)"
                metadata["config_files"].append("setup.py")
            elif (root / "requirements.txt").exists():
                metadata["package_manager"] = "pip (requirements.txt)"
                metadata["config_files"].append("requirements.txt")
            
            # Check for framework indicators
            if (root / "manage.py").exists():
                metadata["framework"] = "Django"
            elif (root / "app.py").exists() or (root / "main.py").exists():
                # Check for FastAPI/Flask indicators in files
                metadata["framework"] = "Unknown (check main.py/app.py)"
        
        return ResourceResult(
            uri="knowledge-base://project/metadata",
            content=json.dumps(metadata, indent=2),
            mimetype="application/json",
        )