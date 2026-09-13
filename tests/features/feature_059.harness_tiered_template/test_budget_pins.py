"""Wave 5 budget-neutrality pins RED — feature_059.

Contract: the 2 new @var records are nav-free (nav_index kinds are only
doc/flow/xref/tool/msg) and render-free (render_agents reads no @var), so the
tight budgets must read EXACTLY their pre-feature values. Any growth fails.
(Pinned values measured 2026-09-06 post-R1: nav_index shifts +3B only from
record line-number drift — this test pins the R1 values as the ceiling.)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "omt"))

import harnessc

# Ceilings: post-R1 measured sizes (the 2 @var cost ir_json only).
# Re-pin 2026-09-12 (feature_077): NAV_INDEX_CEIL 63923 → 63929 — the pinned
# failure seen pre-074..076 was line-number drift of later .omt appends, NOT
# new record kinds (nav_index kinds remain doc/flow/xref/tool/msg; the
# feature_059 contract holds). Re-measured via _sizes() at HEAD.
NAV_INDEX_CEIL = 63929
TOOL_ARGS_CEIL = 2284    # re-pin 2026-09-12 (feature_077): +6B from 073–076 additions (measured, harness budget still 2284/2304 OK)
TOOL_SCHEMAS_CEIL = 1778  # re-pin 2026-09-12 (feature_077): +8B, same class


def _sizes():
    omt_text = (REPO_ROOT / ".meta" / "META_HARNESS.omt").read_text(encoding="utf-8")
    c = harnessc.Corpus(harnessc.parse(omt_text, []))
    harnessc.interpolate(c)
    harnessc.derive_records(c, omt_text)
    agents_md = harnessc.render_agents(c)
    ir_text = json.dumps(harnessc.build_ir(c), indent=2, sort_keys=True) + "\n"
    nav_text = harnessc.render_nav_index(c)
    return harnessc.measure_budgets(c, agents_md, nav_text, ir_text)


def test_tight_budgets_unchanged():
    sizes = _sizes()
    assert sizes["nav_index"][0] <= NAV_INDEX_CEIL, sizes["nav_index"]
    assert sizes["tool_args"][0] <= TOOL_ARGS_CEIL, sizes["tool_args"]
    assert sizes["tool_schemas"][0] <= TOOL_SCHEMAS_CEIL, sizes["tool_schemas"]
    assert sizes["agents_md"][0] <= 2944, sizes["agents_md"]
    assert sizes["gates"][0] == 10, sizes["gates"]
