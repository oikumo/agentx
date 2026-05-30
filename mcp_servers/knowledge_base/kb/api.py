"""High-level public API consumed by `server.py`.

Each function returns a dataclass from `kb.models`. Internal exceptions are
caught and surfaced via the dataclass's `success`/`error` fields so the MCP
layer never has to deal with raw tracebacks.
"""

from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

from .ids import make_entry_id
from .ingest import WorkspaceIngestor
from .logging import get_logger
from .models import (
    AddResult,
    AskResult,
    KBEntry,
    PopulateResult,
    ResetResult,
    SearchResult,
    StatsResult,
)
from .search import hybrid_search
from .store import KBStore, get_default_store
from .synthesis import synthesize


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search(query: str, top_k: int = 5, category: Optional[str] = None,
           store: Optional[KBStore] = None) -> SearchResult:
    """Search the KB. Returns a `SearchResult` (never raises)."""
    try:
        store = store or get_default_store()
        raw = hybrid_search(store.collection, query, category, top_k)
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
        store: Optional[KBStore] = None) -> AskResult:
    """Ask a question and synthesise an answer from KB results."""
    try:
        store = store or get_default_store()
        raw = hybrid_search(store.collection, question, None, top_k)
        return synthesize(question, raw)
    except Exception as exc:
        get_logger().error("ask failed: %s", exc)
        return AskResult(success=False, error=str(exc))


# ---------------------------------------------------------------------------
# Add
# ---------------------------------------------------------------------------

def add_entry(entry_type: str, category: str, title: str, finding: str,
              solution: str, context: str = "", confidence: float = 0.5,
              example: str = "", store: Optional[KBStore] = None) -> AddResult:
    """Insert a new entry into the KB."""
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
        }
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
    """Compute aggregate KB statistics from a metadata sample."""
    try:
        store = store or get_default_store()
        total = store.count()
        by_type: dict = {}
        by_category: dict = {}
        confidences: List[float] = []
        for metadata in store.sample_metadata(limit=1000):
            t = metadata.get("type", "unknown")
            c = metadata.get("category", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
            by_category[c] = by_category.get(c, 0) + 1
            confidences.append(float(metadata.get("confidence", 0.5)))

        high = sum(1 for c in confidences if c >= 0.9)
        medium = sum(1 for c in confidences if 0.6 <= c < 0.9)
        low = sum(1 for c in confidences if c < 0.6)

        return StatsResult(
            success=True,
            total_entries=total,
            by_type=by_type,
            by_category=by_category,
            confidence_distribution={"high": high, "medium": medium, "low": low},
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
