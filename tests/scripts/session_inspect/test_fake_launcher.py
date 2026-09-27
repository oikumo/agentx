"""RED 134 — fake-executor launcher (no live runs)."""


def _manifest():
    from session_inspect import manifest
    return manifest.create(experiment="context_strategy", run="run_001",
                           cases=["markdown-summary", "python-fix"],
                           variants=["baseline", "candidate"], reps=3)


def test_fake_plans_12_in_order():
    from session_inspect import launcher
    trials = launcher.plan_trials(_manifest())
    assert len(trials) == 12
    assert trials[0]["trial"].endswith("_rep01")
    assert len({t["trial"] for t in trials}) == 12


def test_fake_dispatch_sequential_once_each():
    from session_inspect import launcher
    calls = []

    def fake_executor(trial, isolation):
        calls.append(trial["trial"])
        return {"trial": trial["trial"], "outcome": "pass", "duration_s": 1, "attempt": 1}

    trials = launcher.plan_trials(_manifest())[:3]
    results = [launcher.dispatch_fake(t, executor=fake_executor) for t in trials]
    assert [r["trial"] for r in results] == calls
    assert all(r["outcome"] == "pass" for r in results)


def test_timeout_strict_once_no_retry():
    from session_inspect import launcher

    def slow(trial, isolation):
        return {"trial": trial["trial"], "outcome": "pass", "duration_s": 999, "attempt": 1}

    trials = launcher.plan_trials(_manifest())[:1]
    res = launcher.enforce_timeout(launcher.dispatch_fake(trials[0], executor=slow))
    assert res["outcome"] == "timeout_failed"
    assert res["attempt"] == 1


def test_run_fake_refuses_without_gate():
    from session_inspect import launcher
    m = _manifest()
    res = launcher.run_fake(m, executor=lambda t, isolation: {"trial": t["trial"], "outcome": "pass", "duration_s": 1, "attempt": 1},
                            claims=None, explicit_p=False)
    assert res["allowed"] is False
    assert res.get("executed", False) is False
