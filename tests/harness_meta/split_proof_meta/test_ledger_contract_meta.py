"""Ledger projection contract goldens (T2, harness_wrapper_split).

Pins V7 Q4: `.meta/.omt/ledger.jsonl` + named read-only projections, plus the
"read-only = no writes outside append" test. Hermetic everywhere (tmp ledger,
real ledger + projections byte-untouched).

Projections (proposal, pinned here):
  WORK.compiled.md, .meta/.omt/nav.index.jsonl, .meta/.omt/harness.ir.json,
  .meta/.omt/net_state.sidecar.json, WORK.md ## Projects.

RED shape: CLI loaded lazily so missing impl FAILS (exit 1), never breaks
collection (exit 2).
"""

import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "omt"))

CLI = REPO / "scripts" / "omt" / "split_proof.py"
LEDGER = REPO / ".meta" / ".omt" / "ledger.jsonl"

PROJECTIONS = [
    "WORK.compiled.md",
    ".meta/.omt/nav.index.jsonl",
    ".meta/.omt/harness.ir.json",
    ".meta/.omt/net_state.sidecar.json",
    "WORK.md",
]


def _cli():
    try:
        return importlib.import_module("split_proof")
    except ModuleNotFoundError as e:
        raise AssertionError(f"RED: split_proof module missing: {e}")


def _run(*args):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(REPO),
    )


def test_projection_files_pinned():
    for rel in PROJECTIONS:
        assert (REPO / rel).is_file(), f"projection missing: {rel}"
    # Content pins (shape, not values — values drift by construction):
    assert "net_rev:" in (REPO / "WORK.compiled.md").read_text()
    assert "## Projects" in (REPO / "WORK.md").read_text()
    sidecar = json.loads((REPO / ".meta" / ".omt" / "net_state.sidecar.json").read_text())
    assert "revision" in sidecar
    # harness.ir.json is JSON; nav.index.jsonl is JSONL (one object per line).
    json.loads((REPO / ".meta" / ".omt" / "harness.ir.json").read_text())
    lines = (REPO / ".meta" / ".omt" / "nav.index.jsonl").read_text().splitlines()
    assert lines, "nav.index.jsonl empty"
    json.loads(lines[0])


def test_ledger_append_only_shape():
    assert LEDGER.is_file()
    raw = LEDGER.read_bytes()
    assert raw.endswith(b"\n")
    for i, line in enumerate(raw.splitlines(), 1):
        assert line.strip(), f"ledger blank line {i}"
        row = json.loads(line)
        assert "ts" in row, f"ledger row {i} missing ts"


def test_oracle_writes_only_via_append_hermetic(tmp_path):
    # Hermetic prove + attest-bridge must leave the real ledger AND every
    # projection byte-identical (writes go to --ledger tmp only).
    # Racy-honest under a PARALLEL suite (some other suite test appends the
    # real ledger — triage item 3): the real ledger may only GROW in the
    # window, no growth row may be a split_proof.* kind (ours went to tmp),
    # and the projections must stay byte-identical (nothing regenerates them
    # during the suite).
    before_ledger = LEDGER.read_bytes()
    before_proj = {rel: (REPO / rel).read_bytes() for rel in PROJECTIONS}
    led = tmp_path / "ledger.jsonl"
    p = _run("prove", "--lane", "both", "--out", str(tmp_path),
             "--ledger", str(led))
    assert p.returncode == 0, p.stderr
    a = _run("attest-bridge", "--ledger", str(led))
    assert a.returncode == 0, a.stderr
    after_ledger = LEDGER.read_bytes()
    assert after_ledger.startswith(before_ledger), (
        "real ledger mutated outside append"
    )
    growth = [ln for ln in after_ledger[len(before_ledger):].splitlines() if ln.strip()]
    for ln in growth:
        assert not json.loads(ln).get("kind", "").startswith("split_proof."), (
            "oracle wrote split_proof rows to the REAL ledger"
        )
    for rel in PROJECTIONS:
        assert (REPO / rel).read_bytes() == before_proj[rel], f"projection rewritten: {rel}"
    rows = [json.loads(l) for l in led.read_text().splitlines()]
    kinds = [r["kind"] for r in rows]
    assert kinds == ["split_proof.cert", "split_proof.cert", "split_proof.attest"]


def test_cert_chain_prefix_hermetic(tmp_path):
    led = tmp_path / "ledger.jsonl"
    _run("prove", "--lane", "both", "--out", str(tmp_path),
         "--ledger", str(led)).check_returncode()
    rows = [json.loads(l) for l in led.read_text().splitlines()]
    assert [r["lane"] for r in rows] == ["product", "harness"]
    assert rows[0]["ledger_sha"] == _cli().GENESIS_SHA
    raw = led.read_bytes().splitlines(keepends=True)
    assert rows[1]["ledger_sha"] == hashlib.sha256(raw[0]).hexdigest()
    # Prefix-match: row-0 genesis + row-1 sha are strict prefixes of today.
    mod = _cli()
    assert mod._ledger_prefix_match(rows[0]["ledger_sha"], led) == 0
    assert mod._ledger_prefix_match(rows[1]["ledger_sha"], led) == 1
# TA: gotcha: GOTCHA_LEDGER_WINDOW_RACY: the REAL ledger grows during the parallel suite (omt_q live-root probes self-log kind:q telemetry — test_omt_q.py +1/run, test_omt_q_audit.py +4/run, bisected 2026-10-10). Byte-equality before/after windows on the real ledger are racy and fail intermittently; assert append-only (startswith) + no growth rows of the kind under test + exact rows in the --ledger tmp instead (racy-honest pattern, pinned here).
