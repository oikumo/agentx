"""Benchmark report rendering (feature_093.task_cost_benchmark).

Markdown + stable-schema JSON + assumptions + FINDINGS. Pure; no I/O.
"""
from __future__ import annotations

from typing import Any

ASSUMPTIONS = [
    "scripted deterministic agent (not a live LLM) — measures harness interaction cost, not model reasoning cost; steps modeled on recent real features (087/091/092 ceremony shapes)",
    "bash/read denies enforced by opencode core are re-evaluated from the same opencode.jsonc rules text",
    "removal savings assume a rational agent skips ceremony for a removed gate (annotation model)",
    "session bootstrap + thought-injection bytes counted on first result per session (real hook behavior replicated in-probe)",
    "two-hats skip-shadowing (TA:112c): after omt_skip{scope:tests} the skip shadows the tdd phase record so the impl edit and g.tdd_after run un-two-hatted — recorded as FINDING, not failure",
    "net fire receipt is session-agnostic (TA:119); concurrent order is A claim → B double-claim → B no-work_start edit → B stale-rev claim → A fire → A edit → A checkpoint",
    "g.think consult order (TA:124): B think-consults net/state.py before the no-work_start edit, else the g.net removal slip is masked",
]

FINDINGS_STATIC = [
    "two-hats shadow-off: impl edit between red and green runs un-two-hatted after the RED-bootstrap canary skip (reality, not theory)",
    "worktree baseline: fresh pinned-rev worktrees have no .opencode/node_modules so the tdd baseline full-suite run carries pre-existing bun-import failures (lands in baseline_failures)",
]


def _row(task_id: str, m: dict[str, Any]) -> str:
    return (
        f"| {task_id} | {m.get('steps', 0)} | {m.get('harness_calls', 0)} "
        f"| {m.get('blocks_tp', 0)}/{m.get('blocks_fp', 0)}/{m.get('violations_missed', 0)} "
        f"| {m.get('interventions', 0)}/{m.get('recovery', 0)} "
        f"| {m.get('verify_seconds', 0)} | {m.get('io_bytes', 0)} "
        f"| {m.get('tokens_est', 0)} | {'✅' if m.get('success') else '❌'} "
        f"| {m.get('regressions', 0)} |"
    )


def render_markdown(
    per_task: dict[str, dict[str, Any]],
    removal: dict[str, dict[str, Any]] | None = None,
    findings: list[str] | None = None,
    revision: str = "",
) -> str:
    lines: list[str] = []
    lines.append("# Task-cost benchmark — first numbers")
    lines.append("")
    if revision:
        lines.append(f"Pinned rev: `{revision}`")
        lines.append("")
    lines.append(
        "| task | steps | harness_calls | TP/FP/missed | interv/recov "
        "| verify_s | io_bytes | tokens_est | success | regr |"
    )
    lines.append(
        "|---|---|---|---|---|---|---|---|---|---|"
    )
    for task_id in sorted(per_task):
        lines.append(_row(task_id, per_task[task_id]))
    totals = _total(per_task)
    lines.append(_row("TOTAL", totals))
    lines.append("")
    if removal:
        lines.append("## Gate-removal experiments (annotation model)")
        lines.append("")
        lines.append("| gate | saved_calls | saved_bytes | violations_slipped |")
        lines.append("|---|---|---|---|")
        for gate in sorted(removal):
            r = removal[gate]
            lines.append(
                f"| {gate} | {r.get('saved_calls', 0)} "
                f"| {r.get('saved_bytes', 0)} "
                f"| {r.get('violations_slipped', 0)} |"
            )
        lines.append("")
    lines.append("## Assumptions")
    lines.append("")
    for a in ASSUMPTIONS:
        lines.append(f"- {a}")
    lines.append("")
    lines.append("## FINDINGS")
    lines.append("")
    for f in list(FINDINGS_STATIC) + list(findings or []):
        lines.append(f"- {f}")
    lines.append("")
    return "\n".join(lines)


def _total(per_task: dict[str, dict[str, Any]]) -> dict[str, Any]:
    total: dict[str, Any] = {
        "steps": 0,
        "harness_calls": 0,
        "tool_calls": 0,
        "blocks_tp": 0,
        "blocks_fp": 0,
        "violations_missed": 0,
        "interventions": 0,
        "recovery": 0,
        "verify_seconds": 0.0,
        "io_bytes": 0,
        "tokens_est": 0,
        "success": True,
        "regressions": 0,
        "orientation_bytes": 0,
    }
    for m in per_task.values():
        for k in (
            "steps",
            "harness_calls",
            "tool_calls",
            "blocks_tp",
            "blocks_fp",
            "violations_missed",
            "interventions",
            "recovery",
            "io_bytes",
            "tokens_est",
            "regressions",
            "orientation_bytes",
        ):
            v = m.get(k, 0)
            total[k] = total[k] + (0 if v is None else int(v))
        vs = m.get("verify_seconds", 0.0)
        total["verify_seconds"] = round(float(total["verify_seconds"]) + float(vs or 0.0), 3)
        if not m.get("success", True):
            total["success"] = False
    return total


def render_json(
    per_task: dict[str, dict[str, Any]],
    removal: dict[str, dict[str, Any]] | None = None,
    findings: list[str] | None = None,
    revision: str = "",
    manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema": "bench_first_numbers.v1",
        "revision": revision,
        "per_task": per_task,
        "totals": _total(per_task),
        "removal": removal or {},
        "assumptions": list(ASSUMPTIONS),
        "findings": list(FINDINGS_STATIC) + list(findings or []),
        "manifest": manifest or {},
    }
