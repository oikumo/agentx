"""lean_start_swap unit tests — feature_135 (mh14 run001 variant mechanism).

Contract (PROJECT.md D2/D3 + D19):
- swap surface = the SESSION STARTUP line of .agents_prompts/build.md ONLY;
  .meta/META_HARNESS.omt / AGENTS.md stay byte-identical across variants
  (AGENTS.md "Show" is render-agnostic; budget agents_md 3511/3584 has no
  headroom for a lean payload);
- control line pinned byte-exact to the live file (drift guard);
- lean line = control + `LEAN_START_V1` marker + one direct-render clause
  that forbids the startup_table roundtrip (F4 double-render);
- every other byte of build.md untouched; refuse (exit 2, no write) when the
  current line matches neither pinned variant.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SYS_PATH = str(ROOT / "scripts" / "omt")
if SYS_PATH not in sys.path:
    sys.path.insert(0, SYS_PATH)

BUILD_MD = ROOT / ".agents_prompts" / "build.md"

# TA: gotcha: pinned-control drift guard — if build.md's STARTUP line is ever
# hand-edited, this test fails FIRST so the swap constants get re-pinned
# (silent constant drift would make trials compare the wrong "control").
_CONTROL_LINE_EXPECTED_PREFIX = "Read `WORK.compiled.md` (11-line startup header"


def _module():
    import lean_start_swap as m
    return m


def _live_startup_line() -> str:
    text = BUILD_MD.read_text()
    for line in text.splitlines():
        if line.startswith(_CONTROL_LINE_EXPECTED_PREFIX) or line.startswith("LEAN_START_V1"):
            return line
    raise AssertionError("STARTUP line not found in .agents_prompts/build.md")


def test_control_line_pinned_to_live_file():
    m = _module()
    live = _live_startup_line()
    assert live == m.CONTROL_LINE, (
        "build.md STARTUP line drifted from the pinned CONTROL_LINE — "
        "re-pin scripts/omt/lean_start_swap.py constants before any trial"
    )


def test_lean_line_single_factor_delta():
    m = _module()
    lean = m.LEAN_LINE
    # 1) marker + explicit anti-double-render clause
    assert lean.startswith(m.LEAN_MARKER)
    assert m.ANTI_TOOL_CLAUSE in lean
    # 2) every enforcement token of control survives in lean (no gate regression)
    for token in m.CONTROL_ENFORCEMENT_TOKENS:
        assert token in lean, f"lean line lost enforcement token: {token!r}"
    # 3) lean == control body + marker + clause (single-factor variant):
    #    stripping marker/clause from lean must reproduce control exactly
    assert m.strip_variant(lean) == m.CONTROL_LINE


def test_swap_roundtrip_byte_identical(tmp_path):
    m = _module()
    original = BUILD_MD.read_text()
    assert original.splitlines().count(m.CONTROL_LINE) == 1

    work = tmp_path / "build.md"
    work.write_text(original)

    # control -> lean: exactly one line changed, others byte-identical
    report = m.swap_variant(work, "lean_start_v1")
    assert report["ok"] and report["changed"] == 1
    lean_text = work.read_text()
    assert m.LEAN_MARKER in lean_text
    assert lean_text.replace(m.LEAN_LINE, m.CONTROL_LINE, 1) == original

    # lean -> control: byte-identical roundtrip (D3 restore guarantee)
    report = m.swap_variant(work, "control")
    assert report["ok"] and report["changed"] == 1
    assert work.read_text() == original


def test_swap_idempotent_and_refusal(tmp_path):
    m = _module()
    work = tmp_path / "build.md"
    work.write_text(BUILD_MD.read_text())
    m.swap_variant(work, "lean_start_v1")

    # idempotent: lean -> lean is a no-op (changed == 0)
    report = m.swap_variant(work, "lean_start_v1")
    assert report["ok"] and report["changed"] == 0

    # refusal: unknown current line -> no write, exit-ready report
    work.write_text("no startup line here\n")
    before = work.read_text()
    try:
        m.swap_variant(work, "lean_start_v1")
        raised = False
    except SystemExit as e:
        raised = e.code == 2
    assert raised and work.read_text() == before


def test_cli_status_matches_live():
    m = _module()
    rc, out = m.main(["--status"])
    assert rc == 0
    live = _live_startup_line()
    assert (("lean_start_v1" in out) if live == m.LEAN_LINE
            else ("control" in out))
