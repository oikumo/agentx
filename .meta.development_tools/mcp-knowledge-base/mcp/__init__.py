#!/usr/bin/env python3
"""
MCP RAG Tool - Exposes knowledge base functions for opencode.
No external dependencies, stdlib only.
"""

import sys
import json
from pathlib import Path

# Get absolute path to knowledge base
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent  # Points to agent-x root
KB_PATH = PROJECT_ROOT / '.meta.knowledge_base'

# Add to path
sys.path.insert(0, str(KB_PATH))

try:
    from core import (
        init_db, hybrid_search, add_entry, correct_entry, 
        run_evolution, get_stats
    )
    CORE_AVAILABLE = True
except Exception as e:
    CORE_AVAILABLE = False
    # Fallback stubs
    def init_db(): return None
    def hybrid_search(*args, **kwargs): return []
    def add_entry(*args, **kwargs): return {"success": False, "error": "Core not available"}
    def correct_entry(*args, **kwargs): return {"success": False, "error": "Core not available"}
    def run_evolution(): return {"success": False, "error": "Core not available"}
    def get_stats(): return {"success": False, "error": "Core not available"}


def rag_search(query: str, top_k: int = 5, category: str = None) -> dict:
    """Search knowledge base."""
    try:
        conn = init_db()
        results = hybrid_search(conn, query, category, top_k)
        if hasattr(conn, 'close'):
            conn.close()
        
        formatted = [{
            "id": e["id"], "type": e["type"], "category": e["category"],
            "title": e["title"], "confidence": e["confidence"],
            "context": e.get("context", ""), "finding": e.get("finding", ""),
            "solution": e.get("solution", ""), "example": e.get("example", "")
        } for e in results]
        
        return {
            "success": True, "query": query, "count": len(formatted),
            "results": formatted,
            "message": f"Found {len(formatted)} relevant entries" if formatted else "No results found"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "message": f"Search failed: {str(e)}"}


def rag_ask(question: str, top_k: int = 3) -> dict:
    """Ask question with RAG augmentation."""
    try:
        conn = init_db()
        results = hybrid_search(conn, question, None, top_k)
        if hasattr(conn, 'close'):
            conn.close()
        
        # Build augmented prompt
        prompt = """You are an AI agent working on the Agent-X project.
Use the following retrieved knowledge from the project's knowledge base to answer the question.

"""
        if results:
            prompt += "### Retrieved Knowledge:\n\n"
            for i, entry in enumerate(results, 1):
                prompt += f"[{i}] **{entry['title']}** (`{entry['id']}`)\n"
                prompt += f"    Type: {entry['type']} | Category: {entry['category']} | Confidence: {entry['confidence']:.2f}\n"
                if entry.get('finding'):
                    prompt += f"    Finding: {entry['finding']}\n"
                if entry.get('solution'):
                    prompt += f"    Solution: {entry['solution']}\n"
                if entry.get('example'):
                    prompt += f"    Example: {entry['example']}\n"
                prompt += "\n"
        else:
            prompt += "No relevant knowledge found. Answer based on general knowledge.\n\n"
        
        prompt += f"### Question:\n{question}\n\n### Your Answer:\n"
        
        formatted = [{
            "id": e["id"], "title": e["title"], "type": e["type"],
            "confidence": e["confidence"], "finding": e.get("finding", ""),
            "solution": e.get("solution", "")
        } for e in results]
        
        return {
            "success": True, "question": question,
            "augmented_prompt": prompt,
            "context_count": len(formatted),
            "retrieved_context": formatted,
            "message": f"Retrieved {len(formatted)} relevant entries. Use the augmented_prompt to answer."
        }
    except Exception as e:
        return {"success": False, "error": str(e), "message": f"RAG ask failed: {str(e)}"}


def rag_add_entry(entry_type: str, category: str, title: str, finding: str, 
                  solution: str, context: str = "", confidence: float = 0.5) -> dict:
    """Add new entry."""
    return add_entry(entry_type, category, title, finding, solution, context, "", confidence)


def rag_correct(entry_id: str, reason: str, new_finding: str) -> dict:
    """Add correction."""
    return correct_entry(entry_id, reason, new_finding)


def rag_evolve() -> dict:
    """Run evolution."""
    return run_evolution()


def rag_stats() -> dict:
    """Get statistics."""
    return get_stats()


__all__ = [
    'rag_search', 'rag_ask', 'rag_add_entry', 'rag_correct', 'rag_evolve', 'rag_stats'
]
