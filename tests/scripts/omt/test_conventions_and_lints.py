"""feature_089 — mh8 T2-6: conventions + lints.

Goldens:
1. `harnessc lint` flags a planted absolute-date literal (exit 1, file:line).
2. `harnessc lint` passes a fixture using the `now - timedelta` pattern (exit 0).
3. The two convention entries (GOTCHA_STRUCTURAL_PIN, GOTCHA_DATE_LITERAL) are
   nav-queryable — present in the rendered nav index (source-of-truth .omt).
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
HC = REPO_ROOT / "scripts" / "omt" / "harnessc.py"


def _run_lint(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HC), "lint", *args],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )


def test_lint_flags_planted_absolute_date_literal(tmp_path):
    t = tmp_path / "test_planted.py"
    t.write_text(
        'def test_freshness_window():\n'
        '    fresh_ts = "2026-08-09T18:00:00Z"  # planted date-drift candidate\n'
        '    assert fresh_ts\n',
        encoding="utf-8",
    )
    r = _run_lint(str(tmp_path))
    assert r.returncode == 1, r.stdout + r.stderr
    assert "absolute-date literal" in r.stdout
    assert "test_planted.py:2" in r.stdout
    assert "now - timedelta" in r.stdout


def test_lint_clean_on_relative_fixture(tmp_path):
    t = tmp_path / "test_relative.py"
    t.write_text(
        "from datetime import datetime, timedelta, timezone\n"
        "\n"
        "def test_window():\n"
        "    fresh_ts = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()\n"
        "    assert fresh_ts\n",
        encoding="utf-8",
    )
    r = _run_lint(str(tmp_path))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "clean" in r.stdout


def test_lint_ignores_non_matching_lines(tmp_path):
    t = tmp_path / "test_ok.py"
    t.write_text(
        'DATE_DOC = "2026-08-09"  # date-only, not a datetime literal\n'
        'msg = "at 2026-08-09T18:00:00Z we saw it"  # not an assignment literal\n',
        encoding="utf-8",
    )
    r = _run_lint(str(tmp_path))
    assert r.returncode == 0, r.stdout + r.stderr


def test_lint_unknown_flag_and_missing_path(tmp_path):
    r = _run_lint("--bogus")
    assert r.returncode == 2
    r = _run_lint(str(tmp_path / "nope"))
    assert r.returncode == 1
    assert "path not found" in r.stderr


def test_gotcha_entries_nav_queryable():
    """Both convention records must be in the rendered nav index — the same
    projection omt_nav{query:"GOTCHA_..."} searches (built from the live .omt)."""
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "omt"))
    try:
        import harnessc  # noqa: E402
    finally:
        sys.path.pop(0)
    omt_text = (REPO_ROOT / ".meta" / "META_HARNESS.omt").read_text(encoding="utf-8")
    corpus = harnessc.Corpus(harnessc.parse(omt_text, []))
    harnessc.interpolate(corpus)
    nav = harnessc.render_nav_index(corpus)
    assert "GOTCHA_STRUCTURAL_PIN" in nav
    assert "GOTCHA_DATE_LITERAL" in nav
    # payloads carry the convention substance (structural pin / now-timedelta)
    assert "pin STRUCTURE" in nav and "COUNT" in nav
    assert "harnessc.py lint" in nav
