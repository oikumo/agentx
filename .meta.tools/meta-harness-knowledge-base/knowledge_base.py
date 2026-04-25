#!/usr/bin/env python3
import sys
from pathlib import Path

# Path to knowledge base (go up from .meta.development_tools/mcp/meta-harness-knowledge-base to project root)
KB_PATH = Path(__file__).parent.parent.parent / ".meta.data"
DB_PATH = KB_PATH / "kb-meta" / "knowledge-meta.db"

# Add KB to path for imports
sys.path.insert(0, str(KB_PATH))


def kb_search(query: str, top_k: int = 5, category: str = None) -> str:
    """Search knowledge base for relevant entries.
    
    Args:
        query: Search query
        top_k: Number of results (default: 5)
        category: Optional category filter
    """
    from src.rag_tool import rag_search
    result = rag_search(query, top_k, category)
    
    if result.get("success"):
        if result["count"] == 0:
            return "No results found"
        
        formatted = []
        for entry in result["results"]:
            formatted.append(
                f"ID: {entry['id']}\n"
                f"Type: {entry['type']} | Category: {entry['category']} | Confidence: {entry['confidence']:.2f}\n"
                f"Title: {entry['title']}\n"
                f"Finding: {entry.get('finding', 'N/A')}\n"
                f"Solution: {entry.get('solution', 'N/A')}\n"
            )
        return "\n\n".join(formatted)
    else:
        return f"Error: {result.get('error', 'Unknown error')}"


def kb_ask(question: str, top_k: int = 3) -> str:
    """Ask a question and get RAG-augmented response.
    
    Args:
        question: Question to ask
        top_k: Number of context entries (default: 3)
    """
    from src.rag_tool import rag_ask
    result = rag_ask(question, top_k)
    
    if result.get("success"):
        return result["augmented_prompt"]
    else:
        return f"Error: {result.get('error', 'Unknown error')}"


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
    """
    from src.rag_tool import rag_add_entry
    result = rag_add_entry(entry_type, category, title, finding, solution, context, confidence, example)
    
    if result.get("success"):
        return result["message"]
    else:
        return f"Error: {result.get('error', 'Unknown error')}"


def kb_correct(entry_id: str, reason: str, new_finding: str) -> str:
    """Add correction to existing entry.
    
    Args:
        entry_id: ID of entry to correct
        reason: Why correction is needed
        new_finding: Updated information
    """
    from src.rag_tool import rag_correct
    result = rag_correct(entry_id, reason, new_finding)
    
    if result.get("success"):
        return result["message"]
    else:
        return f"Error: {result.get('error', 'Unknown error')}"


def kb_evolve() -> str:
    """Run evolution cycle: decay unused entries, archive low confidence."""
    from src.rag_tool import rag_evolve
    result = rag_evolve()
    
    if result.get("success"):
        return result["message"]
    else:
        return f"Error: {result.get('error', 'Unknown error')}"


def kb_stats() -> str:
    """Get knowledge base statistics."""
    from src.rag_tool import rag_stats
    result = rag_stats()
    
    if result.get("success"):
        lines = [f"Total entries: {result['total_entries']}"]
        lines.append("\nBy type:")
        for type_name, data in result["by_type"].items():
            lines.append(f"  {type_name}: {data['count']} (avg confidence: {data['avg_confidence']:.2f})")
        
        lines.append("\nBy category:")
        for cat, count in result["by_category"].items():
            lines.append(f"  {cat}: {count}")
        
        lines.append(f"\nConfidence distribution:")
        lines.append(f"  High (>=0.9): {result['confidence_distribution']['high']}")
        lines.append(f"  Medium (0.6-0.9): {result['confidence_distribution']['medium']}")
        lines.append(f"  Low (<0.6): {result['confidence_distribution']['low']}")
        
        lines.append(f"\nPending corrections: {result['pending_corrections']}")
        
        return "\n".join(lines)
    else:
        return f"Error: {result.get('error', 'Unknown error')}"

