"""
Meta Tools - Agent-X Development Tools

This module provides access to Meta Project Harness tools including:
- Knowledge Base RAG system (kb_ask, kb_search, kb_add_entry, etc.)
"""

from meta_tools import (
    kb_ask,
    kb_search,
    kb_add_entry,
    kb_correct,
    kb_evolve,
    kb_stats,
)

__all__ = [
    "kb_ask",
    "kb_search",
    "kb_add_entry",
    "kb_correct",
    "kb_evolve",
    "kb_stats",
]

__version__ = "1.0.0"
