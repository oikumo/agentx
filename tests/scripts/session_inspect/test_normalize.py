"""RED 3 — normalize contracts (design_001 §2, op_spec_001 `normalize.py`).

Session/message/part normalization, A1 dual inclusion-variant detection
(analysis §3, quantified 39,421 disjoint vs 675 output⊇reasoning), step
usage, and unknown-part passthrough. Fixtures mirror observed real shapes.
"""
import pytest

from conftest import msg_row, part_row, ses_row, tok


def _normalize():
    from session_inspect import normalize
    return normalize


def _schema():
    from session_inspect import schema
    return schema


def test_session_record():
    normalize, schema = _normalize(), _schema()
    row = ses_row(
        "ses_1", directory="/repo", title="t", agent="build",
        model='{"id":"z-ai/glm-5.3","providerID":"nvidia","variant":"max"}',
        time_created=1790459275166, time_updated=1790459280166,
        ti=100, to=18, tr=0, tcr=9920, tcw=0, cost=0.0,
    )
    rec = normalize.normalize_session(dict(row))
    assert rec.id == "ses_1"
    assert rec.parent_id is None
    assert rec.directory == "/repo"
    assert rec.agent == "build"
    # model JSON -> triple (A9)
    assert rec.model == schema.ModelTriple(
        model_id="z-ai/glm-5.3", provider_id="nvidia", variant="max")
    # ms passthrough (A5); latency is NOT re-scaled
    assert rec.time["created"] == 1790459275166
    assert rec.time["updated"] == 1790459280166
    # session-cumulative counters, null-safe cost
    assert rec.tokens.input == 100 and rec.tokens.cache_read == 9920
    assert rec.cost == 0.0
    # no open tool parts -> completion unknown (not proven complete)
    assert rec.lifecycle.completion == "unknown"

    open_rec = normalize.normalize_session(dict(row), open_tool_part_count=1)
    assert open_rec.lifecycle.completion == "incomplete"  # A7

    # malformed model JSON stays None, never crashes
    bad = dict(row, model="{not json")
    assert normalize.normalize_session(bad).model is None


def test_message_turn_pairing_and_valid_zeros():
    normalize, schema = _normalize(), _schema()
    user = normalize.normalize_message(msg_row("msg_u", "ses_1", role="user"))
    a1 = normalize.normalize_message(msg_row(
        "msg_a1", "ses_1", role="assistant", parent_id="msg_u",
        tokens=tok(total=10038, input=100, output=18, cache_read=9920)))
    # user messages carry no tokens (keys absent -> None)
    assert user.role == "user" and user.tokens is None
    # assistant.parent_id = user turn link (analysis §3)
    assert a1.role == "assistant" and a1.parent_id == "msg_u"
    assert a1.tokens.total == 10038
    # all-zero assistant counters are valid data, kept (A3)
    a0 = normalize.normalize_message(msg_row(
        "msg_a0", "ses_1", role="assistant",
        tokens=tok(total=0, input=0, output=0, reasoning=0, cache_read=0, cache_write=0)))
    assert a0.tokens is not None and a0.tokens.total == 0


def test_usage_variant_detection():
    normalize = _normalize()
    # exact disjoint: total = in+out+reas+cr+cw (verified real shape)
    assert normalize.detect_usage_variant(
        tok(total=10038, input=100, output=18, reasoning=0, cache_read=9920)) == "disjoint"
    # real negative-residual shape: output already contains reasoning
    assert normalize.detect_usage_variant(
        tok(total=16367, input=15615, output=752, reasoning=704)) == "output_includes_reasoning"
    # all-zero is its own variant, a valid zero (A3)
    assert normalize.detect_usage_variant(
        tok(total=0, input=0, output=0, reasoning=0, cache_read=0, cache_write=0)) == "empty"
    # neither formula holds -> ambiguous, never guessed (A1)
    assert normalize.detect_usage_variant(
        tok(total=500, input=100, output=50, reasoning=10)) == "ambiguous"
    # missing total -> ambiguous (never assume inclusion semantics)
    assert normalize.detect_usage_variant(
        tok(input=100, output=50)) == "ambiguous"
    # reasoning=0: both formulas coincide -> disjoint (checked first)
    assert normalize.detect_usage_variant(
        tok(total=118, input=100, output=18, reasoning=0, cache_read=0)) == "disjoint"


def test_step_usage_extraction():
    normalize = _normalize()
    part = normalize.normalize_part(part_row(
        "p1", "m1", "s1", ptype="step-finish",
        payload={"reason": "tool-calls", "snapshot": "abc123",
                 "tokens": tok(total=49382, input=457, output=241,
                               reasoning=236, cache_read=48448)}))
    step = normalize.step_usage(part)
    assert step is not None
    assert step.tokens.total == 49382
    assert step.tokens.variant == "disjoint"  # 457+241+236+48448 = 49382
    assert step.reason == "tool-calls"
    assert step.snapshot == "abc123"

    start = normalize.normalize_part(part_row(
        "p0", "m1", "s1", ptype="step-start", payload={"snapshot": "abc123"}))
    assert normalize.step_usage(start) is None  # step-start carries no usage

    # non-step part -> no usage
    text = normalize.normalize_part(part_row("p2", "m1", "s1", ptype="text"))
    assert normalize.step_usage(text) is None


def test_part_taxonomy_and_unknown_passthrough():
    normalize = _normalize()
    payloads = {
        "tool": {"tool": "bash", "callID": "c1",
                 "state": {"status": "completed"}},
        "text": {"text": "hello", "time": {"start": 1, "end": 2}},
        "reasoning": {"text": "thinking..."},
        "patch": {"hash": "h", "files": ["/x"]},
        "compaction": {"auto": True},
        "agent": {"name": "explore", "source": {"value": "@explore"}},
        "step-start": {"snapshot": "s"},
        "step-finish": {"reason": "tool-calls", "snapshot": "s"},
        "file": {"filename": "f"},
    }
    for ptype, payload in payloads.items():
        rec = normalize.normalize_part(part_row(f"p_{ptype}", "m1", "s1",
                                                ptype=ptype, payload=payload))
        assert rec.type == ptype, ptype
        for k, v in payload.items():  # payload verbatim per type union
            assert rec.payload[k] == v, (ptype, k)

    # unknown type passes through with is_known=False — never dropped
    unk = normalize.normalize_part(part_row("p_x", "m1", "s1",
                                            ptype="future-type", payload={"a": 1}))
    assert unk.type == "future-type"
    assert unk.is_known is False


def test_normalize_snapshot_composition():
    normalize = _normalize()
    # snapshot shape is adapter's; here we feed normalized row dicts directly
    snap = {
        "sessions": [dict(ses_row("ses_1", ti=100, to=18, tcr=9920))],
        "messages": [msg_row("msg_u", "ses_1", role="user"),
                     msg_row("msg_a", "ses_1", role="assistant", parent_id="msg_u",
                             tokens=tok(total=10038, input=100, output=18, cache_read=9920))],
        "parts": [part_row("p_u", "msg_u", "ses_1",
                           ptype="text", payload={"text": "hi"}),
                  part_row("p_tool", "msg_a", "ses_1", ptype="tool",
                           payload={"tool": "bash", "state": {"status": "running"}}),
                  part_row("p_unk", "msg_a", "ses_1", ptype="mystery")],
        "coverage": {"n_sessions": 1, "n_messages": 2, "n_parts": 3,
                     "schema_markers": {}, "warnings": []},
    }
    out = normalize.normalize_snapshot(snap)
    assert len(out["sessions"]) == 1 and len(out["messages"]) == 2
    # running tool part -> session marked incomplete (A7)
    assert out["sessions"][0].lifecycle.completion == "incomplete"
    # unknown part type -> coverage finding, record kept
    names = [f.name for f in out["findings"]]
    assert "schema_unsupported" in names
    types = [p.type for p in out["parts"]]
    assert "mystery" in types
