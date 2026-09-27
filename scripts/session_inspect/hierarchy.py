"""hierarchy.py — session forest with direct vs subtree usage (feature_131 §6).

Direct-session and inclusive-subtree totals are separate bases (never mixed).
Missing children are named coverage findings; parent cycles are reported and
their subtree totals refused (None, propagated upward — a subtree containing
an uncomputable part is uncomputable). Overlapping unions count each session
once and report duplicate_membership.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .schema import Finding, SessionRecord, SourceRef, TokenCounters


@dataclass
class ForestNode:
    id: str
    session: Optional[SessionRecord] = None
    parent: Optional[str] = None
    children: list[str] = field(default_factory=list)
    direct_usage: TokenCounters = field(default_factory=TokenCounters)
    subtree_usage: Optional[TokenCounters] = None  # None = refused (cycle)


@dataclass
class Forest:
    nodes: dict[str, ForestNode] = field(default_factory=dict)
    roots: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)


def _add(a: Optional[int], b: Optional[int]) -> Optional[int]:
    if a is None and b is None:
        return None
    return (a or 0) + (b or 0)


def _sum_usage(a: TokenCounters, b: TokenCounters) -> TokenCounters:
    return TokenCounters(input=_add(a.input, b.input), output=_add(a.output, b.output),
                         reasoning=_add(a.reasoning, b.reasoning),
                         cache_read=_add(a.cache_read, b.cache_read),
                         cache_write=_add(a.cache_write, b.cache_write))


def _direct_of(session: SessionRecord) -> TokenCounters:
    t = session.tokens
    if t is None:
        return TokenCounters()
    return TokenCounters(input=t.input, output=t.output, reasoning=t.reasoning,
                         cache_read=t.cache_read, cache_write=t.cache_write)


def build_forest(sessions: list[SessionRecord],
                 ref: Optional[SourceRef] = None) -> Forest:
    """Assemble the parent/child forest; compute direct vs subtree usage."""
    forest = Forest()
    for s in sessions:
        forest.nodes[s.id] = ForestNode(id=s.id, session=s, parent=s.parent_id,
                                        direct_usage=_direct_of(s))
    for node in forest.nodes.values():
        parent = node.parent
        if parent is None:
            continue
        if parent in forest.nodes:
            forest.nodes[parent].children.append(node.id)
        else:
            forest.findings.append(Finding(
                "missing_child",
                {"session_id": node.id, "referenced_id": parent}, ref))
            node.parent = None  # unattached -> treated as root
    forest.roots = [nid for nid, n in forest.nodes.items() if n.parent is None]

    resolved: dict[str, Optional[TokenCounters]] = {}

    def subtree(nid: str, stack: tuple[str, ...]) -> Optional[TokenCounters]:
        if nid in resolved:
            return resolved[nid]
        if nid in stack:
            cycle = list(stack[stack.index(nid):]) + [nid]
            forest.findings.append(Finding(
                "hierarchy_cycle",
                {"cycle_ids": sorted(set(cycle))}, ref))
            for member in set(cycle):
                resolved[member] = None
            return None
        node = forest.nodes[nid]
        total = node.direct_usage
        for child in node.children:
            child_total = subtree(child, stack + (nid,))
            if child_total is None:
                if resolved.get(child) is None and child in resolved:
                    total = None  # type: ignore[assignment]
                    break
                continue
            total = _sum_usage(total, child_total)  # type: ignore[arg-type]
        resolved[nid] = total
        return total

    for nid in list(forest.nodes):
        if nid not in resolved:
            subtree(nid, ())
    for nid, node in forest.nodes.items():
        node.subtree_usage = resolved.get(nid)
    return forest


def subtree_union(roots: list[str], forest: Forest,
                  ref: Optional[SourceRef] = None) -> tuple[TokenCounters, list[Finding]]:
    """Union usage across selected roots; each session counted exactly once."""
    findings: list[Finding] = []
    seen: set[str] = set()
    total = TokenCounters()

    def visit(nid: str) -> None:
        if nid in seen:
            return
        seen.add(nid)
        node = forest.nodes.get(nid)
        if node is None:
            findings.append(Finding("missing_child", {"referenced_id": nid}, ref))
            return
        total.input = _add(total.input, node.direct_usage.input)
        total.output = _add(total.output, node.direct_usage.output)
        total.reasoning = _add(total.reasoning, node.direct_usage.reasoning)
        total.cache_read = _add(total.cache_read, node.direct_usage.cache_read)
        total.cache_write = _add(total.cache_write, node.direct_usage.cache_write)
        for child in node.children:
            visit(child)

    requested = list(roots)
    if len(set(requested)) != len(requested):
        findings.append(Finding(
            "duplicate_membership",
            {"roots": requested,
             "reason": "same root selected more than once"}, ref))
    for root in dict.fromkeys(requested):
        visit(root)
    return total, findings
