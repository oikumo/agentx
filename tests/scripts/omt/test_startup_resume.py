#!/usr/bin/env python3
"""feature_139: compaction-aware resume startup (mh16 slice 3).

Contract: `startup_table` accepts `resumeDigest` (prior-session context —
`omt_status{op:resume}` digest or any compact summary, <=2KB) and renders a
pickup-first menu: resume INTRO + SUGGESTED leading with the digest's next
task, TASKS map identical (D19). Missing/malformed digest fails open to the
normal menu byte-identically.

Behaviors:
1. resumeDigest renders pickup-first menu, TASKS/options identical.
2. missing/malformed resumeDigest → normal menu (fail-open).
3. tool description documents resumeDigest; arg stays compact.

TS behavior runs under bun (see test_startup_digest.py header note).
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN = REPO_ROOT / ".opencode" / "plugins" / "startup_table.ts"
CHECK = REPO_ROOT / "tests" / "opencode_plugins" / "startup_digest.check.ts"

COMPILED = """# WORK.compiled — GENERATED
<!-- net_rev:60 -->
NEXT: proj:meta_harness_16 (recommended)
Other: none | Blocked: none | Resources: 4/4 free
Pool: pending=0 active=0 done=7 (places 15/15)
Lanes: verification 0/1 free 1, integration 0/1 free 1
Projects: 7 active / 18 complete / 1 draft
Active: agentx_concurrent_development, feature_kb_akb, meta_harness_16, petri_net_studio, project_lifecycle, rag_v2, workflows
Options(9): proj:7 drift:0 unscoped:2
OptionIDs: proj:agentx_concurrent_development, proj:feature_kb_akb, proj:meta_harness_16, proj:petri_net_studio, proj:project_lifecycle, proj:rag_v2, proj:workflows, unscoped:001, unscoped:002
Full: WORK.md (detail) + omt_net probe (live marking) on demand.
"""

DIGEST = {"next": "none", "obs": "drained_complete", "rev": 60,
          "fresh": True, "hint": ""}
RESUME = {"next_task": "adopt feature_137 under mh16",
          "summary": "mh16 active; slices 1-2 shipped; resume pickup test",
          "rev": 60}

bun = pytest.mark.skipif(shutil.which("bun") is None, reason="bun unavailable")


def _run(compiled: str, digest: dict | None, resume: dict | str | None,
         tmp_path: Path) -> dict:
    md = tmp_path / "WORK.compiled.md"
    md.write_text(compiled, encoding="utf-8")
    argv = ["bun", str(CHECK), str(md), "-",
            json.dumps(digest) if digest is not None else "-",
            json.dumps(resume) if isinstance(resume, dict)
            else (resume if resume is not None else "-")]
    proc = subprocess.run(argv, cwd=str(REPO_ROOT / ".opencode"),
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, f"check.ts failed: {proc.stdout} {proc.stderr}"
    return json.loads(proc.stdout)


@bun
def test_resume_pickup_first(tmp_path):
    out = _run(COMPILED, DIGEST, RESUME, tmp_path)
    assert out["md_resume"] is not None and out["md_digest"] is not None
    assert "pick up" in out["md_resume"].lower()
    assert "adopt feature_137 under mh16" in out["md_resume"]
    # TASKS map identical to the normal render
    assert out["agent_resume"]["options"] == out["agent_digest"]["options"]
    assert "Resume" in out["md_resume"].splitlines()[0]


@bun
def test_resume_fail_open(tmp_path):
    plain = _run(COMPILED, DIGEST, None, tmp_path)
    bad = _run(COMPILED, DIGEST, "[[[not-json", tmp_path)
    assert bad["md_resume"] == plain["md_digest"]
    empty = _run(COMPILED, DIGED := DIGEST, "   ", tmp_path)
    assert empty["md_resume"] == plain["md_digest"]


def test_resume_documented_and_compact():
    src = PLUGIN.read_text(encoding="utf-8")
    assert "resumeDigest" in src
    assert "normalizeResume" in src
    assert len(json.dumps(RESUME).encode()) <= 2048
