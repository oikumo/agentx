"""Bridge unit tests — feature_131 slice 1 (Programming→Testing gate).

Real suite lives in tests/scripts/session_inspect/ (25 passed). This bridge
asserts the slice-1 public contracts from the canonical tests/features location.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SYS_PATH = str(ROOT / "scripts")
if SYS_PATH not in sys.path:
    sys.path.insert(0, SYS_PATH)


def test_closed_vocabulary():
    from session_inspect.schema import FAILURE_NAMES, Finding, is_failure_name
    assert "label_grammar_invalid" in FAILURE_NAMES
    assert is_failure_name("trial_incomplete")
    assert not is_failure_name("nope_not_a_name")
    try:
        Finding("nope_not_a_name", {})
        assert False, "unknown name must raise"
    except ValueError:
        pass


def test_a1_variant_residual():
    from session_inspect.normalize import detect_usage_variant
    assert detect_usage_variant(
        {"input": 100, "output": 18, "reasoning": 0,
         "cache": {"read": 9920, "write": 0}, "total": 10038}) == "disjoint"
    assert detect_usage_variant(
        {"input": 15615, "output": 752, "reasoning": 704,
         "cache": {"read": 0, "write": 0}, "total": 16367}
    ) == "output_includes_reasoning"
    assert detect_usage_variant(
        {"input": 0, "output": 0, "reasoning": 0,
         "cache": {"read": 0, "write": 0}, "total": 0}) == "empty"


def test_label_v1_and_legacy():
    from session_inspect.labels import (
        LABEL_PREFIX, parse_label_line, parse_legacy_discharge)
    import json
    line = LABEL_PREFIX + " " + json.dumps(
        {"v": 1, "experiment": "e", "run": "r", "trial": "t",
         "case": "c", "variant": "v", "rep": 1, "attempt": 1,
         "event": "trial_start"})
    parsed = parse_label_line(line)
    assert not hasattr(parsed, "name")
    assert parsed.identity.trial == "t"
    legacy = parse_legacy_discharge(
        "[harness_reason:discharge arm=harness case=H1]",
        run_mapping={"run_id": "run_001"})
    assert not hasattr(legacy, "name")
    assert legacy.identity.variant == "harness"
