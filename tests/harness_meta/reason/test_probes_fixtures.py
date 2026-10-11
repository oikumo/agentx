"""Tier-1 probe fixtures via SSOT (§15.8 1–7 replay, canary-approved).

Shells out to scripts/reason/check.py (the same binary the TS proxy calls).
Byte-stability: check program_digest must equal S0 IR digest across runs.
"""
import json
import subprocess
import sys


def check(program="stage0_ir.json", contract="completion-relevant-v1"):
    r = subprocess.run([sys.executable, "scripts/reason/check.py", "check",
                        "--program", program, "--contract", contract],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_probe1_next_discrepancy_refuses_as_missing_premise():
    env = check()
    assert env["ok"] is True
    assert env["data"]["premises"] in ("invalid", "unknown")
    assert any(i["code"] == "subject_digest_mismatch" for i in env["data"]["issues"])


def test_probe2_reorder_split_under_contracts():
    files_only = check(contract="files-only-v1")
    completion = check(contract="completion-relevant-v1")
    assert files_only["data"]["observation_contract"] == "files-only-v1"
    assert completion["data"]["observation_contract"] == "completion-relevant-v1"
    # Same program, different contracts → envelope records the contract (split verdicts live in compare).
    assert files_only["data"]["program_digest"] == completion["data"]["program_digest"]


def test_probe3_stale_agreement_shape():
    env = check()
    issue = next(i for i in env["data"]["issues"] if i["code"] == "subject_digest_mismatch")
    assert issue["expected"] == "artifact:h2" and issue["observed"] == "receipt-subject:h1"
    assert issue["next_obligation"]


def test_probe6_fresh_obligations_and_unknown_d3():
    env = check()
    assert any(u["node"] == "d3" for u in env["data"]["unknowns"])


def test_probe7_digest_stable():
    a = check()["data"]["program_digest"]
    b = check()["data"]["program_digest"]
    assert a == b and a.startswith("sha256:")
    c = json.load(open(".sandbox/harness_reason/stage0_ir.json"))
    import hashlib
    expect = "sha256:" + hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest()[:16]
    assert a == expect
