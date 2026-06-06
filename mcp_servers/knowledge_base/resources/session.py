#!/usr/bin/env python3
"""
Session Resources for KB MCP v4.

Provides agent session context:
- knowledge-base://session/context
"""

import json
from datetime import datetime
from typing import Any

from .registry import ResourceHandler, ResourceRegistry, ResourceResult


class SessionResources(ResourceHandler):
    """
    Handler for agent session context resources.
    
    Exposes:
    - session/context: Current agent session accumulated context
    """
    
    def __init__(self):
        """Initialize session resources."""
        self._sessions: dict[str, dict[str, Any]] = {}
    
    @property
    def category_prefix(self) -> str:
        return "session"
    
    def register_resources(self, registry: ResourceRegistry) -> None:
        """Register session resources."""
        registry.register_resource(
            uri="knowledge-base://session/context",
            name="Session Context",
            description="Current agent session accumulated context",
            mimetype="application/json",
        )
    
    def read_resource(self, path: str, query_params: dict[str, str] | None = None) -> ResourceResult:
        """
        Read a session resource.
        
        Args:
            path: Resource path (context)
            query_params: Optional query parameters (session_id)
            
        Returns:
            ResourceResult with content
            
        Raises:
            FileNotFoundError: If resource doesn't exist
        """
        query_params = query_params or {}
        
        if path == "context":
            session_id = query_params.get("session_id", "default")
            return self._read_context(session_id, query_params)
        else:
            raise FileNotFoundError(f"Unknown session resource: {path}")
    
    def _read_context(self, session_id: str, query_params: dict[str, str]) -> ResourceResult:
        """Read session context."""
        session = self._sessions.get(session_id)
        
        if not session:
            # Return empty context
            context = {
                "session_id": session_id,
                "created_at": None,
                "updated_at": None,
                "queries": [],
                "learned_entities": [],
                "visited_resources": [],
                "objectives": [],
            }
        else:
            context = {
                "session_id": session_id,
                "created_at": session.get("created_at"),
                "updated_at": session.get("updated_at"),
                "queries": session.get("queries", []),
                "learned_entities": session.get("learned_entities", []),
                "visited_resources": session.get("visited_resources", []),
                "objectives": session.get("objectives", []),
            }
        
        return ResourceResult(
            uri="knowledge-base://session/context",
            content=json.dumps(context, indent=2),
            mimetype="application/json",
        )
    
    def update_context(
        self,
        session_id: str,
        query: str | None = None,
        entity_id: str | None = None,
        resource_uri: str | None = None,
        objective: str | None = None,
    ) -> None:
        """
        Update session context.
        
        Args:
            session_id: The session ID
            query: Optional query that was executed
            entity_id: Optional entity that was learned
            resource_uri: Optional resource that was visited
            objective: Optional objective to add
        """
        now = datetime.now().isoformat()
        
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "created_at": now,
                "updated_at": now,
                "queries": [],
                "learned_entities": [],
                "visited_resources": [],
                "objectives": [],
            }
        
        session = self._sessions[session_id]
        session["updated_at"] = now
        
        if query:
            session["queries"].append({
                "query": query,
                "timestamp": now,
            })
            # Keep last 50 queries
            session["queries"] = session["queries"][-50:]
        
        if entity_id and entity_id not in session["learned_entities"]:
            session["learned_entities"].append({
                "entity_id": entity_id,
                "timestamp": now,
            })
        
        if resource_uri:
            session["visited_resources"].append({
                "uri": resource_uri,
                "timestamp": now,
            })
            # Keep last 100 visited resources
            session["visited_resources"] = session["visited_resources"][-100:]
        
        if objective and objective not in session["objectives"]:
            session["objectives"].append(objective)
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear a session.
        
        Args:
            session_id: The session ID to clear
            
        Returns:
            True if session was cleared
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def get_statistics(self) -> dict[str, Any]:
        """Get session statistics."""
        return {
            "total_sessions": len(self._sessions),
            "active_sessions": len([s for s in self._sessions.values() if s.get("queries")]),
        }