"""RED 2 — adapter contracts (design_001 §3, op_spec_001 `adapter.py`).

Read-only open + capability discovery + bounded snapshot selection + event
cursor + env-gated live smoke. Sources are synthetic fixture DBs (conftest);
the live DB is opt-in via MH13_LIVE_DB=1 and only checked structurally.
"""
import os
import sqlite3

import pytest

from conftest import REPO_ROOT, build_db, ses_row


def _adapter():
    from session_inspect.adapter import FindingError, OpenCodeSqliteAdapter
    return OpenCodeSqliteAdapter, FindingError


def test_readonly_open_and_missing_path(tmp_path):
    OpenCodeSqliteAdapter, FindingError = _adapter()
    db = build_db(tmp_path / "a.db")
    ad = OpenCodeSqliteAdapter(db)
    conn = ad.connect()
    # read-only connection: any write must raise (capture contract 3)
    with pytest.raises(sqlite3.OperationalError):
        conn.execute("CREATE TABLE nope (x)")
    conn.close()

    missing = str(tmp_path / "missing.db")
    ad2 = OpenCodeSqliteAdapter(missing)
    with pytest.raises(FindingError) as exc:
        ad2.connect()
    f = exc.value.finding
    assert f.name == "source_unreadable"
    assert f.detail["path"] == missing
    assert f.source_ref is not None and f.source_ref.path == missing


def test_capability_discovery(tmp_path):
    OpenCodeSqliteAdapter, FindingError = _adapter()
    db = build_db(tmp_path / "a.db")
    ad = OpenCodeSqliteAdapter(db)
    rep = ad.capability_report()
    assert rep["ok"] is True
    assert rep["required_tables"]["part"] is True
    markers = rep["schema_markers"]
    assert markers["drizzle_count"] == 2
    assert markers["drizzle_latest_ms"] == 1778520877000
    assert markers["data_migrations"] == ["legacy_a"]
    assert rep["db_path"] == db


def test_capability_discovery_missing_table(tmp_path):
    OpenCodeSqliteAdapter, FindingError = _adapter()
    db = build_db(tmp_path / "b.db", drop_tables=("part",))
    ad = OpenCodeSqliteAdapter(db)
    with pytest.raises(FindingError) as exc:
        ad.capability_report()
    f = exc.value.finding
    assert f.name == "schema_unsupported"
    assert "part" in f.detail["missing"]


def test_bounded_snapshot_selection_and_order(tmp_path):
    from session_inspect.adapter import SessionSelector

    db = build_db(
        tmp_path / "c.db",
        sessions=[
            ses_row("ses_b", directory="/repo", time_created=2000),
            ses_row("ses_a", directory="/repo", time_created=2000),
            ses_row("ses_other", directory="/elsewhere", time_created=1000),
        ],
    )
    OpenCodeSqliteAdapter, _ = _adapter()
    ad = OpenCodeSqliteAdapter(db)
    snap = ad.snapshot(SessionSelector(directory="/repo"))
    ids = [s["id"] for s in snap["sessions"]]
    # only bounded selection; ties at equal time_created break by stable id (A8)
    assert ids == ["ses_a", "ses_b"]
    cov = snap["coverage"]
    assert cov["n_sessions"] == 2 and cov["n_messages"] == 0 and cov["n_parts"] == 0

    by_ids = ad.snapshot(SessionSelector(session_ids=["ses_other"]))
    assert [s["id"] for s in by_ids["sessions"]] == ["ses_other"]

    # unbounded selector refused
    with pytest.raises(ValueError):
        ad.snapshot(SessionSelector())


def test_event_cursor_idempotent(tmp_path):
    from session_inspect.adapter import SessionSelector

    ev = [
        {"id": "ev1", "aggregate_id": "ses_a", "seq": 1, "type": "t", "data": "{}"},
        {"id": "ev2", "aggregate_id": "ses_a", "seq": 2, "type": "t", "data": "{}"},
    ]
    db = build_db(tmp_path / "d.db", sessions=[ses_row("ses_a")], events=ev)
    OpenCodeSqliteAdapter, _ = _adapter()
    ad = OpenCodeSqliteAdapter(db)
    rows1 = ad.event_cursor("ses_a", after_seq=0)
    rows2 = ad.event_cursor("ses_a", after_seq=0)  # replay is idempotent
    assert [r["seq"] for r in rows1] == [1, 2]
    assert [r["seq"] for r in rows2] == [1, 2]
    assert [r["seq"] for r in ad.event_cursor("ses_a", after_seq=1)] == [2]


@pytest.mark.skipif(not os.environ.get("MH13_LIVE_DB"), reason="opt-in live DB")
def test_live_smoke():
    db_path = os.environ.get("MH13_DB_PATH")
    if not db_path:
        db_path = os.path.expanduser("~/.local/share/opencode/opencode.db")
    OpenCodeSqliteAdapter, _ = _adapter()
    ad = OpenCodeSqliteAdapter(db_path)
    rep = ad.capability_report()
    assert rep["ok"] is True, rep
    from session_inspect.adapter import SessionSelector

    snap = ad.snapshot(SessionSelector(directory=str(REPO_ROOT)))
    assert snap["coverage"]["n_sessions"] >= 1
