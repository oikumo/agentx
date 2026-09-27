"""RED S3 — integration: hotspots → compare → export → replay (design_001 S3)."""
from conftest import build_db, msg_row, ses_row, tok


def _fixture(tmp_path):
    sessions = [
        ses_row("ses_1", directory="/repo", time_created=1790000000000,
                ti=100, to=10, tcr=1000),
        ses_row("ses_2", directory="/repo", time_created=1790000000001,
                ti=200, to=20, tcr=2000),
    ]
    messages = [
        msg_row("msg_1", "ses_1", role="assistant",
                time_created=1790000000000,
                tokens=tok(total=1110, input=100, output=10,
                           cache_read=1000)),
        msg_row("msg_2", "ses_2", role="assistant",
                time_created=1790000000001,
                tokens=tok(total=2220, input=200, output=20,
                           cache_read=2000)),
    ]
    return build_db(tmp_path / "i.db", sessions=sessions, messages=messages)


def test_s3_integration(tmp_path):
    from session_inspect.adapter import OpenCodeSqliteAdapter, SessionSelector
    from session_inspect import compare, exporter, profile
    db = _fixture(tmp_path)
    ad = OpenCodeSqliteAdapter(db)
    snap = ad.snapshot(SessionSelector(directory="/repo"))
    top = profile.hotspots(snap, by="input", limit=1)
    assert top["rows"][0]["message_id"] == "msg_2"
    cmp_res = compare.compare_sessions(snap, ["ses_1", "ses_2"])
    assert cmp_res["delta"]["input"] == 100
    out = exporter.export_bundle(snap, dest=str(tmp_path / "out"),
                                 name="integ")
    assert exporter.replay_bundle(out["paths"]["snapshot"])["digest"] == out["digest"]
    # span-level attribution without boundaries is explicitly unavailable
    span = compare.span_usage(snap, "span_x")
    assert span["usage"] is None
    assert span["reason"] == "span_usage_unavailable"
