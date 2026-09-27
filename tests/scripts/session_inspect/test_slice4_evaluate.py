"""RED S4 — quality-aware comparison (design_001 S4)."""


def _metrics():
    return {
        "case01_baseline_rep01": {"quality": "pass",
                                  "input": 1000, "latency_ms": 50},
        "case01_candidate_rep01": {"quality": "pass",
                                   "input": 600, "latency_ms": 45},
        "case02_baseline_rep01": {"quality": "pass",
                                  "input": 1000, "latency_ms": 50},
        "case02_candidate_rep01": {"quality": "fail",
                                   "input": 100, "latency_ms": 40},
    }


def test_evaluate_comparison():
    from session_inspect import evaluate, manifest
    m = manifest.create(experiment="ctx", run="run_001",
                        cases=["case01", "case02"],
                        variants=["baseline", "candidate"], reps=1)
    res = evaluate.compare(m, _metrics())
    by_case = {c["case"]: c for c in res["cases"]}
    # case01: cheaper + quality held → candidate supported
    assert by_case["case01"]["decision"] == "candidate_supported"
    # case02: cheaper but FAILED task → cannot win
    assert by_case["case02"]["decision"] == "inconclusive"
    assert by_case["case02"]["reason"] == "quality_not_held"
    # overall rule needs every case → inconclusive with missing evidence
    assert res["decision"] == "inconclusive"


def test_run_gated():
    from session_inspect import evaluate, manifest
    m = manifest.create(experiment="ctx", run="run_001",
                        cases=["case01"], variants=["baseline"], reps=1)
    # trial execution is effectful: no safe launch here → named unavailable
    res = evaluate.request_run(m)
    assert res["status"] == "unavailable"
    assert "no_safe_launch" in res["reason"]
    assert res["executed"] is False
    # replay recomputes from saved evidence: N never increases
    assert evaluate.replay_n({"n_independent": 3}) == 3
