#!/usr/bin/env python3
"""
Resource Registry for KB MCP v4.

Handles registration and routing of MCP Resources via URI scheme.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

from graph.engine import KnowledgeGraph
from graph.models import Entity


@dataclass
class ResourceInfo:
    """Metadata about a registered resource."""
    uri: str
    name: str
    description: str
    mimetype: str = "application/json"
    is_template: bool = False
    template_pattern: Optional[str] = None


@dataclass
class ResourceResult:
    """Result of a resource read operation."""
    uri: str
    content: str
    mimetype: str
    metadata: dict[str, Any] | None = None


class ResourceHandler(ABC):
    """
    Abstract base class for resource handlers.
    
    Each handler is responsible for a category of resources
    (e.g., project/, arch/, flows/, etc.).
    """
    
    @property
    @abstractmethod
    def category_prefix(self) -> str:
        """
        Get the URI prefix for this handler.
        
        Returns:
            Prefix string (e.g., "project", "arch")
        """
        pass
    
    @abstractmethod
    def register_resources(self, registry: "ResourceRegistry") -> None:
        """
        Register all resources provided by this handler.
        
        Args:
            registry: The resource registry to register with
        """
        pass
    
    @abstractmethod
    def read_resource(self, path: str, query_params: dict[str, str] | None = None) -> ResourceResult:
        """
        Read a resource at the given path.
        
        Args:
            path: The path within the category (after the prefix)
            query_params: Optional query parameters
            
        Returns:
            ResourceResult with content and metadata
            
        Raises:
            FileNotFoundError: If resource doesn't exist
        """
        pass
    
    def set_graph(self, graph: KnowledgeGraph) -> None:
        """
        Set the knowledge graph reference.
        
        Args:
            graph: The knowledge graph to use
        """
        self._graph = graph
    
    def get_graph(self) -> KnowledgeGraph | None:
        """Get the knowledge graph reference."""
        return getattr(self, "_graph", None)


class ResourceRegistry:
    """
    Central registry for all MCP Resources.
    
    Handles URI routing, template matching, and resource resolution.
    
    Example Usage:
        registry = ResourceRegistry()
        registry.register_handler(ProjectResources())
        result = registry.read("knowledge-base://project/summary")
    """
    
    def __init__(self):
        """Initialize the resource registry."""
        self._handlers: dict[str, ResourceHandler] = {}
        self._resources: dict[str, ResourceInfo] = {}
        self._templates: list[tuple[re.Pattern, ResourceInfo, Callable]] = []
        self._graph: KnowledgeGraph | None = None
    
    def set_graph(self, graph: KnowledgeGraph) -> None:
        """
        Set the knowledge graph for all handlers.
        
        Args:
            graph: The knowledge graph to use
        """
        self._graph = graph
        # Propagate to all registered handlers
        for handler in self._handlers.values():
            handler.set_graph(graph)
    
    def get_graph(self) -> KnowledgeGraph | None:
        """Get the knowledge graph."""
        return self._graph
    
    def register_handler(self, handler: ResourceHandler) -> None:
        """
        Register a resource handler.
        
        Args:
            handler: The handler to register
        """
        prefix = handler.category_prefix
        if prefix in self._handlers:
            raise ValueError(f"Handler for prefix '{prefix}' already registered")
        
        # Set graph reference if available
        if self._graph:
            handler.set_graph(self._graph)
        
        self._handlers[prefix] = handler
        
        # Let handler register its resources
        handler.register_resources(self)
    
    def register_resource(
        self,
        uri: str,
        name: str,
        description: str,
        mimetype: str = "application/json",
        is_template: bool = False,
        template_pattern: str | None = None,
    ) -> None:
        """
        Register a resource URI.
        
        Args:
            uri: The full URI or template pattern
            name: Human-readable name
            description: Resource description
            mimetype: Content MIME type
            is_template: Whether this is a template with parameters
            template_pattern: Regex pattern for template matching
        """
        info = ResourceInfo(
            uri=uri,
            name=name,
            description=description,
            mimetype=mimetype,
            is_template=is_template,
            template_pattern=template_pattern,
        )
        
        if is_template and template_pattern:
            self._templates.append((re.compile(template_pattern), info, None))
        else:
            self._resources[uri] = info
    
    def register_template(
        self,
        uri_pattern: str,
        name: str,
        description: str,
        mimetype: str = "application/json",
    ) -> None:
        """
        Register a resource template with parameter capture.
        
        Args:
            uri_pattern: URI pattern with named groups (e.g., r"entity/(?P<entity_id>.+)")
            name: Human-readable name
            description: Resource description
            mimetype: Content MIME type
        """
        info = ResourceInfo(
            uri=uri_pattern,
            name=name,
            description=description,
            mimetype=mimetype,
            is_template=True,
            template_pattern=uri_pattern,
        )
        self._templates.append((re.compile(uri_pattern), info, None))
    
    def list_resources(self) -> list[ResourceInfo]:
        """
        List all registered resources.
        
        Returns:
            List of resource info objects
        """
        return list(self._resources.values()) + [info for _, info, _ in self._templates]
    
    def has_resource(self, uri: str) -> bool:
        """
        Check if a resource exists at the given URI.
        
        Args:
            uri: The URI to check
            
        Returns:
            True if resource exists
        """
        # Check exact match
        if uri in self._resources:
            return True
        
        # Check template matches
        uri_path = self._extract_path(uri)
        for pattern, _, _ in self._templates:
            if pattern.match(uri_path):
                return True
        
        return False
    
    def read(self, uri: str, query_params: dict[str, str] | None = None) -> ResourceResult:
        """
        Read a resource at the given URI.
        
        Args:
            uri: The full URI (e.g., "knowledge-base://project/summary")
            query_params: Optional query parameters
            
        Returns:
            ResourceResult with content and metadata
            
        Raises:
            FileNotFoundError: If resource doesn't exist
            ValueError: If URI format is invalid
        """
        # Parse URI
        if not uri.startswith("knowledge-base://"):
            raise ValueError(f"Invalid URI scheme: {uri}")
        
        path = uri[len("knowledge-base://"):]
        
        # Extract category prefix
        parts = path.split("/", 1)
        if len(parts) < 1:
            raise ValueError(f"Invalid URI: {uri}")
        
        prefix = parts[0]
        resource_path = parts[1] if len(parts) > 1 else ""
        
        # Find handler
        if prefix not in self._handlers:
            raise FileNotFoundError(f"No handler for category: {prefix}")
        
        handler = self._handlers[prefix]
        
        # Delegate to handler
        try:
            result = handler.read_resource(resource_path, query_params)
            # Ensure URI is preserved in result
            result.uri = uri
            return result
        except FileNotFoundError:
            raise
    
    def _extract_path(self, uri: str) -> str:
        """Extract the path portion from a URI."""
        if not uri.startswith("knowledge-base://"):
            return uri
        return uri[len("knowledge-base://"):]
    
    def get_handler(self, prefix: str) -> ResourceHandler | None:
        """
        Get a handler by prefix.
        
        Args:
            prefix: The category prefix
            
        Returns:
            The handler or None if not found
        """
        return self._handlers.get(prefix)
    
    def get_statistics(self) -> dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Dictionary with counts and metadata
        """
        return {
            "total_handlers": len(self._handlers),
            "total_resources": len(self._resources),
            "total_templates": len(self._templates),
            "categories": list(self._handlers.keys()),
            "graph_connected": self._graph is not None,
        }