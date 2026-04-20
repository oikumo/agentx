#!/usr/bin/env python3
"""
MCP Server: Knowledge Base RAG Server for opencode

This MCP server provides tools for opencode to interact with the
Meta Project Harness Knowledge Base using RAG.

Tools:
- kb_search(query, top_k=5, category=None) - Search KB
- kb_ask(question, top_k=3) - Ask question with RAG
- kb_add_entry(type, category, title, finding, solution, context, confidence) - Add entry
- kb_correct(entry_id, reason, new_finding) - Correct entry
- kb_evolve() - Run evolution cycle
- kb_stats() - Get statistics
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("meta-harness-knowledge-base")


@mcp.tool()
def kb_search(query: str, top_k: int = 5, category: str = None) -> str:
    """Search knowledge base for relevant entries.
    
    Args:
        query: Search query
        top_k: Number of results (default: 5)
        category: Optional category filter
    """
    from rag_tool import rag_search
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


@mcp.tool()
def kb_ask(question: str, top_k: int = 3) -> str:
    """Ask a question and get RAG-augmented response.
    
    Args:
        question: Question to ask
        top_k: Number of context entries (default: 3)
    """
    from rag_tool import rag_ask
    result = rag_ask(question, top_k)
    
    if result.get("success"):
        return result["augmented_prompt"]
    else:
        return f"Error: {result.get('error', 'Unknown error')}"


@mcp.tool()
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
    from rag_tool import rag_add_entry
    result = rag_add_entry(entry_type, category, title, finding, solution, context, confidence, example)
    
    if result.get("success"):
        return result["message"]
    else:
        return f"Error: {result.get('error', 'Unknown error')}"


@mcp.tool()
def kb_correct(entry_id: str, reason: str, new_finding: str) -> str:
    """Add correction to existing entry.
    
    Args:
        entry_id: ID of entry to correct
        reason: Why correction is needed
        new_finding: Updated information
    """
    from rag_tool import rag_correct
    result = rag_correct(entry_id, reason, new_finding)
    
    if result.get("success"):
        return result["message"]
    else:
        return f"Error: {result.get('error', 'Unknown error')}"


@mcp.tool()
def kb_evolve() -> str:
    """Run evolution cycle: decay unused entries, archive low confidence."""
    from rag_tool import rag_evolve
    result = rag_evolve()
    
    if result.get("success"):
        return result["message"]
    else:
        return f"Error: {result.get('error', 'Unknown error')}"


@mcp.tool()
def kb_stats() -> str:
    """Get knowledge base statistics."""
    from rag_tool import rag_stats
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


if __name__ == "__main__":
    mcp.run()
