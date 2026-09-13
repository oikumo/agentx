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
# Re-pin 2026-09-13 (feature_089): NAV_INDEX_CEIL 63963 → 64956 — two new
# @doc gotcha records (GOTCHA_STRUCTURAL_PIN/GOTCHA_DATE_LITERAL) are the
# feature's deliverable (nav-queryable conventions); kinds unchanged, @budget
# nav_index deliberately grown 64000→65536 in the same .omt edit.
# Re-pin 2026-09-13 (feature_092, mh8 T3-3 resume digest): NAV_INDEX_CEIL
# 64956 → 64990 — the @tool omt_status description growth (+28B) lands in the
# tool's nav record too; design §5 "nav_index unchanged" missed that nav
# records carry @tool description text (+34B measured via _sizes(); kinds
# unchanged). Deliberate, budgets still OK (nav_index 64990/65536).
NAV_INDEX_CEIL = 64990
# Re-pin 2026-09-13 (feature_092, mh8 T3-3 resume digest): op describe gains
# "| resume" (+9B) paid by an include_ledger describe diet (-8B) — net +1B
# deliberate (tool_args 2455/2464); design note @ 4.design/features/
# feature_092.resume_digest/design_001_resume_digest.md §5.
TOOL_ARGS_CEIL = 2455    # re-pin 2026-09-13 (feature_080): deliberate omt_net claim ops (task_id/owner/generation describes + op enum) +32B nav drift; harness budgets still OK (tool_args 2454/2464, tool_schemas 1812/1856)
# Re-pin 2026-09-13 (feature_092, mh8 T3-3): @tool omt_status description
# drops "that will fire " (-15B), adds "| resume → ≤2KB post-compaction
# digest" (+43B UTF-8) — net +28B (tool_schemas 1840/1856).
TOOL_SCHEMAS_CEIL = 1840


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
