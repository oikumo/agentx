"""E2 goldens: g.split_proof membrane gate (feature_138).

Bun probes drive the REAL gate_driver (runBeforeGatesDry + runBeforeGates)
against hermetic tmp roots: copied IR + seeded ledger + certs cut by the REAL
split_proof CLI with --root/--ledger/--out pointed at tmp (the real ledger
and repo are never touched).

Pins (V7 §E E2 — fail-open locally/advisory, fail-closed in CI):
- no pinned certs → advisory locally (fired, not blocked, notify carries
  the clearing action), BLOCKED with CI=true
- fresh pinned chain → SILENT pass locally and in CI (no notify) — this also
  pins the TS cert_sha recompute byte-agreeing with Python-cut certs (any
  cross-language drift would advise instead of staying silent)
- tampered cert (verdict) → advisory locally, BLOCKED in CI
- live composition path (runBeforeGates) never throws locally (fail-open)
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
SHARED_LIB = REPO_ROOT / ".opencode" / "lib" / "omt_shared.ts"
DRIVER = REPO_ROOT / ".opencode" / "lib" / "enforcer" / "gate_driver.ts"
STATE = REPO_ROOT / ".opencode" / "lib" / "enforcer" / "session_state.ts"
IR = REPO_ROOT / ".meta" / ".omt" / "harness.ir.json"
CLI = REPO_ROOT / "scripts" / "omt" / "split_proof.py"
# TA: gotcha: gotcha: GOTCHA_PROVE_CERTS_ROOT_STRAY: split_proof.py prove defaults --out '.' — lane certs land at REPO ROOT where the @var root_allowlist stray-hygiene check errors on them (FILESYSTEM-based, NOT a git check — untracking/ignoring does not help; only absence does), failing every check-expecting test (4 in feature_141 R2 2026-10-10: harnessc zero-errors + projections-fresh + budget_diet live pin + toolbox harness.budget_check seed); a root cert present at commit time also gets swept by git add -A. Prove with --out /tmp/... (or delete after); .gitignore carries /split_proof_{product,harness}.cert.json as belt-and-braces; never allowlist the strays.
MANIFEST = REPO_ROOT / "scripts" / "omt" / "split_proof_exemptions.json"
BENCH_TASKS = REPO_ROOT / "scripts" / "omt" / "bench" / "tasks.py"

BUN = shutil.which("bun")
SESSION = "e2-split-proof-probe"
TARGET = "scripts/omt/probe_target.py"

_DRY_PROBE = """
import { initOmtShared } from "%LIB%"
import { runBeforeGatesDry } from "%DRIVER%"
import { createSessionState } from "%STATE%"
initOmtShared(process.argv[2])
if (process.argv[4] === "CI") process.env.CI = "true"
const notes: string[] = []
const env: any = {
  client: {}, $: {}, directory: process.argv[2],
  state: createSessionState(),
  safeLog: () => {},
  notify: async (m: string) => { notes.push(String(m)) },
}
const rel = process.argv[3]
const ctx: any = {
  env, session: "e2-split-proof-probe", tool: "edit",
  input: { tool: "edit" }, output: { args: { filePath: rel } },
  rel, abs: process.argv[2] + "/" + rel, memo: new Map(),
}
const decisions = await runBeforeGatesDry(ctx)
const row = decisions.find((d: any) => d.gate_id === "g.split_proof")
console.log(JSON.stringify({ row, notes }))
"""

_LIVE_PROBE = """
import { initOmtShared } from "%LIB%"
import { runBeforeGates } from "%DRIVER%"
import { createSessionState, OmtBlock } from "%STATE%"
initOmtShared(process.argv[2])
const notes: string[] = []
const env: any = {
  client: {}, $: {}, directory: process.argv[2],
  state: createSessionState(),
  safeLog: () => {},
  notify: async (m: string) => { notes.push(String(m)) },
}
const rel = process.argv[3]
let out: any = { result: "ALLOWED", notes: [] }
try {
  await runBeforeGates(env, "e2-split-proof-probe",
    { tool: "edit" }, { args: { filePath: rel } },
    process.argv[2] + "/" + rel)
  out = { result: "ALLOWED", notes }
} catch (e: any) {
  out = { result: "BLOCKED", message: String(e?.message || e), notes }
}
console.log(JSON.stringify(out))
"""


def _setup_root(tmp_path: Path, *, pin_certs: bool) -> Path:
    """Hermetic probe root: copied IR + seeded ledger + harness target file;
    optionally pins certs cut by the REAL CLI against this root."""
    meta = tmp_path / ".meta" / ".omt"
    meta.mkdir(parents=True, exist_ok=True)
    shutil.copy2(IR, meta / "harness.ir.json")
    ledger = meta / "ledger.jsonl"
    ledger.write_text(json.dumps({"ts": "2026-10-10T00:00:00.000Z",
                                  "kind": "probe_seed"}) + "\n",
                      encoding="utf-8")
    target = tmp_path / TARGET
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# hermetic membrane probe target\n", encoding="utf-8")
    if pin_certs:
        # The exemption manifest pins agentx-string lines in bench fixtures,
        # so the probe root carries byte-copies of every pinned file (pinned
        # lines stay pinned; copies scan clean like the originals).
        pinned = {e["file"] for e in
                  json.loads(MANIFEST.read_text(encoding="utf-8"))
                  ["python_exemptions"]}
        for rel in sorted(pinned):
            dst = tmp_path / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO_ROOT / rel, dst)
        p = subprocess.run(
            [sys.executable, str(CLI),
             "--root", str(tmp_path), "--manifest", str(MANIFEST),
             "prove", "--lane", "both",
             "--ledger", str(ledger), "--out", str(meta)],
            capture_output=True, text=True, timeout=300, cwd=str(REPO_ROOT))
        assert p.returncode == 0, f"hermetic prove failed:\n{p.stderr}"
    return tmp_path


def _run_bun(probe_src: str, root: Path, *, ci: bool = False) -> dict:
    assert BUN is not None, "bun runtime required (guard against skipif bypass)"
    probe = root / "probe.ts"
    probe.write_text(
        probe_src.replace("%LIB%", str(SHARED_LIB))
        .replace("%DRIVER%", str(DRIVER))
        .replace("%STATE%", str(STATE)),
        encoding="utf-8")
    env = {**os.environ,
           "OMT_LEDGER_PATH": str(root / ".meta" / ".omt" / "ledger.jsonl")}
    if ci:
        env = {**env, "CI": "true"}
    out = subprocess.run(
        [BUN, str(probe), str(root), TARGET, "CI" if ci else ""],
        capture_output=True, text=True, timeout=90, env=env)
    assert out.returncode == 0, f"bun probe failed:\n{out.stderr}\n---"
    return json.loads(out.stdout.strip().splitlines()[-1])


@pytest.mark.skipif(BUN is None, reason="bun runtime not available")
def test_no_certs_advisory_local(tmp_path):
    _setup_root(tmp_path, pin_certs=False)
    data = _run_bun(_DRY_PROBE, tmp_path)
    row = data["row"]
    assert row["fired"] is True
    assert row["blocked"] is False
    assert any("g.split_proof" in n and "no pinned split_proof certs" in n
               for n in data["notes"]), data["notes"]
    assert any("prove --lane both" in n for n in data["notes"])


@pytest.mark.skipif(BUN is None, reason="bun runtime not available")
def test_no_certs_strict_ci(tmp_path):
    _setup_root(tmp_path, pin_certs=False)
    data = _run_bun(_DRY_PROBE, tmp_path, ci=True)
    row = data["row"]
    assert row["fired"] is True
    assert row["blocked"] is True, data
    assert "g.split_proof" in row["msg"]


@pytest.mark.skipif(BUN is None, reason="bun runtime not available")
def test_fresh_chain_silent_pass(tmp_path):
    _setup_root(tmp_path, pin_certs=True)
    data = _run_bun(_DRY_PROBE, tmp_path)
    row = data["row"]
    assert row["fired"] is True
    assert row["blocked"] is False, data
    assert data["notes"] == [], f"fresh chain must be silent: {data['notes']}"


@pytest.mark.skipif(BUN is None, reason="bun runtime not available")
def test_fresh_chain_silent_ci(tmp_path):
    _setup_root(tmp_path, pin_certs=True)
    data = _run_bun(_DRY_PROBE, tmp_path, ci=True)
    assert data["row"]["blocked"] is False, data
    assert data["notes"] == []


@pytest.mark.skipif(BUN is None, reason="bun runtime not available")
def test_tampered_cert_advisory_then_strict(tmp_path):
    _setup_root(tmp_path, pin_certs=True)
    cert = tmp_path / ".meta" / ".omt" / "split_proof_product.cert.json"
    data = json.loads(cert.read_text(encoding="utf-8"))
    data["firewall_verdict"] = "VIOLATION:1"
    cert.write_text(json.dumps(data), encoding="utf-8")
    local = _run_bun(_DRY_PROBE, tmp_path)
    assert local["row"]["blocked"] is False
    assert any("VIOLATION:1" in n for n in local["notes"]), local["notes"]
    strict = _run_bun(_DRY_PROBE, tmp_path, ci=True)
    assert strict["row"]["blocked"] is True, strict
    assert "VIOLATION:1" in strict["row"]["msg"]


@pytest.mark.skipif(BUN is None, reason="bun runtime not available")
def test_live_path_never_blocks_local(tmp_path):
    _setup_root(tmp_path, pin_certs=False)
    data = _run_bun(_LIVE_PROBE, tmp_path)
    assert data["result"] == "ALLOWED", data
    assert any("g.split_proof" in n for n in data["notes"]), data["notes"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
