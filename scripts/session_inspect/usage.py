"""usage.py — token bases, variant-aware sums, reconciliation (feature_131 §4).

Three accounting bases (session-cumulative, message-incremental,
step-incremental) are never mixed: combining them returns a named
double_counted_basis finding, not a number. Derived totals sum NAMED
COMPONENTS under a versioned MetricDefinition — never the source `total`
unless the record's inclusion variant is verified compatible (A1). Session
reconciliation compares session-cumulative columns against variant-aware
message component sums and exposes — never smears — the residual (A2).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .schema import Finding, MessageRecord, SessionRecord, SourceRef, TokenCounters

# Basis names (design_001 §4).
BASIS_SESSION = "session_cumulative"
BASIS_MESSAGE = "message_incremental"
BASIS_STEP = "step_incremental"

VARIANT_POLICIES: tuple[str, ...] = ("any", "require_disjoint", "per_variant")


@dataclass
class MetricDefinition:
    """Versioned metric: name + component list + variant policy."""

    name: str
    version: int
    components: tuple[str, ...] = ()
    variant_policy: str = "any"


_COMPONENTS = ("input", "output", "reasoning", "cache_read", "cache_write")


def _val(tc: TokenCounters, comp: str) -> Optional[int]:
    return getattr(tc, comp, None)


def sum_components(items: list[tuple[str, TokenCounters]],
                   metric: MetricDefinition,
                   ref: Optional[SourceRef] = None) -> dict[str, Any] | Finding:
    """Sum named components of same-basis counters under a declared metric."""
    if metric.variant_policy not in VARIANT_POLICIES:
        raise ValueError(f"unknown_variant_policy:{metric.variant_policy}")
    bases = sorted({b for b, _ in items})
    if len(bases) > 1:
        return Finding("double_counted_basis", {"bases": bases}, ref)
    counters = [tc for _, tc in items if tc is not None]
    if metric.variant_policy == "require_disjoint":
        bad = sorted({tc.variant for tc in counters
                      if tc.variant != "disjoint"},
                     key=lambda v: "" if v is None else v)
        if bad:
            return Finding("metric_variant_mismatch",
                           {"metric": metric.name, "variants": bad,
                            "policy": metric.variant_policy}, ref)
    totals: dict[str, Any] = {}
    for comp in metric.components:
        vals = [_val(tc, comp) for tc in counters]
        vals = [v for v in vals if v is not None]
        totals[comp] = sum(vals) if vals else None
    return totals


def reconcile_session(session: SessionRecord,
                      messages: list[MessageRecord],
                      ref: Optional[SourceRef] = None) -> dict[str, Any]:
    """Session cumulative vs variant-aware message component sums (A2).

    Reasoning sums only over disjoint-variant messages: on
    output_includes_reasoning messages the reasoning is already inside output
    (session columns follow message reporting — analysis §3 exact-sum rule;
    reasoning-bearing sessions need live verification per A2).
    """
    counters = [m.tokens for m in messages if m.tokens is not None]

    def _sum(sel) -> int:
        return sum(v for v in (_val(tc, sel) for tc in counters)
                   if v is not None)

    disjoint_reasoning = sum(v for tc in counters
                             if tc.variant in ("disjoint", "empty")
                             for v in [_val(tc, "reasoning")]
                             if v is not None)
    expected = {
        "input": _sum("input"), "output": _sum("output"),
        "reasoning": disjoint_reasoning,
        "cache_read": _sum("cache_read"), "cache_write": _sum("cache_write"),
    }
    sess = session.tokens or TokenCounters()
    residual = {comp: (getattr(sess, comp) or 0) - total
                for comp, total in expected.items()
                if (getattr(sess, comp) or 0) != total}
    if not residual:
        return {"status": "reconciled"}
    return {"status": "reconciliation_discrepancy", "residual": residual,
            "basis": {"session": "session_cumulative",
                      "messages": "message_incremental"}}


def legacy_feature130_metrics(counters: Optional[TokenCounters],
                              ref: Optional[SourceRef] = None) -> dict[str, Any]:
    """Versioned legacy mapping (feature_130): prompt = input + cache_read;
    completion = output + reasoning for disjoint records, output (already
    inclusive) for output_includes_reasoning records. Missing -> null + reason.
    """
    if counters is None:
        return {"prompt": None, "completion": None,
                "reason": "missing_counters"}
    variant = counters.variant
    prompt = None
    if counters.input is not None and counters.cache_read is not None:
        prompt = counters.input + counters.cache_read
    completion = None
    reason = None
    if variant in ("disjoint", "empty"):
        if counters.output is not None and counters.reasoning is not None:
            completion = counters.output + counters.reasoning
        else:
            reason = "missing_counters"
    elif variant == "output_includes_reasoning":
        if counters.output is not None:
            completion = counters.output
        else:
            reason = "missing_counters"
    else:
        reason = "inclusion_semantics_ambiguous"
    if prompt is None and reason is None:
        reason = "missing_counters"
    return {"prompt": prompt, "completion": completion, "reason": reason}
