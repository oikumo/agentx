"""T3-1 escape-replay fold (feature_070.escape_replay_fold).

Golden: op:plan predicted-block msg gains last_escape {scope,reason,ts}
from most-recent matching skip; read-only (agent must still call omt_skip).
"""

import json
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
OMT_Q_PLUGIN = REPO_ROOT / ".opencode" / "plugins" / "omt_q.ts"
SHARED_LIB = REPO_ROOT / ".opencode" / "lib" / "omt_shared.ts"

BUN = shutil.which("bun")


def _copy_real_ir(tmp_path: Path) -> None:
    ir_dst = tmp_path / ".meta" / ".omt"
    ir_dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        REPO_ROOT / ".meta" / ".omt" / "harness.ir.json",
        ir_dst / "harness.ir.json",
    )


def _write_ledger(tmp_path: Path, records: list[dict]) -> None:
    p = tmp_path / ".meta" / ".omt" / "ledger.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


_q_probe_template = """
import { initOmtShared } from "%LIB%"
initOmtShared(process.argv[2])
const mod = await import("%PLUGIN%")
const { tool } = await mod.default({ directory: process.argv[2], worktree: process.argv[2] })
const args = %ARGS%
const result = await tool.omt_q.execute(args, { sessionID: "%SESSION%" })
console.log(result)
"""


def _q_probe(args_str: str, session: str, tmp_path: Path) -> dict:
    assert BUN is not None, "bun runtime required"
    probe = tmp_path / "probe_t31.ts"
    probe.write_text(
        _q_probe_template
        .replace("%LIB%", str(SHARED_LIB))
        .replace("%PLUGIN%", str(OMT_Q_PLUGIN))
        .replace("%ARGS%", args_str)
        .replace("%SESSION%", session),
        encoding="utf-8",
    )
    out = subprocess.run([BUN, str(probe), str(tmp_path)],
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, f"bun probe failed:\n{out.stderr}\n---"
    return json.loads(out.stdout.strip().splitlines()[-1])


class TestEscapeReplayFold:
    """T3-1: blocked predicted entry carries most-recent matching skip."""

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_blocked_nav_carries_last_live_smoke_escape(self, tmp_path):
        _copy_real_ir(tmp_path)
        # Expired ts (30d ago, outside 8h UNLOCK_WINDOW): hasNavUnlock fallback
        # stays false so g.nav BLOCKS, but last_escape replay still surfaces
        # the most-recent matching skip (read-only signal, not an unlock).
        old_ts = (
            datetime.now(timezone.utc) - timedelta(days=30)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        _write_ledger(tmp_path, [
            {"ts": old_ts, "kind": "skip", "session": "ses_old",
             "scope": "nav", "purpose": "override", "reason": "live smoke"},
        ])
        out = _q_probe(
            json.dumps({"op": "plan", "path": "WORK.md",
                        "tool": "grep", "session": "ses_t31a"}),
            session="ses_t31a", tmp_path=tmp_path)
        assert out["op"] == "plan"
        chain = out["predicted_chain"]
        nav = next(d for d in chain if d["gate_id"] == "g.nav")
        assert nav["blocked"] is True, f"g.nav must block without nav consult: {nav}"
        assert nav["skip_ok"] is True
        assert "last_escape" in nav, f"blocked g.nav must carry last_escape: {nav}"
        le = nav["last_escape"]
        assert le["scope"] == "nav"
        assert "live smoke" in le["reason"]
        assert le["ts"] == old_ts

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_non_matching_scope_carries_no_escape(self, tmp_path):
        _copy_real_ir(tmp_path)
        fresh_ts = (
            datetime.now(timezone.utc) - timedelta(hours=1)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        _write_ledger(tmp_path, [
            {"ts": fresh_ts, "kind": "skip", "session": "ses_old",
             "scope": "tests", "purpose": "canary",
             "reason": "approved canary test"},
        ])
        out = _q_probe(
            json.dumps({"op": "plan", "path": "WORK.md",
                        "tool": "grep", "session": "ses_t31b"}),
            session="ses_t31b", tmp_path=tmp_path)
        chain = out["predicted_chain"]
        nav = next(d for d in chain if d["gate_id"] == "g.nav")
        assert nav["blocked"] is True
        assert "last_escape" not in nav, (
            f"scope=tests skip must NOT match g.nav: {nav}")

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_unblocked_carries_no_escape_and_still_requires_skip(self, tmp_path):
        _copy_real_ir(tmp_path)
        fresh_ts = (
            datetime.now(timezone.utc) - timedelta(hours=1)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        _write_ledger(tmp_path, [
            {"ts": fresh_ts, "kind": "skip", "session": "ses_old",
             "scope": "nav", "purpose": "override", "reason": "live smoke"},
        ])
        out = _q_probe(
            json.dumps({"op": "plan", "path": "src/agentx/ui/screens/main/main_controller.py",
                        "tool": "edit", "session": "ses_t31c"}),
            session="ses_t31c", tmp_path=tmp_path)
        chain = out["predicted_chain"]
        # edit tool does not trigger g.nav (search-tools only) — pick an
        # unblocked edit-gate (g.protect: path not in @protect) → no escape,
        # and blocked gates (if any) still require omt_skip (read-only fold).
        prot = next(d for d in chain if d["gate_id"] == "g.protect")
        assert prot["blocked"] is False
        assert "last_escape" not in prot
        for d in chain:
            if d.get("blocked"):
                assert "last_escape" not in d or isinstance(d["last_escape"], dict)
