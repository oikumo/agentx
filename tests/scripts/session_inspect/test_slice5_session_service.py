"""test_slice5_session_service.py — S5 Tier-2 service dispatcher (design_002, RED)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from tests.scripts.session_inspect.conftest import build_db, ses_row, msg_row, part_row, tok


def _svc():
    import importlib
    mod = importlib.import_module("session_inspect.service")
    return mod


def _mini_db(tmp_path):
    db = str(tmp_path / "s5.db")
    build_db(db,
             sessions=[ses_row("ses_a", directory="/repo", title="a", ti=100, to=20)],
             messages=[msg_row("msg_u1", "ses_a", role="user", parent_id=None),
                       msg_row("msg_a1", "ses_a", role="assistant", parent_id="msg_u1",
                               tokens=tok(total=120, input=100, output=20))],
             parts=[part_row("p1", "msg_u1", "ses_a", ptype="text", payload={"text": "hi"})])
    return db


def test_ops_closed(tmp_path):
    service = _svc()
    db = _mini_db(tmp_path)
    r = service.dispatch("nope", {"db": db})
    assert r["ok"] is False and r["error"] == "unknown_op"
    r2 = service.dispatch("experiment", {"db": db, "sub": "launch_missiles"})
    assert r2["ok"] is False


def test_argv_whitelist(tmp_path):
    service = _svc()
    db = _mini_db(tmp_path)
    r = service.dispatch("sessions", {"db": db, "directory": "/repo", "sql": "SELECT 1"})
    assert r["ok"] is False and "whitelist" in r["error"]
    r2 = service.dispatch("query", {"db": db, "query_json": json.dumps({"text": "x; rm -rf /"})})
    assert r2["ok"] is False


def test_budgets_parity():
    service = _svc()
    assert set(service.OPS) == {"sessions", "capture", "query", "inspect", "trace",
                                "profile", "compare", "experiment", "export"}
    for op, flags in service.OP_ARGS.items():
        assert isinstance(flags, (list, tuple)) and len(flags) > 0
        assert "expected_revision" in flags


def test_read_passthrough(tmp_path):
    service = _svc()
    db = _mini_db(tmp_path)
    r = service.dispatch("sessions", {"db": db, "directory": "/repo", "limit": 10})
    assert r["ok"] is True
    body = json.dumps(r["result"]).encode("utf-8")
    assert len(body) <= 2048
    assert "detail_ref" in r["result"]
    r2 = service.dispatch("query", {"db": db, "query_json": json.dumps({"role": "assistant"}),
                                    "limit": 10, "cursor": "stale-digest"})
    assert r2["ok"] is False and r2["error"] == "cursor_stale"


def test_write_bounded(tmp_path):
    service = _svc()
    db = _mini_db(tmp_path)
    r = service.dispatch("export", {"db": db, "selection_json": "{}"})
    assert r["ok"] is False  # missing dest refused
    r2 = service.dispatch("export", {"db": db, "selection_json": "{}",
                                     "dest": "/tmp/../x/.env"})
    assert r2["ok"] is False
    dest = str(tmp_path / "bundle")
    r3 = service.dispatch("export", {"db": db, "selection_json": "{}", "dest": dest})
    assert r3["ok"] is True and Path(dest).exists()


def test_run_gated(tmp_path):
    service = _svc()
    db = _mini_db(tmp_path)
    r = service.dispatch("experiment", {"db": db, "sub": "run", "manifest": "{}"})
    assert r["ok"] is False and r.get("reason") == "no_safe_launch"
    assert r.get("executed") is False
    n1 = service.dispatch("experiment", {"db": db, "sub": "replay", "manifest": "{}"})
    n2 = service.dispatch("experiment", {"db": db, "sub": "replay", "manifest": "{}"})
    assert n1["result"]["n"] == n2["result"]["n"]
