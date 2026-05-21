#!/usr/bin/env python3
"""
MCP Knowledge Base Server

This MCP server provides tools to query and manage the Meta Project Harness
Knowledge Base using RAG (Retrieval-Augmented Generation) with ChromaDB.
"""

from mcp.server.fastmcp import FastMCP
from typing import List, Optional
from kb_module import kb_search, kb_ask, kb_add_entry, kb_stats

mcp = FastMCP("knowledge_base")


# =============================================================================
# Query Tools
# =============================================================================

@mcp.tool()
def kb_search_tool(query: str, top_k: int = 5, category: Optional[str] = None) -> str:
    """
    Search the knowledge base for relevant entries.
    
    Args:
        query: Search query string
        top_k: Maximum number of results to return (default: 5)
        category: Optional category filter (code, class, method, function, workflow, documentation, architecture)
    
    Returns:
        Formatted search results with entries and metadata
    """
    result = kb_search(query, top_k, category)
    
    if not result.success:
        return f"❌ Search failed: {result.error}"
    
    if not result.entries:
        return "No results found."
    
    lines = []
    lines.append(f"📚 Search Results for: '{query}'")
    lines.append(f"Found {len(result.entries)} entries\n")
    
    for i, entry in enumerate(result.entries, 1):
        lines.append(f"{'='*60}")
        lines.append(f"{i}. **{entry.title}** ({entry.id})")
        lines.append(f"   Type: {entry.type} | Category: {entry.category}")
        lines.append(f"   Confidence: {entry.confidence:.2f}")
        
        if entry.finding:
            lines.append(f"   Finding: {entry.finding}")
        if entry.solution:
            lines.append(f"   Solution: {entry.solution}")
        if entry.example:
            lines.append(f"   Example: {entry.example}")
        lines.append("")
    
    return "\n".join(lines)


@mcp.tool()
def kb_ask_tool(question: str, top_k: int = 3) -> str:
    """
    Ask a question and get a synthesized answer from the knowledge base.
    
    This tool uses RAG (Retrieval-Augmented Generation) to retrieve relevant
    context from the knowledge base and synthesize an answer.
    
    Args:
        question: The question to ask
        top_k: Number of context entries to retrieve (default: 3)
    
    Returns:
        Synthesized answer with citations
    """
    result = kb_ask(question, top_k)
    
    if not result.success:
        return f"❌ Query failed: {result.error}"
    
    lines = []
    lines.append(f"💡 Answer (Confidence: {result.confidence:.2f})\n")
    lines.append(result.answer)
    
    if result.sources:
        lines.append("\n📖 Sources:")
        for source in result.sources:
            lines.append(f"  • {source}")
    
    return "\n".join(lines)


# =============================================================================
# Management Tools
# =============================================================================

@mcp.tool()
def kb_add_tool(
    entry_type: str,
    category: str,
    title: str,
    finding: str,
    solution: str,
    context: str = "",
    confidence: float = 0.5,
    example: str = ""
) -> str:
    """
    Add a new entry to the knowledge base.
    
    Args:
        entry_type: Type of entry (pattern, finding, decision, correction)
        category: Category (code, class, method, function, workflow, documentation, architecture)
        title: Entry title
        finding: Main finding or insight
        solution: Solution or recommendation
        context: Additional context (optional)
        confidence: Confidence score 0.0-1.0 (default: 0.5)
        example: Example code or text (optional)
    
    Returns:
        Confirmation message with entry ID
    """
    # Validate entry_type
    valid_types = ["pattern", "finding", "decision", "correction"]
    if entry_type not in valid_types:
        return f"❌ Invalid entry_type '{entry_type}'. Must be one of: {', '.join(valid_types)}"
    
    # Validate confidence
    if not (0.0 <= confidence <= 1.0):
        return "❌ Confidence must be between 0.0 and 1.0"
    
    result = kb_add_entry(
        entry_type, category, title, finding, solution,
        context, confidence, example
    )
    
    if result["success"]:
        return f"✅ Entry added successfully!\n\nID: {result.get('entry_id', 'N/A')}\nTitle: {title}"
    else:
        return f"❌ Failed to add entry: {result.get('error', 'Unknown error')}"


@mcp.tool()
def kb_stats_tool() -> str:
    """
    Get statistics about the knowledge base.
    
    Returns:
        Formatted statistics including entry counts by type and category
    """
    result = kb_stats()
    
    if not result["success"]:
        return f"❌ Failed to get stats: {result.get('error', 'Unknown error')}"
    
    lines = []
    lines.append("📊 Knowledge Base Statistics\n")
    lines.append(f"Total Entries: {result['total_entries']}")
    
    lines.append("\n📁 By Type:")
    for type_name, data in result.get("by_type", {}).items():
        count = data.get("count", 0) if isinstance(data, dict) else data
        lines.append(f"  • {type_name}: {count}")
    
    lines.append("\n📂 By Category:")
    for cat, count in result.get("by_category", {}).items():
        lines.append(f"  • {cat}: {count}")
    
    conf_dist = result.get("confidence_distribution", {})
    lines.append("\n📈 Confidence Distribution:")
    lines.append(f"  • High (≥0.9): {conf_dist.get('high', 0)}")
    lines.append(f"  • Medium (0.6-0.9): {conf_dist.get('medium', 0)}")
    lines.append(f"  • Low (<0.6): {conf_dist.get('low', 0)}")
    
    return "\n".join(lines)


@mcp.tool()
def kb_list_categories() -> str:
    """
    List all available categories and types in the knowledge base.
    
    Returns:
        Formatted list of valid categories and types
    """
    lines = []
    lines.append("📚 Knowledge Base Categories & Types\n")
    
    lines.append("Valid Entry Types:")
    lines.append("  • pattern - Reusable patterns or best practices")
    lines.append("  • finding - Discoveries or insights")
    lines.append("  • decision - Architectural or design decisions")
    lines.append("  • correction - Corrections to existing entries")
    
    lines.append("\nValid Categories:")
    lines.append("  • code - Code-related knowledge")
    lines.append("  • class - Class-level knowledge")
    lines.append("  • method - Method-level knowledge")
    lines.append("  • function - Function-level knowledge")
    lines.append("  • workflow - Workflows and processes")
    lines.append("  • documentation - Documentation guidelines")
    lines.append("  • architecture - Architectural patterns")
    
    return "\n".join(lines)


# =============================================================================
# Entry Point
# =============================================================================

def main() -> None:
    """Run the MCP server."""
    mcp.run(transport="stdio")
    # Alternative: mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
