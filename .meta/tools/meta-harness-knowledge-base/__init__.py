#!/usr/bin/env python3
"""
Meta Harness Knowledge Base MCP Tool

This package provides MCP (Model Context Protocol) tools for opencode to interact
with the Meta Project Harness Knowledge Base using RAG (Retrieval-Augmented Generation).

Available Tools:
- kb_search(query, top_k=5, category=None) - Search KB
- kb_ask(question, top_k=3) - Ask question with RAG
- kb_add_entry(type, category, title, finding, solution, context, confidence) - Add entry
- kb_correct(entry_id, reason, new_finding) - Correct entry
- kb_evolve() - Run evolution cycle
- kb_stats() - Get statistics

Usage:
    from meta_harness_knowledge_base import rag_search, rag_ask, rag_add_entry
    
    # Search
    result = rag_search("TDD workflow", top_k=3)
    
    # Ask
    result = rag_ask("Where should I write tests?")
    
    # Add entry
    result = rag_add_entry(
        entry_type="pattern",
        category="workflow",
        title="My Pattern",
        finding="What I found",
        solution="How to handle"
    )

Or via MCP server:
    echo '{"tool": "kb_stats"}' | python3 -m meta_harness_knowledge-base
"""

