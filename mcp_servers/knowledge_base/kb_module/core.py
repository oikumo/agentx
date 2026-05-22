#!/usr/bin/env python3
"""
Knowledge Base Core API - Adapted for MCP

This module provides a clean, MCP-friendly API for the Meta Harness Knowledge Base.
It wraps the ChromaDB-based RAG system with proper error handling and return types.
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Import path setup
# ---------------------------------------------------------------------------
# The MCP wheel ships ``meta_harness_knowledge_base/src/`` alongside this
# module (see ``pyproject.toml``). When installed by ``uvx`` this lives at
# ``<site-packages>/meta_harness_knowledge_base/src/rag_tool.py``. When
# running from the in-tree source it lives at
# ``mcp_servers/knowledge_base/meta_harness_knowledge_base/src/rag_tool.py``.
# In both cases ``Path(__file__).parent.parent / "meta_harness_knowledge_base"``
# resolves correctly, and adding it to ``sys.path`` lets us do
# ``from src.rag_tool import ...``.
KB_TOOLS_PATH = Path(__file__).parent.parent / "meta_harness_knowledge_base"
sys.path.insert(0, str(KB_TOOLS_PATH))


# ---------------------------------------------------------------------------
# ChromaDB persistence directory resolution
# ---------------------------------------------------------------------------
# Path resolution is now fully relative - no environment variables needed.
# The ChromaDB directory is located at mcp_servers/knowledge_base/chroma_db
# relative to this file's location in the MCP server folder.
# This is handled entirely by rag_tool.get_chroma_client()

@dataclass
class KBEntry:
    """Represents a knowledge base entry."""
    id: str
    type: str
    category: str
    title: str
    finding: str = ""
    solution: str = ""
    context: str = ""
    example: str = ""
    confidence: float = 0.5


@dataclass
class KBSearchResult:
    """Result of a KB search operation."""
    success: bool
    entries: List[KBEntry]
    message: str
    error: Optional[str] = None


@dataclass
class KBAskResult:
    """Result of a KB ask operation."""
    success: bool
    answer: str
    sources: List[str]
    confidence: float = 0.0
    error: Optional[str] = None


def kb_search(query: str, top_k: int = 5, category: Optional[str] = None) -> KBSearchResult:
    """
    Search knowledge base for relevant entries.
    
    Args:
        query: Search query string
        top_k: Number of results to return (default: 5)
        category: Optional category filter
    
    Returns:
        KBSearchResult with entries and metadata
    """
    try:
        from src.rag_tool import rag_search
        
        result = rag_search(query, top_k, category)
        
        if result.get("success"):
            entries = []
            for entry in result.get("results", []):
                entries.append(KBEntry(
                    id=entry.get("id", "unknown"),
                    type=entry.get("type", "unknown"),
                    category=entry.get("category", "general"),
                    title=entry.get("title", "No title"),
                    finding=entry.get("finding", ""),
                    solution=entry.get("solution", ""),
                    context=entry.get("context", ""),
                    example=entry.get("example", ""),
                    confidence=entry.get("confidence", 0.5),
                ))
            
            return KBSearchResult(
                success=True,
                entries=entries,
                message=result.get("message", f"Found {len(entries)} results"),
                error=None
            )
        else:
            return KBSearchResult(
                success=False,
                entries=[],
                message="Search failed",
                error=result.get("error", "Unknown error")
            )
    except Exception as e:
        return KBSearchResult(
            success=False,
            entries=[],
            message="Search failed",
            error=str(e)
        )


def kb_ask(question: str, top_k: int = 3) -> KBAskResult:
    """
    Ask a question and get RAG-augmented response.
    
    Args:
        question: Question to ask
        top_k: Number of context entries to retrieve
    
    Returns:
        KBAskResult with synthesized answer and sources
    """
    try:
        from src.rag_tool import rag_ask
        
        result = rag_ask(question, top_k)
        
        if result.get("success"):
            sources = []
            for ctx in result.get("retrieved_context", []):
                sources.append(f"[{ctx.get('id', '')}] {ctx.get('title', 'Unknown')}")
            
            # Calculate average confidence from context
            confidences = [ctx.get("confidence", 0.5) for ctx in result.get("retrieved_context", [])]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return KBAskResult(
                success=True,
                answer=result.get("augmented_prompt", "No answer generated"),
                sources=sources,
                confidence=avg_confidence,
                error=None
            )
        else:
            return KBAskResult(
                success=False,
                answer="",
                sources=[],
                confidence=0.0,
                error=result.get("error", "Unknown error")
            )
    except Exception as e:
        return KBAskResult(
            success=False,
            answer="",
            sources=[],
            confidence=0.0,
            error=str(e)
        )


def kb_add_entry(
    entry_type: str,
    category: str,
    title: str,
    finding: str,
    solution: str,
    context: str = "",
    confidence: float = 0.5,
    example: str = ""
) -> Dict[str, Any]:
    """
    Add new knowledge entry to the knowledge base.
    
    Args:
        entry_type: Type of entry (pattern, finding, decision, correction)
        category: Category (code, class, method, function, workflow, documentation, architecture)
        title: Entry title
        finding: Main finding/insight
        solution: Solution or recommendation
        context: Additional context (optional)
        confidence: Confidence score 0.0-1.0 (default: 0.5)
        example: Example code or text (optional)
    
    Returns:
        Dict with success status and message
    """
    try:
        from src.rag_tool import rag_add_entry
        
        result = rag_add_entry(
            entry_type, category, title, finding, solution,
            context, confidence, example
        )
        
        if result.get("success"):
            return {
                "success": True,
                "message": result.get("message", "Entry added successfully"),
                "entry_id": result.get("entry_id")
            }
        else:
            return {
                "success": False,
                "message": "Failed to add entry",
                "error": result.get("error", "Unknown error")
            }
    except Exception as e:
        return {
            "success": False,
            "message": "Failed to add entry",
            "error": str(e)
        }


def kb_stats() -> Dict[str, Any]:
    """
    Get knowledge base statistics.
    
    Returns:
        Dict with statistics about the knowledge base
    """
    try:
        from src.rag_tool import rag_stats
        
        result = rag_stats()
        
        if result.get("success"):
            return {
                "success": True,
                "total_entries": result.get("total_entries", 0),
                "by_type": result.get("by_type", {}),
                "by_category": result.get("by_category", {}),
                "confidence_distribution": result.get("confidence_distribution", {}),
                "pending_corrections": result.get("pending_corrections", 0),
                "message": f"Total entries: {result.get('total_entries', 0)}"
            }
        else:
            return {
                "success": False,
                "message": "Failed to get stats",
                "error": result.get("error", "Unknown error")
            }
    except Exception as e:
        return {
            "success": False,
            "message": "Failed to get stats",
            "error": str(e)
        }
