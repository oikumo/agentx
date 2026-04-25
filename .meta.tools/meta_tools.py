#!/usr/bin/env python3
"""
Meta Tools Facade - Agent-X Knowledge Base Tools

This module provides a unified interface to access Meta Project Harness tools,
including the Knowledge Base RAG system.

Usage:
    from meta_tools import kb_ask, kb_search, kb_add_entry, kb_stats
"""

import sys
from pathlib import Path

# Add knowledge base to path
KB_PATH = Path(__file__).parent / "meta-harness-knowledge-base"
sys.path.insert(0, str(KB_PATH))

from knowledge_base import kb_ask as _kb_ask
from knowledge_base import kb_search as _kb_search
from knowledge_base import kb_add_entry as _kb_add_entry
from knowledge_base import kb_correct as _kb_correct
from knowledge_base import kb_evolve as _kb_evolve
from knowledge_base import kb_stats as _kb_stats


def kb_ask(question: str, top_k: int = 3) -> str:
    """Ask a question and get RAG-augmented response.
    
    Args:
        question: Question to ask the knowledge base
        top_k: Number of context entries to retrieve (default: 3)
    
    Returns:
        RAG-augmented prompt with retrieved knowledge
    """
    return _kb_ask(question, top_k)


def kb_search(query: str, top_k: int = 5, category: str = None) -> str:
    """Search knowledge base for relevant entries.
    
    Args:
        query: Search query
        top_k: Number of results (default: 5)
        category: Optional category filter
    
    Returns:
        Formatted search results
    """
    return _kb_search(query, top_k, category)


def kb_add_entry(
    entry_type: str,
    category: str,
    title: str,
    finding: str,
    solution: str,
    context: str = "",
    confidence: float = 0.5,
    example: str = ""
) -> str:
    """Add new knowledge entry to the knowledge base.
    
    Args:
        entry_type: Type of entry (pattern, finding, correction, decision)
        category: Category (workflow, code, test, docs, tool, architecture)
        title: Concise title
        finding: What was discovered
        solution: How to solve it
        context: When/where this applies
        confidence: Confidence score (0.0-1.0)
        example: Optional example
    
    Returns:
        Confirmation message
    """
    return _kb_add_entry(entry_type, category, title, finding, solution, context, confidence, example)


def kb_correct(entry_id: str, reason: str, new_finding: str) -> str:
    """Add correction to existing entry.
    
    Args:
        entry_id: ID of entry to correct
        reason: Why correction is needed
        new_finding: Updated information
    
    Returns:
        Confirmation message
    """
    return _kb_correct(entry_id, reason, new_finding)


def kb_evolve() -> str:
    """Run evolution cycle: decay unused entries, archive low confidence.
    
    Returns:
        Evolution results message
    """
    return _kb_evolve()


def kb_stats() -> str:
    """Get knowledge base statistics.
    
    Returns:
        Formatted statistics
    """
    return _kb_stats()


# Export all functions
__all__ = [
    "kb_ask",
    "kb_search", 
    "kb_add_entry",
    "kb_correct",
    "kb_evolve",
    "kb_stats",
]


# Test if run directly
if __name__ == "__main__":
    print("=== Meta Tools Test ===\n")
    
    print("1. KB Stats:")
    print(kb_stats())
    
    print("\n2. KB Search 'TDD':")
    print(kb_search("TDD", top_k=3))
    
    print("\n3. KB Ask 'Where should I write tests?':")
    print(kb_ask("Where should I write tests?"))
