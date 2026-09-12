#!/usr/bin/env python3
"""feature_076 (T1-6) — workflow index + repair quickfix goldens.

Pins the .workflows/ machine contract in scripts/omt/harnessc.py:

1. Machine authority markers: every manifest-listed workflow file carries
   `<!-- authority: follow|override -->` within its first 10 lines; a missing
   marker is a check error; a manifest-listed-but-missing file is an error;
   an on-disk workflow absent from its subject manifest is a drift WARNING.
2. Projection-edit rule: a workflow line instructing update/edit/modify/write
   of META_HARNESS.md / AGENTS.md (without a safeguard like "never" /
   "regenerate" / ".omt" / "harnessc") is an error pointing at the canonical
   .omt source; the wrong path `meta/META_HARNESS.md` (no leading dot) is an
   error on its own.
3. `harnessc workflows` lists exactly the 6 manifest-backed catalog workflows
   (3 subjects); --subject filters; --plan prints the strategy section (the
   LAST non-Rules/non-Result '# ' heading, so `# ... rules` blocks do not win).

Run with:
    uv run pytest tests/scripts/omt/test_harnessc_workflows.py -q
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "omt"))

import harnessc  # noqa: E402

if not (REPO_ROOT / ".workflows").is_dir():
    pytest.skip(".workflows catalog absent (template tree?)",
                allow_module_level=True)


# --- 1. live catalog: markers + count ---------------------------------------


def test_catalog_lists_the_six_manifest_backed_workflows() -> None:
    entries = harnessc.discover_workflows()
    listed = [e for e in entries if e["listed"]]
    assert len(listed) == 6, f"expected 6 catalog workflows, got {len(listed)}: " + ", ".join(
        f"{e['subject']}/{e['name']}" for e in listed)
    subjects = sorted({e["subject"] for e in listed})
    assert subjects == ["agentx", "app_knowledge_base", "meta_harness"]


def test_every_manifest_listed_workflow_has_a_valid_authority_marker() -> None:
    entries = harnessc.discover_workflows()
    bad = [f"{e['subject']}/{e['name']}" for e in entries
           if e["listed"] and e["authority"] not in ("follow", "override")]
    assert bad == [], f"listed workflows without a valid authority marker: {bad}"


def test_check_workflows_clean_on_live_tree() -> None:
    errors: list[str] = []
    c = harnessc.Corpus(harnessc.parse("", errors))
    harnessc.check_workflows(c)
    assert c.errors == [], f"live catalog must be green: {c.errors}"


def test_evolution_loop_step_6_targets_the_canonical_omt_source() -> None:
    text = (REPO_ROOT / ".workflows" / "meta_harness" / "loops"
            / "meta_harness_evolution.md").read_text(encoding="utf-8")
    step6 = [ln for ln in text.splitlines()
             if ln.startswith("6.") and "META_HARNESS" in ln]
    assert len(step6) == 1
    assert ".meta/META_HARNESS.omt" in step6[0], (
        "evolution step 6 must update the canonical .omt source")
    assert "harnessc.py build" in step6[0]
    assert "./meta/META_HARNESS.md" not in text, (
        "wrong projection path must not survive anywhere in the workflow")


# --- 2. negative goldens on synthetic trees ---------------------------------


def _mk_tree(tmp_path: Path, workflows: dict[str, str]) -> Path:
    """Build a minimal .workflows tree; every workflow file path is passed as
    '<subject>/<rel>' and listed in that subject's META.md by default."""
    by_subject: dict[str, list[tuple[str, str]]] = {}
    for rel, text in workflows.items():
        sub, wrel = rel.split("/", 1)
        by_subject.setdefault(sub, []).append((wrel, text))
    for sub, rows in by_subject.items():
        sdir = tmp_path / ".workflows" / sub
        sdir.mkdir(parents=True)
        listing = "\n".join(f"| `{wrel}` | purpose |" for wrel, _ in rows)
        (sdir / "META.md").write_text(f"# manifest\n{listing}\n", encoding="utf-8")
        for wrel, text in rows:
            p = sdir / wrel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
    return tmp_path


def _check_tree(tmp_path: Path) -> harnessc.Corpus:
    restore = harnessc._swap_root(tmp_path)
    try:
        c = harnessc.Corpus([])
        harnessc.check_workflows(c)
        return c
    finally:
        restore()


def test_missing_authority_marker_is_an_error(tmp_path: Path) -> None:
    _mk_tree(tmp_path, {"s/loops/w.md": "# Rules\n1. Follow omt methodology\n# Do\n1. x\n"})
    c = _check_tree(tmp_path)
    assert any("authority marker" in e and "w.md" in e for e in c.errors), c.errors


def test_invalid_authority_value_is_an_error(tmp_path: Path) -> None:
    _mk_tree(tmp_path, {"s/loops/w.md": "<!-- authority: maybe -->\n# Rules\n# Do\n1. x\n"})
    c = _check_tree(tmp_path)
    assert any("authority marker" in e for e in c.errors), c.errors


def test_manifest_row_without_file_is_an_error(tmp_path: Path) -> None:
    _mk_tree(tmp_path, {"s/loops/there.md": "<!-- authority: follow -->\n# Do\n1. x\n"})
    meta = tmp_path / ".workflows" / "s" / "META.md"
    meta.write_text(meta.read_text(encoding="utf-8")
                    + "\n| `loops/ghost.md` | gone |\n", encoding="utf-8")
    c = _check_tree(tmp_path)
    assert any("ghost.md" in e and "does not exist" in e for e in c.errors), c.errors


def test_unlisted_on_disk_workflow_is_a_drift_warning(tmp_path: Path) -> None:
    root = _mk_tree(tmp_path, {"s/loops/listed.md": "<!-- authority: follow -->\n# Do\n1. x\n"})
    (root / ".workflows" / "s" / "loops" / "extra.md").write_text(
        "<!-- authority: follow -->\n# Do\n1. x\n", encoding="utf-8")
    c = _check_tree(tmp_path)
    assert c.errors == [], c.errors
    assert any("extra.md" in w and "not listed" in w for w in c.warnings), c.warnings


def test_projection_edit_instruction_is_an_error(tmp_path: Path) -> None:
    _mk_tree(tmp_path, {
        "s/loops/w.md": "<!-- authority: override -->\n# Do\n"
                        "1. Update the META_HARNESS.md file with the new state\n"})
    c = _check_tree(tmp_path)
    assert any("generated projection" in e for e in c.errors), c.errors


def test_projection_edit_with_safeguard_language_is_exempt(tmp_path: Path) -> None:
    _mk_tree(tmp_path, {
        "s/loops/w.md": "<!-- authority: override -->\n# Do\n"
                        "1. Update .meta/META_HARNESS.omt, then harnessc.py build to "
                        "regenerate META_HARNESS.md (never edit the projections)\n"})
    c = _check_tree(tmp_path)
    assert c.errors == [], c.errors


def test_wrong_projection_path_is_an_error(tmp_path: Path) -> None:
    _mk_tree(tmp_path, {
        "s/loops/w.md": "<!-- authority: override -->\n# Do\n"
                        "1. p p p. See ./meta/META_HARNESS.md for the state.\n"})
    c = _check_tree(tmp_path)
    assert any("wrong path" in e for e in c.errors), c.errors


# --- 3. subcommand surface ----------------------------------------------------


def test_cmd_workflows_lists_six(capsys: pytest.CaptureFixture) -> None:
    rc = harnessc.cmd_workflows([])
    assert rc == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert len(out) == 6
    assert all("authority=" in ln and ".workflows/" in ln for ln in out)
    assert any("meta_harness/meta_harness_evolution  authority=override" in ln
               for ln in out)


def test_cmd_workflows_subject_filter(capsys: pytest.CaptureFixture) -> None:
    rc = harnessc.cmd_workflows(["--subject", "agentx"])
    assert rc == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert len(out) == 2 and all(ln.startswith("agentx/") for ln in out)


def test_cmd_workflows_plan_prints_strategy_not_rules(capsys: pytest.CaptureFixture) -> None:
    rc = harnessc.cmd_workflows(["--plan", "meta_harness_evolution"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "# Improvement strategy\n" in out
    assert "IMPROVEMENT_OPTIONS.md" in out
    assert "Do not consider previous iterations history" not in out, (
        "the '# Improvement strategy rules' block must not win over the strategy")


def test_cmd_workflows_plan_unknown_is_error(capsys: pytest.CaptureFixture) -> None:
    assert harnessc.cmd_workflows(["--plan", "nope_nothing"]) == 1
    assert "no workflow named" in capsys.readouterr().err


def test_workflow_plan_steps_picks_last_strategy_heading() -> None:
    text = ("problem line\n\n# X rules\n1. r\n\n# The strategy\n1. s1\n2. s2\n\n"
            "# Result\ndone\n")
    out = harnessc.workflow_plan_steps(text)
    assert out.startswith("# The strategy")
    assert "s1" in out and "rules" not in out and "Result" not in out
