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

# v4 imports
from analyzer import PythonASTAnalyzer
from graph import KnowledgeGraph, GraphBuilder, GraphStore, GraphQueries
from graph.models import Entity, Relationship, ImpactResult, EntityKind, RelationshipKind
from resources import (
    ResourceRegistry,
    ProjectResources,
    ArchitectureResources,
    FlowResources,
    APIResources,
    CodeResources,
    SessionResources,
    QualityResources,
)
from prompts import PromptEngine, PromptRegistry
from pathlib import Path

# Timeout for long-running operations (default: 1800s = 30 minutes)
KB_TIMEOUT = int(os.environ.get("KB_MCP_TIMEOUT", "1800"))

# Initialize MCP server
mcp = FastMCP(
    "knowledge_base",
    instructions=f"Knowledge Base v4 server with {KB_TIMEOUT}s timeout. Provides semantic code understanding via knowledge graph."
)

# =============================================================================
# V4 Component Initialization
# =============================================================================

_analyzer: Optional[PythonASTAnalyzer] = None
_graph: Optional[KnowledgeGraph] = None
_graph_store: Optional[GraphStore] = None
_resource_registry: Optional[ResourceRegistry] = None
_prompt_engine: Optional[PromptEngine] = None
_project_resources: Optional[ProjectResources] = None
_arch_resources: Optional[ArchitectureResources] = None
_flow_resources: Optional[FlowResources] = None
_api_resources: Optional[APIResources] = None
_code_resources: Optional[CodeResources] = None
_session_resources: Optional[SessionResources] = None
_quality_resources: Optional[QualityResources] = None


def get_v4_components():
    """Get or initialize v4 components."""
    global _analyzer, _graph, _graph_store, _resource_registry, _prompt_engine
    global _project_resources, _arch_resources, _flow_resources
    global _api_resources, _code_resources, _session_resources, _quality_resources
    
    if _analyzer is None:
        _analyzer = PythonASTAnalyzer()
    
    if _graph is None:
        _graph = KnowledgeGraph()
        _graph_store = GraphStore()
        try:
            _graph_store.load_into(_graph)
        except Exception:
            pass
    
    if _resource_registry is None:
        _resource_registry = ResourceRegistry()
        _project_resources = ProjectResources(_graph)
        _arch_resources = ArchitectureResources(_graph)
        _flow_resources = FlowResources(_graph)
        _api_resources = APIResources(_graph)
        _code_resources = CodeResources(_graph)
        _session_resources = SessionResources()
        _quality_resources = QualityResources(_graph)
    
    if _prompt_engine is None:
        _prompt_engine = PromptEngine()
    
    return {
        'analyzer': _analyzer,
        'graph': _graph,
        'graph_store': _graph_store,
        'resource_registry': _resource_registry,
        'prompt_engine': _prompt_engine,
        'project_resources': _project_resources,
        'arch_resources': _arch_resources,
        'flow_resources': _flow_resources,
        'api_resources': _api_resources,
        'code_resources': _code_resources,
        'session_resources': _session_resources,
        'quality_resources': _quality_resources,
    }


# =============================================================================
# Query Tools
# =============================================================================

@mcp.tool()
def kb_search_tool(
    query: str,
    top_k: int = 5,
    category: Optional[str] = None,
    search_mode: str = "hybrid",
    embedding_model: str = "bge-small-en",
    rerank: bool = True,
    reranker_model: str = "ms-marco-MiniLM-L6-v2",
    query_mode: str = "direct",
) -> str:
    """
    Search the knowledge base for relevant entries.

    Args:
        query: Search query string
        top_k: Maximum number of results to return (default: 5)
        category: Optional category filter (code, class, method, function, workflow, documentation, architecture)
        search_mode: "hybrid" (dense+sparse+RRF), "dense", or "sparse" (default: "hybrid")
        embedding_model: Embedding model for dense retrieval (default: "bge-small-en")
        rerank: Whether to apply cross-encoder reranking (default: True)
        reranker_model: Cross-encoder model name (default: "ms-marco-MiniLM-L6-v2")
        query_mode: Query preprocessing mode: "direct", "rewrite", "hyde", "multi_query", "decompose" (default: "direct")

    Returns:
        Formatted search results with entries and metadata
    """
    result = search(
        query, top_k, category,
        search_mode=search_mode,
        embedding_model=embedding_model,
        rerank=rerank,
        reranker_model=reranker_model,
        query_mode=query_mode,
    )

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
def kb_ask_tool(
    question: str,
    top_k: int = 3,
    search_mode: str = "hybrid",
    embedding_model: str = "bge-small-en",
    rerank: bool = True,
    reranker_model: str = "ms-marco-MiniLM-L6-v2",
    query_mode: str = "direct",
    synthesis_mode: str = "template",
) -> str:
    """
    Ask a question and get a synthesized answer from the knowledge base.

    This tool uses RAG (Retrieval-Augmented Generation) to retrieve relevant
    context from the knowledge base and synthesize an answer.

    Args:
        question: The question to ask
        top_k: Number of context entries to retrieve (default: 3)
        search_mode: "hybrid" (dense+sparse+RRF), "dense", or "sparse" (default: "hybrid")
        embedding_model: Embedding model for dense retrieval (default: "bge-small-en")
        rerank: Whether to apply cross-encoder reranking (default: True)
        reranker_model: Cross-encoder model name (default: "ms-marco-MiniLM-L6-v2")
        query_mode: Query preprocessing mode: "direct", "rewrite", "hyde", "multi_query", "decompose" (default: "direct")
        synthesis_mode: "template" (default) or "llm" (requires LLM support)

    Returns:
        Synthesized answer with citations
    """
    result = ask(
        question, top_k,
        search_mode=search_mode,
        embedding_model=embedding_model,
        rerank=rerank,
        reranker_model=reranker_model,
        query_mode=query_mode,
        synthesis_mode=synthesis_mode,
    )

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
    lines.append(f"  • High   (≥0.9):   {cd.get('high', 0)}")
    lines.append(f"  • Medium (0.6-0.9): {cd.get('medium', 0)}")
    lines.append(f"  • Low    (<0.6):   {cd.get('low', 0)}")
    lines.append(f"  • Mean:   {result.mean_confidence:.4f}")
    lines.append(f"  • Median: {result.median_confidence:.4f}")

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
# V4 Graph Tools
# =============================================================================

@mcp.tool()
def kb_graph_tool(
    operation: str = "list",
    entity_id: Optional[str] = None,
    relationship_kind: Optional[str] = None,
    depth: int = 3,
    direction: str = "outgoing",
    format: str = "json",
) -> str:
    """Perform graph operations."""
    try:
        components = get_v4_components()
        graph = components['graph']
        queries = GraphQueries(graph)
        
        if operation == "list":
            entities = list(graph.entities.keys())[:100]
            return f"📊 Knowledge Graph: {len(entities)} entities\n\n" + "\n".join(entities[:20])
        elif operation == "traverse":
            if not entity_id:
                return "❌ entity_id required"
            result = queries.traverse(entity_id, direction, depth)
            return f"🔍 Traversal from {entity_id}:\n\n" + str(result)
        elif operation == "layers":
            layers = queries.get_layers()
            return "🏗️  Layers:\n\n" + "\n".join(f"{k}: {len(v)} entities" for k, v in layers.items())
        elif operation == "entry_points":
            eps = queries.find_entry_points()
            return f"🚪 Entry Points ({len(eps)}):\n\n" + "\n".join(eps[:20])
        else:
            return f"❌ Unknown operation: {operation}"
    except Exception as e:
        return f"❌ Graph operation failed: {e}"


@mcp.tool()
def kb_impact_tool(entity_id: str, change_type: str = "modify", depth: int = 3) -> str:
    """Analyze impact of changing an entity."""
    try:
        components = get_v4_components()
        graph = components['graph']
        result = graph.impact_analysis(entity_id, depth)
        
        lines: List[str] = []
        lines.append(f"🎯 Impact: {entity_id} ({change_type})\n")
        lines.append(f"Affected: {len(result.affected_entities)}")
        for eid in result.affected_entities[:20]:
            risk = result.risk_levels.get(eid, "unknown")
            icon = "🔴" if risk == "high" else "🟡" if risk == "medium" else "🟢"
            lines.append(f"  {icon} {eid}")
        if result.test_files:
            lines.append(f"\n🧪 Tests: {len(result.test_files)}")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Impact analysis failed: {e}"


@mcp.tool()
def kb_visualize_tool(view: str = "full", format: str = "mermaid", root: Optional[str] = None, depth: int = 2) -> str:
    """Generate visual diagram."""
    try:
        components = get_v4_components()
        graph = components['graph']
        if view == "full":
            if format == "mermaid": return graph.to_mermaid()
            elif format == "dot": return graph.to_dot()
            elif format == "ascii": return graph.to_ascii()
        elif view == "tree" and root:
            return graph.to_ascii(root_id=root, max_depth=depth)
        return f"❌ Unknown view: {view}"
    except Exception as e:
        return f"❌ Visualization failed: {e}"


@mcp.tool()
def kb_trace_flow_tool(source: str, target: str, max_depth: int = 5) -> str:
    """Trace flow between entities."""
    try:
        components = get_v4_components()
        graph = components['graph']
        path = graph.find_path(source, target)
        if not path: return f"❌ No path from {source} to {target}"
        lines = [f"🔀 Flow: {source} → {target}", f"Length: {len(path)}\n"]
        for i, eid in enumerate(path): lines.append(f"{i+1}. {eid}")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Flow tracing failed: {e}"


@mcp.tool()
def kb_code_location_tool(symbol: str, include_code: bool = False, context_lines: int = 3) -> str:
    """Find code location for symbol."""
    try:
        components = get_v4_components()
        graph = components['graph']
        matches = [eid for eid in graph.entities.keys() if symbol in eid]
        if not matches: return f"❌ Symbol '{symbol}' not found"
        lines = [f"📍 Found {len(matches)} match(es):\n"]
        for m in matches[:10]:
            e = graph.entities[m]
            lines.append(f"• {e.name} @ {e.file_path}:{e.line_start}")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Lookup failed: {e}"


@mcp.tool()
def kb_find_pattern_tool(pattern: str, language: str = "python") -> str:
    """Find design patterns."""
    try:
        components = get_v4_components()
        graph = components['graph']
        matches = [(eid, e) for eid, e in graph.entities.items() if pattern.lower() in [p.lower() for p in e.metadata.get('pattern', [])]]
        if not matches: return f"❌ Pattern '{pattern}' not found"
        lines = [f"🔍 Found {len(matches)} match(es):\n"]
        for eid, e in matches[:20]:
            lines.append(f"🟢 {e.name} @ {e.file_path}:{e.line_start}")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Pattern search failed: {e}"


@mcp.tool()
def kb_session_tool(action: str = "get", key: Optional[str] = None, value: Optional[str] = None) -> str:
    """Manage session context."""
    try:
        components = get_v4_components()
        session = components['session_resources']
        if action == "get":
            return f"📝 {key}={session.context.get(key)}" if key else "📝 " + ", ".join(f"{k}={v}" for k,v in session.context.items())
        elif action == "set":
            session.context[key] = value
            return f"✅ {key}={value}"
        elif action == "clear":
            session.context.clear()
            return "✅ Cleared"
        return f"❌ Unknown action: {action}"
    except Exception as e:
        return f"❌ Session failed: {e}"


# =============================================================================
# V4 MCP Resources (15 resources)
# =============================================================================

@mcp.resource("knowledge-base://project/tree")
def get_project_tree() -> str:
    """Project tree."""
    try:
        components = get_v4_components()
        return components['project_resources'].get_project_tree()
    except Exception as e:
        return f"❌ {e}"

@mcp.resource("knowledge-base://project/summary")
def get_project_summary() -> str:
    """Project summary."""
    try:
        components = get_v4_components()
        return components['project_resources'].get_summary()
    except Exception as e:
        return f"❌ {e}"

@mcp.resource("knowledge-base://project/metadata")
def get_project_metadata() -> str:
    """Project metadata."""
    try:
        components = get_v4_components()
        return components['project_resources'].get_metadata()
    except Exception as e:
        return f"❌ {e}"

@mcp.resource("knowledge-base://arch/components")
def get_arch_components() -> str:
    """Components."""
    try:
        components = get_v4_components()
        return components['arch_resources'].get_components()
    except Exception as e:
        return f"❌ {e}"

@mcp.resource("knowledge-base://arch/dependencies?format={format}")
def get_arch_dependencies(format: str = "json") -> str:
    """Dependencies."""
    try:
        components = get_v4_components()
        return components['arch_resources'].get_dependencies(format)
    except Exception as e:
        return f"❌ {e}"

@mcp.resource("knowledge-base://arch/layers")
def get_arch_layers() -> str:
    """Layers."""
    try:
        components = get_v4_components()
        return components['arch_resources'].get_layers()
    except Exception as e:
        return f"❌ {e}"

@mcp.resource("knowledge-base://arch/patterns")
def get_arch_patterns() -> str:
    """Patterns."""
    try:
        components = get_v4_components()
        return components['arch_resources'].get_patterns()
    except Exception as e:
        return f"❌ {e}"

@mcp.resource("knowledge-base://flows/data")
def get_data_flow() -> str:
    """Data flow."""
    try:
        components = get_v4_components()
        return components['flow_resources'].get_data_flow()
    except Exception as e:
        return f"❌ {e}"

@mcp.resource("knowledge-base://flows/control")
def get_control_flow() -> str:
    """Control flow."""
    try:
        components = get_v4_components()
        return components['flow_resources'].get_control_flow()
    except Exception as e:
        return f"❌ {e}"

@mcp.resource("knowledge-base://flows/imports")
def get_import_flow() -> str:
    """Import flow."""
    try:
        components = get_v4_components()
        return components['flow_resources'].get_import_flow()
    except Exception as e:
        return f"❌ {e}"

@mcp.resource("knowledge-base://flows/events")
def get_event_channels() -> str:
    """Event channels."""
    try:
        components = get_v4_components()
        return components['flow_resources'].get_event_channels()
    except Exception as e:
        return f"❌ {e}"

@mcp.resource("knowledge-base://api/endpoints")
def get_api_endpoints() -> str:
    """Endpoints."""
    try:
        components = get_v4_components()
        return components['api_resources'].get_endpoints()
    except Exception as e:
        return f"❌ {e}"

@mcp.resource("knowledge-base://api/public")
def get_public_api() -> str:
    """Public API."""
    try:
        components = get_v4_components()
        return components['api_resources'].get_public_api()
    except Exception as e:
        return f"❌ {e}"

@mcp.resource("knowledge-base://code/search?query={query}")
def search_code(query: str = "") -> str:
    """Search code."""
    try:
        components = get_v4_components()
        return components['code_resources'].search(query) if query else components['code_resources'].list_all()
    except Exception as e:
        return f"❌ {e}"

@mcp.resource("knowledge-base://health")
def get_health() -> str:
    """Health metrics."""
    try:
        components = get_v4_components()
        g = components['graph']
        return f"💚 Entities: {len(g.entities)}\nRelationships: {g.graph.number_of_edges()}\nUpdated: {g.metadata.updated_at}"
    except Exception as e:
        return f"❌ {e}"


# =============================================================================
# V4 MCP Prompts (10 prompts)
# =============================================================================

@mcp.prompt("onboard-agent")
def onboard_agent() -> str:
    """Onboard agent."""
    try:
        components = get_v4_components()
        return components['prompt_engine'].render_prompt("onboard-agent", {})
    except Exception as e:
        return f"❌ {e}"

@mcp.prompt("find-entry-point")
def find_entry_point() -> str:
    """Find entry points."""
    try:
        components = get_v4_components()
        return components['prompt_engine'].render_prompt("find-entry-point", {})
    except Exception as e:
        return f"❌ {e}"

@mcp.prompt("plan-feature")
def plan_feature(feature_description: str) -> str:
    """Plan feature."""
    try:
        components = get_v4_components()
        return components['prompt_engine'].render_prompt("plan-feature", {"feature_description": feature_description})
    except Exception as e:
        return f"❌ {e}"

@mcp.prompt("trace-bug")
def trace_bug(symptom: str) -> str:
    """Trace bug."""
    try:
        components = get_v4_components()
        return components['prompt_engine'].render_prompt("trace-bug", {"symptom": symptom})
    except Exception as e:
        return f"❌ {e}"

@mcp.prompt("understand-flow")
def understand_flow(source: str, target: str) -> str:
    """Understand flow."""
    try:
        components = get_v4_components()
        return components['prompt_engine'].render_prompt("understand-flow", {"source": source, "target": target})
    except Exception as e:
        return f"❌ {e}"

@mcp.prompt("review-change")
def review_change(planned_changes: str = "") -> str:
    """Review change."""
    try:
        components = get_v4_components()
        return components['prompt_engine'].render_prompt("review-change", {"planned_changes": planned_changes})
    except Exception as e:
        return f"❌ {e}"

@mcp.prompt("find-similar")
def find_similar(code_pattern: str) -> str:
    """Find similar."""
    try:
        components = get_v4_components()
        return components['prompt_engine'].render_prompt("find-similar", {"code_pattern": code_pattern})
    except Exception as e:
        return f"❌ {e}"

@mcp.prompt("write-test")
def write_test(module_path: str) -> str:
    """Write test."""
    try:
        components = get_v4_components()
        return components['prompt_engine'].render_prompt("write-test", {"module_path": module_path})
    except Exception as e:
        return f"❌ {e}"

@mcp.prompt("refactor-guide")
def refactor_guide(target: str, goal: str) -> str:
    """Refactor guide."""
    try:
        components = get_v4_components()
        return components['prompt_engine'].render_prompt("refactor-guide", {"target": target, "goal": goal})
    except Exception as e:
        return f"❌ {e}"

@mcp.prompt("summarize-changes")
def summarize_changes(from_ref: str = "HEAD~1", to_ref: str = "HEAD") -> str:
    """Summarize changes."""
    try:
        components = get_v4_components()
        return components['prompt_engine'].render_prompt("summarize-changes", {"from_ref": from_ref, "to_ref": to_ref})
    except Exception as e:
        return f"❌ {e}"


# =============================================================================
# Entry Point
# =============================================================================

def main() -> None:
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()