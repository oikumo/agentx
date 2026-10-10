#!/usr/bin/env python3
"""Golden tests for T2-4 skip-scope alignment (feature_087, meta_harness_8).

PROJECT.md T2-4 / mh3 P2-7: the coverage-gate override must honor the natural
scope (`scope:tests`) — not just break-glass `scope:all` — OR the block
message must name the exact required `omt_skip` call.

Goldens (hermetic tmp-root fixtures; no real ledger/repo mutation):
  1. scope:tests satisfies the coverage override (the T2-4 fix).
  2. scope:all still satisfies (no regression of the feature_024 hatch).
  3. scope:nav does NOT satisfy coverage (no scope-creep).
  4. TS block message names the exact required call (scope:"all" verbatim).
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "omt"))

from tdd import gates, state  # noqa: E402

FEATURE = "feature_synth.skip_scope_alignment"

SRC = "def value():\n    return 1\n"
TEST_BODY = (
    "import agentx.synth_mod\n\n\n"
    "def test_value():\n"
    "    assert agentx.synth_mod.value() == 1\n"
)
CONFTEST = (
    "import sys\nfrom pathlib import Path\n"
    "sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'src'))\n"
)


@pytest.fixture()
def hermetic(tmp_path, monkeypatch):
    """Hermetic ledger + synthetic repo with a seeded coverage gap.

    The src gains a second public method (`extra`) the test never
    references, so validate-exit blocks on coverage (not on behavioral).
    """
    monkeypatch.setattr(state, "LEDGER_PATH", tmp_path / "ledger.jsonl")
    monkeypatch.setattr(state, "SNAPSHOT_DIR", tmp_path / "snapshots")
    monkeypatch.setattr(state, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gates, "REPO_ROOT", tmp_path)
    src_pkg = tmp_path / "src" / "agentx"
    src_pkg.mkdir(parents=True)
    (src_pkg / "__init__.py").write_text("", encoding="utf-8")
    (src_pkg / "synth_mod.py").write_text(
        SRC + "\ndef extra():\n    return 9\n", encoding="utf-8"
    )
    test_dir = tmp_path / "tests" / "features" / FEATURE
    test_dir.mkdir(parents=True)
    (test_dir / "conftest.py").write_text(CONFTEST, encoding="utf-8")
    (test_dir / "test_synth.py").write_text(TEST_BODY, encoding="utf-8")
    return tmp_path


def _blocks(hermetic) -> dict:
    res = gates.cmd_validate_exit(SimpleNamespace(feature=FEATURE))
    assert res["ok"] is False
    assert res["coverage_gaps"], "fixture must block on a coverage gap"
    return res


class TestSkipScopeAlignment:
    def test_baseline_blocks_on_coverage_gap(self, hermetic):
        """Sanity: the fixture blocks without any skip."""
        _blocks(hermetic)

    def test_scope_tests_satisfies_coverage_override(self, hermetic):
        """T2-4 GOLDEN: the natural scope satisfies the coverage override."""
        _blocks(hermetic)
        state.write_ledger({"kind": "skip", "scope": "tests", "reason": "t2-4 golden"})
        res = gates.cmd_validate_exit(SimpleNamespace(feature=FEATURE))
        assert res["ok"] is True
        assert res["summary"]["skip_override"] is True

    def test_scope_all_still_satisfies(self, hermetic):
        """No regression: break-glass scope:all still overrides."""
        _blocks(hermetic)
        state.write_ledger({"kind": "skip", "scope": "all", "reason": "g"})
        res = gates.cmd_validate_exit(SimpleNamespace(feature=FEATURE))
        assert res["ok"] is True
        assert res["summary"]["skip_override"] is True

    def test_scope_nav_does_not_satisfy_coverage(self, hermetic):
        """No scope-creep: an unrelated scope must NOT clear coverage."""
        _blocks(hermetic)
        state.write_ledger({"kind": "skip", "scope": "nav", "reason": "g"})
        res = gates.cmd_validate_exit(SimpleNamespace(feature=FEATURE))
        assert res["ok"] is False
        assert res["coverage_gaps"], "nav scope must leave the gap blocking"

    def test_block_message_names_exact_skip_call(self):
        """T2-4 second disjunct: the TS block text states scope:\"all\"."""
        ts = (
            REPO_ROOT
            / ".opencode"
            / "lib"
            / "enforcer"
            / "phase_gate.ts"
        ).read_text(encoding="utf-8")
        assert 'scope:"all"' in ts, (
            "phase_gate.ts block message must name the exact required "
            'omt_skip call (scope:"all" verbatim)'
        )
