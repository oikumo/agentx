"""test_trace_bounded_paging.py — feature_137 (mh15 slice 1).

Bare `trace` must no longer dump ~100KB/350-entry skeletons (mh15 F3:
349/391/332-entry skeletons, 92-111KB per sampled session). Default page is
bounded; totals + truncated + stable paging + digest-bound detail_ref keep
every entry retrievable and replay-stable. Synthetic fixture DBs only
(conftest policy: no raw transcript bodies).
"""
import json

from conftest import build_db, msg_row, part_row, ses_row


def _fixture(tmp_path, n_events=60, n_msgs=30, n_parts=40):
    t0 = 1790000000000
    sessions = [ses_row("ses_t", directory="/repo", time_created=t0)]
    messages = [
        msg_row(f"msg_{i:03d}", "ses_t",
                role="user" if i % 2 == 0 else "assistant",
                time_created=t0 + i * 100)
        for i in range(n_msgs)
    ]
    parts = [
        part_row(f"p_{i:03d}", f"msg_{i % n_msgs:03d}", "ses_t",
                 ptype="text", payload={"text": f"synthetic-{i}"},
                 time_created=t0 + i * 100)
        for i in range(n_parts)
    ]
    events = [{"id": f"e{i}", "aggregate_id": "ses_t", "seq": i,
               "type": "t", "data": "{}"} for i in range(1, n_events + 1)]
    return build_db(tmp_path / "trace_paged.db", sessions=sessions,
                    messages=messages, parts=parts, events=events)


def _snap(db):
    from session_inspect.adapter import OpenCodeSqliteAdapter, SessionSelector
    ad = OpenCodeSqliteAdapter(db)
    return ad.snapshot(SessionSelector(directory="/repo"))


def test_default_page_bounded_with_totals(tmp_path):
    from session_inspect import trace
    snap = _snap(_fixture(tmp_path))
    tl = trace.timeline(snap, "ses_t")
    assert len(tl["events"]) == 10
    assert len(tl["skeleton"]) == 10
    assert tl["truncated"] is True
    assert tl["coverage"]["n_events"] == 60
    assert tl["coverage"]["n_messages_parts"] == 70
    assert tl["page"] == 0 and tl["page_size"] == 10
    assert tl["detail_ref"].startswith("trace:ses_t:p0/")
    body = json.dumps(tl).encode()
    assert len(body) <= 2048  # bounded default; real-data bytes in report


def test_pages_union_reconstructs_full_order(tmp_path):
    from session_inspect import trace
    snap = _snap(_fixture(tmp_path))
    full_e = trace.timeline(snap, "ses_t", page_size=1000)["events"]
    full_s = trace.timeline(snap, "ses_t", page_size=1000)["skeleton"]
    got_e, got_s, last = [], [], None
    for pg in range(7):
        last = trace.timeline(snap, "ses_t", page=pg)
        got_e += last["events"]
        got_s += last["skeleton"]
    assert got_e == full_e
    assert got_s == full_s
    assert last["truncated"] is False
    assert last["coverage"]["pages"] == 7  # max(ceil(60/10), ceil(70/10))


def test_explicit_full_page_not_truncated(tmp_path):
    from session_inspect import trace
    snap = _snap(_fixture(tmp_path))
    tl = trace.timeline(snap, "ses_t", page_size=1000)
    assert len(tl["events"]) == 60
    assert len(tl["skeleton"]) == 70
    assert tl["truncated"] is False


def test_replay_stable_detail_ref(tmp_path):
    from session_inspect import trace
    snap = _snap(_fixture(tmp_path))
    a = trace.timeline(snap, "ses_t")
    b = trace.timeline(snap, "ses_t")
    assert a["detail_ref"] == b["detail_ref"]
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    c = trace.timeline(snap, "ses_t", page=1)
    assert c["detail_ref"] != a["detail_ref"]  # page-bound ref


def test_event_seq_order_preserved_on_pages(tmp_path):
    from session_inspect import trace
    snap = _snap(_fixture(tmp_path))
    tl = trace.timeline(snap, "ses_t", page=1)
    seqs = [e["seq"] for e in tl["events"]]
    assert seqs == sorted(seqs) == list(range(11, 21))


def test_service_dispatch_paging(tmp_path):
    from session_inspect import service
    db = _fixture(tmp_path)
    dflt = service.dispatch("trace", {"db": db, "session_id": "ses_t"})
    assert dflt["ok"] is True
    assert len(dflt["result"]["events"]) == 10
    assert dflt["result"]["truncated"] is True
    p1 = service.dispatch("trace", {"db": db, "session_id": "ses_t",
                                   "page": "1"})
    assert p1["ok"] is True
    assert p1["result"]["page"] == 1
    assert [e["seq"] for e in p1["result"]["events"]] == list(range(11, 21))
    full = service.dispatch("trace", {"db": db, "session_id": "ses_t",
                                     "per_page": "1000"})
    assert full["ok"] is True
    assert full["result"]["truncated"] is False
    assert full["result"]["coverage"]["n_events"] == 60
