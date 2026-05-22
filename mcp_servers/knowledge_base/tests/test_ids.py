"""Unit tests for `kb.ids.make_entry_id`."""

from datetime import datetime

from kb.ids import make_entry_id


def test_prefix_for_pattern_is_PAT():
    eid = make_entry_id("pattern", "class", "Foo")
    assert eid.startswith("PAT-")


def test_prefix_for_finding_is_FIND():
    assert make_entry_id("finding", "function", "x").startswith("FIND-")


def test_prefix_for_decision_is_DEC():
    assert make_entry_id("decision", "architecture", "x").startswith("DEC-")


def test_prefix_for_correction_is_COR():
    assert make_entry_id("correction", "code", "x").startswith("COR-")


def test_unknown_type_falls_back_to_KB():
    assert make_entry_id("nonsense", "code", "x").startswith("KB-")


def test_id_has_4char_uppercase_hex_suffix():
    eid = make_entry_id("pattern", "class", "Foo")
    prefix, suffix = eid.split("-")
    assert len(suffix) == 4
    assert suffix == suffix.upper()
    assert all(c in "0123456789ABCDEF" for c in suffix)


def test_explicit_now_makes_id_deterministic_modulo_random_term():
    # Same inputs and same `now` -> same id (the only randomness is via
    # built-in hash() which is process-stable but salt-randomised between
    # processes, so we only test stability *within* this process).
    now = datetime(2026, 5, 21, 12, 0, 0)
    a = make_entry_id("pattern", "class", "Foo", now=now)
    b = make_entry_id("pattern", "class", "Foo", now=now)
    assert a == b
