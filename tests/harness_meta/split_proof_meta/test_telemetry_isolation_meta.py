"""Telemetry isolation golden (feature_148, harness_wrapper_split).

Proves PROPOSAL_V7 telemetry-isolation: omt_q live probes read the live
substrate without polluting the real ledger when OMT_Q_TELEMETRY=off.

- Live probe with flag off: real ledger line-count unchanged, envelope valid.
- Hermetic probe default: tmp ledger gains exactly 1 kind:q row (telemetry
  still logged hermetically; production default unchanged for ceremony/meter).

RED shape: bun missing skips; plugin missing fails (never breaks collection).
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
PLUGIN = REPO / ".opencode" / "plugins" / "omt_q.ts"
LIB = REPO / ".opencode" / "lib" / "omt_shared.ts"
BUN = shutil.which("bun")

PROBE = """
import { initOmtShared } from "%LIB%"
initOmtShared(process.argv[2])
const mod = await import("%PLUGIN%")
const plugin = mod.default
const captured = {}
const mockCtx = {
  location: { directory: process.argv[2], project: { id: "test", directory: process.argv[2], canonical: process.argv[2] } },
  options: {},
  tool: {
    transform: async (cb) => {
      const editor = { add: (t) => { captured[t.name] = t }, list: () => Object.values(captured), get: (id) => captured[id], update: () => {}, remove: () => {}, namespace: () => {} }
      cb(editor)
      return { dispose: async () => {} }
    },
    hook: async () => ({ dispose: async () => {} }),
    list: async () => [], reload: async () => {},
  },
  event: { subscribe: async function* () {} },
  storage: { get: async () => undefined, set: async () => {}, remove: async () => {}, scan: async () => ({ entries: [] }) },
}
await plugin.setup(mockCtx)
const result = await captured["omt_q"].execute(%ARGS%, { sessionID: "ses_t148" })
console.log(typeof result === "string" ? result : (result.content ?? JSON.stringify(result)))
"""


def _ledger_lines() -> int:
    p = REPO / ".meta" / ".omt" / "ledger.jsonl"
    if not p.exists():
        return 0
    return sum(1 for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip())


def _run(args_json: str, root: Path, probe_file: Path, env_extra: dict | None) -> dict:
    probe_file.write_text(
        PROBE.replace("%LIB%", str(LIB)).replace("%PLUGIN%", str(PLUGIN)).replace("%ARGS%", args_json),
        encoding="utf-8",
    )
    env = {**os.environ, **(env_extra or {})} if env_extra else None
    out = subprocess.run(["bun", str(probe_file), str(root)], capture_output=True, text=True, timeout=60, env=env)
    assert out.returncode == 0, f"bun probe failed:\n{out.stderr}\n---"
    return json.loads(out.stdout.strip().splitlines()[-1])


@pytest.mark.skipif(BUN is None, reason="bun not available")
def test_live_probe_with_flag_off_does_not_grow_real_ledger(tmp_path):
    before = _ledger_lines()
    out = _run(json.dumps({"op": "state"}), REPO, tmp_path / "probe_live.ts", {"OMT_Q_TELEMETRY": "off"})
    assert out["op"] == "state"
    assert "as_of_commit" in out
    after = _ledger_lines()
    assert after == before, f"live probe with OMT_Q_TELEMETRY=off grew real ledger: {before} -> {after}"


@pytest.mark.skipif(BUN is None, reason="bun not available")
def test_hermetic_probe_default_still_logs_to_tmp_ledger(tmp_path):
    # Hermetic root: copy IR so loadIr works, write empty ledger.
    ir_dst = tmp_path / ".meta" / ".omt"
    ir_dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO / ".meta" / ".omt" / "harness.ir.json", ir_dst / "harness.ir.json")
    (ir_dst / "ledger.jsonl").write_text("", encoding="utf-8")
    out = _run(json.dumps({"op": "state"}), tmp_path, tmp_path / "probe_herm.ts", None)
    assert out["op"] == "state"
    lines = [ln for ln in (ir_dst / "ledger.jsonl").read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, f"hermetic default should log exactly 1 q row to tmp ledger, got {len(lines)}"
    rec = json.loads(lines[0])
    assert rec.get("kind") == "q" and rec.get("op") == "state"
