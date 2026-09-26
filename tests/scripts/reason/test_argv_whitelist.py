"""Tier-1 argv whitelist pins (canary-approved, stdlib+pytest, no harness writes).

Mirrors scripts/reason/check.py subparsers + .opencode/plugins/reason_check.ts ALLOW.
Widening the enum (e.g. adding plan) or a flag must update BOTH + this pin.
"""
import subprocess
import sys

OPS = ("check", "explain", "compare", "concretize")

ALLOW = {
    "check": {"--program", "--context", "--contract"},
    "explain": {"--program", "--node", "--context", "--contract"},
    "compare": {"--program-a", "--program-b", "--contract"},
    "concretize": {"--row", "--bound"},
}


def run(*argv):
    r = subprocess.run([sys.executable, "scripts/reason/check.py", *argv],
                       capture_output=True, text=True)
    return r


def test_closed_enum_rejects_plan():
    r = run("plan", "--program", "stage0_ir.json")
    assert r.returncode != 0
    assert "invalid choice" in r.stderr


def test_each_op_help_lists_whitelisted_flags():
    import re
    for op, flags in ALLOW.items():
        r = subprocess.run([sys.executable, "scripts/reason/check.py", op, "--help"],
                           capture_output=True, text=True)
        assert r.returncode == 0
        for f in flags:
            assert f in r.stdout, f"{op} help missing {f}"


def test_unknown_flag_rejected():
    r = run("check", "--program", "stage0_ir.json", "--evil", "1")
    assert r.returncode != 0
    assert "unrecognized arguments" in r.stderr


def test_concretize_bound_type_pinned():
    r = run("concretize", "--row", '{"row":"d3"}', "--bound", "notanint")
    assert r.returncode != 0
