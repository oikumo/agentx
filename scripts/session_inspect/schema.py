"""schema.py — normalized records + closed failure vocabulary (feature_131 §2).

Design refs: design_001_core_architecture.md §2, operation_spec_001 (schema.py).
Every finding carries a SourceRef (provenance, proposal capture-contract 6).
The failure vocabulary is CLOSED: construction with an unknown name raises,
so names cannot drift into strings at runtime.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

# --- closed failure vocabulary (frozen; design_001 §2) ---------------------
FAILURE_NAMES: tuple[str, ...] = (
    "source_unreadable",
    "schema_unsupported",
    "inclusion_semantics_ambiguous",
    "deletion_coverage_unavailable",
    "session_incomplete",
    "missing_child",
    "hierarchy_cycle",
    "duplicate_membership",
    "label_grammar_invalid",
    "label_identity_conflict",
    "label_orphan_event",
    "span_reversed",
    "label_unbound_to_manifest",
    "echo_not_trial",
    "query_limit_exceeded",
    "cursor_stale",
    "metric_variant_mismatch",
    "reconciliation_discrepancy",
    "double_counted_basis",
    "trial_incomplete",
    "manifest_invalid",
)

_FAILURE_NAME_SET = frozenset(FAILURE_NAMES)


def is_failure_name(name: str) -> bool:
    """True iff `name` belongs to the closed failure vocabulary."""
    return name in _FAILURE_NAME_SET


@dataclass
class SourceRef:
    """Provenance attached to every finding/derived value."""

    path: str
    schema_markers: dict[str, Any] = field(default_factory=dict)
    snapshot_digest: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "schema_markers": self.schema_markers,
            "snapshot_digest": self.snapshot_digest,
        }


@dataclass
class Finding:
    """Named failure with provenance — never a bare string."""

    name: str
    detail: dict[str, Any] = field(default_factory=dict)
    source_ref: Optional[SourceRef] = None

    def __post_init__(self) -> None:
        if not is_failure_name(self.name):
            raise ValueError(
                f"unknown_failure_name: {self.name!r} not in closed vocabulary"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "detail": self.detail,
            "source_ref": self.source_ref.to_dict() if self.source_ref else None,
        }


class FindingError(Exception):
    """Typed error carrying a closed-vocabulary Finding (never a bare string)."""

    def __init__(self, finding: Finding) -> None:
        self.finding = finding
        super().__init__(finding.name)


# ---------------------------------------------------------------------------
# Normalized OpenCode records (analysis_001 §§2–3, design_001 §2)
# ---------------------------------------------------------------------------

# Inclusion-semantics variants (A1): how a tokens object composes its total.
USAGE_VARIANTS: tuple[str, ...] = (
    "disjoint",                  # total = in+out+reas+cache_read+cache_write
    "output_includes_reasoning",  # total = in+out+cache_read+cache_write
    "empty",                     # valid zero row (A3)
    "ambiguous",                 # neither formula holds — never guessed
)

COMPLETION_STATES: tuple[str, ...] = ("complete", "incomplete", "unknown")


@dataclass
class ModelTriple:
    """Normalized session/message model identity (A9)."""

    model_id: Optional[str] = None
    provider_id: Optional[str] = None
    variant: Optional[str] = None


@dataclass
class TokenCounters:
    """One usage accounting basis. Components are Optional: missing stays null
    with a reason at the metric layer — never zero-filled, never estimated."""

    input: Optional[int] = None
    output: Optional[int] = None
    reasoning: Optional[int] = None
    cache_read: Optional[int] = None
    cache_write: Optional[int] = None
    total: Optional[int] = None
    variant: Optional[str] = None  # one of USAGE_VARIANTS, or None (unverifiable)

    def to_dict(self) -> dict[str, Any]:
        return {
            "input": self.input, "output": self.output,
            "reasoning": self.reasoning, "cache_read": self.cache_read,
            "cache_write": self.cache_write, "total": self.total,
            "variant": self.variant,
        }


@dataclass
class Lifecycle:
    completion: str = "unknown"  # one of COMPLETION_STATES
    is_child: bool = False


@dataclass
class SessionRecord:
    id: str
    directory: Optional[str] = None
    title: Optional[str] = None
    agent: Optional[str] = None
    parent_id: Optional[str] = None
    model: Optional[ModelTriple] = None
    time: dict[str, Any] = field(default_factory=dict)      # created/updated(+..)
    tokens: Optional[TokenCounters] = None                  # session-cumulative basis
    cost: Optional[float] = None                            # stored cost only (A4)
    lifecycle: Lifecycle = field(default_factory=Lifecycle)


@dataclass
class MessageRecord:
    id: str
    session_id: str
    role: Optional[str] = None
    parent_id: Optional[str] = None  # turn link: assistant.parentID = user msg (analysis §3)
    time_created: Optional[int] = None
    tokens: Optional[TokenCounters] = None  # per-generation basis; None for user msgs
    cost: Optional[float] = None
    model: Optional[str] = None


@dataclass
class PartRecord:
    id: str
    message_id: str
    session_id: str
    type: Optional[str] = None
    time: dict[str, Any] = field(default_factory=dict)
    payload: dict[str, Any] = field(default_factory=dict)  # verbatim per-type union
    is_known: bool = True                                    # unknown passes through (never dropped)


@dataclass
class StepUsage:
    tokens: TokenCounters
    reason: Optional[str] = None
    snapshot: Optional[str] = None
