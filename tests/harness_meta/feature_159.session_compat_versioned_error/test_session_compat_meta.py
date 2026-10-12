"""Session-compat versioned error goldens (feature_159) — hermetic + live-DB bounded."""
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
LIVE_DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"

class TestSessionCompat:
    def test_missing_db_versioned(self):
        sys.path.insert(0, str(REPO / "scripts"))
        try:
            from session_inspect import service as svc
            res = svc.dispatch("sessions", {"directory": "/repo", "limit": "2"})
        finally:
            sys.path.pop(0)
            for m in ("session_inspect.service", "session_inspect.adapter", "session_inspect.schema"):
                sys.modules.pop(m, None)
        assert res.get("version") == 1
        assert res.get("code") == "MISSING_DB"
        assert res.get("read_only") is True
        assert "explicit" in str(res.get("remediation", "")).lower() and "--db" in str(res.get("remediation", ""))

    def test_source_unreadable_versioned(self):
        sys.path.insert(0, str(REPO / "scripts"))
        try:
            from session_inspect import service as svc
            res = svc.dispatch("sessions", {"db": "/tmp/159-nope-missing.db", "directory": "/repo", "limit": "2"})
        finally:
            sys.path.pop(0)
            for m in ("session_inspect.service", "session_inspect.adapter", "session_inspect.schema"):
                sys.modules.pop(m, None)
        assert res.get("version") == 1
        assert res.get("code") == "SOURCE_UNREADABLE"
        assert res.get("read_only") is True

    def test_schema_unsupported_versioned(self):
        assert LIVE_DB.is_file(), "live DB required for compat golden"
        sys.path.insert(0, str(REPO / "scripts"))
        try:
            from session_inspect import service as svc
            con = sqlite3.connect(f"file:{LIVE_DB}?mode=ro", uri=True, timeout=5)
            try:
                sid = con.execute("SELECT id FROM session LIMIT 1").fetchone()[0]
            finally:
                con.close()
            res = svc.dispatch("sessions", {"db": str(LIVE_DB), "session_ids": sid, "limit": "2"})
        finally:
            sys.path.pop(0)
            for m in ("session_inspect.service", "session_inspect.adapter", "session_inspect.schema"):
                sys.modules.pop(m, None)
        assert res.get("version") == 1
        assert res.get("code") == "SCHEMA_UNSUPPORTED"
        assert "traceback" not in str(res).lower()
        assert len(str(res.get("detail", ""))) <= 200

    def test_over_budget_versioned(self):
        assert LIVE_DB.is_file()
        sys.path.insert(0, str(REPO / "scripts"))
        try:
            from session_inspect import service as svc
            res = svc.dispatch("sessions", {"db": str(LIVE_DB), "directory": "/home/oikumo/develop/production/agentx", "limit": "2"})
        finally:
            sys.path.pop(0)
            for m in ("session_inspect.service", "session_inspect.adapter", "session_inspect.schema"):
                sys.modules.pop(m, None)
        assert res.get("version") == 1
        assert res.get("code") == "QUERY_LIMIT_EXCEEDED"
        assert isinstance(res.get("total"), int) and res["total"] > res.get("cap", 0)
        assert "cursor" in res

    def test_read_only_proof(self):
        assert LIVE_DB.is_file()
        adap_text = (REPO / "scripts" / "session_inspect" / "adapter.py").read_text(encoding="utf-8")
        assert "mode=ro" in adap_text
        con = sqlite3.connect(f"file:{LIVE_DB}?mode=ro", uri=True, timeout=5)
        try:
            try:
                con.execute("CREATE TABLE IF NOT EXISTS _159_ro_probe(x)")
                con.commit()
                wrote = True
            except Exception:
                wrote = False
            assert wrote is False
        finally:
            con.close()

    def test_no_secret_path_in_skills(self):
        for base in (REPO / ".opencode" / "skills", REPO / ".agents" / "skills"):
            if not base.exists():
                continue
            for skill_dir in base.iterdir():
                if not skill_dir.is_dir():
                    continue
                for fname in ("SKILL.md", "skill.contract.json"):
                    f = skill_dir / fname
                    if not f.exists():
                        continue
                    text = f.read_text(encoding="utf-8")
                    assert "opencode.db" not in text, f"{skill_dir.name}/{fname}"
                    assert ".local/share/opencode" not in text, f"{skill_dir.name}/{fname}"

    def test_from_session_maps_to_envelope(self):
        sys.path.insert(0, str(REPO / "scripts" / "omt"))
        try:
            import skill_result as sr
            assert hasattr(sr, "from_session"), "skill_result.from_session missing"
            shapes = [
                {"ok": False, "version": 1, "error": "missing_db", "code": "MISSING_DB", "detail": "x", "detail_ref": "sessions:missing", "retryable": True},
                {"ok": False, "version": 1, "error": "sessions_failed", "code": "SOURCE_UNREADABLE", "detail": "source_unreadable", "retryable": True},
                {"ok": False, "version": 1, "error": "sessions_failed", "code": "SCHEMA_UNSUPPORTED", "detail": "schema_unsupported", "retryable": False},
                {"ok": False, "version": 1, "error": "query_limit_exceeded", "code": "QUERY_LIMIT_EXCEEDED", "detail": "over", "total": 100, "cap": 20, "retryable": True},
            ]
            for shape in shapes:
                env = sr.from_session(shape)
                assert sr.validate_envelope(env) == [], shape
                assert (env["ok"] is True) == (env["outcome"] == "succeeded")
                if env["outcome"] == "blocked":
                    assert "blocker" in env and env["blocker"]["gate"] == "omt_session"
        finally:
            sys.path.pop(0)
            sys.modules.pop("skill_result", None)
