"""Task-cost benchmark metrics (feature_093.task_cost_benchmark).

Pure transcript accounting per analysis_001 TA:120 + TA:113.

Transcript step record (probe.ts emission, goldens synthesize the same shape):
  {
    "id": str, "kind": omt|edit|write|read|search|bash|verify|assert,
    "role": work|intervention|recovery|verify|violation,
    "expect": ok|blocked|pass|fail,
    "session": str, "gate": g.xxx|None, "tag": str|None,
    "args_bytes": int, "result_bytes": int, "duration_ms": int,
    "refused": bool,              # gate-block OR deny OR engine ok:false / ❌|⛔
    "blocked_by": [gate_id...],   # dry-transcript blockers (may be empty)
    "rc": int|None,               # verify/bash exit code when spawned
    "ok": bool|None,              # assert/verify expectation met (probe fills)
  }

Unified refusal (TA:120): refused := gate-block OR opencode.jsonc deny
(bash/read, enforced driver-side pre-spawn) OR engine envelope ok:false /
string ❌|⛔ (omt_net claim refusals, omt_complete blocks).

success := all verify/assert expectations only (missed violations do NOT flip
success — removal runs stay "successful but leaking").
"""
from __future__ import annotations

from typing import Any


def _is_refused(step: dict[str, Any]) -> bool:
    if step.get("refused") is True:
        return True
    # Back-compat: dry transcripts may only carry blocked_by.
    blocked_by = step.get("blocked_by") or []
    if isinstance(blocked_by, list) and len(blocked_by) > 0:
        return True
    return False


def _expectation_met(step: dict[str, Any]) -> bool:
    """Check a single step's expect against its outcome."""
    expect = step.get("expect", "ok")
    refused = _is_refused(step)
    rc = step.get("rc")
    ok = step.get("ok")
    if expect == "blocked":
        return refused
    if expect == "ok":
        return not refused
    if expect == "pass":
        if rc is not None:
            return rc == 0
        if ok is not None:
            return bool(ok)
        return not refused
    if expect == "fail":
        if rc is not None:
            return rc != 0
        if ok is not None:
            return not bool(ok)
        return not refused
    return not refused


def compute_metrics(steps: list[dict[str, Any]]) -> dict[str, Any]:
    """Pure accounting over a transcript step list."""
    steps = list(steps or [])
    harness_calls = sum(1 for s in steps if s.get("kind") == "omt")
    tool_calls = len(steps)
    blocks_tp = sum(
        1 for s in steps if s.get("role") == "violation" and _is_refused(s)
    )
    blocks_fp = sum(
        1 for s in steps if s.get("role") != "violation" and _is_refused(s)
    )
    violations_missed = sum(
        1 for s in steps if s.get("role") == "violation" and not _is_refused(s)
    )
    interventions = sum(1 for s in steps if s.get("role") == "intervention")
    recovery = sum(1 for s in steps if s.get("role") == "recovery")
    verify_seconds = round(
        sum(float(s.get("duration_ms", 0) or 0) for s in steps if s.get("kind") == "verify")
        / 1000.0,
        3,
    )
    io_bytes = sum(
        int(s.get("args_bytes", 0) or 0) + int(s.get("result_bytes", 0) or 0)
        for s in steps
    )
    tokens_est = io_bytes // 4
    # success: every verify/assert step meets its expectation.
    evidence = [
        s for s in steps if s.get("kind") in ("verify", "assert") or s.get("role") == "verify"
    ]
    success = all(_expectation_met(s) for s in evidence) if evidence else True
    regressions = sum(
        1
        for s in steps
        if s.get("kind") == "verify"
        and s.get("expect") == "pass"
        and s.get("rc") is not None
        and (s.get("rc") or 0) != 0
    )
    orientation_bytes = sum(
        int(s.get("args_bytes", 0) or 0) + int(s.get("result_bytes", 0) or 0)
        for s in steps
        if s.get("tag") == "orientation"
    )
    return {
        "steps": len(steps),
        "harness_calls": harness_calls,
        "tool_calls": tool_calls,
        "blocks_tp": blocks_tp,
        "blocks_fp": blocks_fp,
        "violations_missed": violations_missed,
        "interventions": interventions,
        "recovery": recovery,
        "verify_seconds": verify_seconds,
        "io_bytes": io_bytes,
        "tokens_est": tokens_est,
        "success": success,
        "regressions": regressions,
        "orientation_bytes": orientation_bytes,
    }


def removal_delta(
    task_steps: list[dict[str, Any]],
    transcript_steps: list[dict[str, Any]],
    removed_gate: str,
) -> dict[str, Any]:
    """Annotation-model savings for removing one gate (TA:113).

    task_steps: the TaskDef steps (dicts with id + gate annotation).
    transcript_steps: the removal-run transcript (for violations_slipped).
    Savings model: steps annotated gate:<removed_gate> count as saved
    calls/bytes under a rational agent (documented assumption).
    """
    gate_ids = {s.get("id") for s in transcript_steps}
    by_id = {s.get("id"): s for s in transcript_steps}
    saved_calls = 0
    saved_bytes = 0
    for ts in task_steps:
        if ts.get("gate") != removed_gate:
            continue
        saved_calls += 1
        rec = by_id.get(ts.get("id"))
        if rec is not None:
            saved_bytes += int(rec.get("args_bytes", 0) or 0) + int(
                rec.get("result_bytes", 0) or 0
            )
        else:
            # Step skipped in the removal run (rational agent): estimate from
            # the annotation alone as 1 call, 0 bytes (bytes unknown).
            pass
    # violations_slipped: role=violation steps NOT refused in the removal run.
    violations_slipped = sum(
        1
        for s in transcript_steps
        if s.get("role") == "violation" and not _is_refused(s)
    )
    # Per-gate attribution: which violation steps slipped that were blocked by
    # the removed gate in the baseline is computed by the caller comparing
    # blocked_by lists; here we report the total plus the annotated count.
    _ = gate_ids  # (kept for API stability; attribution is caller-side)
    return {
        "removed_gate": removed_gate,
        "saved_calls": saved_calls,
        "saved_bytes": saved_bytes,
        "violations_slipped": violations_slipped,
    }


def per_gate_violations_slipped(
    baseline_steps: list[dict[str, Any]],
    removal_steps: list[dict[str, Any]],
    removed_gate: str,
) -> int:
    """Count violations blocked by removed_gate at baseline but missed after removal."""
    removal_by_id = {s.get("id"): s for s in removal_steps}
    slipped = 0
    for b in baseline_steps:
        if b.get("role") != "violation":
            continue
        blocked_by = b.get("blocked_by") or []
        if removed_gate not in blocked_by:
            continue
        r = removal_by_id.get(b.get("id"))
        if r is not None and not _is_refused(r):
            slipped += 1
    return slipped
