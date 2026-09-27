"""RED S3 — profile hotspots + failures (design_001 S3)."""
from conftest import build_db, msg_row, part_row, ses_row, tok


def _fixture(tmp_path):
    sessions = [ses_row("ses_1", directory="/repo", time_created=1790000000000,
                        ti=300, to=30, tcr=3000)]
    messages = [
        msg_row("msg_1", "ses_1", role="assistant",
                time_created=1790000000000,
                tokens=tok(total=1110, input=100, output=10, cache_read=1000)),
        msg_row("msg_2", "ses_1", role="assistant",
                time_created=1790000000100,
                tokens=tok(total=2220, input=200, output=20, cache_read=2000)),
        msg_row("msg_u", "ses_1", role="user",
                time_created=1790000000050),
    ]
    return build_db(tmp_path / "p.db", sessions=sessions, messages=messages)


def test_profile_hotspots(tmp_path):
    from session_inspect.adapter import OpenCodeSqliteAdapter, SessionSelector
    from session_inspect import profile
    db = _fixture(tmp_path)
    ad = OpenCodeSqliteAdapter(db)
    snap = ad.snapshot(SessionSelector(directory="/repo"))
    top = profile.hotspots(snap, by="input", limit=2)
    assert [r["message_id"] for r in top["rows"]] == ["msg_2", "msg_1"]
    assert top["coverage"]["n_messages"] >= 2


def test_profile_failures(tmp_path):
    from session_inspect.adapter import OpenCodeSqliteAdapter, SessionSelector
    from session_inspect import profile
    sessions = [ses_row("ses_f", directory="/repo",
                        time_created=1790000000000)]
    messages = [msg_row("msg_a", "ses_f", role="assistant",
                        time_created=1790000000000)]
    parts = [
        part_row("p1", "msg_a", "ses_f", ptype="tool",
                 payload={"tool": "bash",
                          "state": {"status": "error", "output": "boom"}},
                 time_created=1790000000000),
        part_row("p2", "msg_a", "ses_f", ptype="tool",
                 payload={"tool": "bash",
                          "state": {"status": "error", "output": "boom"}},
                 time_created=1790000000100),
    ]
    db = build_db(tmp_path / "f.db", sessions=sessions,
                   messages=messages, parts=parts)
    ad = OpenCodeSqliteAdapter(db)
    snap = ad.snapshot(SessionSelector(directory="/repo"))
    res = profile.failures(snap, min_repeats=2)
    assert res["coverage"]["n_error_parts"] >= 2
    assert any("bash" in str(f) for f in res["findings"])
