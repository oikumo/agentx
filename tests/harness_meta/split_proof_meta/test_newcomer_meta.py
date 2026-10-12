"""Newcomer probe golden (feature_138, Oracle firewall slice).

AgentX-vision guard: a student runs `uv run agentx`, sends `help`, gets an
answer, exits on EOF — with zero harness knowledge. v1 asserts boot +
meaningful answer (mentions "agent") + clean exit; exact REPL wording is NOT
pinned (deferred with note below).

Deviation (2026-10-10, pinned in split_proof.py): the 0.2.0 console is a
command REPL (`help` + Ctrl+C/EOF to exit) — single letters answer "Unknown
command". The V7 "`c`/`q`" narrative rotted; this golden guards what the
console IS (boot + answer + clean exit), mirroring newcomer_probe (`help`).
"""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CLI = REPO / "scripts" / "omt" / "split_proof.py"

TIMEOUT = 120


def _boot_repl():
    return subprocess.run(
        ["uv", "run", "agentx"],
        input="help\n",
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        cwd=str(REPO),
    )


def test_newcomer_repl_boots_answers_quits():
    p = _boot_repl()
    assert p.returncode == 0, p.stderr[-2000:]
    assert p.stdout.strip() != "", "REPL answered nothing to `help`"
    assert "agent" in p.stdout.lower(), "newcomer answer must mention the agent (vision guard)"


def test_cli_newcomer_probe_agrees():
    p = subprocess.run(
        [sys.executable, str(CLI), "newcomer-probe"],
        capture_output=True,
        text=True,
        timeout=TIMEOUT + 60,
        cwd=str(REPO),
    )
    assert p.returncode == 0, p.stderr
    assert "pass" in p.stdout.lower()
