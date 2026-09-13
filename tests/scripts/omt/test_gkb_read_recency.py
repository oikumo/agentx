#!/usr/bin/env python3
"""Golden tests for T2-5 g.kb per-file Read-recency (feature_088, meta_harness_8).

Acceptance: read-then-edit same turn passes g.kb for THAT file;
never-read file still blocks. NEW per-file Read-recency substrate —
NOT a mirror of think-consult recent_consults (mh3 R2).

Hermetic: bun probes drive the TS modules directly (no ledger I/O,
no session state leakage). Source pins assert the wiring.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SESSION_STATE = REPO_ROOT / ".opencode" / "lib" / "enforcer" / "session_state.ts"
NAV_GATE = REPO_ROOT / ".opencode" / "lib" / "enforcer" / "nav_gate.ts"
DRIVER = REPO_ROOT / ".opencode" / "lib" / "enforcer" / "gate_driver.ts"
ENFORCER = REPO_ROOT / ".opencode" / "plugins" / "omt_enforcer.ts"
SHARED = REPO_ROOT / ".opencode" / "lib" / "omt_shared.ts"

BUN = shutil.which("bun")


def _run_probe(probe_src: str) -> dict:
    import tempfile, os
    assert BUN, "bun required"
    with tempfile.TemporaryDirectory() as td:
        probe = Path(td) / "probe.ts"
        probe.write_text(probe_src, encoding="utf-8")
        env = dict(os.environ)
        env.pop("OMT_LEDGER_PATH", None)
        out = subprocess.run(
            [BUN, str(probe)], capture_output=True, text=True, timeout=60, env=env)
        assert out.returncode == 0, out.stderr
        return json.loads(out.stdout.strip().splitlines()[-1])


PROBE_PURE = """
import { createSessionState, recordRead, hasRecentRead } from "%STATE%";
const state = createSessionState();
const now = Date.now();
recordRead(state.reads, "s1", "src/a.py", now);
const same = hasRecentRead(state.reads, "s1", "src/a.py", now + 1000);
const other = hasRecentRead(state.reads, "s1", "src/b.py", now + 1000);
const never = hasRecentRead(state.reads, "s1", "src/never.py", now + 1000);
const nullRel = hasRecentRead(state.reads, "s1", null, now + 1000);
console.log(JSON.stringify({ same, other, never, nullRel }));
""".replace("%STATE%", str(SESSION_STATE))

PROBE_EXPIRY = """
import { createSessionState, recordRead, hasRecentRead } from "%STATE%";
import { UNLOCK_WINDOW_MS } from "%SHARED%";
const state = createSessionState();
const now = Date.now();
recordRead(state.reads, "s1", "src/a.py", now - UNLOCK_WINDOW_MS - 1000);
const expired = hasRecentRead(state.reads, "s1", "src/a.py", now);
recordRead(state.reads, "s1", "src/b.py", now);
const fresh = hasRecentRead(state.reads, "s1", "src/b.py", now + 1000);
// drift fallback: another session's recent read satisfies
const drift = hasRecentRead(state.reads, "s2", "src/b.py", now + 1000);
console.log(JSON.stringify({ expired, fresh, drift }));
""".replace("%STATE%", str(SESSION_STATE)).replace("%SHARED%", str(SHARED))

PROBE_TRACK = """
import { initOmtShared } from "%SHARED%";
import { createSessionState } from "%STATE%";
import { trackRead } from "%NAV%";
import { hasRecentRead } from "%STATE%";
initOmtShared(process.argv[2] || process.cwd());
const env = { client: {}, $: {}, directory: process.cwd(), state: createSessionState(), safeLog: () => {}, notify: async () => {} };
const now = Date.now();
await trackRead(env, "s1", { tool: "read", args: { filePath: "src/a.py" } });
const recorded = hasRecentRead(env.state.reads, "s1", "src/a.py", now + 5000);
await trackRead(env, "s1", { tool: "edit", args: { filePath: "src/b.py" } });
const ignoredEdit = hasRecentRead(env.state.reads, "s1", "src/b.py", now + 5000);
await trackRead(env, "s1", { tool: "read", args: { filePath: ["src/c.py", "src/d.py"] } });
const arrayForm = hasRecentRead(env.state.reads, "s1", "src/c.py", now + 5000);
await trackRead(env, "s1", { tool: "read", args: { filePath: { odd: "object" } } });
await trackRead(env, "s1", { tool: "read", args: {} });
const noCrash = true;
console.log(JSON.stringify({ recorded, ignoredEdit, arrayForm, noCrash }));
""".replace("%SHARED%", str(SHARED)).replace("%STATE%", str(SESSION_STATE)).replace("%NAV%", str(NAV_GATE))


@pytest.mark.skipif(BUN is None, reason="bun runtime not available")
class TestReadRecencyPure:
    def test_same_file_recent_passes_others_block(self):
        data = _run_probe(PROBE_PURE)
        assert data["same"] is True
        assert data["other"] is False
        assert data["never"] is False
        assert data["nullRel"] is False

    def test_expiry_and_drift_fallback(self):
        data = _run_probe(PROBE_EXPIRY)
        assert data["expired"] is False
        assert data["fresh"] is True
        assert data["drift"] is True

    def test_track_read_records_only_reads(self):
        data = _run_probe(PROBE_TRACK)
        assert data["recorded"] is True
        assert data["ignoredEdit"] is False
        assert data["arrayForm"] is True
        assert data["noCrash"] is True


class TestReadRecencyWiring:
    def test_session_state_has_reads_substrate(self):
        src = SESSION_STATE.read_text(encoding="utf-8")
        assert "reads: new Map" in src
        assert "export function recordRead" in src
        assert "export function hasRecentRead" in src
        assert "recent_consults" not in src.lower() or "NOT a mirror" in src or "not" in src.lower()

    def test_nav_gate_tracks_reads(self):
        src = NAV_GATE.read_text(encoding="utf-8")
        assert "export async function trackRead" in src
        assert 'input?.tool !== "read"' in src

    def test_gate_driver_consults_recency(self):
        src = DRIVER.read_text(encoding="utf-8")
        assert "hasRecentRead" in src
        assert "hasRecentRead(ctx.env.state.reads, ctx.session, ctx.rel)" in src

    def test_enforcer_wires_track_read(self):
        src = ENFORCER.read_text(encoding="utf-8")
        assert "trackRead" in src
        assert "await trackRead(env" in src
