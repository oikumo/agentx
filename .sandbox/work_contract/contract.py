"""S3 thin work contract — read-only sidecar projection (feature_100).

Composes the mh8-shipped substrate without re-implementing it:
  072 policy_decision.ts  -> policy via vocabulary + durable/temp/consult split
  073 task_prep.ts        -> restrictions/next-action (block == preflight), risk, evidence
  092 resume digest       -> ≤2KB cap + continuation + detail-ref pointer pattern
  055/062 preflight.ts    -> SINGLE source for obligations (no second engine)

Pure stdlib, no ledger writes, no shell-outs, no network. Inputs are
caller-supplied dicts (seeded for the S3 demo; S4 wires live composition).
Renderer guarantees: ≤2048B default + required-continuation (never mid-sentence
cut); next_action + stale_or_unknown never dropped; the four required UNKNOWNs
(parity, proxies, C6, C1) always present; blocked == preflight would_block.
"""

from __future__ import annotations

import copy
import json

CONTRACT_CAP = 2048
CAP_MARKER = "… contract capped at 2048B — detail: {ref}"

REQUIRED_UNKNOWNS = [
    "dry/live report-parity: UNKNOWN (live evaluates all obligations per S2 F03; "
    "dry op:plan continues-all — block agrees, report shape may differ)",
    "cost: PROXY only (no host per-call token usage — tokens_est/io_bytes/delivered-bytes are proxies, not metered)",
    "C6: UNKNOWN Petri execution (lifecycle ops bypass transition relation — no execution guarantee claimed)",
    "C1: UNKNOWN replay durability (clear-before-record crash window open — do not depend on replay surviving it)",
]

ALLOWED_VERBS = ("clear ", "edit ", "run ", "consult ", "ask-user ")


def _trunc(s: str, n: int) -> str:
    s = str(s or "")
    return s if len(s) <= n else s[: n - 1] + "…"


def _bytes(s: str) -> int:
    return len(s.encode("utf-8"))


def build_contract(data: dict) -> dict:
    """Assemble the contract dict from caller-supplied parts (projection only)."""
    d = copy.deepcopy(data or {})
    request = d.get("request", {})
    scope = d.get("scope", {})
    obligations = d.get("obligations", {})
    next_action = d.get("next_action", {})
    evidence = list(d.get("required_evidence", None) or next_action.get("required_evidence", []) or [])
    stale = list(d.get("stale_or_unknown", []))
    refs = list(d.get("detail_refs", []))
    preflight = d.get("preflight", {})

    task = request.get("task", "UNKNOWN (no task text supplied)")
    acceptance = request.get("acceptance_refs", "UNKNOWN (no verify ref found)")
    if isinstance(acceptance, list) and not acceptance:
        acceptance = "UNKNOWN (no verify ref found)"

    completed = list(obligations.get("completed", []))
    unresolved = list(obligations.get("unresolved", []))
    would_block = int(preflight.get("would_block", len([u for u in unresolved])))
    first_blocker = preflight.get("first_blocker", None)
    if first_blocker is None:
        first_blocker = (unresolved[0].get("gate_id") if unresolved else None)

    action = str(next_action.get("action", ""))
    if not action.startswith(ALLOWED_VERBS):
        action = "ask-user UNKNOWN action verb — clarify: " + _trunc(action or "(empty)", 120)
    reason = str(next_action.get("reason", "UNKNOWN (no reason supplied)"))

    via = str(d.get("via", "defer_untyped"))
    if via not in ("activation_solo_skip", "exception_break_glass",
                    "deny_concurrent_no_grant", "defer_untyped"):
        via = "defer_untyped"

    # Required UNKNOWNs are structural — inject any the caller omitted.
    for req in REQUIRED_UNKNOWNS:
        key = req.split(":")[0]
        if not any(str(s).startswith(key) for s in stale):
            stale.append(req)

    candidate_id = scope.get("candidate_id") or (
        f"{scope.get('path', 'UNKNOWN')}@{scope.get('revision', 'UNKNOWN')}"
    )
    identity = scope.get("identity", "UNKNOWN (solo, no claim)")
    render_rev = str(scope.get("revision", "UNKNOWN"))
    dispatch_rev = str(scope.get("dispatch_revision", render_rev))
    if dispatch_rev != render_rev:
        stale.append(
            f"stale revision: rendered @{render_rev} but dispatch @{dispatch_rev} — "
            "re-render before acting (S4 rechecks at dispatch)"
        )

    return {
        "op": "work_contract",
        "request": {"task": _trunc(task, 280), "acceptance_refs": acceptance},
        "scope": {
            "path": str(scope.get("path", "UNKNOWN")),
            "tool": str(scope.get("tool", "edit")),
            "task_type": str(scope.get("task_type", "bug_fix")),
            "candidate_id": _trunc(candidate_id, 160),
            "revision": render_rev,
            "identity": _trunc(str(identity), 120),
        },
        "obligations": {"completed": completed, "unresolved": unresolved},
        "next_action": {
            "action": _trunc(action, 280),
            "reason": _trunc(reason, 280),
            "required_evidence": evidence,
        },
        "decision": {
            "blocked": would_block > 0,
            "first_blocker": first_blocker,
            "via": via,
        },
        "stale_or_unknown": stale,
        "detail_refs": refs,
        "note": str(d.get("note", "")),
    }


def render_text(c: dict, cap: int = CONTRACT_CAP) -> str:
    """Bounded text render. Drop order: detail_refs tail -> completed tail ->
    hard-cut with marker. next_action + stale_or_unknown never dropped."""
    c = copy.deepcopy(c)
    lines: list[str] = []

    def build() -> list[str]:
        req = c["request"]
        acc = req["acceptance_refs"]
        acc_s = "; ".join(acc) if isinstance(acc, list) else str(acc)
        out = [
            f"📋 WORK CONTRACT — {c['scope']['task_type']} {c['scope']['candidate_id']}",
            f"request: {_trunc(str(req['task']), 200)}",
            f"accept: {_trunc(acc_s, 200)}",
            f"scope: {c['scope']['path']} [{c['scope']['tool']}] id={c['scope']['identity']}",
            f"obligations: {len(c['obligations']['completed'])} done / "
            f"{len(c['obligations']['unresolved'])} open",
        ]
        for g in c["obligations"]["completed"]:
            out.append(f"  ✓ {g}")
        for u in c["obligations"]["unresolved"]:
            gid = u.get("gate_id", "?") if isinstance(u, dict) else str(u)
            clr = (u.get("clearing_action", "") if isinstance(u, dict) else "")
            out.append(f"  ✗ {gid} — clear: {_trunc(clr, 120)}")
        na = c["next_action"]
        out.append(f"next: {na['action']}")
        out.append(f"why: {na['reason']}")
        out.append(f"evidence: {'; '.join(na['required_evidence']) or 'UNKNOWN'}")
        out.append(
            f"decision: {'BLOCKED' if c['decision']['blocked'] else 'CLEAR'}"
            + (f" first={c['decision']['first_blocker']}" if c["decision"]["first_blocker"] else "")
            + f" via={c['decision']['via']}"
        )
        out.append("stale-or-unknown:")
        for s in c["stale_or_unknown"]:
            out.append(f"  ? {s}")
        if c["detail_refs"]:
            out.append("refs:")
            for r in c["detail_refs"]:
                out.append(f"  → {r}")
        if c["note"]:
            out.append(f"note: {c['note']}")
        return out

    lines = build()
    text = "\n".join(lines)
    if _bytes(text) <= cap:
        return text
    # Drop detail_refs tail first (keep at least the continuation pointer).
    while c["detail_refs"] and _bytes(text) > cap:
        c["detail_refs"] = c["detail_refs"][:-1]
        lines = build()
        first_ref = "detail: contract projection (refs dropped to fit cap)"
        text = "\n".join(lines)
        if not c["detail_refs"]:
            text = text + f"\n{CAP_MARKER.format(ref=first_ref)}"
            break
    # Then completed tail (unresolved + next + unknowns are load-bearing).
    while c["obligations"]["completed"] and _bytes(text) > cap:
        c["obligations"]["completed"] = c["obligations"]["completed"][:-1]
        lines = build()
        text = "\n".join(lines) + f"\n{CAP_MARKER.format(ref='completed-list truncated to fit cap')}"
    # Hard-cut on a line boundary (never mid-sentence): drop whole trailing lines.
    if _bytes(text) > cap:
        kept = []
        for ln in text.split("\n"):
            trial = "\n".join(kept + [ln])
            if _bytes(trial) > cap - _bytes("\n" + CAP_MARKER.format(ref="see detail refs")):
                break
            kept.append(ln)
        text = "\n".join(kept) + f"\n{CAP_MARKER.format(ref='see detail refs')}"
    return text


def check_invariants(c: dict, raw: dict) -> list[str]:
    """S3 invariants: block == preflight, verb closed, UNKNOWNs present."""
    problems: list[str] = []
    unresolved = c["obligations"]["unresolved"]
    pre = raw.get("preflight", {})
    expect_blocked = int(pre.get("would_block", len(unresolved))) > 0
    if c["decision"]["blocked"] != expect_blocked:
        problems.append("blocked != preflight.would_block")
    expect_first = pre.get("first_blocker", (unresolved[0].get("gate_id") if unresolved else None))
    if c["decision"]["first_blocker"] != expect_first:
        problems.append("first_blocker != preflight.first_blocker")
    if not c["next_action"]["action"].startswith(ALLOWED_VERBS + ("ask-user UNKNOWN",)):
        problems.append("next_action verb outside closed set")
    for req in REQUIRED_UNKNOWNS:
        if not any(str(s).startswith(req.split(":")[0]) for s in c["stale_or_unknown"]):
            problems.append(f"missing required UNKNOWN: {req.split(':')[0]}")
    if not c["stale_or_unknown"]:
        problems.append("stale_or_unknown empty (unknown must stay unknown, never dropped)")
    return problems


DEMO_A = {
    "request": {
        "task": "Fix null-check crash in session summary formatter",
        "acceptance_refs": ["tests/test_session_summary.py::test_null_summary"],
    },
    "scope": {
        "path": "src/agentx/session/summary.py",
        "tool": "edit",
        "task_type": "bug_fix",
        "revision": "3490fd5",
        "identity": "UNKNOWN (solo, no claim)",
    },
    "obligations": {
        "completed": ["g.nav: consulted via omt_nav quick_ref", "g.kb: consulted (no surface match)"],
        "unresolved": [],
    },
    "next_action": {
        "action": "edit src/agentx/session/summary.py with edit, then validate",
        "reason": "no blockers — preflight 0 would-block; low risk (no contracts/auth/boundary signals)",
        "required_evidence": ["repro/behavioral test for the fix", "targeted suite green, no new MVC hard violations"],
    },
    "preflight": {"would_block": 0, "first_blocker": None},
    "via": "activation_solo_skip",
    "detail_refs": [
        "WORK.md Tasks menu (pool 0/0/7)",
        ".opencode/lib/enforcer/task_prep.ts:116 (block == preflight)",
        ".opencode/lib/enforcer/preflight.ts:103 (projection core)",
    ],
}

DEMO_B = {
    "request": {
        "task": "Resume interrupted gate_driver repair follow-up",
        "acceptance_refs": ["test_omt_enforcer_guard_source_pins.py (32 pins)"],
    },
    "scope": {
        "path": ".opencode/lib/enforcer/gate_driver.ts",
        "tool": "edit",
        "task_type": "bug_fix",
        "revision": "f1be918",
        "dispatch_revision": "3490fd5",
        "identity": "UNKNOWN (solo, no claim)",
    },
    "obligations": {
        "completed": ["g.nav: consulted", "g.phase: feature_100 Analysis declared"],
        "unresolved": [
            {"gate_id": "g.receipt", "clearing_action": "refresh e2e receipt (one edit/file/round)"},
            {"gate_id": "g.tests", "clearing_action": 'omt_skip{scope:"tests", reason:"canary"}'},
        ],
    },
    "next_action": {
        "action": "clear g.receipt: refresh e2e receipt (one edit/file/round)",
        "reason": "first blocker (would_block=2); harness surface needs staged receipt",
        "required_evidence": [
            "repro test for the fix",
            "targeted suite green, no new MVC violations",
            "KB consult for touched surface",
            "e2e receipt (harness surface)",
        ],
    },
    "preflight": {"would_block": 2, "first_blocker": "g.receipt"},
    "via": "activation_solo_skip",
    "detail_refs": [
        "gate_driver.ts:342-361 (S2 F03 live evaluates all)",
        "policy_decision.ts:138 (ONE evaluator)",
        "feature_099 test_report.md (allow/deny matrix)",
        "CURRENT_STATE.md newest entry (session trail)",
    ],
}


def main() -> int:
    for name, raw in (("demo_a_routine_fix", DEMO_A), ("demo_b_interrupted_resumed", DEMO_B)):
        c = build_contract(raw)
        problems = check_invariants(c, raw)
        text = render_text(c)
        blob = json.dumps(c, indent=1, ensure_ascii=False)
        print(f"== {name}: {len(text.encode())}B text / {len(blob.encode())}B json "
              f"blocked={c['decision']['blocked']} first={c['decision']['first_blocker']}")
        assert _bytes(text) <= CONTRACT_CAP, f"{name} text over cap"
        assert not problems, f"{name} invariants: {problems}"
        # Orient-from-projection-alone: next action + evidence + unknowns survive the cap.
        assert c["next_action"]["action"] in text
        for req in REQUIRED_UNKNOWNS:
            assert req.split(":")[0] in text, f"{name} dropped {req.split(':')[0]}"
    print("S3 projection OK: 2/2 demos orient from projection alone, cap + invariants hold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
