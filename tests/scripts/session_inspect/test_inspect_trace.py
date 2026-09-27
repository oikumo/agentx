"""Legacy alias for S2 inspect+trace RED node (feature_131 S2 close-out).

The S2 RED was declared at this path, then the suite was renamed to
`test_slice2_inspect_trace.py` to avoid a collection collision with
`toolbox/test_query.py`. This alias re-runs the same drill-down + timeline
checks so `omt_tdd sync` can write the same-node GREEN and unblock `done`.
Canonical tests live in `test_slice2_inspect_trace.py`; this file stays as a
thin same-node close-out (see impl_notes S2 rename note).
"""
from conftest import build_db, msg_row, part_row, ses_row


def _fixture(tmp_path):
    sessions = [ses_row("ses_a", directory="/repo", time_created=1790000000000)]
    messages = [msg_row("msg_u", "ses_a", role="user",
                        time_created=1790000000000),
                msg_row("msg_a", "ses_a", role="assistant",
                        parent_id="msg_u", time_created=1790000000100)]
    parts = [
        part_row("p_t", "msg_a", "ses_a", ptype="text",
                 payload={"text": "x" * 5000},
                 time_created=1790000000100),
        part_row("p_tool", "msg_a", "ses_a", ptype="tool",
                 payload={"tool": "bash",
                          "state": {"status": "completed", "output": "ok"}},
                 time_created=1790000000200),
    ]
    events = [{"id": f"e{i}", "aggregate_id": "ses_a", "seq": i,
               "type": "t", "data": "{}"} for i in (1, 2, 3)]
    return build_db(tmp_path / "it.db", sessions=sessions,
                     messages=messages, parts=parts, events=events)


def test_inspect_paged_content_legacy_alias(tmp_path):
    from session_inspect.adapter import OpenCodeSqliteAdapter, SessionSelector
    from session_inspect import inspect as insp
    db = _fixture(tmp_path)
    ad = OpenCodeSqliteAdapter(db)
    snap = ad.snapshot(SessionSelector(directory="/repo"))
    got = insp.get_part(snap, "p_t", page=0, page_size=100)
    assert got["truncated"] is True
    assert got["total_chars"] == 5000


def test_trace_event_seq_order_legacy_alias(tmp_path):
    from session_inspect.adapter import OpenCodeSqliteAdapter, SessionSelector
    from session_inspect import trace
    db = _fixture(tmp_path)
    ad = OpenCodeSqliteAdapter(db)
    snap = ad.snapshot(SessionSelector(directory="/repo"))
    tl = trace.timeline(snap, "ses_a")
    seqs = [e["seq"] for e in tl["events"] if "seq" in e]
    assert seqs == sorted(seqs)
    assert tl["coverage"]["n_events"] == 3
