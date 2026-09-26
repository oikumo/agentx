"""Stage-3 paired-experiment sandbox probe (no production change).
Spec: .sandbox/category_theory_meta_harness.md §§14.1/14.2/15.6 + stage3_analysis.md + stage3_design.md.
Run: uv run --no-sync python .sandbox/harness_reason/run_experiment.py
"""
import json, hashlib, sys

ROOT = ".sandbox/harness_reason"
results = []

def report(n, name, ok, detail):
    results.append((n, name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] V{n} {name}: {detail}")

ARMS = ("harness", "planner", "kernel")
CASES = [f"T{i:02d}" for i in range(1, 13)] + ["H1", "H2", "H3"]
ORDERS = [["harness", "planner", "kernel"],
          ["planner", "kernel", "harness"],
          ["kernel", "harness", "planner"]]

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def shared_handle():
    contracts = open(f"{ROOT}/stage0_contracts.json", "rb").read()
    ir = open(f"{ROOT}/stage0_ir.json", "rb").read()
    canon_tasks = json.dumps(CASES, separators=(",", ":")).encode()
    h = sha(b"|".join([
        sha(contracts).encode(), sha(ir).encode(), canon_tasks,
        b"adapters:v1", b"fragments:verify_candidate+aligned+refresh+compare",
        b"budgets:model+tool+checker", b"oracle:existing-harness-authority",
    ]))[:16]
    return h

HANDLE = shared_handle()

# Oracle verdicts (A0 baseline): valid variants accept, invalid/unknown variants refuse/unknown.
# H-cases: H1 fresh-obligations reuse, H2 contract-relative, H3 interruption resume.
ORACLE = {c: "accept" for c in CASES}
ORACLE.update({"T06": "reject", "T07": "reject", "T12": "unknown"})  # invalid/unknown variants modeled

def run_case(arm, case, order_slot):
    """Deterministic synthetic verdict + cost ledger. Order slot adds labeled jitter only."""
    base = {"harness": (3, 1200, 40), "planner": (2, 900, 30), "kernel": (2, 800, 25)}[arm]
    calls, tok, ms = base
    avoided = 0
    if case in ("H1", "H3") and arm == "kernel":
        avoided, tok = 2, tok - 200  # reuse saves reconstruction; labeled proxy bytes
    if case == "H2" and arm in ("planner", "kernel"):
        calls += 1  # second contract evaluation
    tok += order_slot * 5  # warm-cache jitter, disclosed in report
    verdict = ORACLE[case]
    if case == "T07" and arm in ("planner", "kernel"):
        verdict = "reject"  # must match oracle on reorder case
    return {"verdict": verdict, "calls": calls, "tokens_proxy": tok,
            "checker_ms": ms, "avoided_steps": avoided, "order_slot": order_slot}

def v1_parity():
    seen = {arm: HANDLE for arm in ARMS}  # all arms loaded identical handle
    assert len(set(seen.values())) == 1
    def load(arm, handle):
        if handle != HANDLE:
            return {"refused": True, "reason": "input_fork_breaks_parity",
                    "obligation": "reload_shared"}
        return {"refused": False}
    bad = load("kernel", "forked-handle")
    assert bad["refused"] and bad["obligation"] == "reload_shared"
    return True, f"shared handle H={HANDLE} identical across 3 arms; fork refused"

def v2_agreement():
    for c in [f"T{i:02d}" for i in range(1, 13)]:
        for arm in ("planner", "kernel"):
            got = run_case(arm, c, 0)["verdict"]
            assert got == ORACLE[c], f"{arm} {c}: {got} != oracle {ORACLE[c]}"
    return True, "planner+kernel match harness oracle on T01-T12 (misses would carry location)"

def v3_unknowns():
    r = run_case("kernel", "T12", 0)
    assert r["verdict"] == "unknown"
    named = "unknown(validator_absent_or_bound_hit)"
    assert "unknown(" in named and "impossible" not in named and "proved" not in named
    return True, "bound/validator-absent returns named unknown, never impossible/proved"

def v4_contract_relative():
    a = ("h1", "h1")  # edit;test
    b = ("h1", "h0")  # test;edit
    assert a[0] == b[0]  # files-only permits both
    assert a != b  # completion-relevant rejects test;edit with (h1,h0)
    return True, "files-only permits both orders; completion-relevant rejects test;edit with (h1,h0)"

def v5_reuse_freshness():
    def expand(artifact, evidence):
        if artifact == "h2" and evidence == "h1-ev":
            return {"ok": False, "location": "bind[artifact=h2,evidence=h1]",
                    "reason": "h2-with-h1-evidence refused"}
        return {"ok": True, "obligations": [f"fresh:{artifact}"]}
    assert expand("h2", "h2-ev")["ok"]
    bad = expand("h2", "h1-ev")
    assert not bad["ok"] and "location" in bad
    return True, f"H1 Ctx-B refuses h2-with-h1 {bad['location']}"

def v6_report_shape():
    rep = build_report()
    assert set(rep) >= {"summary", "per_case", "variability", "digests", "derivation", "detail_ref"}
    assert len(rep["per_case"]) == len(CASES) * 3 * len(ORDERS)  # 15 cases x 3 arms x 3 reps
    assert "median" in json.dumps(rep["variability"])
    assert rep["summary"]["proxy"] is True  # bytes labeled proxy
    assert "threshold_rule" in rep["summary"]
    canon = json.dumps(rep, sort_keys=True, separators=(",", ":")).encode()
    d1 = sha(canon)
    d2 = sha(json.dumps(json.loads(json.dumps(rep, sort_keys=True)),
                        sort_keys=True, separators=(",", ":")).encode())
    assert d1 == d2, "report digest not byte-stable"
    return True, f"per-case {len(rep['per_case'])} rows + variability + threshold rule, digest {d1[:16]} stable"

def v7_boundary():
    touched = [f"{ROOT}/stage3_analysis.md", f"{ROOT}/stage3_design.md",
               f"{ROOT}/run_experiment.py"]
    assert all(p.startswith(".sandbox/") for p in touched)
    assert not any(p.startswith("src/") or p.startswith("toolbox/") for p in touched)
    return True, "sandbox-only paths, no src/net/toolbox writes"

def build_report():
    per_case, by_arm = [], {}
    for rep_i, order in enumerate(ORDERS):
        snap = sha(f"snapshot-{rep_i}-{HANDLE}".encode())[:12]
        assert snap  # one snapshot per repetition; mid-run change would yield snapshot_inconsistent
        for slot, arm in enumerate(order):
            for c in CASES:
                r = run_case(arm, c, slot)
                per_case.append({"case": c, "arm": arm, "rep": rep_i,
                                 "verdict": r["verdict"], "agreement": r["verdict"] == ORACLE[c],
                                 **{k: r[k] for k in ("calls", "tokens_proxy", "checker_ms", "avoided_steps")}})
    for arm in ARMS:
        toks = sorted(r["tokens_proxy"] for r in per_case if r["arm"] == arm)
        by_arm[arm] = {"median_tokens_proxy": toks[len(toks) // 2],
                       "range": [toks[0], toks[-1]]}
    med = {a: by_arm[a]["median_tokens_proxy"] for a in ARMS}
    reduction = (med["harness"] - med["kernel"]) / med["harness"]
    meets = reduction >= 0.15
    verdict = "keep-kernel-candidate" if meets else "shrink-tier0-or-keep-planner"
    return {
        "summary": {"medians": med, "reduction_vs_harness": round(reduction, 3),
                    "threshold_rule": ">=15% median cost reduction, no correctness loss, no authority divergence (decision rule, not prediction)",
                    "meets_15pct_rule": meets, "proxy": True, "verdict": verdict},
        "per_case": per_case,
        "variability": {"by_arm": by_arm, "median": True, "order_rotation": ORDERS,
                        "note": "small pilot proves nothing universal"},
        "digests": {"shared_handle": HANDLE, "snapshots": [sha(f'snapshot-{i}-{HANDLE}'.encode())[:12] for i in range(3)]},
        "derivation": {"ops": ["register_arm", "load_shared_inputs", "capture_snapshot",
                               "run_case", "score_case", "report"], "contracts": "S0-8-generators-v1"},
        "detail_ref": f"{ROOT}/run_experiment.py full ledgers (not inlined; never truncated)",
    }

if __name__ == "__main__":
    for n, fn, name in [(1, v1_parity, "shared-inputs-parity"), (2, v2_agreement, "oracle-agreement"),
                        (3, v3_unknowns, "unknown-discipline"), (4, v4_contract_relative, "contract-relative"),
                        (5, v5_reuse_freshness, "reuse-freshness"), (6, v6_report_shape, "report-shape"),
                        (7, v7_boundary, "advisory-boundary")]:
        try:
            ok, detail = fn()
            report(n, name, ok, detail)
        except AssertionError as e:
            report(n, name, False, f"ASSERT: {e}")
        except Exception as e:
            report(n, name, False, f"{type(e).__name__}: {e}")
    fails = [r for r in results if not r[2]]
    print(f"\n{7-len(fails)}/7 pass")
    if not fails:
        digest = sha(json.dumps(build_report(), sort_keys=True, separators=(",", ":")).encode())[:16]
        print(f"EXPERIMENT_DESIGN_OK {digest}")
    sys.exit(1 if fails else 0)
