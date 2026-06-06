"""High-level public API consumed by `server.py`.

Each function returns a dataclass from `kb.models`. Internal exceptions are
caught and surfaced via the dataclass's `success`/`error` fields so the MCP
layer never has to deal with raw tracebacks.
"""

from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

from .chunking import chunk_entry_text
from .ids import make_entry_id
from .ingest import WorkspaceIngestor
from .logging import get_logger
from .models import (
    AddResult,
    AskResult,
    ChunkInfo,
    KBEntry,
    PopulateResult,
    ResetResult,
    SearchResult,
    StatsResult,
)
from .search import hybrid_search
from .store import KBStore, get_default_store
from .synthesis import synthesize
from .query_engine import QueryEngine
from .retrieval import DenseRetriever
from .sparse_index import get_default_retriever


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search(query: str, top_k: int = 5, category: Optional[str] = None,
           store: Optional[KBStore] = None,
           search_mode: str = "hybrid",
           embedding_model: str = "bge-small-en",
           rerank: bool = True,
           reranker_model: str = "ms-marco-MiniLM-L6-v2",
           query_mode: str = "direct",
           ) -> SearchResult:
    """Search the KB using hybrid retrieval.

    Args:
        query: The search query.
        top_k: Maximum number of results.
        category: Optional category filter.
        store: KBStore instance (uses default if None).
        search_mode: ``"hybrid"`` (dense+sparse+RRF),
                     ``"dense"`` (dense-only), ``"sparse"`` (sparse-only).
        embedding_model: Embedding model for dense retrieval.
        rerank: Whether to apply cross-encoder reranking.
        reranker_model: Cross-encoder model name.
        query_mode: Query preprocessing mode (``"direct"``, ``"rewrite"``,
                    ``"hyde"``, ``"multi_query"``, ``"decompose"``).

    Returns:
        A ``SearchResult`` (never raises).
    """
    try:
        store = store or get_default_store()

        # Build query engine if needed
        qe: Optional[QueryEngine] = None
        if query_mode != "direct":
            qe = QueryEngine(mode=query_mode)

        # Setup retrievers
        dense_retriever = DenseRetriever(model_name=embedding_model, store=store)
        
        sparse_retriever = None
        if search_mode in ("hybrid", "sparse"):
            sparse_retriever = get_default_retriever()

        # Setup reranker
        reranker = None
        if rerank:
            try:
                from .reranking import CrossEncoderReranker
                reranker = CrossEncoderReranker(model_name=reranker_model)
            except ImportError:
                reranker = None

        # Query preprocessing
        queries = [query]
        if qe is not None:
            queries = qe.process(query)

        # Run search for each query variant and merge results
        all_results = []
        seen_ids = set()
        for q in queries:
            if not q.strip():
                continue
            results = hybrid_search(
                query=q,
                dense_retriever=dense_retriever,
                sparse_retriever=sparse_retriever,
                reranker=reranker,
                top_k=top_k,
                category=category,
                rerank=rerank,
            )
            for r in results:
                if r["id"] not in seen_ids:
                    seen_ids.add(r["id"])
                    all_results.append(r)

        # Re-sort merged results by combined_score descending
        all_results.sort(key=lambda r: float(r.get("combined_score", 0)), reverse=True)
        raw = all_results[:top_k]

        entries = [KBEntry(
            id=r.get("id", "unknown"),
            type=r.get("type", "unknown"),
            category=r.get("category", "general"),
            title=r.get("title", "(untitled)"),
            finding=r.get("finding", ""),
            solution=r.get("solution", ""),
            context=r.get("context", ""),
            example=r.get("example", ""),
            confidence=float(r.get("confidence", 0.5)),
            combined_score=float(r.get("combined_score", 0.0)),
        ) for r in raw]
        return SearchResult(
            success=True,
            entries=entries,
            message=f"Found {len(entries)} relevant entries" if entries else "No results found",
        )
    except Exception as exc:
        get_logger().error("search failed: %s", exc)
        return SearchResult(success=False, message="Search failed", error=str(exc))


# ---------------------------------------------------------------------------
# Ask (synthesised)
# ---------------------------------------------------------------------------

def ask(question: str, top_k: int = 3,
        store: Optional[KBStore] = None,
        search_mode: str = "hybrid",
        embedding_model: str = "bge-small-en",
        rerank: bool = True,
        reranker_model: str = "ms-marco-MiniLM-L6-v2",
        query_mode: str = "direct",
        synthesis_mode: str = "template",
        ) -> AskResult:
    """Ask a question and synthesise an answer from KB results.

    Args:
        question: The question to answer.
        top_k: Number of context entries to retrieve.
        store: KBStore instance (uses default if None).
        search_mode: ``"hybrid"`` (dense+sparse+RRF),
                     ``"dense"``, ``"sparse"``.
        embedding_model: Embedding model for dense retrieval.
        rerank: Whether to apply cross-encoder reranking.
        reranker_model: Cross-encoder model name.
        query_mode: Query preprocessing mode (``"direct"``, ``"rewrite"``,
                    ``"hyde"``, ``"multi_query"``, ``"decompose"``).
        synthesis_mode: ``"template"`` or ``"llm"``
                        (LLM-based generation, requires llm callable).

    Returns:
        An ``AskResult`` (never raises).
    """
    try:
        store = store or get_default_store()

        # Build query engine if needed
        qe: Optional[QueryEngine] = None
        if query_mode != "direct":
            qe = QueryEngine(mode=query_mode)

        # Setup retrievers
        dense_retriever = DenseRetriever(model_name=embedding_model, store=store)
        
        sparse_retriever = None
        if search_mode in ("hybrid", "sparse"):
            sparse_retriever = get_default_retriever()

        # Setup reranker
        reranker = None
        if rerank:
            try:
                from .reranking import CrossEncoderReranker
                reranker = CrossEncoderReranker(model_name=reranker_model)
            except ImportError:
                reranker = None

        # Query preprocessing
        queries = [question]
        if qe is not None:
            queries = qe.process(question)

        # Run search for each query variant and merge results
        all_results = []
        seen_ids = set()
        for q in queries:
            if not q.strip():
                continue
            results = hybrid_search(
                query=q,
                dense_retriever=dense_retriever,
                sparse_retriever=sparse_retriever,
                reranker=reranker,
                top_k=top_k,
                category=None,
                rerank=rerank,
            )
            for r in results:
                if r["id"] not in seen_ids:
                    seen_ids.add(r["id"])
                    all_results.append(r)

        # Re-sort merged results by combined_score descending
        all_results.sort(key=lambda r: float(r.get("combined_score", 0)), reverse=True)
        raw = all_results[:top_k]

        # Synthesize answer
        if synthesis_mode == "template":
            return synthesize(question, raw)
        elif synthesis_mode == "llm":
            # LLM synthesis — requires LLM callable, falls back to template
            try:
                from .synthesis import llm_synthesize
                return llm_synthesize(question, raw, model=embedding_model)
            except (ImportError, NotImplementedError):
                get_logger().warning(
                    "LLM synthesis not available, falling back to template"
                )
                return synthesize(question, raw)
        else:
            get_logger().warning(
                "Unknown synthesis_mode %r, falling back to template",
                synthesis_mode,
            )
            return synthesize(question, raw)

    except Exception as exc:
        get_logger().error("ask failed: %s", exc)
        return AskResult(success=False, error=str(exc))


# ---------------------------------------------------------------------------
# Add
# ---------------------------------------------------------------------------

def add_entry(entry_type: str, category: str, title: str, finding: str,
              solution: str, context: str = "", confidence: float = 0.5,
              example: str = "", store: Optional[KBStore] = None,
              enable_chunking: bool = True) -> AddResult:
    """Insert a new entry into the KB.

    Args:
        entry_type: Type of entry (pattern, finding, decision, correction).
        category: Category (code, class, method, function, workflow, documentation, architecture).
        title: Entry title.
        finding: Main finding or insight.
        solution: Solution or recommendation.
        context: Additional context (optional).
        confidence: Confidence score 0.0-1.0 (default: 0.5).
        example: Example code or text (optional).
        store: KBStore instance (uses default if None).
        enable_chunking: If True, automatically chunk long entries into
                         smaller pieces for better retrieval precision.

    Returns:
        AddResult with success status and entry ID.
    """
    try:
        store = store or get_default_store()
        entry_id = make_entry_id(entry_type=entry_type, category=category, title=title)
        document_text = " ".join([title, finding, solution, context, example])
        metadata = {
            "entry_id": entry_id,
            "type": entry_type,
            "category": category,
            "title": title,
            "finding": finding,
            "solution": solution,
            "context": context,
            "example": example,
            "confidence": confidence,
            "created_at": datetime.now().isoformat(),
            "is_chunked": False,
        }
        store.add(entry_id=entry_id, document_text=document_text, metadata=metadata)

        # Auto-chunk if enabled and text is long enough
        if enable_chunking and len(document_text) > 512:
            chunks = chunk_entry_text(
                text=document_text,
                parent_id=entry_id,
                source_type="kb_entry",
                chunk_size=512,
                chunk_overlap=64,
                metadata={
                    "type": entry_type,
                    "category": category,
                    "title": title,
                    "confidence": confidence,
                },
            )
            if len(chunks) > 1:
                store.add_chunks(chunks=chunks)
                # Update entry metadata to indicate chunking
                metadata["is_chunked"] = True
                metadata["chunk_count"] = len(chunks)
                store.add(entry_id=entry_id, document_text=document_text, metadata=metadata)

        return AddResult(
            success=True,
            entry_id=entry_id,
            message=f"Added {entry_type.upper()} entry: {entry_id} - {title}",
        )
    except Exception as exc:
        get_logger().error("add_entry failed: %s", exc)
        return AddResult(success=False, error=str(exc), message="Failed to add entry")


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def stats(store: Optional[KBStore] = None) -> StatsResult:
    """Compute exact aggregate KB statistics over the whole collection.

    Walks every entry via ``store.iter_metadata()`` so the by-type / by-category /
    confidence breakdowns reconcile with ``total_entries`` (previously they were
    computed from a capped 1000-row sample and diverged once the KB grew larger).
    """
    try:
        store = store or get_default_store()
        total = store.count()
        by_type: dict = {}
        by_category: dict = {}
        confidences: List[float] = []
        for metadata in store.iter_metadata():
            t = metadata.get("type", "unknown")
            c = metadata.get("category", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
            by_category[c] = by_category.get(c, 0) + 1
            confidences.append(float(metadata.get("confidence", 0.5)))

        # Invariant: a full scan must visit exactly `total` entries.
        counted = sum(by_type.values())
        if counted != total:
            get_logger().warning(
                "stats mismatch: counted %s entries but count() reports %s",
                counted, total,
            )

        high = sum(1 for c in confidences if c >= 0.9)
        medium = sum(1 for c in confidences if 0.6 <= c < 0.9)
        low = sum(1 for c in confidences if c < 0.6)

        # Compute mean and median confidence
        mean_conf = 0.0
        median_conf = 0.0
        if confidences:
            mean_conf = sum(confidences) / len(confidences)
            sorted_confs = sorted(confidences)
            n = len(sorted_confs)
            if n % 2 == 1:
                median_conf = sorted_confs[n // 2]
            else:
                median_conf = (sorted_confs[n // 2 - 1] + sorted_confs[n // 2]) / 2.0

        return StatsResult(
            success=True,
            total_entries=total,
            by_type=by_type,
            by_category=by_category,
            confidence_distribution={"high": high, "medium": medium, "low": low},
            mean_confidence=round(mean_conf, 4),
            median_confidence=round(median_conf, 4),
        )
    except Exception as exc:
        get_logger().error("stats failed: %s", exc)
        return StatsResult(success=False, error=str(exc))


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------

def reset(store: Optional[KBStore] = None) -> ResetResult:
    """Delete all entries (drops and recreates the Chroma collection)."""
    try:
        store = store or get_default_store()
        store.reset()
        return ResetResult(
            success=True,
            total_entries=0,
            message="Knowledge base reset successfully. All entries deleted.",
        )
    except Exception as exc:
        get_logger().error("reset failed: %s", exc)
        return ResetResult(success=False, error=str(exc), message=f"Reset failed: {exc}")


# ---------------------------------------------------------------------------
# Populate workspace
# ---------------------------------------------------------------------------

_DEFAULT_EXCLUDES = {
    "__pycache__", ".venv", "venv", ".git", "node_modules",
    "chroma_db", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "dist", "build", ".tox", ".eggs", "site-packages",
    # Note: .env directories and files are also excluded via special handling
    # in the is_excluded() function to catch .env, .env.local, .env.production, etc.
}


# Type alias for progress callback: fn(current, total, message) -> None
ProgressCallback = Optional[Callable[[int, int, str], None]]


def populate_workspace(workspace_root: Optional[str] = None,
                       include_python: bool = True,
                       include_markdown: bool = True,
                       exclude_dirs: Optional[List[str]] = None,
                       reset_first: bool = True,
                       store: Optional[KBStore] = None,
                       progress_callback: ProgressCallback = None,
                       ) -> PopulateResult:
    """Walk a workspace and ingest its Python / Markdown files.

    Args:
        workspace_root: Root directory to scan.
        include_python: Whether to ingest Python files.
        include_markdown: Whether to ingest Markdown files.
        exclude_dirs: Additional directory names to exclude.
        reset_first: If True, reset the KB before population.
        store: KBStore instance (uses default if None).
        progress_callback: Optional callback fn(current, total, message)
                           called periodically to report progress.
    """
    try:
        store = store or get_default_store()

        if workspace_root is None:
            # repo root: 4 levels up from kb/api.py
            root_path = Path(__file__).resolve().parent.parent.parent.parent
        else:
            root_path = Path(workspace_root).resolve()

        if not root_path.exists() or not root_path.is_dir():
            return PopulateResult(
                success=False,
                error=f"Workspace root does not exist or is not a directory: {root_path}",
                message="Population failed",
            )

        excludes = set(_DEFAULT_EXCLUDES)
        if exclude_dirs:
            excludes.update(exclude_dirs)

        if reset_first:
            store.reset()

        patterns: List[str] = []
        if include_python:
            patterns.append("*.py")
        if include_markdown:
            patterns.append("*.md")

        if not patterns:
            return PopulateResult(
                success=False,
                error="No file types selected",
                message="Set at least one of include_python or include_markdown to True",
            )

        ingestor = WorkspaceIngestor(store=store, workspace_root=root_path)

        def is_excluded(p: Path) -> bool:
            # Check if any path part matches an exclude directory
            for part in p.parts:
                if part in excludes:
                    return True
                # Also check for .env directories and files (exact match or starts with .env.)
                if part == ".env" or part.startswith(".env."):
                    return True
            return False

        # Collect all matching file paths upfront so we can report progress
        all_files: List[Path] = []
        for pattern in patterns:
            for file_path in root_path.rglob(pattern):
                if is_excluded(file_path) or not file_path.is_file():
                    continue
                all_files.append(file_path)

        total_files = len(all_files)
        if progress_callback:
            progress_callback(0, total_files, f"Scanning {total_files} files...")

        by_pattern: dict = {}
        files_processed = 0
        errors: List[str] = []

        # Process in batches, reporting progress each time
        PROGRESS_INTERVAL = max(1, total_files // 20)  # ~20 updates total

        for idx, file_path in enumerate(all_files):
            pattern_key = file_path.suffix
            try:
                ids_out = ingestor.ingest_file(file_path)
                count = len(ids_out)
                by_pattern[pattern_key] = by_pattern.get(pattern_key, 0) + count
                files_processed += 1
            except Exception as exc:  # pragma: no cover - belt-and-braces
                errors.append(f"{file_path}: {exc}")

            # Report progress periodically
            if progress_callback and (idx % PROGRESS_INTERVAL == 0 or idx == total_files - 1):
                progress_callback(
                    min(idx + 1, total_files),
                    total_files,
                    f"Processed {files_processed} files, {sum(by_pattern.values())} entries...",
                )

        total = sum(by_pattern.values())
        if progress_callback:
            progress_callback(
                total_files, total_files,
                f"Done: {total} entries from {files_processed} files",
            )

        return PopulateResult(
            success=True,
            workspace_root=str(root_path),
            reset_performed=reset_first,
            files_processed=files_processed,
            total_entries=total,
            by_pattern=by_pattern,
            excluded_dirs=sorted(excludes),
            errors=errors[:20],
            error_count=len(errors),
            message=f"Populated KB with {total} entries from {files_processed} files",
        )
    except Exception as exc:
        get_logger().error("populate_workspace failed: %s", exc)
        return PopulateResult(success=False, error=str(exc),
                              message=f"Population failed: {exc}")