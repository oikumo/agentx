"""Tier-1 cert replay + truncation + compare/concretize pins (canary-approved)."""
import json
import subprocess
import sys


def run(*argv):
    r = subprocess.run([sys.executable, "scripts/reason/check.py", *argv],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_cert_replay_stable_and_budget():
    a = run("check", "--program", "stage0_ir.json")
    b = run("check", "--program", "stage0_ir.json")
    assert a["data"]["certificate_digest"] == b["data"]["certificate_digest"]
    assert len(json.dumps(a)) <= 4096
    for key in ("structural", "premises", "execution", "goal"):
        assert key in a["data"]


def test_explain_slice_known_and_unknown():
    known = run("explain", "--program", "stage0_ir.json", "--node", "accept_tests")
    assert known["slice"]["node"] == "accept_tests"
    assert known["slice"]["first_unsupported"]["code"] == "subject_digest_mismatch"
    unknown = run("explain", "--program", "stage0_ir.json", "--node", "nope-node")
    assert unknown["slice"]["verdict"] == "unknown"


def test_compare_files_only_permits_identical():
    env = run("compare", "--program-a", "stage0_ir.json", "--program-b", "stage0_ir.json",
              "--contract", "files-only-v1")
    assert env["verdict"] == "equivalent"


def test_compare_unknown_contract_is_unknown():
    env = run("compare", "--program-a", "stage0_ir.json", "--program-b", "stage0_ir.json",
              "--contract", "weird-v9")
    assert env["verdict"] == "unknown"


def test_concretize_bounded_and_over_bound_unknown():
    ok = run("concretize", "--row", '{"row":"d3"}', "--bound", "8")
    assert ok["count"] == 4 and ok["distinguishing_info"][0] == "recorded"
    over = run("concretize", "--row", '{"row":"d3"}', "--bound", "2")
    assert over["verdict"] == "unknown" and over["unknown"]["reason"] == "bound_exceeded"
