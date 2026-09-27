"""RED 4 — label protocol contracts (design_001 §5, op_spec_001 `labels.py`).

[mh13.experiment] v1 grammar, trial-identity binding rules, nested-span
discipline, legacy [harness_reason:discharge] adapter, echo immunity, plus an
env-gated live check against the real legacy captures.
"""
import os

import pytest


V1 = "[mh13.experiment]"


def line(**kw):
    import json
    return V1 + " " + json.dumps(kw)


START = dict(v=1, experiment="context_strategy", run="run_001",
             trial="case01_baseline_rep01", case="case01", variant="baseline",
             rep=1, attempt=1, event="trial_start")


def _labels():
    from session_inspect import labels
    return labels


def _schema():
    from session_inspect import schema
    return schema


def test_v1_grammar_valid_and_invalid():
    labels, schema = _labels(), _schema()

    parsed = labels.parse_label_line(line(**START))
    assert isinstance(parsed, labels.ParsedLabel)
    assert parsed.identity.trial == "case01_baseline_rep01"
    assert parsed.identity.case == "case01"
    assert parsed.identity.variant == "baseline"
    assert parsed.identity.rep == 1 and parsed.identity.attempt == 1
    assert parsed.event == "trial_start"
    assert parsed.raw.startswith(V1)

    bad_cases = {
        "fuzzy prefix": "[mh13.experiment!]" + ' {"v":1,"event":"trial_start"}',
        "trailing junk": line(**START) + " extra",
        "not json": V1 + " not-json",
        "unknown event": line(**{**START, "event": "trial_begins"}),
        "checkpoint without id": line(v=1, run="r", trial="t", attempt=1,
                                      event="checkpoint"),
        "trial_start missing identity": line(v=1, run="r", trial="t",
                                             attempt=1, event="trial_start"),
        "span_start without span": line(v=1, run="r", trial="t", attempt=1,
                                         event="span_start"),
    }
    for reason, raw in bad_cases.items():
        out = labels.parse_label_line(raw)
        assert isinstance(out, schema.Finding), reason
        assert out.name == "label_grammar_invalid", reason
        assert out.detail["raw"] == raw, reason  # raw line always preserved


def test_identity_rules_conflict_orphan_reversed():
    labels, schema = _labels(), _schema()

    seq = [
        line(**START),
        line(v=1, run="run_001", trial="case01_baseline_rep01", attempt=1,
             event="span_start", span="inspect", parent_span=None),
        line(v=1, run="run_001", trial="case01_baseline_rep01", attempt=1,
             event="span_end", span="inspect"),
        line(v=1, run="run_001", trial="case01_baseline_rep01", attempt=1,
             event="trial_end", outcome="completed"),
    ]
    binding = labels.bind_labels(_synth_snapshot(seq))
    assert binding.findings == [] or all(
        f.name != "label_grammar_invalid" for f in binding.findings)
    trial = binding.trials["case01_baseline_rep01"]
    assert trial.identity.case == "case01"
    assert trial.outcome == "completed"
    assert list(trial.spans.keys()) == ["inspect"]

    # idempotent identical repeat dedupes (not an error)
    seq_repeat = seq + [line(**START)]
    b2 = labels.bind_labels(_synth_snapshot(seq_repeat))
    assert len(b2.trials) == 1

    # conflicting duplicate identity -> label_identity_conflict
    conflict = line(**{**START, "variant": "kernel"})
    b3 = labels.bind_labels(_synth_snapshot([line(**START), conflict]))
    assert any(f.name == "label_identity_conflict" for f in b3.findings)

    # later event disagreeing with established identity -> conflict
    b4 = labels.bind_labels(_synth_snapshot([
        line(**START),
        line(v=1, run="run_001", trial="case01_baseline_rep01", attempt=1,
             event="trial_end", outcome="completed", case="case02"),
    ]))
    assert any(f.name == "label_identity_conflict" for f in b4.findings)

    # orphan span_end -> label_orphan_event
    b5 = labels.bind_labels(_synth_snapshot([
        line(v=1, run="run_001", trial="t1", attempt=1, event="span_end",
             span="ghost"),
    ]))
    assert any(f.name == "label_orphan_event" for f in b5.findings)

    # reversed span: end observed before its start -> span_reversed
    b6 = labels.bind_labels(_synth_snapshot([
        line(v=1, run="run_001", trial="t1", attempt=1, event="trial_start",
             experiment="e", case="c", variant="v", rep=1),
        line(v=1, run="run_001", trial="t1", attempt=1, event="span_end",
             span="s1"),
        line(v=1, run="run_001", trial="t1", attempt=1, event="span_start",
             span="s1"),
    ]))
    assert any(f.name == "span_reversed" for f in b6.findings)


def _synth_snapshot(lines, *, role="user"):
    """Synthesize a snapshot fragment: one user message, one part per line."""
    from conftest import msg_row, part_row
    import json
    messages, parts = [], []
    mid = "msg_u1"
    messages.append(msg_row(mid, "ses_1", role=role, time_created=1000))
    for i, ln in enumerate(lines):
        parts.append(part_row(f"p{i}", mid, "ses_1", ptype="text",
                              payload={"text": ln},
                              time_created=1000 + i))
    return {"sessions": [], "messages": messages, "parts": parts,
            "coverage": {"schema_markers": {}}}


def test_legacy_discharge_adapter():
    labels, schema = _labels(), _schema()
    raw = "[harness_reason:discharge arm=harness case=H1]"
    mapping = {"run_id": "run_discharge_2026-09-26"}

    parsed = labels.parse_legacy_discharge(raw, run_mapping=mapping)
    assert isinstance(parsed, labels.ParsedLabel)
    assert parsed.fields["arm"] == "harness" and parsed.fields["case"] == "H1"
    # no invented repetitions: rep/attempt stay unavailable (None)
    assert parsed.identity.rep is None and parsed.identity.attempt is None
    assert parsed.identity.run == "run_discharge_2026-09-26"

    # grammar miss
    miss = labels.parse_legacy_discharge("[harness_reason:discharge arm=x case=H9]",
                                         run_mapping=mapping)
    assert isinstance(miss, schema.Finding) and miss.name == "label_grammar_invalid"

    # missing run mapping -> unbound
    unbound = labels.parse_legacy_discharge(raw, run_mapping=None)
    assert isinstance(unbound, schema.Finding)
    assert unbound.name == "label_unbound_to_manifest"


def test_echo_immunity():
    labels, schema = _labels(), _schema()
    from conftest import msg_row, part_row

    # label text in an ASSISTANT message part (tool output / text) — echo only
    snap = {
        "sessions": [{"id": "ses_e", "title": line(**START)}],
        "messages": [msg_row("msg_a", "ses_e", role="assistant",
                             time_created=1000),
                     msg_row("msg_u", "ses_e", role="user", time_created=2000)],
        "parts": [part_row("p_tool", "msg_a", "ses_e", ptype="tool",
                           payload={"tool": "bash",
                                    "state": {"status": "completed",
                                              "output": line(**START)}},
                           time_created=1000),
                  part_row("p_txt", "msg_a", "ses_e", ptype="text",
                           payload={"text": line(**START)},
                           time_created=1001),
                  part_row("p_u", "msg_u", "ses_e", ptype="text",
                           payload={"text": "no labels here"},
                           time_created=2000)],
        "coverage": {"schema_markers": {}},
    }
    binding = labels.bind_labels(snap)
    assert binding.trials == {}  # no trial minted from echoes
    assert binding.echoes  # echoes recorded
    assert all(f.name == "echo_not_trial" for f in binding.findings)


@pytest.mark.skipif(not os.environ.get("MH13_LIVE_DB"), reason="opt-in live DB")
def test_live_legacy_label_parses():
    db_path = os.environ.get("MH13_DB_PATH") or os.path.expanduser(
        "~/.local/share/opencode/opencode.db")
    from session_inspect.adapter import OpenCodeSqliteAdapter, SessionSelector
    from session_inspect.normalize import normalize_snapshot

    ad = OpenCodeSqliteAdapter(db_path)
    conn = ad.connect()
    rows = conn.execute(
        "SELECT s.id FROM session s WHERE s.title LIKE "
        "'[harness_reason:discharge%' ORDER BY s.time_created LIMIT 1").fetchall()
    assert rows, "no legacy discharge sessions in live DB"
    snap = ad.snapshot(SessionSelector(session_ids=[rows[0][0]]))
    norm = normalize_snapshot(snap)
    labels = _labels()
    first_user = next(p for m in norm["messages"] if m.role == "user"
                      for p in norm["parts"] if p.message_id == m.id
                      and p.type == "text")
    parsed = labels.parse_legacy_discharge(
        first_user.payload["text"].splitlines()[0],
        run_mapping={"run_id": "live_check"})
    assert isinstance(parsed, labels.ParsedLabel), parsed
