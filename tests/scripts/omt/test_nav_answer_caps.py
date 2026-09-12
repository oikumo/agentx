"""T1-5 nav-answer caps — feature_069.

Contract (mh8 T1-5 / mh3 P2·T2):
- `omt_nav` answers get a size cap with an explicit truncation marker +
  narrowing hint (parity with `omt_kb_nav` MAX_RECORDS=25 + capRecords).
- Wide query (> cap records) truncates with marker; under-cap answers are
  byte-identical to pre-cap output.

Bun probes exercise the REAL TS helper (test_nav_cache_hit.py idiom):
import { NAV_MAX_RECORDS, capNavLines } from lib/omt_shared.ts directly
(the helper lives in the shared lib — plugin files keep function-only named
exports + the default factory, DEFECT A loader contract).
Static pins prove every omt_nav op (nav / list_sections / cross_ref /
quick_ref) routes through the cap helper on both index and grep-fallback
paths.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
OMT_NAV = REPO_ROOT / ".opencode" / "plugins" / "omt_nav.ts"
OMT_SHARED = REPO_ROOT / ".opencode" / "lib" / "omt_shared.ts"

BUN = shutil.which("bun")


def _run_probe(tmp_path: Path, body: str) -> dict:
    assert BUN is not None, "bun runtime required (guard against skipif bypass)"
    probe = tmp_path / "probe.ts"
    probe.write_text(body, encoding="utf-8")
    env = {**os.environ}
    out = subprocess.run([BUN, str(probe)], capture_output=True, text=True,
                         timeout=90, cwd=str(REPO_ROOT), env=env)
    assert out.returncode == 0, f"bun probe failed:\n{out.stderr}\n---"
    return json.loads(out.stdout.strip().splitlines()[-1])


_CAP_PROBE = """
import { NAV_MAX_RECORDS, capNavLines } from "%SHARED%"
const under = ["a:1: x", "b:2: y", "c:3: z"]
const wide = Array.from({ length: NAV_MAX_RECORDS + 10 }, (_, i) => `f:${i}: line ${i}`)
const underOut = capNavLines(under, "\\n")
const wideOut = capNavLines(wide, "\\n")
const wideCtx = capNavLines(wide, "\\n\\n")
const out = {
  max: NAV_MAX_RECORDS,
  under_identical: underOut === under.join("\\n"),
  under_out: underOut,
  wide_lines: wideOut.split("\\n").length,
  wide_total: wide.length,
  wide_has_marker: wideOut.includes("truncated") && wideOut.includes(`${NAV_MAX_RECORDS}/${wide.length}`),
  wide_has_hint: wideOut.includes("file:") && wideOut.includes("tag_type:"),
  wide_head_kept: wideOut.startsWith("f:0: line 0"),
  ctx_sep_kept: wideCtx.includes("\\n\\n") && wideCtx.includes("truncated"),
  empty_ok: capNavLines([], "\\n") === "",
}
console.log(JSON.stringify(out))
"""


class TestCapProbe:
    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_under_cap_byte_identical(self, tmp_path: Path) -> None:
        out = _run_probe(tmp_path, _CAP_PROBE.replace("%SHARED%", OMT_SHARED.as_posix()))
        assert out["max"] == 25, out
        assert out["under_identical"] is True, out
        assert out["under_out"] == "a:1: x\nb:2: y\nc:3: z", out
        assert out["empty_ok"] is True, out

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_wide_query_truncates_with_marker_and_hint(self, tmp_path: Path) -> None:
        out = _run_probe(tmp_path, _CAP_PROBE.replace("%SHARED%", OMT_SHARED.as_posix()))
        # 25 kept + 1 marker line
        assert out["wide_lines"] == out["max"] + 1, out
        assert out["wide_has_marker"] is True, out
        assert out["wide_has_hint"] is True, out
        assert out["wide_head_kept"] is True, out
        assert out["ctx_sep_kept"] is True, out


class TestStaticPins:
    def test_cap_helper_exported_from_shared_lib(self) -> None:
        src = OMT_SHARED.read_text(encoding="utf-8")
        assert "export const NAV_MAX_RECORDS = 25" in src
        assert "export function capNavLines" in src
        assert "narrow with file:/tag_type:" in src

    def test_plugin_imports_helper_no_local_def(self) -> None:
        src = OMT_NAV.read_text(encoding="utf-8")
        assert "capNavLines } from \"../lib/omt_shared\"" in src, (
            "omt_nav.ts must import capNavLines from the shared lib")
        assert "export function capNavLines" not in src, (
            "plugin files keep function-only named exports + default factory (DEFECT A)")
        assert "export const NAV_MAX_RECORDS" not in src

    def test_all_ops_route_through_cap(self) -> None:
        src = OMT_NAV.read_text(encoding="utf-8")
        # nav (index plain + index ctx + grep) + list_sections (index + grep)
        # + cross_ref (index + grep) + quick_ref (index + grep) — every
        # hit-join must go through capNavLines so no op can bypass the cap.
        assert src.count("capNavLines(") >= 8, src.count("capNavLines(")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
