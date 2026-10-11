"""RED S3 — compare sessions (design_001 S3)."""
from conftest import build_db, msg_row, ses_row, tok


def _fixture(tmp_path):
    sessions = [
        ses_row("ses_1", directory="/repo", time_created=1790000000000,
                ti=100, to=10, tcr=1000),
        ses_row("ses_2", directory="/repo", time_created=1790000000001,
                ti=300, to=30, tcr=3000),
    ]
    messages = [
        msg_row("msg_1", "ses_1", role="assistant",
                time_created=1790000000000,
                tokens=tok(total=1110, input=100, output=10,
                           cache_read=1000)),
        msg_row("msg_2", "ses_2", role="assistant",
                time_created=1790000000001,
                tokens=tok(total=3330, input=300, output=30,
                           cache_read=3000)),
    ]
    return build_db(tmp_path / "c.db", sessions=sessions, messages=messages)


def test_compare_sessions(tmp_path):
    from session_inspect.adapter import OpenCodeSqliteAdapter, SessionSelector
    from session_inspect import compare
    db = _fixture(tmp_path)
    ad = OpenCodeSqliteAdapter(db)
    snap = ad.snapshot(SessionSelector(directory="/repo"))
    res = compare.compare_sessions(snap, ["ses_1", "ses_2"])
    assert [r["session_id"] for r in res["rows"]] == ["ses_1", "ses_2"]
    assert res["delta"]["input"] == 200
    assert "warnings" in res
