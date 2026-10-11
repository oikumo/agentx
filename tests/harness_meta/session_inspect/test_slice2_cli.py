"""RED S2-cli — local CLI trace/sessions (design_001 S2)."""
from conftest import build_db, ses_row


def test_cli_sessions_and_trace(tmp_path):
    from session_inspect.cli import cmd_sessions
    from session_inspect import trace as trace_mod
    assert hasattr(trace_mod, "timeline")
    db = build_db(tmp_path / "c.db",
                   sessions=[ses_row("ses_c", directory="/repo")])
    out = cmd_sessions(str(db), "/repo", limit=5)
    assert out["total"] == 1
    assert out["rows"][0]["session_id"] == "ses_c"
    # trace command helper must exist on cli
    assert hasattr(__import__("session_inspect.cli", fromlist=["cmd_trace"]),
                    "cmd_trace")
