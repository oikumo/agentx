#!/usr/bin/env python3
"""Production hook-effects verification — pytest wrapper.

REWRITE (2026-07-19, feature_023 deep audit): the previous version of this
file was conceptually broken — it tried to `importlib.util.spec_from_file_location`
the TypeScript plugins (`.opencode/plugin/omt_think.ts` — note the stale
singular path, too) as if they were Python modules. `spec` came back None and
every test died with `AttributeError: 'NoneType' object has no attribute
'loader'`. Python cannot import TypeScript; hook effects must be verified by
executing the plugins under a JS runtime.

Two complementary suites do that job:

  1. tests/scripts/omt/test_hook_effects_production.ts — drives the REAL
     plugins under node/tsx with SDK-shaped fixtures (fast, no LLM). This
     module wraps it so `pytest` runs it too.
  2. tests/scripts/omt/test_omt_live_opencode_guards.py — drives the REAL
     opencode binary end-to-end (slow, LLM) and would have caught the
     before-hook contract violation (BUG-A) the fixtures missed.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
TS_SUITE = REPO_ROOT / "tests" / "scripts" / "omt" / "test_hook_effects_production.ts"
NPX = shutil.which("npx")
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(
    not (NPX or NODE), reason="neither npx nor node available to run the TS suite"
)


def test_hook_effects_production_ts_suite():
    """Run the node/tsx production suite (real plugins, SDK-shaped fixtures)
    and require its success banner. Covers: TA digest on first tool result,
    nav reminder on first tool result, D1 read-time thought injection,
    after-hook payload shapes (args on input — F14), inert session.start."""
    assert TS_SUITE.exists(), f"TS suite missing: {TS_SUITE}"
    if NPX:
        cmd = [NPX, "tsx", str(TS_SUITE)]
    else:
        cmd = [NODE, "--experimental-strip-types", str(TS_SUITE)]
    proc = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=180,
    )
    assert proc.returncode == 0, (
        f"production hook-effects suite failed:\n{proc.stdout}\n{proc.stderr}")
    assert "ALL PRODUCTION HOOK EFFECTS VERIFIED" in proc.stdout, (
        f"success banner missing — suite incomplete?\n{proc.stdout}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
