"""collect.py — snapshot -> normalize -> bind -> trial report (feature_131).

Slice-1 pipeline entry: binds label lines in selected sessions to trials,
classifies usable vs excluded trials with reasons, and attaches per-trial
usage from the bound sessions' cumulative counters. Manifest-bound
validation (collect/validate/compare) lands in slice 4; `manifest` is
accepted and recorded but not enforced here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .labels import LabelBinding, TrialIdentity, bind_labels
from .normalize import normalize_snapshot
from .schema import Finding, SessionRecord, SourceRef, TokenCounters

_COMPONENTS = ("input", "output", "reasoning", "cache_read", "cache_write")


@dataclass
class TrialEntry:
    """One bound trial as seen by the pipeline."""

    identity: Optional[TrialIdentity] = None
    outcome: Optional[str] = None
    complete: bool = False
    usable: bool = False
    exclusions: list[str] = field(default_factory=list)
    session_ids: list[str] = field(default_factory=list)
    usage: Optional[dict[str, Any]] = None


@dataclass
class TrialReport:
    trials: dict[str, TrialEntry] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    echoes: list[dict[str, Any]] = field(default_factory=list)
    coverage: dict[str, Any] = field(default_factory=dict)


def _trial_usage(sessions: dict[str, SessionRecord],
                 session_ids: list[str]) -> Optional[dict[str, Any]]:
    totals: dict[str, int] = {}
    seen_any = False
    for sid in session_ids:
        rec = sessions.get(sid)
        if rec is None or rec.tokens is None:
            continue
        for comp in _COMPONENTS:
            val = getattr(rec.tokens, comp)
            if val is not None:
                totals[comp] = totals.get(comp, 0) + val
                seen_any = True
    return totals if seen_any else None


def collect_trials(adapter: Any, selector: Any, *, manifest: Any = None,
                   run_mapping: Optional[dict[str, Any]] = None) -> TrialReport:
    """Run the slice-1 collection pipeline over a bounded selection."""
    snapshot = adapter.snapshot(selector)
    normalized = normalize_snapshot(snapshot)
    binding: LabelBinding = bind_labels(
        {"sessions": normalized["sessions"],
         "messages": normalized["messages"],
         "parts": normalized["parts"],
         "coverage": snapshot.get("coverage", {})},
        manifest=manifest, run_mapping=run_mapping)

    by_session = {s.id: s for s in normalized["sessions"]}
    entries: dict[str, TrialEntry] = {}
    labeled: set[str] = set()
    for trial_id, trial in binding.trials.items():
        usage = _trial_usage(by_session, trial.session_ids)
        exclusions: list[str] = []
        if not trial.has_start:
            exclusions.append("trial_incomplete")
        if not trial.complete:
            exclusions.append("trial_incomplete")
        entry = TrialEntry(
            identity=trial.identity, outcome=trial.outcome,
            complete=trial.complete, usable=not exclusions,
            exclusions=sorted(set(exclusions)),
            session_ids=list(trial.session_ids), usage=usage)
        entries[trial_id] = entry
        if trial.session_ids:
            labeled.update(trial.session_ids)

    base_coverage = dict(snapshot.get("coverage", {}))
    usable = sum(1 for e in entries.values() if e.usable)
    report = TrialReport(
        trials=entries,
        findings=list(normalized.get("findings", ())) + list(binding.findings),
        echoes=list(binding.echoes),
        coverage={**base_coverage,
                  "n_trials": len(entries),
                  "n_labeled_sessions": len(labeled),
                  "n_usable_trials": usable})
    return report
