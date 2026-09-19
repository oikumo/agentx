"""O2 multi-select + directive protocol — pure parse + plan (feature_111).

Stdlib-only, no net/ledger I/O. The caller (`state.apply_selection`)
supplies the live O1 `Options:` IDs + `enabled[]` for validation; this module
parses the selection grammar, maps IDs to existing-op plans (M0 bound: at most
one net-mutating op per batch + N overlay annotations + N D4 proposals), and
describes the plan for the approval gate / ledger reasoning field.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

__all__ = [
    "SelectionError",
    "Selection",
    "Plan",
    "parse_selection",
    "validate_selection",
    "plan_selection",
    "describe_plan",
]

_ID = r"(?:pool:[^\s,}]+|proj:[A-Za-z0-9_]+|drift:[^:\s,}]+:[^,}]+?|unscoped:\d+)"
_DIRECTIVE = re.compile(
    r"(?P<id>" + _ID + r")\s*:\s*(?P<q>[\"'])(?P<text>(?:\\.|(?!\2).)*?)\2"
)
_PICK_HEAD = re.compile(r"\s*pick\s*\{\s*(?P<body>[^}]*)\}\s*(?P<tail>.*)", re.S)


class SelectionError(ValueError):
    """Stable-code selection refusal (code + human detail)."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}{(': ' + detail) if detail else ''}")
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class Selection:
    ids: tuple[str, ...]
    directives: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Plan:
    mutate: tuple[dict[str, str], ...]  # at most one entry in M0
    annotations: dict[str, str]
    proposals: tuple[str, ...]


def _split_ids(body: str) -> list[str]:
    parts = [p.strip() for p in body.split(",")]
    return [p for p in parts if p]


def parse_selection(text: str) -> Selection:
    """Parse `pick {id,…} [+ id:\"directive\" …]` (pure)."""
    m = _PICK_HEAD.match(text or "")
    if not m:
        raise SelectionError("bad_syntax", "expected: pick {id, …} [+ id:\"…\"]")
    ids = _split_ids(m.group("body"))
    if not ids:
        raise SelectionError("bad_syntax", "empty pick set")
    if len(set(ids)) != len(ids):
        dup = next(i for i in ids if ids.count(i) > 1)
        raise SelectionError("dup_id", dup)
    for i in ids:
        if not re.fullmatch(_ID, i):
            raise SelectionError("bad_syntax", f"bad id: {i}")
    tail = m.group("tail").strip()
    directives: dict[str, str] = {}
    if tail:
        chunks = [c.strip() for c in re.split(r"\s*\+\s*", tail) if c.strip()]
        for c in chunks:
            dm = _DIRECTIVE.fullmatch(c)
            if not dm:
                raise SelectionError("bad_syntax", f"bad directive: {c}")
            did = dm.group("id")
            if did not in ids:
                raise SelectionError("directive_without_id", did)
            if did in directives:
                raise SelectionError("dup_id", f"directive:{did}")
            directives[did] = dm.group("text").replace('\\"', '"').replace("\\'", "'")
    return Selection(ids=tuple(ids), directives=dict(directives))


def validate_selection(sel: Selection, valid_ids: set[str] | frozenset[str]) -> Selection:
    """Refuse unknown IDs against the live O1 `Options:` set (pure)."""
    for i in sel.ids:
        if i not in valid_ids:
            raise SelectionError("unknown_id", i)
    return sel


def _is_mutating(i: str, enabled: set[str] | frozenset[str]) -> bool:
    return i.startswith("pool:") and i[len("pool:"):] in enabled


def plan_selection(
    sel: Selection,
    *,
    valid_ids: set[str] | frozenset[str] | None = None,
    enabled: list[str] | set[str] | frozenset[str] | None = None,
) -> Plan:
    """Map IDs to existing-op plans (pure, M0 single-mutate bound)."""
    if valid_ids is not None:
        validate_selection(sel, set(valid_ids))
    en = set(enabled or ())
    mutates: list[dict[str, str]] = []
    annotations: dict[str, str] = {}
    proposals: list[str] = []
    for i in sel.ids:
        if i in sel.directives:
            annotations[i] = sel.directives[i]
        if _is_mutating(i, en):
            mutates.append({"kind": "fire", "transition": i[len("pool:"):]})
        elif i.startswith("pool:"):
            # Disabled pool transition: executor's fire refuses authoritatively;
            # still counts as the one mutate slot so the batch stays atomic.
            mutates.append({"kind": "fire", "transition": i[len("pool:"):]})
        elif i.startswith("proj:"):
            slug = i[len("proj:"):]
            annotations.setdefault(i, "selected")
            proposals.append(f"open {slug} project home (claim handles are O3)")
        elif i.startswith("drift:"):
            proposals.append(f"hygiene {i}: propose splice/sync (D4 proposal-only)")
        elif i.startswith("unscoped:"):
            proposals.append(f"scope {i} before fire (proposal-only)")
    if len(mutates) > 1:
        second = mutates[1].get("transition", "?")
        raise SelectionError("multi_mutate_deferred_o4", f"second mutate: {second}")
    return Plan(mutate=tuple(mutates), annotations=annotations, proposals=tuple(proposals))


def describe_plan(plan: Plan) -> str:
    """One-line summary for the approval gate / ledger reasoning."""
    if plan.mutate:
        m = plan.mutate[0]
        head = f"{m['kind']}:{m.get('transition', m.get('task_id', '?'))}"
    else:
        head = "annotate-only"
    return (
        f"apply {{mutate={head}, annotations={len(plan.annotations)}, "
        f"proposals={len(plan.proposals)}}}"
    )
