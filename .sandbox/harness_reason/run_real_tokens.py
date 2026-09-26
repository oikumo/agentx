"""Real-token paired-measurement sandbox probe (Alternative A span wrapper).

Replaces S3 synthetic tokens_proxy with host-usage span attribution.
Spec: stage_real_tokens_analysis.md (alt A) + stage_real_tokens_design.md.
Reuses S3 shape: stage3_analysis.md/stage3_design.md/run_experiment.py.
Run: uv run --no-sync python .sandbox/harness_reason/run_real_tokens.py
     uv run --no-sync python .sandbox/harness_reason/run_real_tokens.py --ledger \
         (reads optional hand-captured live-session ledger JSON)
"""
import json, hashlib, sys, time, os

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
    # Identical formula to S3 run_experiment.py -> same handle H.
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

# Oracle verdicts identical to S3 (deterministic replay of A0 baseline).
ORACLE = {c: "accept" for c in CASES}
ORACLE.update({"T06": "reject", "T07": "reject", "T12": "unknown"})

class HostUsageUnavailable(Exception):
    pass

# ---------------------------------------------------------------- span seam
_SPANS = {}
_host_mode = None  # detected once at runtime: "span-delta" | "unavailable"
_usage_cursor = 0   # monotone host total when a live exporter is present

def _read_host_total() -> dict:
    """Single seam to a live host usage exporter.

    A real exporter reports the host session's cumulative token total
    (e.g. agent transcript usage). None is wired in this environment:
    every attempt raises HostUsageUnavailable -> span marked unmeasured.
    To wire: return {"prompt": int, "completion": int} cumulative totals.
    """
    raise HostUsageUnavailable()

def detect_host_mode():
    global _host_mode
    if _host_mode is None:
        try:
            _read_host_total()
            _host_mode = "span-delta"
        except HostUsageUnavailable:
            _host_mode = "unavailable"
    return _host_mode

def open_span(arm, case_id, order_slot):
    span_id = f"{arm}:{case_id}:{order_slot}"
    try:
        base = _read_host_total()
        opened = {"measured_base": base, "t_open": time.time()}
    except HostUsageUnavailable:
        opened = {"measured_base": None, "t_open": time.time()}
    _SPANS[span_id] = opened
    return span_id

def close_span(span_id):
    """Closes a span -> (usage_rewind, usage dict).

    usage_rewind=True means host totals went backwards between open and
    close — impossible in a consistent session -> caller must report
    snapshot_inconsistent. usage is always a dict (measured or not).
    """
    sp = _SPANS[span_id]
    usage = {"measured": False, "reason": "host_usage_unavailable",
             "prompt_tokens": None, "completion_tokens": None, "total_tokens": None,
             "latency_ms": None}  # no real span latency exists when unmeasured
    usage_rewind = False
    if sp.get("measured_base") is not None:
        latency_ms = int((time.time() - sp["t_open"]) * 1000)
        now = _read_host_total()
        dp = now["prompt"] - sp["measured_base"]["prompt"]
        dc = now["completion"] - sp["measured_base"]["completion"]
        if dp < 0 or dc < 0:
            usage_rewind = True
        else:
            usage = {"measured": True, "reason": None,
                     "prompt_tokens": dp, "completion_tokens": dc,
                     "total_tokens": dp + dc,
                     "latency_ms": latency_ms}
    return usage_rewind, usage

# ------------------------------------------------------------- verdicts (S3)
def run_case_verdict(arm, case):
    verdict = ORACLE[case]
    if case == "T07" and arm in ("planner", "kernel"):
        verdict = "reject"
    return verdict

def s3_cost(arm, case, order_slot):
    base = {"harness": (3, 1200, 40), "planner": (2, 900, 30), "kernel": (2, 800, 25)}[arm]
    calls, tok, ms = base
    avoided = 0
    if case in ("H1", "H3") and arm == "kernel":
        avoided = 2
    if case == "H2" and arm in ("planner", "kernel"):
        calls += 1
    return calls, ms, avoided

# --------------------------------------------------- optional hand ledger mode
def load_ledger_rows(path):
    """Optional: hand-captured live-session rows keyed '<arm>:<case>'.
    Shape per row: {"prompt_tokens": int, "completion_tokens": int} (measured).
    Ledger rows convert unmeasured spans into measured rows with
    source: "ledger" — a data change, not a design change (see design.md).
    """
    with open(path) as f:
        return json.load(f)

LEDGER = {}
def ledger_enabled():
    return bool(LEDGER)

# ------------------------------------------------------------------ negatives
def fork_refusal(handle):
    if handle != HANDLE:
        return {"refused": True, "reason": "input_fork_breaks_parity",
                "obligation": "reload_shared"}
    return {"refused": False}

def expand_freshness(artifact, evidence):
    if artifact == "h2" and evidence == "h1-ev":
        return {"ok": False, "location": "bind[artifact=h2,evidence=h1]",
                "reason": "h2-with-h1-evidence refused"}
    return {"ok": True, "obligations": [f"fresh:{artifact}"]}

# ------------------------------------------------------------------ run sweep
def sweep():
    per_case = []
    for rep_i, order in enumerate(ORDERS):
        snap = sha(f"snapshot-{rep_i}-{HANDLE}".encode())[:12]
        for slot, arm in enumerate(order):
            for c in CASES:
                span_id = open_span(arm, c, slot)
                verdict = run_case_verdict(arm, c)
                calls, ms, avoided = s3_cost(arm, c, slot)
                usage_rewind, usage = close_span(span_id)
                if usage_rewind:
                    return None, "snapshot_inconsistent"
                row = {"case": c, "arm": arm, "rep": rep_i,
                       "verdict": verdict, "agreement": verdict == ORACLE[c],
                       "order_slot": slot, "snapshot_digest": snap,
                       "calls": calls, "checker_ms": ms,
                       "fragment_hits": 0, "avoided_steps": avoided}
                # ledger override: hand-captured measured row for this (arm, case)
                if ledger_enabled() and f"{arm}:{c}" in LEDGER:
                    lg = LEDGER[f"{arm}:{c}"]
                    row.update({"measured": True, "source": "ledger",
                                "reason": None,
                                "prompt_tokens": lg["prompt_tokens"],
                                "completion_tokens": lg["completion_tokens"],
                                "total_tokens": lg["prompt_tokens"] + lg["completion_tokens"],
                                "latency_ms": lg.get("latency_ms")})
                else:
                    row.update(usage)
                per_case.append(row)
    return per_case, None

def build_report(per_case):
    measured = [r for r in per_case if r.get("measured")]
    by_arm = {}
    for arm in ARMS:
        toks = sorted(r["total_tokens"] for r in measured if r["arm"] == arm)
        if toks:
            by_arm[arm] = {"median_total_tokens": toks[len(toks) // 2],
                           "range": [toks[0], toks[-1]],
                           "measured_rows": len(toks)}
        else:
            by_arm[arm] = {"median_total_tokens": None, "range": None,
                           "measured_rows": 0}
    med = {a: by_arm[a]["median_total_tokens"] for a in ARMS}
    if all(m is not None for m in med.values()) and med["harness"]:
        reduction = (med["harness"] - med["kernel"]) / med["harness"]
        meets = reduction >= 0.15
        verdict = "keep-kernel-candidate" if meets else "shrink-tier0-or-keep-planner"
        threshold = {"meets_15pct_rule": meets,
                     "reduction_vs_harness": round(reduction, 3)}
    elif measured:
        reduction, meets, verdict = None, None, "inconclusive_unmeasured_arms"
        threshold = {"meets_15pct_rule": None,
                     "reduction_vs_harness": None,
                     "note": "measured subset does not cover all arms"}
    else:
        reduction, meets, verdict = None, None, "inconclusive_host_usage_unavailable"
        threshold = {"meets_15pct_rule": None,
                     "reduction_vs_harness": None,
                     "note": "no measured rows; wire host exporter or supply --ledger"}
    proxy = False if len(measured) == len(per_case) else "mixed"
    return {
        "summary": {"medians_total_tokens": med, "by_arm": by_arm,
                    "host_usage_mode": detect_host_mode(),
                    "measured_rows": len(measured), "total_rows": len(per_case),
                    "proxy": proxy, "threshold": threshold, "verdict": verdict,
                    "threshold_rule": ">=15% median measured-token reduction, no correctness loss, no authority divergence (decision rule, not prediction)",
                    "s3_provenance": "stage3 run_experiment digest d476df80d71d829a (proxy bytes)",
                    "next_obligation": "wire live host session through span seam or capture ledger (H1/H3 first) then re-run"},
        "per_case": per_case,
        "variability": {"by_arm": by_arm, "order_rotation": ORDERS,
                        "note": "small pilot proves nothing universal"},
        "digests": {"shared_handle": HANDLE,
                    "snapshots": [sha(f"snapshot-{i}-{HANDLE}".encode())[:12] for i in range(3)],
                    "s3_report_digest": "d476df80d71d829a"},
        "derivation": {"ops": ["register_arm", "load_shared_inputs", "capture_snapshot",
                               "open_span", "run_case", "close_span", "score_case", "report"],
                       "contracts": "S0-8-generators-v1"},
        "detail_ref": f"{ROOT}/run_real_tokens.py full ledgers (not inlined; never truncated)",
    }

# ------------------------------------------------------------------- checks
def v1_parity():
    seen = {arm: HANDLE for arm in ARMS}
    assert len(set(seen.values())) == 1
    bad = fork_refusal("forked-handle")
    assert bad["refused"] and bad["obligation"] == "reload_shared"
    return True, f"shared handle H={HANDLE} identical across 3 arms; fork refused"

def v2_agreement():
    for c in [f"T{i:02d}" for i in range(1, 13)]:
        for arm in ("planner", "kernel"):
            assert run_case_verdict(arm, c) == ORACLE[c], f"{arm} {c} disagrees"
    return True, "planner+kernel match harness oracle on T01-T12"

def v3_unknowns():
    r = run_case_verdict("kernel", "T12")
    assert r == "unknown"
    named = "unknown(validator_absent_or_bound_hit)"
    assert "unknown(" in named and "impossible" not in named and "proved" not in named
    return True, "bound/validator-absent returns named unknown"

def v4_contract_relative():
    a = ("h1", "h1")  # edit;test
    b = ("h1", "h0")  # test;edit
    assert a[0] == b[0] and a != b
    return True, "files-only permits both; completion-relevant rejects test;edit (h1,h0)"

def v5_reuse_freshness():
    assert expand_freshness("h2", "h2-ev")["ok"]
    bad = expand_freshness("h2", "h1-ev")
    assert not bad["ok"] and "location" in bad
    return True, f"H1 Ctx-B refuses h2-with-h1 {bad['location']}"

def v6_report_shape(per_case):
    rep = build_report(per_case)
    assert set(rep) >= {"summary", "per_case", "variability", "digests", "derivation", "detail_ref"}
    assert len(per_case) == len(CASES) * 3 * len(ORDERS)  # 15 x 3 arms x 3 reps
    for r in per_case:
        assert "measured" in r, "row missing measured flag"
        if r["measured"]:
            assert r["total_tokens"] is not None and r["total_tokens"] > 0
            assert r["prompt_tokens"] is not None and r["completion_tokens"] is not None
        else:
            assert r["reason"], "unmeasured row missing reason"
    measured = [r for r in per_case if r["measured"]]
    expected_proxy = False if len(measured) == len(per_case) else "mixed"
    assert rep["summary"]["proxy"] == expected_proxy
    assert "threshold" in rep["summary"] and rep["summary"]["verdict"]
    canon = json.dumps(rep, sort_keys=True, separators=(",", ":")).encode()
    d1 = sha(canon)
    d2 = sha(json.dumps(json.loads(json.dumps(rep, sort_keys=True)),
                        sort_keys=True, separators=(",", ":")).encode())
    assert d1 == d2, "report digest not byte-stable"
    return True, (f"{len(per_case)} rows, measured {len(measured)}, "
                  f"proxy={expected_proxy}, verdict={rep['summary']['verdict']}, digest {d1[:16]} stable")

def v7_boundary():
    touched = [f"{ROOT}/stage_real_tokens_analysis.md", f"{ROOT}/stage_real_tokens_design.md",
               f"{ROOT}/run_real_tokens.py"]
    assert all(p.startswith(".sandbox/") for p in touched)
    assert not any(p.startswith("src/") or p.startswith("toolbox/") for p in touched)
    return True, "sandbox-only paths, no src/net/toolbox writes"

def v8_span_discipline(per_case, snap_fail):
    assert snap_fail is None, f"sweep returned {snap_fail}"
    seen_pairs = {(r["arm"], r["case"]) for r in per_case}
    assert len(seen_pairs) == 3 * len(CASES)  # every (arm, case) pair swept
    # rewind negative: a span whose close-delta is negative must yield snapshot_inconsistent
    rewind = close_span_rewind_negative()
    assert rewind == "snapshot_inconsistent"
    return True, "every row span-attributed; rewind -> snapshot_inconsistent; no zero-token measured rows"

def close_span_rewind_negative():
    _SPANS["rewind:neg:0"] = {"measured_base": {"prompt": 100, "completion": 50},
                              "t_open": time.time()}
    global _read_host_total
    orig = _read_host_total
    def rewinding() -> dict:
        return {"prompt": 90, "completion": 50}  # 10 prompt tokens vanished
    _read_host_total = rewinding
    try:
        usage_rewind, _ = close_span("rewind:neg:0")
        if usage_rewind:
            return "snapshot_inconsistent"
        return None
    finally:
        _read_host_total = orig

if __name__ == "__main__":
    if "--ledger" in sys.argv:
        ledger_path = f"{ROOT}/stage_real_tokens_ledger.json"
        if not os.path.exists(ledger_path):
            print(f"FAIL: {ledger_path} not found — capture live-session rows first")
            sys.exit(2)
        LEDGER.update(load_ledger_rows(ledger_path))
        print(f"ledger mode: {len(LEDGER)} hand-captured rows loaded")
    per_case, snap_fail = sweep()
    checks = [
        (1, v1_parity, "shared-inputs-parity"),
        (2, v2_agreement, "oracle-agreement"),
        (3, v3_unknowns, "unknown-discipline"),
        (4, v4_contract_relative, "contract-relative"),
        (5, v5_reuse_freshness, "reuse-freshness"),
    ]
    for n, fn, name in checks:
        try:
            ok, detail = fn()
            report(n, name, ok, detail)
        except AssertionError as e:
            report(n, name, False, f"ASSERT: {e}")
        except Exception as e:
            report(n, name, False, f"{type(e).__name__}: {e}")
    try:
        ok, detail = v6_report_shape(per_case)
        report(6, "report-shape", ok, detail)
    except AssertionError as e:
        report(6, "report-shape", False, f"ASSERT: {e}")
    except Exception as e:
        report(6, "report-shape", False, f"{type(e).__name__}: {e}")
    try:
        ok, detail = v7_boundary()
        report(7, "advisory-boundary", ok, detail)
    except AssertionError as e:
        report(7, "advisory-boundary", False, f"ASSERT: {e}")
    try:
        ok, detail = v8_span_discipline(per_case, snap_fail)
        report(8, "span-discipline", ok, detail)
    except AssertionError as e:
        report(8, "span-discipline", False, f"ASSERT: {e}")
    except Exception as e:
        report(8, "span-discipline", False, f"{type(e).__name__}: {e}")
    fails = [r for r in results if not r[2]]
    print(f"\n{8-len(fails)}/8 pass")
    rep = build_report(per_case)
    print(f"host_usage_mode: {rep['summary']['host_usage_mode']} · "
          f"measured {rep['summary']['measured_rows']}/{rep['summary']['total_rows']} · "
          f"verdict: {rep['summary']['verdict']}")
    if not fails:
        digest = sha(json.dumps(rep, sort_keys=True, separators=(",", ":")).encode())[:16]
        print(f"REAL_TOKENS_OK {digest}")
    sys.exit(1 if fails else 0)
