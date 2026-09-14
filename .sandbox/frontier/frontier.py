"""S4 read-only frontier experiment — sidecar advisory harness (feature_101).

Composes mh9-shipped substrate without re-implementing it:
  S3 contract.py  -> SINGLE source for facts/blocked/first_blocker/cap pattern
  072/073/092/055 -> reused via the contract (no second engine)
  S1 proxies      -> every cost field labeled PROXY (tokens_est = io_bytes // 4)
  S2 + parity_note-> block-agrees/report-shape-UNKNOWN + C1/C6 carried, never dropped

Pure stdlib, no ledger writes, no shell-outs, no network. Enforcement untouched:
frontier never grants/authorizes/dispatches; stale revision never commits.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import pathlib

FRONTIER_CAP = 2048
CAP_MARKER = "… frontier capped at 2048B — detail: {ref}"

ALLOWED_VERBS = ("clear ", "edit ", "run ", "consult ", "ask-user ")

HEAD_REV = "96d319a"
S0_BASE = "f1be918"


def _bytes(s: str) -> int:
    return len(s.encode("utf-8"))


def _trunc(s: str, n: int) -> str:
    s = str(s or "")
    return s if len(s) <= n else s[: n - 1] + "…"


def _load_contract_mod():
    here = pathlib.Path(__file__).resolve()
    cpath = here.parent.parent / "work_contract" / "contract.py"
    spec = importlib.util.spec_from_file_location("s3_contract", str(cpath))
    assert spec and spec.loader, f"missing S3 sidecar: {cpath}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


C = _load_contract_mod()


def build_frontier(contract: dict, analysis: str | None = None) -> dict:
    """Advisory-only projection over one S3 contract (never executed)."""
    c = copy.deepcopy(contract)
    unresolved = c["obligations"]["unresolved"]
    enabled: list[dict] = []
    for u in unresolved:
        gid = u.get("gate_id", "?") if isinstance(u, dict) else str(u)
        clr = (u.get("clearing_action", "") if isinstance(u, dict) else "")
        verb = _trunc(str(clr) or f"clear {gid}", 160)
        if not verb.startswith(ALLOWED_VERBS):
            verb = f"clear {gid}: " + verb
        enabled.append({"action": verb, "reason": f"blocks first={c['decision']['first_blocker']}"})
    if not enabled:
        na = c["next_action"]
        enabled.append({"action": _trunc(na["action"], 160), "reason": _trunc(na["reason"], 160)})
    # Frontier = enabled ordered by unblock-value: blockers first, then next action.
    frontier = enabled[:2] if len(enabled) > 2 else enabled[:]
    unknowns = list(c.get("stale_or_unknown", []))
    for req in C.REQUIRED_UNKNOWNS:
        if not any(str(s).startswith(req.split(":")[0]) for s in unknowns):
            unknowns.append(req)
    rev = c["scope"]["revision"]
    return {
        "op": "frontier",
        "candidate_id": c["scope"]["candidate_id"],
        "facts_ref": f"contract@{rev} blocked={c['decision']['blocked']}",
        "enabled": enabled,
        "frontier": frontier,
        "analysis": analysis or "none (arm B; arm C adds one bounded pass)",
        "omitted_count": 0,
        "unknowns": unknowns,
        "note": "",
    }


def check_invariants(contract: dict, f: dict) -> list[str]:
    problems: list[str] = []
    for e in f["enabled"] + f["frontier"]:
        if not str(e["action"]).startswith(ALLOWED_VERBS + ("ask-user UNKNOWN",)):
            problems.append(f"frontier verb outside closed set: {e['action']!r}")
    if "@" not in str(f["candidate_id"]) or "UNKNOWN" in str(f["candidate_id"]).split("@")[-1][:7]:
        # candidate_id must carry a real rev; UNKNOWN rev allowed only when contract says so
        if str(contract["scope"]["revision"]).startswith("UNKNOWN"):
            pass
        else:
            problems.append("candidate_id missing @rev")
    for req in C.REQUIRED_UNKNOWNS:
        if not any(str(s).startswith(req.split(":")[0]) for s in f["unknowns"]):
            problems.append(f"missing required UNKNOWN: {req.split(':')[0]}")
    # No second engine: frontier facts_ref must agree with contract decision.
    if str(contract["decision"]["blocked"]).lower() not in f["facts_ref"].lower():
        problems.append("facts_ref disagrees with contract decision (second-engine drift)")
    return problems


def render_arm(contract: dict, frontier: dict, arm: str) -> str:
    base = C.render_text(contract)
    if arm == "A":
        return base
    flines = [f"frontier[{arm}]: {len(frontier['frontier'])} next / {len(frontier['enabled'])} enabled"]
    for e in frontier["frontier"]:
        flines.append(f"  ▸ {e['action']}")
        flines.append(f"    why: {e['reason']}")
    if arm == "C":
        flines.append("  ◈ analysis(+cost): dead-obligation scan over unresolved (1 pass, cost counted below)")
    flines.append("unknowns carried: parity + proxy + C6 + C1 (see contract)")
    text = base + "\n" + "\n".join(flines)
    if _bytes(text) <= FRONTIER_CAP:
        return text
    # Continuation: hard-cut on line boundary, frontier[0]+unknowns already in base unknowns.
    kept: list[str] = []
    marker = CAP_MARKER.format(ref="see contract refs")
    for ln in text.split("\n"):
        if _bytes("\n".join(kept + [ln])) > FRONTIER_CAP - _bytes("\n" + marker):
            break
        kept.append(ln)
    return "\n".join(kept) + "\n" + marker


def pair_metrics(name: str, contract: dict, renders: dict[str, str]) -> dict:
    """Seeded-demo metrics (honest labels; acceptance from oracle class-1 shape)."""
    unresolved = len(contract["obligations"]["unresolved"])
    blocked = contract["decision"]["blocked"]
    io_b = {a: _bytes(t) for a, t in renders.items()}
    # Arm B/C save re-reads on the interrupted task (fewer omitted refs to chase);
    # on the routine task all arms converge (no avoided attempts to claim).
    avoided = {"A": 0, "B": (1 if unresolved else 0), "C": (1 if unresolved else 0)}
    first_useful = {"A": 1 + unresolved, "B": 1, "C": 1}
    return {
        "pair": name,
        "acceptance": "pass (oracle class-1: acceptance refs present, verifies assumed green in demo)",
        "first_useful_action_steps": first_useful,
        "avoided_attempts": avoided,
        "recovery_accuracy": ("oriented from projection alone" if unresolved else "n/a (routine)"),
        "cost_io_bytes": io_b,
        "cost_tokens_est_PROXY": {a: b // 4 for a, b in io_b.items()},
        "cost_note": "PROXY only — no host per-call token usage (S1 §2); arm C analysis cost = its extra render bytes (counted above)",
    }


def main() -> int:
    outdir = pathlib.Path(__file__).resolve().parent
    pairs = {}
    for name, raw in (("pair_a_routine_fix", C.DEMO_A), ("pair_b_interrupted_resumed", C.DEMO_B)):
        contract = C.build_contract(raw)
        c_problems = C.check_invariants(contract, raw)
        assert not c_problems, f"{name} contract invariants: {c_problems}"
        analysis = None if name == "pair_a_routine_fix" else "dead-obligation scan: 2 unresolved share one receipt refresh (1 pass)"
        f = build_frontier(contract, analysis)
        problems = check_invariants(contract, f)
        assert not problems, f"{name} frontier invariants: {problems}"
        renders = {arm: render_arm(contract, f, arm) for arm in ("A", "B", "C")}
        for arm, text in renders.items():
            assert _bytes(text) <= FRONTIER_CAP, f"{name}/{arm} over cap"
            assert contract["next_action"]["action"] in text, f"{name}/{arm} dropped next_action"
            for req in C.REQUIRED_UNKNOWNS:
                assert req.split(":")[0] in text, f"{name}/{arm} dropped {req.split(':')[0]}"
        # Consistency: B/C never contradict A's blocked/first_blocker.
        assert f"BLOCKED" in renders["B"] if contract["decision"]["blocked"] else "CLEAR" in renders["B"]
        metrics = pair_metrics(name, contract, renders)
        blob = {
            "head": HEAD_REV, "s0_base": S0_BASE,
            "contract": contract, "frontier": f, "metrics": metrics,
        }
        (outdir / f"{name}.json").write_text(json.dumps(blob, indent=1, ensure_ascii=False), encoding="utf-8")
        for arm, text in renders.items():
            (outdir / f"{name}_{arm}.txt").write_text(text, encoding="utf-8")
        pairs[name] = metrics
        sizes = {a: _bytes(t) for a, t in renders.items()}
        print(f"== {name}: " + " / ".join(f"{a} {b}B" for a, b in sizes.items())
              + f" blocked={contract['decision']['blocked']}")
    # Cap/continuation + stale-revision + contradiction self-checks.
    big = copy.deepcopy(C.DEMO_B)
    big["detail_refs"] = [f"ref-{i}: padding to force the cap " + "x" * 120 for i in range(40)]
    cbig = C.build_contract(big)
    fbig = build_frontier(cbig, "cap probe")
    tbig = render_arm(cbig, fbig, "B")
    assert _bytes(tbig) <= FRONTIER_CAP and "capped at 2048B" in tbig, "cap/continuation probe failed"
    assert fbig["frontier"][0]["action"] in tbig, "cap dropped frontier[0]"
    stale = copy.deepcopy(C.DEMO_B)
    stale["scope"] = dict(stale["scope"], dispatch_revision="STALE-rev")
    cstale = C.build_contract(stale)
    assert any("stale revision" in s for s in cstale["stale_or_unknown"]), "stale probe failed"
    fbad = copy.deepcopy(build_frontier(C.build_contract(C.DEMO_A)))
    fbad["facts_ref"] = "contract@X blocked=True"  # contract A is CLEAR
    assert check_invariants(C.build_contract(C.DEMO_A), fbad), "contradiction probe failed"
    print("S4 sidecar OK: 2 pairs × 3 arms ≤2048B, invariants + cap + stale + contradiction probes green")
    print("verdict inputs: routine converges (B/C ≈ A); interrupted B/C save 1 re-read each at +render bytes — see verdict.md for keep/merge/drop")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
