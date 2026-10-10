#!/usr/bin/env python3
"""Golden tests for T4-3 completion hardening (feature_075, meta_harness_8).

Improvement002 D-part / PROJECT.md T4-3: completion evidence must be stronger
than public-method call-coverage — a feature whose OWN tests are broken
(s representative fault / seeded broken behavior) must FAIL completion, even
when every other validate-exit dimension (dangling reds, coverage diff) is
clean. The golden is the seeded-fault flip: green feature tests → ok:true;
mutate the src so one test goes red → ok:false with failing_tests populated.
Hermetic tmp-root fixtures; no real ledger/receipt/repo mutation.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "omt"))

from tdd import gates, state  # noqa: E402

FEATURE = "feature_synth.completion_hardening"

SRC_GOOD = "def value():\n    return 1\n"
SRC_BROKEN = "def value():\n    return 2\n"  # seeded fault: representative broken behavior

TEST_BODY = (
    "import synth_mod\n\n\n"
    "def test_value():\n"
    "    assert synth_mod.value() == 1\n"
)

CONFTEST = (
    "import sys\nfrom pathlib import Path\n"
    "sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'src'))\n"
)


@pytest.fixture()
def hermetic(tmp_path, monkeypatch):
    """Hermetic ledger + synthetic repo: feature src + its own test dir."""
    monkeypatch.setattr(state, "LEDGER_PATH", tmp_path / "ledger.jsonl")
    monkeypatch.setattr(state, "SNAPSHOT_DIR", tmp_path / "snapshots")
    monkeypatch.setattr(state, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gates, "REPO_ROOT", tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "synth_mod.py").write_text(SRC_GOOD, encoding="utf-8")
    test_dir = tmp_path / "tests" / "features" / FEATURE
    test_dir.mkdir(parents=True)
    (test_dir / "conftest.py").write_text(CONFTEST, encoding="utf-8")
    (test_dir / "test_synth.py").write_text(TEST_BODY, encoding="utf-8")
    return tmp_path


class TestCompletionHardening:
    def test_green_feature_tests_complete(self, hermetic):
        """T4-3 baseline: clean dangling/coverage AND green feature tests → ok."""
        res = gates.cmd_validate_exit(SimpleNamespace(feature=FEATURE))
        assert res["ok"] is True
        assert res["failing_tests"] == []
        assert res["summary"]["behavioral"] == {"ran": True, "failures": 0}

    def test_seeded_broken_behavior_fails_completion(self, hermetic):
        """T4-3 GOLDEN: seed a representative fault (value() returns 2) —
        the feature's test goes red and completion FAILS even though there
        are no dangling reds and no coverage gap (call is still referenced).
        This is the beyond-call-coverage strengthening."""
        (hermetic / "src" / "synth_mod.py").write_text(SRC_BROKEN, encoding="utf-8")
        res = gates.cmd_validate_exit(SimpleNamespace(feature=FEATURE))
        assert res["ok"] is False
        assert res["dangling_reds"] == []
        assert res["coverage_gaps"] == []
        assert any("test_synth.py::test_value" in f for f in res["failing_tests"])
        assert res["summary"]["behavioral"] == {"ran": True, "failures": 1}

    def test_skip_all_override_still_bypasses(self, hermetic):
        """Existing escape hatch (feature_024): a fresh omt_skip{scope:all}
        overrides the behavioral block too — never silently strengthened."""
        (hermetic / "src" / "synth_mod.py").write_text(SRC_BROKEN, encoding="utf-8")
        state.write_ledger({"kind": "skip", "scope": "all", "reason": "g"})
        res = gates.cmd_validate_exit(SimpleNamespace(feature=FEATURE))
        assert res["ok"] is True
        assert res["summary"]["skip_override"] is True
        assert res["summary"]["behavioral"]["failures"] == 1

    def test_no_test_dir_leaves_legacy_behavior(self, tmp_path, monkeypatch):
        """A feature with no tests/features/<feature>/ dir pays no behavioral
        run and completes exactly as before (no invented requirements)."""
        monkeypatch.setattr(state, "LEDGER_PATH", tmp_path / "ledger.jsonl")
        monkeypatch.setattr(state, "SNAPSHOT_DIR", tmp_path / "snapshots")
        monkeypatch.setattr(state, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(gates, "REPO_ROOT", tmp_path)
        res = gates.cmd_validate_exit(SimpleNamespace(feature=FEATURE))
        assert res["ok"] is True
        assert res["summary"]["behavioral"] == {"ran": False, "failures": 0}
        assert res["failing_tests"] == []

    def test_collection_error_is_a_behavioral_failure(self, hermetic):
        """A feature test that cannot even be COLLECTED (broken import) is
        broken behavior — completion fails with the runner tail, never a
        silent pass."""
        (hermetic / "tests" / "features" / FEATURE / "test_synth.py").write_text(
            "import does_not_exist_zzz\n", encoding="utf-8")
        res = gates.cmd_validate_exit(SimpleNamespace(feature=FEATURE))
        assert res["ok"] is False
        assert res["failing_tests"]
