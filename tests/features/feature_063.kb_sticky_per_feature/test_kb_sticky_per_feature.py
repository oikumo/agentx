"""Wave 0 / P0-3 kb_sticky_per_feature — feature_063.

Contract (GREEN pins the implementation):
- STICKY: a kb_consult ledger record (written by nav_gate.kbTrack on any
  omt_kb_nav op, scoped to the ACTIVE feature + scope + task_type) satisfies
  g.kb for the SAME feature across sessions/restarts — the consult no longer
  re-pays every session (message-only improvement over the session-only
  in-memory flag).
- SCOPE CHANGE: major_feature/new_screen re-consult when the CURRENT scope
  string differs from the consult's scope (string identity — a rephrased scope
  IS a scope change). minors/bug_fix/refactor/test/docs ignore scope: any
  same-feature consult within the window satisfies.
- GUARDRAILS: g.think/g.protect untouched (kbTrack only feeds g.kb); the write
  is ledger-backed (auditable, window-visible) — NOT an in-memory flag (C2
  round-3: sticky in-memory flags would outlive a later scope change).

Bun probes exercise the REAL TS modules (feature_054 idiom): hermetic ledger
via OMT_LEDGER_PATH, real IR for the full before-chain probe.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
SESSION_STATE = REPO_ROOT / ".opencode" / "lib" / "enforcer" / "session_state.ts"
GATE_DRIVER = REPO_ROOT / ".opencode" / "lib" / "enforcer" / "gate_driver.ts"
NAV_GATE = REPO_ROOT / ".opencode" / "lib" / "enforcer" / "nav_gate.ts"

BUN = shutil.which("bun")

F = "feature_063.kb_sticky_per_feature"


# --- ledger record builders ---------------------------------------------------

def _ts(hours_ago: float = 0.0) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).isoformat()


def _phase(tt: str, session: str = "s1", feature: str = F, scope: str = "c3 test",
           hours_ago: float = 0.0) -> dict:
    return {"ts": _ts(hours_ago), "kind": "phase", "session": session,
            "task_type": tt, "phase": "Programming", "scope": scope,
            "feature": feature, "design_doc": "", "tdd_mode": False}


def _kb_consult(feature: str = F, scope: str = "c3 test", tt: str = "minor_feature",
                session: str = "s1", hours_ago: float = 0.0) -> dict:
    return {"ts": _ts(hours_ago), "kind": "kb_consult", "session": session,
            "feature": feature, "scope": scope, "task_type": tt}


# --- bun probe plumbing -------------------------------------------------------

def _run_probe(tmp_path: Path, body: str, cwd: Path | None = None,
               extra_env: dict | None = None) -> dict:
    """Write body to tmp/probe.ts, run bun with a hermetic ledger env."""
    assert BUN is not None, "bun runtime required (guard against skipif bypass)"
    ledger = tmp_path / "ledger.jsonl"
    probe = tmp_path / "probe.ts"
    probe.write_text(body, encoding="utf-8")
    env = {**os.environ, "OMT_LEDGER_PATH": str(ledger),
           **(extra_env or {})}
    out = subprocess.run([BUN, str(probe)], capture_output=True, text=True,
                         timeout=90, cwd=str(cwd or tmp_path), env=env)
    assert out.returncode == 0, f"bun probe failed:\n{out.stderr}\n---"
    return json.loads(out.stdout.strip().splitlines()[-1])


# --- static pins (guardrails + wiring) ----------------------------------------

class TestStaticPins:
    def test_static_session_state_helper(self) -> None:
        src = SESSION_STATE.read_text(encoding="utf-8")
        assert "export function hasStickyKbConsult" in src, (
            "P0-3 requires the sticky consult helper in session_state.ts")
        assert 'r.kind === "kb_consult"' in src, (
            "hasStickyKbConsult must filter the ledger on kind=kb_consult")
        assert "getActiveUnlock(session)?.record" in src, (
            "the sticky consult resolves the ACTIVE feature via getActiveUnlock")

    def test_static_gate_driver_wiring(self) -> None:
        src = GATE_DRIVER.read_text(encoding="utf-8")
        assert "hasStickyKbConsult(ctx.session)" in src, (
            "kb_consulted predicate must OR-in the sticky consult")

    def test_static_nav_gate_write(self) -> None:
        src = NAV_GATE.read_text(encoding="utf-8")
        assert "recordKbStickyConsult" in src, (
            "P0-3 requires the consult writer in nav_gate.ts")
        assert 'kind: "kb_consult"' in src, (
            "the persisted record must carry kind=kb_consult")
        assert "getActiveUnlock(session)?.record" in src, (
            "the writer scopes the consult to the active feature (latest phase)")

    def test_static_think_protect_untouched(self) -> None:
        """P0-3 MUST NOT touch g.think/g.protect — kbTrack only feeds g.kb."""
        src = NAV_GATE.read_text(encoding="utf-8")
        assert "guardThoughts" not in src and "guardProtectedPath" not in src, (
            "kbTrack must not reach into think/protect guards (kb-only scope)")


# --- probe A: hasStickyKbConsult (session_state.ts, real module) --------------

_A_PROBE = """
import { writeFileSync } from "node:fs"
import { hasStickyKbConsult } from "%SS%"
const ledger = process.env.OMT_LEDGER_PATH!
const cases: Record<string, any[]> = %CASES%
const out: Record<string, boolean> = {}
for (const [name, recs] of Object.entries(cases)) {
  writeFileSync(ledger, recs.map((r: any) => JSON.stringify(r)).join("\\n") + "\\n")
  out[name] = hasStickyKbConsult("s1")
}
console.log(JSON.stringify(out))
"""


class TestHasStickyKbConsultBun:
    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_bun_sticky_consult_matrix(self, tmp_path) -> None:
        cases = {
            # minors/bug_fix: same-feature consult satisfies (scope ignored)
            "minor_sticky": [_phase("minor_feature"), _kb_consult()],
            "minor_no_consult": [_phase("minor_feature")],
            "minor_stale": [_phase("minor_feature"),
                            _kb_consult(hours_ago=9)],
            "minor_ignores_scope": [_phase("minor_feature", scope="NEW"),
                                    _kb_consult(scope="OLD")],
            "bug_fix_sticky": [_phase("bug_fix"), _kb_consult(tt="bug_fix")],
            # feature scoping: a consult for ANOTHER feature never satisfies
            "other_feature_consult": [_phase("minor_feature"),
                                      _kb_consult("feature_999.other")],
            "latest_feature_wins": [_phase("minor_feature",
                                           feature="feature_999.other"),
                                    _kb_consult(F)],
            # majors/new_screen re-consult on scope change (string identity)
            "major_same_scope": [_phase("major_feature", scope="SAME"),
                                 _kb_consult(scope="SAME", tt="major_feature")],
            "major_changed_scope": [_phase("major_feature", scope="NEW"),
                                    _kb_consult(scope="OLD", tt="major_feature")],
            "new_screen_changed": [_phase("new_screen", scope="NEW"),
                                   _kb_consult(scope="OLD", tt="new_screen")],
            # no feature / no ledger
            "no_feature": [_phase("minor_feature", feature="")],
            "empty_ledger": [],
        }
        out = _run_probe(tmp_path, _A_PROBE
                         .replace("%SS%", str(SESSION_STATE))
                         .replace("%CASES%", json.dumps(cases)))
        assert out == {
            "minor_sticky": True, "minor_no_consult": False,
            "minor_stale": False, "minor_ignores_scope": True,
            "bug_fix_sticky": True,
            "other_feature_consult": False, "latest_feature_wins": False,
            "major_same_scope": True, "major_changed_scope": False,
            "new_screen_changed": False,
            "no_feature": False, "empty_ledger": False,
        }, f"hasStickyKbConsult matrix mismatch: {out}"


# --- probe B: kbTrack persists the consult (nav_gate.ts, real module) ---------

_B_PROBE = """
import { writeFileSync, readFileSync } from "node:fs"
import { kbTrack } from "%NG%"
import { createSessionState } from "%SS%"
const env: any = { state: createSessionState(), safeLog: () => {},
  client: {}, $: {}, directory: "." }
const ledger = process.env.OMT_LEDGER_PATH!
const scenarios: Record<string, any[]> = %SCENARIOS%
const out: Record<string, any> = {}
for (const [name, recs] of Object.entries(scenarios)) {
  writeFileSync(ledger, recs.map((r: any) => JSON.stringify(r)).join("\\n") + "\\n")
  env.state = createSessionState()
  await kbTrack(env, "s1", { tool: "omt_kb_nav" })
  const lines = readFileSync(ledger, "utf8").trim().split("\\n").filter(Boolean)
  const consults = lines.map((l) => JSON.parse(l)).filter((r: any) => r.kind === "kb_consult")
  out[name] = {
    consults: consults.map((r: any) => ({ feature: r.feature, scope: r.scope,
      task_type: r.task_type })),
    consulted: env.state.kb.get("s1")?.consulted === true,
  }
}
console.log(JSON.stringify(out))
"""


class TestKbTrackWritesBun:
    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_bun_kb_track_persists_scoped_consult(self, tmp_path) -> None:
        scenarios = {
            "with_phase": [_phase("minor_feature", scope="c3 scope")],
            "no_phase": [],
        }
        out = _run_probe(tmp_path, _B_PROBE
                         .replace("%NG%", str(NAV_GATE))
                         .replace("%SS%", str(SESSION_STATE))
                         .replace("%SCENARIOS%", json.dumps(scenarios)))
        assert out["with_phase"]["consults"] == [{
            "feature": F, "scope": "c3 scope",
            "task_type": "minor_feature",
        }], out
        assert out["with_phase"]["consulted"] is True, out
        # no active phase → no record written, but the in-memory flag still set
        assert out["no_phase"]["consults"] == [], out
        assert out["no_phase"]["consulted"] is True, out


# --- probe C: full before-chain (gate_driver.ts runBeforeGates) ----------------

_C_PROBE = """
import { writeFileSync } from "node:fs"
import { runBeforeGates } from "%GD%"
import { createSessionState, OmtBlock } from "%SS%"
const env: any = { client: {}, $: undefined, directory: process.env.C3_REPO_ROOT!,
  state: createSessionState(), safeLog: () => {}, notify: async () => {} }
const ledger = process.env.OMT_LEDGER_PATH!
const scenarios: Record<string, any[]> = %SCENARIOS%
const out: Record<string, string> = {}
for (const [name, recs] of Object.entries(scenarios)) {
  writeFileSync(ledger, recs.map((r: any) => JSON.stringify(r)).join("\\n") + "\\n")
  try {
    await runBeforeGates(env, "s1", { tool: "edit" },
      { args: { filePath: "src/agentx/__init__.py" } }, "src/agentx/__init__.py")
    out[name] = "allow"
  } catch (e: any) {
    out[name] = e instanceof OmtBlock ? "block:" + e.message.slice(0, 140) : "error:" + String(e)
  }
}
console.log(JSON.stringify(out))
"""


class TestGateChainBun:
    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_bun_before_chain_sticky_kb(self, tmp_path) -> None:
        scenarios = {
            # a same-feature consult satisfies g.kb cross-session (no in-memory
            # flag — createSessionState() is fresh every scenario).
            "minor_sticky": [_kb_consult(), _phase("minor_feature")],
            "minor_no_consult": [_phase("minor_feature")],
            "minor_stale_consult": [_kb_consult(hours_ago=9),
                                    _phase("minor_feature")],
            "minor_other_feature": [_kb_consult("feature_999.other"),
                                    _phase("minor_feature")],
            "empty_ledger": [],
        }
        out = _run_probe(tmp_path, _C_PROBE
                         .replace("%GD%", str(GATE_DRIVER))
                         .replace("%SS%", str(SESSION_STATE))
                         .replace("%SCENARIOS%", json.dumps(scenarios)),
                         cwd=REPO_ROOT,
                         extra_env={"C3_REPO_ROOT": str(REPO_ROOT)})
        assert out["minor_sticky"] == "allow", out
        assert out["minor_no_consult"].startswith("block"), out
        assert "g.kb" in out["minor_no_consult"], out
        assert out["minor_stale_consult"].startswith("block"), out
        assert out["minor_other_feature"].startswith("block"), out
        assert "omt_phase" in out["empty_ledger"], out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])