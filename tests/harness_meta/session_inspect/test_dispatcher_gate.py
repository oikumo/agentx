"""RED 133 — dispatcher wires run_gate (no launches)."""
import json


def _manifest():
    return {"version": 1, "experiment": "context_strategy", "run": "run_001",
            "cases": ["markdown-summary", "python-fix"],
            "variants": ["baseline", "candidate"], "reps": 3}


def test_dispatcher_refuses_invalid_manifest():
    from session_inspect import service
    res = service.dispatch("experiment", {"sub": "run", "manifest": json.dumps({"version": 1})})
    assert res["ok"] is False
    # S5/S6 contract: run refusals stay no_safe_launch, detail keeps manifest_invalid cause
    assert res.get("reason") == "no_safe_launch"
    assert "manifest_invalid" in str(res.get("detail", ""))
    assert res.get("executed", False) is False


def test_dispatcher_no_safe_launch_without_p():
    from session_inspect import service
    m = _manifest()
    m["budgets"] = {"tokens": 1000, "time_s": 60, "concurrency": 1}
    m["isolation"] = {"base": "/tmp/mh133-iso"}
    res = service.dispatch("experiment", {"sub": "run", "manifest": json.dumps(m)})
    assert res["ok"] is False
    assert "no_safe_launch" in str(res.get("reason", ""))
    assert res.get("executed", False) is False


def test_dispatcher_allowed_with_gate_pass():
    from session_inspect import service
    m = _manifest()
    m["budgets"] = {"tokens": 1000, "time_s": 60, "concurrency": 1}
    m["isolation"] = {"base": "/tmp/mh133-iso"}
    m["claims"] = {"held": 12}
    m["explicit_p"] = True
    res = service.dispatch("experiment", {"sub": "run", "manifest": json.dumps(m)})
    # Wiring target: gate pass → ok True, allowed True, still executed False
    assert res["ok"] is True
    assert res["result"]["allowed"] is True
    assert res["result"]["n_trials"] == 12
    assert res["result"].get("executed", False) is False
