"""RED 132 — guarded run pre-checks (operation_spec_001, no launches)."""


def _manifest():
    from session_inspect import manifest
    return manifest.create(experiment="context_strategy", run="run_001",
                           cases=["markdown-summary", "python-fix"],
                           variants=["baseline", "candidate"], reps=3)


def test_gate_rejects_invalid_manifest():
    from session_inspect import run_gate
    bad = {"version": 1, "experiment": "context_strategy"}
    try:
        run_gate.check_manifest(bad)
        assert False, "invalid manifest must fail"
    except Exception as exc:
        assert "manifest_invalid" in str(exc)


def test_gate_refuses_protected_isolation():
    from session_inspect import run_gate
    m = _manifest()
    try:
        run_gate.check_isolation(m, base="/tmp/mh132-iso", dest=".env")
        assert False, "protected dest must fail"
    except Exception as exc:
        assert "isolation_unavailable" in str(exc) or "protected" in str(exc)


def test_gate_refuses_missing_budgets():
    from session_inspect import run_gate
    m = _manifest()
    try:
        run_gate.check_budgets(m, budgets={})
        assert False, "missing budgets must fail"
    except Exception as exc:
        assert "budget_missing" in str(exc)


def test_gate_no_safe_launch_without_claims():
    from session_inspect import run_gate
    m = _manifest()
    res = run_gate.gate_run(m, isolation={"base": "/tmp/mh132-iso"},
                            budgets={"tokens": 1000, "time_s": 60, "concurrency": 1},
                            claims=None, explicit_p=False)
    assert res["allowed"] is False
    assert "no_safe_launch" in str(res.get("reason", "")) or "p" in str(res.get("reason", "")).lower()
    assert res.get("executed", False) is False


def test_gate_allows_only_when_all_pass():
    from session_inspect import run_gate
    m = _manifest()
    res = run_gate.gate_run(m, isolation={"base": "/tmp/mh132-iso"},
                            budgets={"tokens": 1000, "time_s": 60, "concurrency": 1},
                            claims={"held": 12}, explicit_p=True)
    assert res["allowed"] is True
    assert res["n_trials"] == 12
    assert res.get("executed", False) is False
