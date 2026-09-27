"""RED S3 — exporter bundle + replay (design_001 S3)."""
from conftest import build_db, msg_row, ses_row, tok


def _fixture(tmp_path):
    sessions = [ses_row("ses_e", directory="/repo",
                        time_created=1790000000000, ti=100)]
    messages = [msg_row("msg_e1", "ses_e", role="assistant",
                        time_created=1790000000000,
                        tokens=tok(total=1110, input=100, output=10,
                                   cache_read=1000))]
    return build_db(tmp_path / "e.db", sessions=sessions, messages=messages)


def test_exporter_bundle(tmp_path):
    from session_inspect.adapter import OpenCodeSqliteAdapter, SessionSelector
    from session_inspect import exporter
    db = _fixture(tmp_path)
    ad = OpenCodeSqliteAdapter(db)
    snap = ad.snapshot(SessionSelector(directory="/repo"))
    out = exporter.export_bundle(snap, dest=str(tmp_path / "out"),
                                 name="bundle1")
    assert out["digest"]
    assert out["paths"]["snapshot"].endswith(".json")
    # replay: digest stable without new model calls
    again = exporter.replay_bundle(out["paths"]["snapshot"])
    assert again["digest"] == out["digest"]
