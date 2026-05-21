"""
Knowledge Base Module for MCP Server

This module provides a clean API for the Meta Harness Knowledge Base,
adapted for use with MCP tools.
"""

from .core import (
    kb_search,
    kb_ask,
    kb_add_entry,
    kb_stats,
    KBEntry,
    KBSearchResult,
    KBAskResult,
)

__all__ = [
    "kb_search",
    "kb_ask",
    "kb_add_entry",
    "kb_stats",
    "KBEntry",
    "KBSearchResult",
    "KBAskResult",
]
