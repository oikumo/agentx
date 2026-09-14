"""Goldens for feature_094 (mh8 T3-6 pilot, option A: sidecar + advisory).

Acceptance: relevant change refreshes, unrelated edits stay silent,
retrieval quality green on representative tasks. Advisory-only: lookup never
grants authority and never mutates the sidecar.
"""

import copy
import json

from scripts.omt.kb_pilot import (
    ADVISORY_KEYS,
    REQUIRED_FIELDS,
    active_lessons,
    load_lessons,
    lookup,
    needs_refresh,
    promote,
    retire,
)


def _doc():
    return load_lessons()


def test_sidecar_loads_three_active_lessons_with_metadata():
    doc = _doc()
    assert len(active_lessons(doc)) == 3
    for lesson in active_lessons(doc):
        for field in REQUIRED_FIELDS:
            assert field in lesson, f"{lesson['id']} missing {field}"
        assert lesson["evidence_test"], f"{lesson['id']} needs evidence_test"
        assert lesson["content_version"], f"{lesson['id']} needs content_version"
        assert lesson["expiry"], f"{lesson['id']} needs expiry"


def test_lookup_relevant_file_returns_lesson():
    advisories = lookup(_doc(), changed_files=["scripts/omt/tdd/cli.py"])
    ids = [a["id"] for a in advisories]
    assert ids == ["tdd_node"]


def test_lookup_relevant_symbol_returns_lesson():
    advisories = lookup(_doc(), changed_symbols=["guardTestsPath"])
    assert [a["id"] for a in advisories] == ["tests_canary_shadow"]


def test_lookup_unrelated_surface_returns_empty():
    doc = _doc()
    assert lookup(doc, changed_files=["src/agentx/ui/screens/react/react_view.py"]) == []
    assert lookup(doc, changed_symbols=["some.unknown.symbol"]) == []
    assert lookup(doc) == []


def test_lookup_includes_dependents():
    advisories = lookup(
        _doc(), changed_files=["tests/scripts/omt/test_gate_two_hats_message.py"]
    )
    assert [a["id"] for a in advisories] == ["tdd_node"]
    assert advisories[0]["matched_on"] == [
        "dependent:tests/scripts/omt/test_gate_two_hats_message.py"
    ]


def test_needs_refresh_on_version_change_and_not_on_same():
    lesson = active_lessons(_doc())[0]
    assert needs_refresh(lesson, lesson["content_version"]) is False
    assert needs_refresh(lesson, "something-else-v99") is True


def test_promote_records_check_and_reason_without_mutating_original():
    lesson = active_lessons(_doc())[0]
    before = copy.deepcopy(lesson)
    updated = promote(lesson, check_ref="tests/x/test_y.py::test_z", reason="hot + testable")
    assert lesson == before  # original untouched
    assert updated["status"] == "promoted"
    assert updated["replacement_check"] == "tests/x/test_y.py::test_z"
    assert updated["retire_reason"] == "hot + testable"


def test_retire_records_reason():
    lesson = active_lessons(_doc())[0]
    updated = retire(lesson, reason="superseded by automated check")
    assert updated["status"] == "retired"
    assert updated["retire_reason"] == "superseded by automated check"
    assert lesson["status"] == "active"  # original untouched


def test_lookup_is_advisory_only():
    doc = _doc()
    snapshot = json.dumps(doc, sort_keys=True)
    advisories = lookup(doc, changed_files=["scripts/omt/harnessc.py"])
    assert len(advisories) == 1
    assert set(advisories[0].keys()) == set(ADVISORY_KEYS)
    assert json.dumps(doc, sort_keys=True) == snapshot  # no side effects


def test_retrieval_quality_on_representative_tasks():
    doc = _doc()
    tasks = [
        ({"changed_files": ["scripts/omt/tdd/cli.py"]}, ["tdd_node"]),
        ({"changed_files": ["scripts/omt/harnessc.py"]}, ["stage_policy_order"]),
        ({"changed_symbols": ["guardTestsPath"]}, ["tests_canary_shadow"]),
        (
            {"changed_files": ["src/agentx/ui/screens/react/react_view.py"]},
            [],
        ),
    ]
    for kwargs, expected in tasks:
        assert [a["id"] for a in lookup(doc, **kwargs)] == expected
