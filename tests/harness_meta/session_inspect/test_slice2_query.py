"""RED S2 — typed query + top-cost + cursors (design_001 S2)."""
from conftest import build_db, msg_row, part_row, ses_row, tok


def _fixture(tmp_path):
    sessions = [ses_row(f"ses_{i}", directory="/repo", time_created=1790000000000 + i,
                        ti=100 * i, to=10 * i, tcr=1000 * i) for i in (1, 2, 3)]
    messages, parts = [], []
    for i in (1, 2, 3):
        mid = f"msg_{i}"
        messages.append(msg_row(mid, f"ses_{i}", role="assistant",
                                time_created=1790000000000 + i,
                                tokens=tok(total=100 * i + 10 * i + 1000 * i,
                                           input=100 * i, output=10 * i,
                                           cache_read=1000 * i)))
        parts.append(part_row(f"p_{i}", mid, f"ses_{i}", ptype="text",
                              payload={"text": f"hello {i}"},
                              time_created=1790000000000 + i))
    # error tool part in ses_3 for typed filter
    messages.append(msg_row("msg_e", "ses_3", role="assistant",
                            time_created=1790000000100))
    parts.append(part_row("p_e", "msg_e", "ses_3", ptype="tool",
                          payload={"tool": "bash", "state": {"status": "error"}},
                          time_created=1790000000100))
    return build_db(tmp_path / "q.db", sessions=sessions,
                     messages=messages, parts=parts)


def test_typed_query_and_cursor(tmp_path):
    from session_inspect.adapter import OpenCodeSqliteAdapter, SessionSelector
    from session_inspect import query
    db = _fixture(tmp_path)
    ad = OpenCodeSqliteAdapter(db)
    snap = ad.snapshot(SessionSelector(directory="/repo"))
    res = query.run_query(snap, {"filters": {"directory": "/repo"},
                                 "limit": 2})
    assert res["truncated"] is True
    assert len(res["rows"]) == 2
    page2 = query.fetch_page(res["cursor"], 2)
    assert len(page2["rows"]) >= 1
    # stale cursor fails explicitly
    try:
        query.fetch_page({"snapshot_digest": "stale", "offset": 0,
                          "query_hash": res["cursor"]["query_hash"]}, 2)
        assert False, "stale must fail"
    except Exception as exc:
        assert "cursor_stale" in str(exc)


def test_top_cost_no_missing_duplicates(tmp_path):
    from session_inspect.adapter import OpenCodeSqliteAdapter, SessionSelector
    from session_inspect import query
    db = _fixture(tmp_path)
    ad = OpenCodeSqliteAdapter(db)
    snap = ad.snapshot(SessionSelector(directory="/repo"))
    top = query.top_cost(snap, by="input", limit=2)
    assert [r["session_id"] for r in top["rows"]] == ["ses_3", "ses_2"]
    assert top["coverage"]["n_sessions"] == 3
