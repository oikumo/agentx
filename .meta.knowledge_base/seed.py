#!/usr/bin/env python3
"""
Seed the knowledge base with initial entries for Agent-X.
Run once after setup.
"""

import subprocess
import sys
from pathlib import Path

KB_TOOL = Path(__file__).parent / "kb.py"

def seed_knowledge():
    """Add initial knowledge entries."""
    
    entries = [
        # Workflow patterns
        {
            "type": "pattern",
            "category": "workflow",
            "title": "TDD in .meta.tests_sandbox",
            "finding": "Tests must be written before code in .meta.tests_sandbox/ following Kent Beck methodology",
            "solution": "1. Write failing test in .meta.tests_sandbox/ 2. Implement minimum code in .meta.sandbox/ 3. Run tests 4. Refactor",
            "context": "When implementing new features or fixing bugs in Agent-X",
            "confidence": "0.98"
        },
        {
            "type": "pattern",
            "category": "workflow",
            "title": "Never modify production code directly",
            "finding": "Production code must never be modified without going through safe spaces",
            "solution": "Always work in .meta.sandbox/ for code changes, .meta.tests_sandbox/ for tests, .meta.experiments/ for prototypes",
            "context": "Core directive from AGENTS.md",
            "confidence": "1.0"
        },
        {
            "type": "pattern",
            "category": "workflow",
            "title": "Check git log before any changes",
            "finding": "Must understand recent changes before making modifications",
            "solution": "Run 'git log --oneline -10' before starting any task",
            "context": "Core directive #4 from AGENTS.md",
            "confidence": "1.0"
        },
        
        # Tool findings
        {
            "type": "finding",
            "category": "tool",
            "title": "Use uv for dependency management",
            "finding": "uv is faster and more reliable than pip, and is the project standard",
            "solution": "Always use 'uv add package' instead of 'pip install' or 'pip'",
            "context": "When adding Python packages to Agent-X",
            "example": "uv add requests --dev",
            "confidence": "0.95"
        },
        {
            "type": "finding",
            "category": "tool",
            "title": "SQLite FTS5 for full-text search",
            "finding": "SQLite FTS5 provides fast, built-in full-text search without external dependencies",
            "solution": "Use FTS5 virtual tables for keyword search, combine with BM25 scoring",
            "context": "When implementing search functionality",
            "confidence": "0.90"
        },
        
        # Code patterns
        {
            "type": "pattern",
            "category": "code",
            "title": "Standalone tools with no dependencies",
            "finding": "Tools should work without external dependencies when possible",
            "solution": "Use stdlib only, make optional dependencies truly optional, provide fallbacks",
            "context": "When creating development tools",
            "confidence": "0.85"
        },
        {
            "type": "pattern",
            "category": "code",
            "title": "LLM-optimized output",
            "finding": "Output should be concise, structured for LLM consumption",
            "solution": "Use clear structure, minimal tokens, no unnecessary preamble",
            "context": "When writing documentation or tool output",
            "confidence": "0.90"
        },
        
        # Architecture decisions
        {
            "type": "decision",
            "category": "architecture",
            "title": "Meta Project Harness structure",
            "finding": "Safe spaces (.meta.*) separate production from development work",
            "solution": "Work in .meta.sandbox/, .meta.experiments/, or .meta.tests_sandbox/ based on task type",
            "context": "All development work on Agent-X",
            "confidence": "1.0"
        },
        {
            "type": "decision",
            "category": "architecture",
            "title": "Self-evolving knowledge base",
            "finding": "Knowledge must evolve through corrections and decay, not manual updates",
            "solution": "Use confidence scores, auto-correction mechanism, and periodic evolution cycles",
            "context": "Knowledge base maintenance",
            "confidence": "0.95"
        },
        
        # Documentation
        {
            "type": "pattern",
            "category": "docs",
            "title": "META.md first policy",
            "finding": "Always read META.md files before working in a directory",
            "solution": "Check directory META.md for rules and guidelines",
            "context": "Starting work in any .meta.* directory",
            "confidence": "0.98"
        },
    ]
    
    print("📦 Seeding knowledge base with initial entries...\n")
    
    for i, entry in enumerate(entries, 1):
        cmd = f'{KB_TOOL} add'
        cmd += f' --type {entry["type"]}'
        cmd += f' --category {entry["category"]}'
        cmd += f' --title "{entry["title"]}"'
        cmd += f' --finding "{entry["finding"]}"'
        cmd += f' --solution "{entry["solution"]}"'
        cmd += f' --context "{entry["context"]}"'
        if "example" in entry:
            cmd += f' --example "{entry["example"]}"'
        cmd += f' --confidence {entry["confidence"]}'
        
        print(f"{i}/{len(entries)}: Adding {entry['title'][:50]}...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ✗ Error: {result.stderr}")
        else:
            print(f"  ✓ Added")
    
    print("\n✓ Seeding complete!")
    print("\nRun 'python kb.py stats' to see all entries.")


if __name__ == '__main__':
    seed_knowledge()
