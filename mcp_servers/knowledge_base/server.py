#!/usr/bin/env python3
"""
MCP Knowledge Base Server with extended timeout support.

This server wraps the standard MCP server to support longer-running operations
like workspace population. It uses environment variables to configure timeouts.
"""

import asyncio
import os
import sys
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import Context

import anyio

from kb import (
    add_entry,
    ask,
    populate_workspace,
    reset,
    search,
    stats,
)
from kb.models import PopulateResult

# Timeout for long-running operations (default: 1800s = 30 minutes)
# The server sends progress notifications to keep the client connection alive
KB_TIMEOUT = int(os.environ.get("KB_MCP_TIMEOUT", "1800"))

mcp = FastMCP(
    "knowledge_base",
    instructions=f"Knowledge Base server with {KB_TIMEOUT}s timeout for long-running operations"
)


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
    result = search(query, top_k, category)

    if not result.success:
        return f"❌ Search failed: {result.error}"

    if not result.entries:
        return "No results found."

    lines: List[str] = []
    lines.append(f"📚 Search Results for: '{query}'")
    lines.append(f"Found {len(result.entries)} entries\n")

    for i, entry in enumerate(result.entries, 1):
        lines.append("=" * 60)
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
    result = ask(question, top_k)

    if not result.success:
        return f"❌ Query failed: {result.error}"

    lines: List[str] = []
    lines.append(
        f"✓ Answer synthesized from {len(result.sources)} sources "
        f"(Confidence: {result.confidence:.2f})\n"
    )
    lines.append(result.answer)

    if result.sources:
        lines.append("\n📖 Sources:")
        for src in result.sources:
            lines.append(f"  • [{src.id}] {src.title} (Conf: {src.confidence:.2f})")

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
    valid_types = ["pattern", "finding", "decision", "correction"]
    if entry_type not in valid_types:
        return f"❌ Invalid entry_type '{entry_type}'. Must be one of: {', '.join(valid_types)}"

    if not (0.0 <= confidence <= 1.0):
        return "❌ Confidence must be between 0.0 and 1.0"

    result = add_entry(
        entry_type, category, title, finding, solution,
        context, confidence, example,
    )

    if result.success:
        return f"✅ Entry added successfully!\n\nID: {result.entry_id or 'N/A'}\nTitle: {title}"
    return f"❌ Failed to add entry: {result.error or 'Unknown error'}"


@mcp.tool()
def kb_stats_tool() -> str:
    """
    Get statistics about the knowledge base.

    Returns:
        Formatted statistics including entry counts by type and category
    """
    result = stats()

    if not result.success:
        return f"❌ Failed to get stats: {result.error or 'Unknown error'}"

    lines: List[str] = []
    lines.append("📊 Knowledge Base Statistics\n")
    lines.append(f"Total Entries: {result.total_entries}")

    lines.append("\n📁 By Type:")
    for type_name, count in result.by_type.items():
        lines.append(f"  • {type_name}: {count}")

    lines.append("\n📂 By Category:")
    for cat, count in result.by_category.items():
        lines.append(f"  • {cat}: {count}")

    cd = result.confidence_distribution
    lines.append("\n📈 Confidence Distribution:")
    lines.append(f"  • High (≥0.9): {cd.get('high', 0)}")
    lines.append(f"  • Medium (0.6-0.9): {cd.get('medium', 0)}")
    lines.append(f"  • Low (<0.6): {cd.get('low', 0)}")

    return "\n".join(lines)


@mcp.tool()
def kb_reset_tool() -> str:
    """
    Reset the knowledge base. Deletes ALL entries from ChromaDB.

    WARNING: This operation is destructive and cannot be undone.

    Returns:
        Confirmation message with reset status.
    """
    result = reset()

    if result.success:
        return (
            "✅ Knowledge base reset successfully.\n"
            f"All entries have been deleted. Total entries: {result.total_entries}"
        )
    return f"❌ Reset failed: {result.error or 'Unknown error'}"


@mcp.tool()
async def kb_populate_workspace_tool(
    ctx: Context,
    workspace_root: Optional[str] = None,
    include_python: bool = True,
    include_markdown: bool = True,
    exclude_dirs: Optional[List[str]] = None,
    reset_first: bool = True,
) -> str:
    """
    Populate the knowledge base by scanning the workspace.

    This tool scans the workspace for Python and Markdown files, extracts
    structural information (classes, methods, functions, documentation),
    and ingests them into the ChromaDB-backed knowledge base.

    ⚠️  NOTE: This is a long-running operation that may take 30-300 seconds
    depending on the size of your workspace. Progress notifications are sent
    periodically to keep the client informed.

    By default, the KB is RESET first (all existing entries are deleted)
    before population, ensuring a clean knowledge base.

    Args:
        workspace_root: Root directory to scan. If None, defaults to the repo root.
        include_python: Whether to ingest Python files (default: True).
        include_markdown: Whether to ingest Markdown files (default: True).
        exclude_dirs: Additional directory names to exclude from the scan.
        reset_first: If True, reset the KB before population (default: True).

    Returns:
        Formatted population report with counts and any errors.
    """
    from queue import Queue as ThreadQueue

    TOTAL_STEPS = 100
    await ctx.report_progress(0, TOTAL_STEPS, "Starting workspace scan...")

    # Thread-safe queue to receive progress updates from the worker thread
    progress_queue: "ThreadQueue[tuple[int, int, str]]" = ThreadQueue()

    # Sentinel to signal "done"
    _SENTINEL: tuple[int, int, str] = (-1, -1, "")

    def on_progress(current: int, total: int, message: str) -> None:
        """Called from populate_workspace (runs in a thread)."""
        pct = int((current / max(total, 1)) * TOTAL_STEPS) if total > 0 else 0
        try:
            progress_queue.put_nowait((pct, TOTAL_STEPS, message))
        except Exception:
            pass  # Queue full or closed — ignore

    # Run the synchronous populate_workspace in a thread pool
    async def run_populate() -> PopulateResult:
        try:
            return await anyio.to_thread.run_sync(
                lambda: populate_workspace(
                    workspace_root=workspace_root,
                    include_python=include_python,
                    include_markdown=include_markdown,
                    exclude_dirs=exclude_dirs,
                    reset_first=reset_first,
                    progress_callback=on_progress,
                ),
            )
        finally:
            # Signal the progress drainer that we're done
            try:
                progress_queue.put_nowait(_SENTINEL)
            except Exception:
                pass

    # Drain progress queue and report to client
    async def drain_progress() -> None:
        last_pct = -1
        while True:
            # Poll the thread-safe queue (non-blocking)
            try:
                pct, total_pct, msg = progress_queue.get_nowait()
            except Exception:
                # Queue empty — yield control briefly, then retry
                await anyio.sleep(0.5)
                continue

            if (pct, total_pct, msg) == _SENTINEL:
                progress_queue.task_done()
                break
            if pct != last_pct:
                last_pct = pct
                await ctx.report_progress(pct, total_pct, msg)
            progress_queue.task_done()

    # Run both concurrently
    async with anyio.create_task_group() as tg:
        tg.start_soon(drain_progress)
        p_result = await run_populate()

    await ctx.report_progress(TOTAL_STEPS, TOTAL_STEPS, "Population complete!")

    if not p_result.success:
        return f"❌ Population failed: {p_result.error or 'Unknown error'}"

    lines: List[str] = []
    lines.append("✅ Knowledge Base Population Complete\n")
    lines.append(f"Workspace root: {p_result.workspace_root}")
    lines.append(f"Reset performed: {p_result.reset_performed}")
    lines.append(f"Files processed: {p_result.files_processed}")
    lines.append(f"Total entries created: {p_result.total_entries}")

    lines.append("\n📁 Entries by file pattern:")
    for pattern, count in p_result.by_pattern.items():
        lines.append(f"  • {pattern}: {count}")

    lines.append("\n🚫 Excluded directories:")
    lines.append(f"  {', '.join(p_result.excluded_dirs)}")

    if p_result.error_count:
        lines.append(f"\n⚠️  Errors encountered: {p_result.error_count} (showing first 20):")
        for err in p_result.errors:
            lines.append(f"  • {err}")

    return "\n".join(lines)


@mcp.tool()
def kb_list_categories() -> str:
    """
    List all available categories and types in the knowledge base.

    Returns:
        Formatted list of valid categories and types
    """
    lines: List[str] = []
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


if __name__ == "__main__":
    main()