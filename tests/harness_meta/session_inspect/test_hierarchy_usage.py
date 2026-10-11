"""RED 5 — hierarchy + usage contracts (design_001 §4/§6, op_spec_001).

Session forest (direct vs subtree, missing children, cycles, duplicate
membership), three token bases never mixed, variant-aware reconciliation,
and the versioned legacy feature-130 metric.
"""
import pytest

from conftest import ses_row, tok


def _hierarchy():
    from session_inspect import hierarchy
    return hierarchy


def _usage():
    from session_inspect import usage
    return usage


def _normalize():
    from session_inspect import normalize
    return normalize


def _schema():
    from session_inspect import schema
    return schema


def _rec(sid, parent=None, ti=0, to=0, tr=0, tcr=0, tcw=0):
    return _normalize().normalize_session(
        dict(ses_row(sid, parent_id=parent, ti=ti, to=to, tr=tr, tcr=tcr, tcw=tcw)))


def test_forest_direct_vs_subtree():
    hierarchy = _hierarchy()
    recs = [
        _rec("root", ti=100),
        _rec("child_a", parent="root", ti=10),
        _rec("child_b", parent="root", ti=20),
        _rec("grand", parent="child_a", ti=5),
    ]
    forest = hierarchy.build_forest(recs)
    node = forest.nodes["root"]
    # direct and inclusive subtree usage are SEPARATE (never mixed)
    assert node.direct_usage.input == 100
    assert node.subtree_usage.input == 135
    assert forest.nodes["child_a"].subtree_usage.input == 15
    assert forest.roots == ["root"]


def test_forest_missing_child_and_cycle():
    hierarchy = _hierarchy()
    # referenced but absent child -> named coverage finding (not silence)
    forest = hierarchy.build_forest([_rec("r", ti=1),
                                     _rec("c", parent="ghost", ti=2)])
    assert any(f.name == "missing_child" and f.detail["referenced_id"] == "ghost"
               for f in forest.findings)

    # parent cycle -> reported, subtree total refused
    cyc = hierarchy.build_forest([_rec("a", parent="b"), _rec("b", parent="a")])
    assert any(f.name == "hierarchy_cycle" for f in cyc.findings)
    assert cyc.nodes["a"].subtree_usage is None

    # not-a-cycle sanity: chain still totals
    chain = hierarchy.build_forest([_rec("a", parent="b", ti=1), _rec("b")])
    assert chain.nodes["b"].subtree_usage.input == 1


def test_subtree_union_counts_each_session_once():
    hierarchy = _hierarchy()
    recs = [_rec("r1", ti=1), _rec("r2", ti=2), _rec("kid", parent="r1", ti=4)]
    forest = hierarchy.build_forest(recs)
    totals, findings = hierarchy.subtree_union(["r1", "r2"], forest)
    # overlapping roots must not duplicate usage
    assert totals.input == 7
    assert any(f.name == "duplicate_membership" for f in findings) is False
    # selecting the same root twice -> duplicate_membership finding, still once
    totals2, findings2 = hierarchy.subtree_union(["r1", "r1"], forest)
    assert totals2.input == 5
    assert any(f.name == "duplicate_membership" for f in findings2)


def test_bases_never_mixed_and_reconciliation():
    usage, schema = _usage(), _schema()
    normalize = _normalize()

    sess = _rec("s", ti=100, to=18, tr=0, tcr=9920)
    msgs = [
        normalize.normalize_message(_msg("m1", total=10038, input=100, output=18, cache_read=9920)),
    ]

    # cross-basis sum (session cumulative + message incremental) -> named
    # finding, never a number
    mixed = usage.sum_components(
        [("session_cumulative", sess.tokens), ("message_incremental", msgs[0].tokens)],
        usage.MetricDefinition(name="t", version=1,
                               components=("input",), variant_policy="any"))
    assert isinstance(mixed, schema.Finding)
    assert mixed.name == "double_counted_basis"

    # variant-aware reconciliation: Σ message components == session cumulative
    res = usage.reconcile_session(sess, msgs)
    assert res["status"] == "reconciled"

    # tampered session counters -> discrepancy with exposed residual
    tampered = _rec("s", ti=101, to=18, tr=0, tcr=9920)
    res2 = usage.reconcile_session(tampered, msgs)
    assert res2["status"] == "reconciliation_discrepancy"
    assert res2["residual"]["input"] == 1  # exposed, never smeared

    # output_includes_reasoning messages reconcile too (variant-aware)
    sess2 = _rec("s2", ti=15615, to=752, tr=0, tcr=0)
    # session columns keep reasoning separate (verified real shape):
    # msg total=16367 = in 15615 + out 752 (out already includes reasoning 704)
    m2 = normalize.normalize_message(_msg("m2", total=16367, input=15615,
                                          output=752, reasoning=704))
    res3 = usage.reconcile_session(sess2, [m2])
    assert res3["status"] == "reconciled", res3


def _msg(mid, *, total, input, output, reasoning=0, cache_read=0, cache_write=0):
    from conftest import msg_row
    return msg_row(mid, "s", role="assistant", tokens=tok(
        total=total, input=input, output=output, reasoning=reasoning,
        cache_read=cache_read, cache_write=cache_write))


def test_legacy_feature130_metric():
    usage = _usage()
    normalize = _normalize()

    # disjoint variant: prompt = input + cache_read; completion = output + reasoning
    m = normalize.normalize_message(_msg("m", total=10038, input=100, output=18,
                                         cache_read=9920))
    got = usage.legacy_feature130_metrics(m.tokens)
    assert got["prompt"] == 10020 and got["completion"] == 18

    # output_includes_reasoning: completion = output (reasoning already inside)
    m2 = normalize.normalize_message(_msg("m2", total=16367, input=15615,
                                           output=752, reasoning=704))
    got2 = usage.legacy_feature130_metrics(m2.tokens)
    assert got2["prompt"] == 15615 and got2["completion"] == 752

    # valid zeros pass through (A3)
    m0 = normalize.normalize_message(_msg("m0", total=0, input=0, output=0))
    got0 = usage.legacy_feature130_metrics(m0.tokens)
    assert got0["prompt"] == 0 and got0["completion"] == 0

    # missing counters -> null + reason, never synthesized
    got_none = usage.legacy_feature130_metrics(None)
    assert got_none["prompt"] is None and got_none["completion"] is None
    assert got_none["reason"]


def test_metric_variant_mismatch():
    usage, schema = _usage(), _schema()
    normalize = _normalize()

    # strict_disjoint policy fed an output_includes_reasoning record
    m = normalize.normalize_message(_msg("m", total=16367, input=15615,
                                         output=752, reasoning=704))
    out = usage.sum_components(
        [("message_incremental", m.tokens)],
        usage.MetricDefinition(name="strict_sum", version=1,
                               components=("input", "output", "reasoning"),
                               variant_policy="require_disjoint"))
    assert isinstance(out, schema.Finding)
    assert out.name == "metric_variant_mismatch"

    # homogeneous disjoint sum works
    m2 = normalize.normalize_message(_msg("m2", total=10038, input=100,
                                           output=18, cache_read=9920))
    ok = usage.sum_components(
        [("message_incremental", m2.tokens)],
        usage.MetricDefinition(name="s", version=1,
                               components=("input", "cache_read"),
                               variant_policy="require_disjoint"))
    assert ok["input"] == 100 and ok["cache_read"] == 9920
