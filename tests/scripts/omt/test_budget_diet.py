#!/usr/bin/env python3
"""Golden tests for T3-7 budget-diet-bot (feature_091, meta_harness_8).

PROJECT.md T3-7 / mh7 P1-4: harnessc check/build warns (never errors) while a
byte budget's headroom is <=64B, naming the longest single contributor as the
trim target with the bytes-to-free that clear the zone.

Goldens:
  Pure core (budget_diet_warnings — synthetic sizes + longest dicts):
  1. near-cap fires with the full suggestion (contributor + free >=N math).
  2. boundary: headroom 64 fires / 65 silent; at-cap (0) fires.
  3. over-cap stays silent here (the generic past-cap error owns it).
  4. gates / capless / TS-pinned sizes never fire.
  5. tool_schemas + nav_index labels; generic hint when no contributor;
     multiple budgets render in sorted order.
  Wiring (diet_longest_contributors / check_budget_diet):
  6. synthetic @tool corpus: tool_schemas diet names the longer payload;
     ties break lexicographically (max over sorted).
  Live pins (2026-09-13 numbers — deliberate re-pin when budgets move):
  7. live check rc=0: tool_args 2454/2464 (10B), agents_md 2918/2944 (26B),
     tool_schemas 1812/1856 (44B) diet warnings fire; nav_index (580B) and
     ir_json (401B) stay silent.

Run with:
    uv run pytest tests/scripts/omt/test_budget_diet.py -q
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "omt"))

import harnessc  # noqa: E402


LONGEST = {
    "tool_args": ("@tool omt_net arg describes", 612),
    "tool_schemas": ("@tool omt_net payload", 431),
    "nav_index": ("nav record #612", 512),
}


# --- 1-5. pure core --------------------------------------------------------------


def test_near_cap_fires_with_full_suggestion() -> None:
    warns = harnessc.budget_diet_warnings({"tool_args": (2454, 2464)}, LONGEST)
    assert len(warns) == 1
    w = warns[0]
    assert w.startswith(
        "budget-diet: tool_args 2454/2464B — 10B headroom (≤64B)")
    assert "diet: longest @tool omt_net arg describes 612B" in w
    assert "free ≥55B" in w, "headroom 10 → need 65-10=55B to clear the zone"
    assert "grow the cap deliberately in the same .omt edit" in w


def test_boundary_headroom_64_fires_65_silent() -> None:
    assert harnessc.budget_diet_warnings({"tool_args": (2400, 2464)}, LONGEST)
    assert harnessc.budget_diet_warnings(
        {"tool_args": (2399, 2464)}, LONGEST) == []


def test_at_cap_fires_over_cap_silent() -> None:
    assert harnessc.budget_diet_warnings({"tool_args": (2464, 2464)}, LONGEST)
    assert harnessc.budget_diet_warnings(
        {"tool_args": (2465, 2464)}, LONGEST) == [], (
        "over-cap belongs to the generic past-cap error, not the diet")


def test_gates_capless_tspin_never_fire() -> None:
    sizes = {"gates": (12, 12), "agents_md": (2944, None), "nav_tip": (-1, 512)}
    assert harnessc.budget_diet_warnings(sizes, LONGEST) == [], (
        "count budget / unbudgeted / TS-pinned report-only stay out of scope")


def test_labels_and_generic_hint() -> None:
    w = harnessc.budget_diet_warnings({"tool_schemas": (1812, 1856)}, LONGEST)[0]
    assert "longest @tool omt_net payload 431B" in w
    assert "free ≥21B" in w, "headroom 44 → need 65-44=21B"
    w = harnessc.budget_diet_warnings({"nav_index": (65472, 65536)}, LONGEST)[0]
    assert "longest nav record #612 512B" in w
    w = harnessc.budget_diet_warnings({"agents_md": (2918, 2944)}, {})[0]
    assert "trim, or grow the cap deliberately in the same .omt edit" in w
    assert "@tool" not in w


def test_multiple_budgets_sorted_deterministic() -> None:
    sizes = {"tool_args": (2454, 2464), "agents_md": (2918, 2944),
             "tool_schemas": (1812, 1856)}
    warns = harnessc.budget_diet_warnings(sizes, LONGEST)
    assert [w.split()[1] for w in warns] == [
        "agents_md", "tool_args", "tool_schemas"]


# --- 6. wiring -------------------------------------------------------------------


OMT_SNIPPET = (
    "@tool short : short description\n"
    "@tool long_tool : a much longer one-line description payload here\n"
)


def test_check_budget_diet_names_longer_payload(monkeypatch) -> None:
    errors: list[str] = []
    c = harnessc.Corpus(harnessc.parse(OMT_SNIPPET, errors))
    assert not errors, f"fixture .omt failed to parse: {errors}"
    monkeypatch.setattr(harnessc, "per_tool_arg_bytes", lambda _c: {})  # hermetic
    harnessc.check_budget_diet(c, {"tool_schemas": (100, 110)}, "")
    assert len(c.warnings) == 1
    assert "budget-diet: tool_schemas 100/110B — 10B headroom (≤64B)" in (
        c.warnings[0])
    assert "@tool long_tool payload" in c.warnings[0]


def test_diet_ties_break_lexicographically(monkeypatch) -> None:
    c = harnessc.Corpus([])
    monkeypatch.setattr(harnessc, "per_tool_arg_bytes",
                        lambda _c: {"omt_b": 100, "omt_a": 100})
    longest = harnessc.diet_longest_contributors(c, "")
    assert longest["tool_args"] == ("@tool omt_a arg describes", 100)


# --- 7. live pins ----------------------------------------------------------------


def test_live_check_emits_diet_warnings(capsys) -> None:
    """LIVE PIN (2026-09-13, re-pin feature_092 mh8 T3-3 resume digest):
    tool_args 2455/2464 (9B), agents_md 2918/2944 (26B), tool_schemas
    1840/1856 (16B) sit inside the 64B zone; nav_index 64990/65536 (546B)
    and ir_json 20113/20480 (367B) stay silent. Re-pin deliberately whenever
    these budgets move (feature_059 pin discipline)."""
    assert harnessc.main(["harnessc.py", "check"]) == 0
    err = capsys.readouterr().err
    assert "budget-diet: tool_args 2455/2464B — 9B headroom (≤64B)" in err
    assert "diet: longest @tool" in err, "composable hint names a real @tool"
    assert "budget-diet: agents_md 2918/2944B — 26B headroom (≤64B)" in err
    assert "budget-diet: tool_schemas 1840/1856B — 16B headroom (≤64B)" in err
    assert "budget-diet: nav_index" not in err
    assert "budget-diet: ir_json" not in err
