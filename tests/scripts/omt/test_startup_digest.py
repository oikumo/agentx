#!/usr/bin/env python3
"""feature_138: compact probe digest + render-once startup (mh16 slice 2).

Contract: `startup_table` accepts a compact `probeDigest` JSON
(~120B: next/obs/rev/fresh) and renders byte-identical output to the full
`probeJson` envelope (~1.2KB). The STARTUP protocol goes digest-first and the
agent relays the tool output verbatim (render-once: one canonical renderer,
zero hand-render variance, identical D19 map).

Behaviors:
1. digest renders byte-identical markdown + metadata map vs full envelope.
2. legacy probeJson path unchanged; malformed digest fails open (file-only).
3. STARTUP text pins digest-first + verbatim relay (AGENTS.md projection).
4. measured call-turn bytes recorded (digest ~10x smaller than envelope).

TS behavior runs under bun (repo has .opencode/node_modules + bun; no
vitest covers .opencode/plugins). Skips if bun is unavailable.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN = REPO_ROOT / ".opencode" / "plugins" / "startup_table.ts"
CHECK = REPO_ROOT / "tests" / "opencode_plugins" / "startup_digest.check.ts"

COMPILED = """# WORK.compiled — GENERATED
<!-- net_rev:60 -->
NEXT: proj:agentx_concurrent_development (recommended)
Other: none | Blocked: none | Resources: 4/4 free
Pool: pending=0 active=0 done=7 (places 15/15)
Lanes: verification 0/1 free 1, integration 0/1 free 1
Projects: 6 active / 18 complete / 2 draft
Active: agentx_concurrent_development, feature_kb_akb, petri_net_studio, project_lifecycle, rag_v2, workflows
Options(8): proj:6 drift:0 unscoped:2
OptionIDs: proj:agentx_concurrent_development, proj:feature_kb_akb, proj:petri_net_studio, proj:project_lifecycle, proj:rag_v2, proj:workflows, unscoped:001, unscoped:002
Full: WORK.md (detail) + omt_net probe (live marking) on demand.
"""

# Real brief-probe envelope shape (rev 60, drained pool) as the agent receives it.
ENVELOPE = {
    "ok": True, "op": "probe", "revision": 60, "brief": True,
    "observation": {"state": "drained_complete",
                    "reason": "done=7 (no pending/active work)", "revision": 60,
                    "basis": "live_marking rev 60"},
    "menu": {"next": "none", "other_enabled": [], "blocked": [],
             "resources": {"free": 4, "total": 4}, "claims": [],
             "parallel": [], "capacity": {"workers_used": 0, "workers_total": 2, "free": 2},
             "verification": {"used": 0, "total": 1, "free": 1},
             "integration": {"used": 0, "ready": 0, "total": 1, "free": 1}},
    "freshness": {"stamped_rev": 60, "live_rev": 60, "fresh": True, "hint": ""},
}

DIGEST = {"next": "none", "obs": "drained_complete", "rev": 60,
          "fresh": True, "hint": ""}

bun = pytest.mark.skipif(shutil.which("bun") is None, reason="bun unavailable")


def _run(compiled: str, probe: dict | None, digest: dict | str | None,
         tmp_path: Path) -> dict:
    md = tmp_path / "WORK.compiled.md"
    md.write_text(compiled, encoding="utf-8")
    argv = ["bun", str(CHECK), str(md),
            json.dumps(probe) if probe is not None else "-",
            json.dumps(digest) if isinstance(digest, dict)
            else (digest if digest is not None else "-")]
    proc = subprocess.run(argv, cwd=str(REPO_ROOT / ".opencode"),
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, f"check.ts failed: {proc.stdout} {proc.stderr}"
    return json.loads(proc.stdout)


@bun
def test_digest_renders_identical(tmp_path):
    out = _run(COMPILED, ENVELOPE, DIGEST, tmp_path)
    assert out["md_full"] is not None and out["md_digest"] is not None
    assert out["md_digest"] == out["md_full"]
    assert out["agent_digest"]["options"] == out["agent_full"]["options"]
    assert out["agent_digest"]["suggested_id"] == out["agent_full"]["suggested_id"]


@bun
def test_legacy_envelope_unchanged_and_digest_fail_open(tmp_path):
    out = _run(COMPILED, ENVELOPE, None, tmp_path)
    assert "task picker from WORK.compiled.md rev 60" in out["md_full"]
    assert "A - agentx_concurrent_development" in out["md_full"]
    bad = _run(COMPILED, None, "not-json{{{", tmp_path)
    assert "file-only" in bad["md_digest"]


@bun
def test_digest_call_turn_bytes(tmp_path, capsys):
    env_b = len(json.dumps(ENVELOPE).encode())
    dig_b = len(json.dumps(DIGEST).encode())
    print(f"\nprobeJson call-turn arg: {env_b} B; probeDigest arg: {dig_b} B "
          f"({env_b / dig_b:.1f}x)")
    assert dig_b * 5 < env_b  # compact: >=5x smaller arg


def test_startup_text_pins_digest_and_verbatim():
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "probeDigest" in agents
    assert "verbatim" in agents.lower()
    src = PLUGIN.read_text(encoding="utf-8")
    assert "probeDigest" in src
    assert "normalizeProbe" in src
    # legacy path intact
    assert "probeJson" in src
    # render-once: ONE shared renderer — digest and envelope funnel into the
    # same renderTables call (digest normalized to probe-like first)
    assert len(re.findall(r"renderTables\(parsed, probe", src)) == 1
    assert "normalizeProbe(digestRaw)" in src
