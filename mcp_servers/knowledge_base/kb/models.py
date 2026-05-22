"""Dataclass models for the knowledge base public API.

Return shapes for every public `kb.*` function are defined here so callers
(MCP `server.py`, tests) get consistent, introspectable results instead of
hand-rolled `dict`s.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class KBEntry:
    """A single knowledge-base entry as returned by search/ask."""
    id: str
    type: str
    category: str
    title: str
    finding: str = ""
    solution: str = ""
    context: str = ""
    example: str = ""
    confidence: float = 0.5
    combined_score: float = 0.0


@dataclass
class SearchResult:
    """Result of a `kb.search` call."""
    success: bool
    entries: List[KBEntry] = field(default_factory=list)
    message: str = ""
    error: Optional[str] = None


@dataclass
class AskSource:
    """A citation row returned alongside a synthesized answer."""
    id: str
    title: str
    type: str
    category: str
    confidence: float


@dataclass
class AskResult:
    """Result of a `kb.ask` call. `answer` is a synthesized markdown string."""
    success: bool
    answer: str = ""
    sources: List[AskSource] = field(default_factory=list)
    confidence: float = 0.0
    error: Optional[str] = None


@dataclass
class AddResult:
    """Result of `kb.add_entry`."""
    success: bool
    entry_id: Optional[str] = None
    message: str = ""
    error: Optional[str] = None


@dataclass
class StatsResult:
    """Result of `kb.stats`."""
    success: bool
    total_entries: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)
    by_category: Dict[str, int] = field(default_factory=dict)
    confidence_distribution: Dict[str, int] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class ResetResult:
    """Result of `kb.reset`."""
    success: bool
    total_entries: int = 0
    message: str = ""
    error: Optional[str] = None


@dataclass
class PopulateResult:
    """Result of `kb.populate_workspace`."""
    success: bool
    workspace_root: str = ""
    reset_performed: bool = False
    files_processed: int = 0
    total_entries: int = 0
    by_pattern: Dict[str, int] = field(default_factory=dict)
    excluded_dirs: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    error_count: int = 0
    message: str = ""
    error: Optional[str] = None
