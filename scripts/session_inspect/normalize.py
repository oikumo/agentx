"""normalize.py — adapter rows -> normalized records (feature_131 §2/A1–A10).

Turn pairing, valid zeros, model triple, epoch-ms passthrough, and the A1
dual inclusion-variant residual test all live here. Unknown record types
pass through (is_known=False); the SNAPSHOT layer attaches the coverage
finding so no record is ever silently dropped.
"""
from __future__ import annotations

import json
from typing import Any, Optional

from .schema import (Finding, Lifecycle, MessageRecord, ModelTriple,
                     PartRecord, SessionRecord, SourceRef, StepUsage,
                     TokenCounters)

KNOWN_PART_TYPES: frozenset = frozenset({
    "step-start", "step-finish", "tool", "text", "reasoning",
    "patch", "file", "compaction", "agent",
})

_OPEN_TOOL_STATUSES = frozenset({"pending", "running"})


def _parse_json(data: Any, *, field: str) -> dict[str, Any]:
    if isinstance(data, dict):
        return data
    if not isinstance(data, str):
        raise ValueError(f"malformed_source_row: {field} is not text")
    try:
        return json.loads(data)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"malformed_source_row: {field} invalid JSON") from exc


def detect_usage_variant(tokens: Optional[dict[str, Any]]) -> str:
    """A1 residual test: classify how a tokens object composes its total.

    Returns one of USAGE_VARIANTS. Missing `total` or a formula miss yields
    "ambiguous" — inclusion semantics are never assumed.
    """
    if not tokens:
        return "empty"
    def _i(v: Any) -> int:
        return int(v) if isinstance(v, (int, float)) and v == int(v) else 0
    cache = tokens.get("cache") or {}
    inp = _i(tokens.get("input"))
    out = _i(tokens.get("output"))
    reas = _i(tokens.get("reasoning"))
    cr = _i(cache.get("read"))
    cw = _i(cache.get("write"))
    total = tokens.get("total")
    if total is None:
        return "ambiguous"
    total = _i(total)
    if total == 0 and inp == 0 and out == 0 and reas == 0 and cr == 0 and cw == 0:
        return "empty"
    if total == inp + out + reas + cr + cw:
        return "disjoint"
    if total == inp + out + cr + cw:
        return "output_includes_reasoning"
    return "ambiguous"


def _counters(tokens: Optional[dict[str, Any]]) -> Optional[TokenCounters]:
    if tokens is None:
        return None
    def _opt(v: Any) -> Optional[int]:
        if v is None:
            return None
        return int(v) if isinstance(v, (int, float)) else None
    cache = tokens.get("cache") or {}
    return TokenCounters(
        input=_opt(tokens.get("input")), output=_opt(tokens.get("output")),
        reasoning=_opt(tokens.get("reasoning")),
        cache_read=_opt(cache.get("read")), cache_write=_opt(cache.get("write")),
        total=_opt(tokens.get("total")),
        variant=detect_usage_variant(tokens))


def normalize_session(row: dict[str, Any], *, open_tool_part_count: int = 0) -> SessionRecord:
    """One `session` row -> SessionRecord (session-cumulative basis; A2–A9)."""
    model: Optional[ModelTriple] = None
    raw_model = row.get("model")
    if raw_model is not None:
        try:
            parsed = _parse_json(raw_model, field="session.model")
            model = ModelTriple(
                model_id=parsed.get("id"), provider_id=parsed.get("providerID"),
                variant=parsed.get("variant"))
        except ValueError:
            model = None  # malformed model JSON stays None, never crashes
    completion = "incomplete" if open_tool_part_count > 0 else "unknown"  # A7
    return SessionRecord(
        id=row["id"], directory=row.get("directory"), title=row.get("title"),
        agent=row.get("agent"), parent_id=row.get("parent_id"), model=model,
        time={"created": row.get("time_created"), "updated": row.get("time_updated"),
              "compacting": row.get("time_compacting"), "archived": row.get("time_archived")},
        tokens=TokenCounters(
            input=row.get("tokens_input"), output=row.get("tokens_output"),
            reasoning=row.get("tokens_reasoning"),
            cache_read=row.get("tokens_cache_read"),
            cache_write=row.get("tokens_cache_write")),
        cost=row.get("cost"),
        lifecycle=Lifecycle(completion=completion,
                            is_child=row.get("parent_id") is not None))


def normalize_message(row: dict[str, Any]) -> MessageRecord:
    """One `message` row -> MessageRecord (per-generation basis for assistants)."""
    data = _parse_json(row.get("data"), field="message.data")
    role = data.get("role")
    tokens = None if role == "user" else _counters(data.get("tokens"))
    return MessageRecord(
        id=row["id"], session_id=row.get("session_id"), role=role,
        parent_id=data.get("parentID"), time_created=row.get("time_created"),
        tokens=tokens, cost=data.get("cost"), model=data.get("modelID"))


def normalize_part(row: dict[str, Any]) -> PartRecord:
    """One `part` row -> PartRecord (payload verbatim; unknown types pass through)."""
    data = _parse_json(row.get("data"), field="part.data")
    ptype = data.get("type")
    return PartRecord(
        id=row["id"], message_id=row.get("message_id"),
        session_id=row.get("session_id"), type=ptype,
        time={"created": row.get("time_created"), "updated": row.get("time_updated")},
        payload={k: v for k, v in data.items() if k != "type"},
        is_known=ptype in KNOWN_PART_TYPES)


def step_usage(part: PartRecord) -> Optional[StepUsage]:
    """Extract the step-incremental usage from a step-finish part (A2 third basis)."""
    if part.type != "step-finish":
        return None
    counters = _counters(part.payload.get("tokens"))
    if counters is None:
        return None
    return StepUsage(tokens=counters, reason=part.payload.get("reason"),
                     snapshot=part.payload.get("snapshot"))


def normalize_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Normalize a full adapter snapshot: rows -> records + coverage findings.

    Open tool parts (A7) flip their session's completion to `incomplete`;
    unknown part types attach a `schema_unsupported` coverage finding and are
    kept (never dropped).
    """
    coverage = snapshot.get("coverage") or {}
    ref = SourceRef(path="snapshot",
                    schema_markers=coverage.get("schema_markers", {}))

    parts = [normalize_part(r) for r in snapshot.get("parts", ())]
    messages = [normalize_message(r) for r in snapshot.get("messages", ())]

    open_counts: dict[str, int] = {}
    for p in parts:
        status = (p.payload.get("state") or {}).get("status")
        if p.type == "tool" and status in _OPEN_TOOL_STATUSES:
            open_counts[p.session_id] = open_counts.get(p.session_id, 0) + 1

    sessions = [normalize_session(s, open_tool_part_count=open_counts.get(s["id"], 0))
                for s in snapshot.get("sessions", ())]

    findings: list[Finding] = []
    unknown = sorted({p.type for p in parts if not p.is_known})
    if unknown:
        findings.append(Finding(
            "schema_unsupported",
            {"record_types": unknown, "policy": "pass_through"},
            ref))
    return {"sessions": sessions, "messages": messages, "parts": parts,
            "findings": findings, "coverage": coverage}
