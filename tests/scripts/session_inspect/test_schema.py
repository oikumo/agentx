"""RED 1 — schema.failure_vocabulary (design_001 §2, op_spec_001 `schema.py`).

Closed failure vocabulary + Finding contract: stable names (drift-checked),
`source_ref` provenance on every finding, unknown names fail construction so
the vocabulary stays closed at runtime.
"""
import json


def _schema():
    from session_inspect import schema
    return schema


def test_vocabulary_is_closed_and_frozen():
    schema = _schema()
    expected = {
        "source_unreadable", "schema_unsupported", "inclusion_semantics_ambiguous",
        "deletion_coverage_unavailable", "session_incomplete", "missing_child",
        "hierarchy_cycle", "duplicate_membership", "label_grammar_invalid",
        "label_identity_conflict", "label_orphan_event", "span_reversed",
        "label_unbound_to_manifest", "echo_not_trial", "query_limit_exceeded",
        "cursor_stale", "metric_variant_mismatch", "reconciliation_discrepancy",
        "double_counted_basis", "trial_incomplete", "manifest_invalid",
    }
    names = set(schema.FAILURE_NAMES)
    assert names == expected, (
        f"vocabulary drift: missing={sorted(expected - names)} "
        f"extra={sorted(names - expected)}"
    )
    assert isinstance(schema.FAILURE_NAMES, tuple)
    assert schema.is_failure_name("source_unreadable")
    assert not schema.is_failure_name("not_a_failure")


def test_finding_serializes_with_source_ref():
    schema = _schema()
    ref = schema.SourceRef(path="x.db", schema_markers={"drizzle_count": 2})
    f = schema.Finding(name="source_unreadable", detail={"reason": "absent"},
                       source_ref=ref)
    d = json.loads(json.dumps(f.to_dict()))
    assert d["name"] == "source_unreadable"
    assert d["detail"]["reason"] == "absent"
    assert d["source_ref"]["path"] == "x.db"
    assert d["source_ref"]["schema_markers"]["drizzle_count"] == 2


def test_unknown_name_fails_construction():
    import pytest
    schema = _schema()
    ref = schema.SourceRef(path="x.db", schema_markers={})
    with pytest.raises(ValueError):
        schema.Finding(name="made_up_failure", detail={}, source_ref=ref)
