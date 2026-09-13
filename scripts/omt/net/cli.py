"""omt_net CLI — feature_039.adaptive_net_engine + feature_040.net_composition_supervisor
+ feature_042.goal_net_synthesis + feature_044.mined_behavioral_net.

Single tool, closed op enum (IDEA-002 v4 §5.0, PROJECT.md D10 + D7-gated
phase-2 extension at 044):

    probe|fire|invariant   feature_039 (observe / marking-only fire / drift)
    splice|sync            feature_040 (structural transactions + net↔reality)
    claim|release|transfer|checkpoint  feature_080 (task claim + generation fencing, T5-2 2B)
    + feature_081 (workspace stamp + managed gate, T5-3 2C)
    synthesize             feature_042 (goal→net template proposal, D4)
    mine                   feature_044 (ledger→net behavioral draft, D4)

Contract (tests/scripts/omt/test_net_{cli,splice,sync,synthesize}.py ARE the
spec): one JSON envelope on stdout, exit 0 ok / 1 error; bootstrap ordering
§5.1 — probe/fire/invariant/synthesize fail clean with net_not_bootstrapped
until the bundle exists (sync is the first-call entry point). `fire` is
marking-only (no conformance regression, §5.0 matrix); splice (all modes) +
sync bootstrap run the 9-vector conformance gate pre-save; proposal-only sync
stays read-only (D4 — the agent applies proposals via splice). `synthesize`
is proposal-only (D4 — the agent applies the fragment via splice, which runs
the gate + D20 cap check). `invariant` folds the old `drift` op — net-vs-ledger
revision drift is surfaced (exit stays 0) and logged to
harness.net.drift.jsonl (D7).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import state
from .analysis import PetriNetAnalyzer
from .errors import (
    PetriNetError,
    TransitionNotEnabledError,
    UnknownTransitionError,
)
from .lock import LockError

RESERVED_OPS: tuple[str, ...] = ()
# TA: xref: feature_042 (goal_net_synthesis): RESERVED_OPS emptied — synthesize
# is live (template proposal, D4/D20 pool-aware, reuses --mutation/--feature).
# TA: xref: feature_041 (pause_2026-08-30d.md R4): _invariant envelope gains ADDITIVE resources[] (per catalog place: capacity/live/capacity_ok/holders — holders for agent_attention = subnets with f{N}_active marked) + conflicts[] (pending subnets whose f{N}_start is not enabled, blocked_by = empty unprefixed input places) via state.resource_report(st) — the D7 omt_complete exit hook then surfaces capacity conflicts mechanically; additive keys only (test_net_cli.py exact-shape risk).
# TA: xref: feature_040 (pause_2026-08-30c.md): splice args --mode add|remove|disable|undo|repair --mutation '<json>' --subnet --reasoning; sync bootstraps supervisor skeleton (feature_ready=1, resource_token=1, goal_satisfied=0, NO supervisor transitions v1) then emits PROPOSAL only (D4 — agent applies via splice).
DEFAULT_MAX_STATES = 1000


def _emit(envelope: dict[str, Any], code: int) -> int:
    print(json.dumps(envelope, ensure_ascii=False))
    return code


def _error(code_str: str, op: str, message: str = "") -> tuple[dict[str, Any], int]:
    envelope: dict[str, Any] = {"ok": False, "error": code_str, "op": op}
    if message:
        envelope["message"] = message
    return envelope, 1


# feature_064.named_work_truthful_observation (slice 1): task-bound
# observation over the pool engine. Additive envelope keys only — existing
# keys stay byte-identical (test_net_cli.py key-access pins).
_TASK_ACTION = {
    "work_pending": "implement",
    "work_active": "verify",
    "work_done": "review",
}
_TASK_PLACE_ORDER = ("work_pending", "work_active", "work_done")


def _named_task_actions(bindings: list[dict[str, Any]]) -> list[str]:
    by_place: dict[str, list[str]] = {}
    for b in bindings:
        if isinstance(b, dict) and isinstance(b.get("id"), str):
            by_place.setdefault(str(b.get("place")), []).append(b["id"])
    actions: list[str] = []
    for place in _TASK_PLACE_ORDER:
        for bid in sorted(by_place.get(place, [])):
            actions.append(f"{_TASK_ACTION[place]} {bid}")
    return actions


def _start_blockers(st: Any) -> list[str]:
    """Unmarked input places of work_start (pool nets); [] when n/a."""
    try:
        inputs = st.net.inputs.get("work_start", [])
    except AttributeError:
        return []
    return [p for p in inputs if st.live_marking.get(p, 0) == 0]


def _task_observation(
    st: Any, validation: dict[str, Any], enabled: list[str]
) -> dict[str, Any]:
    counts = state.pool_counts(st.live_marking)
    errors = list(validation.get("errors", []))
    rev = st.revision
    if errors:
        return {
            "state": "inconsistent",
            "reason": "; ".join(errors),
            "revision": rev,
            "basis": f"live_marking rev {rev}",
        }
    pending, active, done = (
        counts.get("work_pending", 0),
        counts.get("work_active", 0),
        counts.get("work_done", 0),
    )
    if active > 0:
        return {
            "state": "executing",
            "reason": f"work_active={active} (agent attention committed)",
            "revision": rev,
            "basis": f"live_marking rev {rev}",
        }
    if pending > 0:
        if "work_start" in enabled:
            return {
                "state": "ready",
                "reason": f"work_pending={pending}, work_start enabled",
                "revision": rev,
                "basis": f"live_marking rev {rev}",
            }
        blockers = _start_blockers(st)
        detail = f" blocked by {','.join(blockers)}" if blockers else ""
        return {
            "state": "awaiting_capacity",
            "reason": f"work_pending={pending}, work_start not enabled{detail}",
            "revision": rev,
            "basis": f"live_marking rev {rev}",
        }
    if done > 0:
        return {
            "state": "drained_complete",
            "reason": f"done={done} (no pending/active work)",
            "revision": rev,
            "basis": f"live_marking rev {rev}",
        }
    return {
        "state": "idle_empty",
        "reason": "no pending/active/done work",
        "revision": rev,
        "basis": f"live_marking rev {rev}",
    }


def _task_menu(
    st: Any, bindings: list[dict[str, Any]], enabled: list[str]
) -> dict[str, Any]:
    actions = _named_task_actions(bindings)
    ordered_enabled = sorted(enabled)
    if actions:
        nxt = actions[0]
        other = actions[1:] + ordered_enabled
    else:
        nxt = ordered_enabled[0] if ordered_enabled else "none"
        other = ordered_enabled[1:]
    blocked: list[dict[str, Any]] = []
    if "work_start" not in enabled and any(
        isinstance(b, dict) and b.get("place") == "work_pending" for b in bindings
    ):
        blockers = _start_blockers(st)
        for b in bindings:
            if isinstance(b, dict) and b.get("place") == "work_pending":
                blocked.append(
                    {"action": f"implement {b.get('id')}", "blocked_by": blockers}
                )
    for b in bindings:
        if isinstance(b, dict) and b.get("block_reason"):
            blocked.append(
                {"action": f"{b.get('id')}", "blocked_by": [b.get("block_reason")]}
            )
    try:
        rep = state.resource_report(st)
        resources = {
            "free": sum(1 for r in rep.get("resources", []) if r.get("capacity_ok")),
            "total": len(rep.get("resources", [])),
        }
    except Exception:
        resources = {"free": 0, "total": 0}
    # feature_082 (T5-4 2D): additive parallel offer + worker capacity view
    # (existing keys untouched — test_net_cli exact-shape risk). Pending
    # tasks refused by capacity/scope surface here with stable reason codes.
    try:
        _cap_total = int(getattr(state, "WORKER_SLOTS_CAPACITY", 2) or 2)
    except Exception:
        _cap_total = 2
    try:
        _active_bs = [
            b
            for b in bindings
            if isinstance(b, dict) and b.get("place") == "work_active"
        ]
        _used = len(_active_bs)
    except Exception:
        _used = 0
        _active_bs = []
    try:
        _parallel = list(state.eligible_parallel_tasks(st, limit=2))
    except Exception:
        _parallel = []
    try:
        for b in bindings:
            if not isinstance(b, dict) or b.get("place") != "work_pending":
                continue
            _bid = b.get("id")
            if _used >= _cap_total:
                blocked.append(
                    {
                        "action": f"implement {_bid}",
                        "blocked_by": ["worker_capacity_exhausted"],
                    }
                )
                continue
            try:
                _blk = state._scope_conflict_with_active(_active_bs, b.get("scope", []))
            except Exception:
                _blk = None
            if _blk is not None:
                blocked.append(
                    {
                        "action": f"implement {_bid}",
                        "blocked_by": [f"scope_conflict:{_blk}"],
                    }
                )
    except Exception:
        pass
    # feature_083 (T5-5 3A): additive lane occupancy (existing keys untouched).
    try:
        _verifying = sum(1 for b in bindings if isinstance(b, dict) and b.get("place") == "work_verifying")
        _ready = sum(1 for b in bindings if isinstance(b, dict) and b.get("place") == "work_integration_ready")
        _integrating = sum(1 for b in bindings if isinstance(b, dict) and b.get("place") == "work_integrating")
    except Exception:
        _verifying, _ready, _integrating = 0, 0, 0
    return {
        "next": nxt,
        "other_enabled": other,
        "blocked": blocked,
        "resources": resources,
        "parallel": _parallel,
        "capacity": {
            "workers_used": _used,
            "workers_total": _cap_total,
            "free": max(0, _cap_total - _used),
        },
        "verification": {"used": _verifying, "total": 1, "free": max(0, 1 - _verifying)},
        "integration": {"used": _integrating, "ready": _ready, "total": 1, "free": max(0, 1 - _integrating)},
    }


def _probe(base: Path, max_states: int) -> tuple[dict[str, Any], int]:
    st = state.load(base)
    analyzer = PetriNetAnalyzer(st.net)
    live_tuple = tuple(st.live_marking[p] for p in st.net.place_order)
    deadlocks = analyzer.deadlocks(max_states=max_states)
    bounds = analyzer.bounds(max_states=max_states)
    envelope = {
        "ok": True,
        "op": "probe",
        "revision": st.revision,
        "marking": st.live_marking,
        "enabled": st.net.enabled_transitions_at(live_tuple),
        "advice": {
            "deadlocks": [list(m) for m in deadlocks.deadlocks],
            "deadlocks_complete": deadlocks.complete,
            "bounded": bounds.bounded,
            "bounds": bounds.bounds,
            "place_invariants": [list(v) for v in analyzer.place_invariants()],
            "transition_invariants": [
                list(v) for v in analyzer.transition_invariants()
            ],
            "max_states": max_states,
            "basis": (
                f"initial-marking analysis (≤{max_states} states), not a "
                "claim about the live marking"
            ),
        },
    }
    bindings = list(getattr(st, "task_bindings", []) or [])
    validation = state.validate_task_bindings(bindings, st.live_marking)
    enabled_list = list(envelope["enabled"])
    envelope["tasks"] = bindings
    envelope["bindings_valid"] = validation["ok"]
    envelope["binding_errors"] = list(validation["errors"])
    envelope["coverage"] = {
        place: dict(numbers)
        for place, numbers in validation["per_place"].items()
    }
    envelope["observation"] = _task_observation(st, validation, enabled_list)
    envelope["menu"] = _task_menu(st, bindings, enabled_list)
    return envelope, 0


def _fire(base: Path, transition: str, reasoning: str, session: str, expected_revision: int | None = None, command_id: str | None = None) -> tuple[dict[str, Any], int]:
    st = state.fire(base, transition, reasoning=reasoning, session=session, expected_revision=expected_revision, command_id=command_id)
    envelope = {
        "ok": True,
        "op": "fire",
        "revision": st.revision,
        "marking": st.live_marking,
    }
    return envelope, 0


# feature_080.task_claim_generation (T5-2 2B): thin envelopes over the
# claim/release/transfer/checkpoint transactions in state.py. The `task`
# block reports the post-commit binding so workers learn their generation
# without a follow-up probe.
def _task_envelope(op: str, st: Any, task_id: str) -> dict[str, Any]:
    b = next(
        (
            x
            for x in (st.task_bindings or [])
            if isinstance(x, dict) and x.get("id") == task_id
        ),
        {},
    )
    return {
        "ok": True,
        "op": op,
        "revision": st.revision,
        "marking": st.live_marking,
        "task": {
            "id": task_id,
            "place": b.get("place"),
            "owner": b.get("owner"),
            "generation": b.get("generation", 0),
            "workspace": b.get("workspace"),
        },
    }


def _claim(base: Path, args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    st = state.claim_task(
        base,
        args.task_id,
        owner=args.owner or args.session or "context",
        session=args.session,
        expected_revision=getattr(args, "expected_revision", None),
        command_id=getattr(args, "command_id", None) or None,
    )
    return _task_envelope("claim", st, args.task_id), 0


def _release(base: Path, args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    st = state.release_task(
        base,
        args.task_id,
        owner=args.owner or None,
        session=args.session,
        expected_revision=getattr(args, "expected_revision", None),
        command_id=getattr(args, "command_id", None) or None,
    )
    return _task_envelope("release", st, args.task_id), 0


def _transfer(base: Path, args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    st = state.transfer_task(
        base,
        args.task_id,
        owner=args.owner or args.session or "context",
        session=args.session,
        expected_revision=getattr(args, "expected_revision", None),
        command_id=getattr(args, "command_id", None) or None,
    )
    return _task_envelope("transfer", st, args.task_id), 0


def _checkpoint(
    base: Path,
    task_id: str,
    generation: int,
    checkpoint: Any,
    results: Any,
    head_commit: Any,
    patch_digest: Any,
    session: str,
    expected_revision: int | None,
    command_id: str | None,
) -> tuple[dict[str, Any], int]:
    st = state.checkpoint_task(
        base,
        task_id,
        generation=generation,
        checkpoint=checkpoint,
        results=results,
        head_commit=head_commit,
        patch_digest=patch_digest,
        session=session,
        expected_revision=expected_revision,
        command_id=command_id,
    )
    return _task_envelope("checkpoint", st, task_id), 0


# feature_084.recovery_and_transaction_journal (T5-6 3B): thin envelopes over
# heartbeat_task / recover_task / reconcile_transactions in state.py.
# CLI-only in this slice (no omt_net plugin exposure — tool budgets ~99%
# full, the T1-6/083 precedent: harnessc CLI subcommand over a new tool).
def _heartbeat(base: Path, args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    st = state.heartbeat_task(
        base,
        args.task_id,
        generation=args.generation,
        session=args.session,
        expected_revision=getattr(args, "expected_revision", None),
        command_id=getattr(args, "command_id", None) or None,
    )
    return _task_envelope("heartbeat", st, args.task_id), 0


def _recover(base: Path, args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    st = state.recover_task(
        base,
        args.task_id,
        owner=args.owner or args.session or "context",
        session=args.session,
        expected_revision=getattr(args, "expected_revision", None),
        command_id=getattr(args, "command_id", None) or None,
    )
    return _task_envelope("recover", st, args.task_id), 0


def _reconcile(base: Path, args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    outcome = state.reconcile_transactions(base, session=args.session)
    status = str(outcome.get("status", "diagnosis"))
    if status == "clean":
        return {"ok": True, "op": "reconcile", "status": status}, 0
    if status in ("recovered_aborted", "recovered_committed"):
        return {"ok": True, "op": "reconcile", **outcome}, 0
    return {"ok": False, "op": "reconcile", "error": str(outcome.get("code", "txn_diverged")), "message": str(outcome.get("message", "")), "status": status}, 1


# feature_083.verification_integration_lane (T5-5 3A): thin envelopes over the
# submit/verify/integrate_start/integrate_finish transactions in state.py.
# CLI-only in this slice (no omt_net plugin exposure — tool budgets ~99%
# full, the T1-6 precedent: harnessc CLI subcommand over a new tool).
# `mutation` carries the result/evidence JSON (checkpoint precedent);
# verify/integrate are coordinator-only (--coordinator).
def _submit(base: Path, args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    payload: dict[str, Any] = {}
    if getattr(args, "mutation", ""):
        try:
            payload = json.loads(args.mutation)
        except json.JSONDecodeError as exc:
            return _emit(*_error(
                "invalid_mutation", "submit", f"--mutation is not valid JSON: {exc}"
            ))
    if not isinstance(payload, dict):
        return _emit(*_error("invalid_mutation", "submit", "--mutation must be a JSON object"))
    st = state.submit_result(
        base,
        args.task_id,
        generation=args.generation,
        owner=getattr(args, "owner", "") or None,
        result=payload,
        session=args.session,
        expected_revision=getattr(args, "expected_revision", None),
        command_id=getattr(args, "command_id", None) or None,
    )
    return _task_envelope("submit", st, args.task_id), 0


def _verify(base: Path, args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    st = state.verify_result(
        base,
        args.task_id,
        generation=args.generation,
        verdict=args.verdict,
        coordinator=bool(getattr(args, "coordinator", False)),
        detail=getattr(args, "detail", "") or "",
        session=args.session,
        expected_revision=getattr(args, "expected_revision", None),
        command_id=getattr(args, "command_id", None) or None,
    )
    return _task_envelope("verify", st, args.task_id), 0


def _integrate_start(base: Path, args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    st = state.integrate_start(
        base,
        args.task_id,
        generation=args.generation,
        coordinator=bool(getattr(args, "coordinator", False)),
        session=args.session,
        expected_revision=getattr(args, "expected_revision", None),
        command_id=getattr(args, "command_id", None) or None,
    )
    return _task_envelope("integrate_start", st, args.task_id), 0


def _integrate_finish(base: Path, args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    st = state.integrate_finish(
        base,
        args.task_id,
        generation=args.generation,
        verdict=args.verdict,
        coordinator=bool(getattr(args, "coordinator", False)),
        detail=getattr(args, "detail", "") or "",
        session=args.session,
        expected_revision=getattr(args, "expected_revision", None),
        command_id=getattr(args, "command_id", None) or None,
    )
    return _task_envelope("integrate_finish", st, args.task_id), 0


def _splice(base: Path, args: argparse.Namespace, mutation: Any) -> tuple[dict[str, Any], int]:
    st, info = state.splice(
        base,
        args.mode,
        mutation=mutation,
        subnet=args.subnet,
        reasoning=args.reasoning,
        session=args.session,
        feature=args.feature,
        expected_revision=getattr(args, "expected_revision", None),
        command_id=getattr(args, "command_id", None) or None,
    )
    envelope = {
        "ok": True,
        "op": "splice",
        "mode": args.mode,
        "revision": st.revision,
        "marking": st.live_marking,
        **info,
    }
    return envelope, 0


def _sync(base: Path, args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    work_md = getattr(args, "work_md", "")
    if work_md:
        import os as _os

        _os.environ["OMT_NET_WORK_MD"] = work_md
    st, info = state.sync(
        base,
        reasoning=args.reasoning,
        session=args.session,
        direction=getattr(args, "direction", "proposal"),
        dry_run=getattr(args, "dry_run", False),
    )
    envelope: dict[str, Any] = {
        "ok": True,
        "op": "sync",
        "bootstrap": info["bootstrap"],
        "revision": st.revision,
        "proposal": info["proposal"],
    }
    if info.get("conformance") is not None:
        envelope["conformance"] = info["conformance"]
    if info.get("rendered") is not None:
        envelope["rendered"] = info["rendered"]
    if info.get("proposals") is not None:
        envelope["proposals"] = info["proposals"]
    return envelope, 0


def _synthesize(base: Path, args: argparse.Namespace, goal: Any) -> tuple[dict[str, Any], int]:
    st, info = state.synthesize(
        base,
        goal,
        reasoning=args.reasoning,
        session=args.session,
        feature=args.feature,
    )
    envelope: dict[str, Any] = {
        "ok": True,
        "op": "synthesize",
        "revision": st.revision,
        "applied": info["applied"],
        "pool_net": info["pool_net"],
        "prefix": info["prefix"],
        "fragment": info["fragment"],
        "places_after": info["places_after"],
        "would_exceed_cap": info["would_exceed_cap"],
    }
    return envelope, 0


def _mine(base: Path, args: argparse.Namespace, params: Any) -> tuple[dict[str, Any], int]:
    st, info = state.mine(
        base,
        params,
        reasoning=args.reasoning,
        session=args.session,
        feature=args.feature,
    )
    envelope: dict[str, Any] = {
        "ok": True,
        "op": "mine",
        "revision": st.revision,
        "applied": info["applied"],
        "pool_net": info["pool_net"],
        "prefix": info["prefix"],
        "fragment": info["fragment"],
        "places_after": info["places_after"],
        "would_exceed_cap": info["would_exceed_cap"],
        "mining": info["mining"],
        "relations": info["relations"],
        "drift": info["drift"],
        "empirical": info["empirical"],
        "manifest": info["manifest"],
    }
    return envelope, 0


def _invariant(base: Path) -> tuple[dict[str, Any], int]:
    st = state.load(base)
    analyzer = PetriNetAnalyzer(st.net)
    place_invariants = analyzer.place_invariants()
    live_tuple = tuple(st.live_marking[p] for p in st.net.place_order)
    initial = st.net.initial_marking_tuple()
    hold = all(
        sum(y[i] * live_tuple[i] for i in range(len(y)))
        == sum(y[i] * initial[i] for i in range(len(y)))
        for y in place_invariants
    )
    records = state.read_ledger_net_records()
    ledger_revision = records[-1].get("revision", 0) if records else 0
    drifted = st.revision != ledger_revision
    drift = {
        "drifted": drifted,
        "net_revision": st.revision,
        "ledger_revision": ledger_revision,
    }
    if drifted:
        state.append_drift(base, {
            "op": "invariant",
            "net_revision": st.revision,
            "ledger_revision": ledger_revision,
        })
    envelope = {
        "ok": True,
        "op": "invariant",
        "place_invariants": [list(v) for v in place_invariants],
        "transition_invariants": [
            list(v) for v in analyzer.transition_invariants()
        ],
        "live_marking_invariants_hold": hold,
        "drift": drift,
        # feature_041 R4: additive capacity/conflict surfacing (D7 exit hook)
        "resources": state.resource_report(st)["resources"],
        "conflicts": state.resource_report(st)["conflicts"],
    }
    return envelope, 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="omt_net",
        description="Meta-harness concurrency net (IDEA-002 v4 §5.0 closed op enum).",
    )
    sub = parser.add_subparsers(dest="op", required=True)

    p_probe = sub.add_parser("probe", help="Observe marking + enabled + analyzer advice.")
    p_probe.add_argument("--max-states", type=int, default=DEFAULT_MAX_STATES)
    p_probe.add_argument("--expected-revision", "--expected_revision", type=int, default=None, help="Stale-rev guard.")

    p_fire = sub.add_parser("fire", help="Fire an enabled transition (marking-only).")
    p_fire.add_argument("--transition", required=True)
    p_fire.add_argument("--reasoning", required=True)
    p_fire.add_argument("--session", default="")
    p_fire.add_argument("--expected-revision", "--expected_revision", type=int, default=None, help="Stale-rev guard.")
    p_fire.add_argument("--command-id", "--command_id", default="", help="Idempotency key (feature_079: same ID + same command replays, no double-fire).")
    p_claim = sub.add_parser("claim", help="Claim a pending task (task-aware work_start, gen-fenced).")
    p_claim.add_argument("--task-id", "--task_id", required=True)
    p_claim.add_argument("--owner", default="", help="New owner (default: --session).")
    p_claim.add_argument("--reasoning", required=True)
    p_claim.add_argument("--session", default="")
    p_claim.add_argument("--expected-revision", "--expected_revision", type=int, default=None, help="Stale-rev guard.")
    p_claim.add_argument("--command-id", "--command_id", default="", help="Idempotency key (feature_080: same ID + same claim replays, no double-claim).")
    p_release = sub.add_parser("release", help="Release an active claim back to pending.")
    p_release.add_argument("--task-id", "--task_id", required=True)
    p_release.add_argument("--owner", default="", help="Owner check (optional; mismatch refuses).")
    p_release.add_argument("--reasoning", required=True)
    p_release.add_argument("--session", default="")
    p_release.add_argument("--expected-revision", "--expected_revision", type=int, default=None, help="Stale-rev guard.")
    p_release.add_argument("--command-id", "--command_id", default="", help="Idempotency key (feature_080).")
    p_transfer = sub.add_parser("transfer", help="Hand an active claim to a new owner (gen+1).")
    p_transfer.add_argument("--task-id", "--task_id", required=True)
    p_transfer.add_argument("--owner", required=True, help="New owner.")
    p_transfer.add_argument("--reasoning", required=True)
    p_transfer.add_argument("--session", default="")
    p_transfer.add_argument("--expected-revision", "--expected_revision", type=int, default=None, help="Stale-rev guard.")
    p_transfer.add_argument("--command-id", "--command_id", default="", help="Idempotency key (feature_080).")
    p_checkpoint = sub.add_parser("checkpoint", help="Record checkpoint/result evidence against a held generation.")
    p_checkpoint.add_argument("--task-id", "--task_id", required=True)
    p_checkpoint.add_argument("--generation", type=int, required=True, help="Held generation (stale refuses).")
    p_checkpoint.add_argument("--mutation", default="", help="JSON evidence object ({checkpoint?, results?}).")
    p_checkpoint.add_argument("--reasoning", required=True)
    p_checkpoint.add_argument("--session", default="")
    p_checkpoint.add_argument("--expected-revision", "--expected_revision", type=int, default=None, help="Stale-rev guard.")
    p_checkpoint.add_argument("--command-id", "--command_id", default="", help="Idempotency key (feature_080).")
    p_heartbeat = sub.add_parser("heartbeat", help="Record liveness evidence for a held generation (T5-6 3B).")
    p_heartbeat.add_argument("--task-id", "--task_id", required=True)
    p_heartbeat.add_argument("--generation", type=int, required=True, help="Held generation (stale refuses).")
    p_heartbeat.add_argument("--reasoning", required=True)
    p_heartbeat.add_argument("--session", default="")
    p_heartbeat.add_argument("--expected-revision", "--expected_revision", type=int, default=None, help="Stale-rev guard.")
    p_heartbeat.add_argument("--command-id", "--command_id", default="", help="Idempotency key (feature_079).")
    p_recover = sub.add_parser("recover", help="Recover an active claim to a new owner, preserving checkpoint (T5-6 3B).")
    p_recover.add_argument("--task-id", "--task_id", required=True)
    p_recover.add_argument("--owner", default="", help="New owner (default: --session).")
    p_recover.add_argument("--reasoning", required=True)
    p_recover.add_argument("--session", default="")
    p_recover.add_argument("--expected-revision", "--expected_revision", type=int, default=None, help="Stale-rev guard.")
    p_recover.add_argument("--command-id", "--command_id", default="", help="Idempotency key (feature_079).")
    p_reconcile = sub.add_parser("reconcile", help="Startup reconcile for the transaction journal (T5-6 3B).")
    p_reconcile.add_argument("--reasoning", required=True)
    p_reconcile.add_argument("--session", default="")
    p_submit = sub.add_parser("submit", help="Worker publishes a result: active→verifying (T5-5 3A).")
    p_submit.add_argument("--task-id", "--task_id", required=True)
    p_submit.add_argument("--generation", type=int, required=True, help="Held generation (stale refuses).")
    p_submit.add_argument("--owner", default="", help="Owner check (optional; mismatch refuses).")
    p_submit.add_argument("--mutation", default="", help="JSON result object ({head_commit, patch_digest, base_commit?, local_checks?}).")
    p_submit.add_argument("--reasoning", required=True)
    p_submit.add_argument("--session", default="")
    p_submit.add_argument("--expected-revision", "--expected_revision", type=int, default=None, help="Stale-rev guard.")
    p_submit.add_argument("--command-id", "--command_id", default="", help="Idempotency key (feature_079).")
    p_verify = sub.add_parser("verify", help="Coordinator verifies: verifying→ready|pending (T5-5 3A).")
    p_verify.add_argument("--task-id", "--task_id", required=True)
    p_verify.add_argument("--generation", type=int, required=True, help="Submission generation (stale refuses).")
    p_verify.add_argument("--verdict", required=True, choices=["pass", "fail"])
    p_verify.add_argument("--coordinator", action="store_true", help="Coordinator role (required; workers refused).")
    p_verify.add_argument("--detail", default="", help="Failure evidence (fail verdict).")
    p_verify.add_argument("--reasoning", required=True)
    p_verify.add_argument("--session", default="")
    p_verify.add_argument("--expected-revision", "--expected_revision", type=int, default=None, help="Stale-rev guard.")
    p_verify.add_argument("--command-id", "--command_id", default="", help="Idempotency key (feature_079).")
    p_istart = sub.add_parser("integrate_start", help="Coordinator opens the lane: ready→integrating (T5-5 3A).")
    p_istart.add_argument("--task-id", "--task_id", required=True)
    p_istart.add_argument("--generation", type=int, required=True, help="Submission generation (stale refuses).")
    p_istart.add_argument("--coordinator", action="store_true", help="Coordinator role (required).")
    p_istart.add_argument("--reasoning", required=True)
    p_istart.add_argument("--session", default="")
    p_istart.add_argument("--expected-revision", "--expected_revision", type=int, default=None, help="Stale-rev guard.")
    p_istart.add_argument("--command-id", "--command_id", default="", help="Idempotency key (feature_079).")
    p_ifinish = sub.add_parser("integrate_finish", help="Coordinator closes the lane: integrating→done|pending (T5-5 3A).")
    p_ifinish.add_argument("--task-id", "--task_id", required=True)
    p_ifinish.add_argument("--generation", type=int, required=True, help="Submission generation (stale refuses).")
    p_ifinish.add_argument("--verdict", required=True, choices=["pass", "fail"])
    p_ifinish.add_argument("--coordinator", action="store_true", help="Coordinator role (required).")
    p_ifinish.add_argument("--detail", default="", help="Failure evidence (fail verdict, e.g. combined e2e).")
    p_ifinish.add_argument("--reasoning", required=True)
    p_ifinish.add_argument("--session", default="")
    p_ifinish.add_argument("--expected-revision", "--expected_revision", type=int, default=None, help="Stale-rev guard.")
    p_ifinish.add_argument("--command-id", "--command_id", default="", help="Idempotency key (feature_079).")

    p_splice = sub.add_parser(
        "splice", help="Atomic structural transaction (conformance-gated, §3)."
    )
    p_splice.add_argument(
        "--mode", required=True, choices=["add", "remove", "disable", "undo", "repair"]
    )
    p_splice.add_argument("--mutation", default="", help="JSON mutation object.")
    p_splice.add_argument("--subnet", default="", help="Subnet key (disable mode).")
    p_splice.add_argument("--reasoning", required=True)
    p_splice.add_argument("--session", default="")
    p_splice.add_argument("--feature", default="")
    p_splice.add_argument("--expected-revision", "--expected_revision", type=int, default=None, help="Stale-rev guard.")
    p_splice.add_argument("--command-id", "--command_id", default="", help="Idempotency key (feature_079: same ID + same command replays, no double-apply).")

    p_sync = sub.add_parser(
        "sync", help="net↔reality bootstrap + resync (proposal-only, D4)."
    )
    p_sync.add_argument("--reasoning", default="")
    p_sync.add_argument("--session", default="")
    p_sync.add_argument(
        "--direction", default="proposal",
        choices=["proposal", "net_to_md", "md_to_net_propose"],
    )
    p_sync.add_argument("--dry-run", action="store_true")
    p_sync.add_argument("--work-md", default="")
    p_sync.add_argument("--expected-revision", "--expected_revision", type=int, default=None, help="Stale-rev guard.")

    p_inv = sub.add_parser("invariant", help="Invariants + net-vs-ledger drift (D7).")
    p_inv.add_argument("--expected-revision", "--expected_revision", type=int, default=None, help="Stale-rev guard.")
# TA: gotcha: gotcha (feature_050 wrap-up): invariant subparser lacks --expected-revision while omt_net.ts OP_ARGS whitelists it → test_omt_net_plugin_args::TestWhitelistMirrorsCli RED; add the flag mirroring probe/fire/splice/sync/synthesize/mine/gate

    p_synth = sub.add_parser(
        "synthesize", help="Goal→net template proposal (D4, feature_042)."
    )
    p_synth.add_argument("--mutation", default="", help="JSON goal object.")
    p_synth.add_argument("--reasoning", required=True)
    p_synth.add_argument("--session", default="")
    p_synth.add_argument("--feature", default="")
    p_synth.add_argument("--expected-revision", "--expected_revision", type=int, default=None, help="Stale-rev guard.")

    p_mine = sub.add_parser(
        "mine", help="Ledger→net behavioral mining (read-only draft, D4, feature_044)."
    )
    p_mine.add_argument("--mutation", default="", help="JSON mine params object.")
    p_mine.add_argument("--reasoning", required=True)
    p_mine.add_argument("--session", default="")
    p_mine.add_argument("--feature", default="")
    p_mine.add_argument("--expected-revision", "--expected_revision", type=int, default=None, help="Stale-rev guard.")

    p_gate = sub.add_parser("gate", help="g.net permission-to-act check (feature_050).")
    p_gate.add_argument("--path", required=True, help="Target path being edited.")
    p_gate.add_argument("--session", default="")
    p_gate.add_argument("--task-id", "--task_id", default="", help="Managed scope: task id (feature_081 workspace-fenced edit check).")
    p_gate.add_argument("--owner", default="", help="Managed scope: owner check (feature_081).")
    p_gate.add_argument("--generation", type=int, default=None, help="Managed scope: held generation (feature_081).")
    p_gate.add_argument("--expected-revision", "--expected_revision", type=int, default=None, help="Stale-rev guard.")

    for op in RESERVED_OPS:
        sub.add_parser(op, help="Reserved — future.")

    return parser


def main(argv: list[str] | None = None) -> int:
# TA: risk: risk (feature_050 wrap-up @ .sandbox/pause_2026-09-05c.md): gate op passes net_available=True hardcoded and never passes drifted/expected_revision/live_revision → ERR_NET_DRIFT_CONFLICT + ERR_NET_STALE_REV + ERR_NET_DOWN unreachable in the LIVE enforcer path; fix = load state, drifted = st.revision != read_ledger_net_records()[-1].revision (same as _invariant), NetNotBootstrappedError/Exception → net_available=False (fail-closed D3)
    args = _build_parser().parse_args(argv)
    op: str = args.op

    if op in RESERVED_OPS:
        return _emit(*_error(
            "not_implemented",
            op,
            f"omt_net{{op:{op}}} is reserved — IDEA-002 v4 §5.0",
        ))

    base = state.net_dir()
    # Stale-rev check for all ops (feature_050: extend feat_046 to all ops)
    expected_rev = getattr(args, "expected_revision", None)
    if expected_rev is not None:
        try:
            st = state.load(base)
            if st.revision != expected_rev:
                return _emit(*_error("revision_mismatch", op, f"expected revision {expected_rev}, current is {st.revision}"))
        except state.NetNotBootstrappedError:
            pass  # net not bootstrapped yet, let the op handler deal with it
    try:
        if op == "probe":
            return _emit(*_probe(base, args.max_states))
        if op == "fire":
            return _emit(*_fire(base, args.transition, args.reasoning, args.session, getattr(args, "expected_revision", None), getattr(args, "command_id", None) or None))
        if op == "claim":
            return _emit(*_claim(base, args))
        if op == "release":
            return _emit(*_release(base, args))
        if op == "transfer":
            return _emit(*_transfer(base, args))
        if op == "checkpoint":
            payload: dict[str, Any] = {}
            if args.mutation:
                try:
                    payload = json.loads(args.mutation)
                except json.JSONDecodeError as exc:
                    return _emit(*_error(
                        "invalid_mutation", op, f"--mutation is not valid JSON: {exc}"
                    ))
            if not isinstance(payload, dict):
                return _emit(*_error("invalid_mutation", op, "--mutation must be a JSON object"))
            return _emit(*_checkpoint(
                base, args.task_id, args.generation,
                payload.get("checkpoint"), payload.get("results"),
                payload.get("head_commit"), payload.get("patch_digest"),
                args.session, getattr(args, "expected_revision", None),
                getattr(args, "command_id", None) or None))
        if op == "heartbeat":
            return _emit(*_heartbeat(base, args))
        if op == "recover":
            return _emit(*_recover(base, args))
        if op == "reconcile":
            return _emit(*_reconcile(base, args))
        if op == "submit":
            return _emit(*_submit(base, args))
        if op == "verify":
            return _emit(*_verify(base, args))
        if op == "integrate_start":
            return _emit(*_integrate_start(base, args))
        if op == "integrate_finish":
            return _emit(*_integrate_finish(base, args))
        if op == "splice":
            mutation = None
            if args.mutation:
                try:
                    mutation = json.loads(args.mutation)
                except json.JSONDecodeError as exc:
                    return _emit(*_error(
                        "invalid_mutation", op, f"--mutation is not valid JSON: {exc}"
                    ))
            return _emit(*_splice(base, args, mutation))
        if op == "sync":
            return _emit(*_sync(base, args))
        if op == "synthesize":
            goal = None
            if args.mutation:
                try:
                    goal = json.loads(args.mutation)
                except json.JSONDecodeError as exc:
                    return _emit(*_error(
                        "invalid_mutation", op, f"--mutation is not valid JSON: {exc}"
                    ))
            return _emit(*_synthesize(base, args, goal))
        if op == "mine":
            params = None
            if args.mutation:
                try:
                    params = json.loads(args.mutation)
                except json.JSONDecodeError as exc:
                    return _emit(*_error(
                        "invalid_mutation", op, f"--mutation is not valid JSON: {exc}"
                    ))
            return _emit(*_mine(base, args, params))
        if op == "invariant":
            return _emit(*_invariant(base))
        if op == "gate":
            from . import gate  # local import
            # feature_050 wrap-up: live wiring — drift mirrors _invariant
            # (net rev vs last ledger net-record rev); fail-closed on load
            # error (D3); expected_revision flows through for stale-rev.
            # feature_053 C1: forward the live marking so gate.py can apply
            # the net_marking(active>1) concurrency predicate (solo → allow
            # without a fire receipt; unreadable bundle → fail-closed).
            net_available = True
            drifted = False
            live_revision: int | None = None
            live_marking: dict | None = None
            try:
                st = state.load(base)
                live_revision = st.revision
                live_marking = dict(st.live_marking)
                records = state.read_ledger_net_records()
                ledger_revision = records[-1].get("revision", 0) if records else 0
                drifted = st.revision != ledger_revision
            except Exception:
                net_available = False  # net-down / unbootstrapped → BLOCK (D3)
            res = gate.check_edit_allowed(
                base,
                path=args.path,
                has_fire_receipt=False,  # gate.py reads the ledger itself
                expected_revision=getattr(args, "expected_revision", None),
                live_revision=live_revision,
                drifted=drifted,
                net_available=net_available,
                live_marking=live_marking,
            )
            if not res["allowed"]:
                return _emit({"ok": False, "allowed": False, "code": res["code"], "message": res["code"]}, 1)
            if getattr(args, "task_id", ""):
                if getattr(args, "generation", None) is None:
                    return _emit({"ok": False, "allowed": False, "code": "workspace_mismatch", "message": "workspace_mismatch"}, 1)
                managed = gate.check_managed_edit_allowed(
                    base,
                    task_id=args.task_id,
                    generation=args.generation,
                    path=args.path,
                    owner=getattr(args, "owner", "") or None,
                    session=args.session,
                )
                if not managed["allowed"]:
                    return _emit({"ok": False, "allowed": False, "code": managed["code"], "message": managed["code"]}, 1)
            return _emit({"ok": True, "allowed": True, "code": "OK"}, 0)
    except state.SpliceError as exc:
        return _emit(*_error(exc.code, op, str(exc)))
    except LockError as exc:
        return _emit(*_error(exc.code, op, str(exc)))
    except state.NetNotBootstrappedError as exc:
        return _emit(*_error("net_not_bootstrapped", op, str(exc)))
    except state.RevisionMismatchError as exc:
        return _emit(*_error("revision_mismatch", op, str(exc)))
    except TransitionNotEnabledError:
        return _emit(*_error("transition_not_enabled", op))
    except UnknownTransitionError:
        return _emit(*_error("unknown_transition", op))
    except PetriNetError as exc:
        return _emit(*_error("petri_net_error", op, str(exc)))
    raise AssertionError(f"unreachable op dispatch: {op}")


if __name__ == "__main__":
    sys.exit(main())
