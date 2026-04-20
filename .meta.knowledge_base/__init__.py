#!/usr/bin/env python3
"""
Meta Project Harness Knowledge Base
Self-evolving knowledge storage with RAG support.
"""

from core import (
    init_db, hybrid_search, add_entry, correct_entry,
    run_evolution, get_stats
)

__version__ = "1.0.0"
__all__ = [
    'init_db', 'hybrid_search', 'add_entry', 'correct_entry',
    'run_evolution', 'get_stats'
]
