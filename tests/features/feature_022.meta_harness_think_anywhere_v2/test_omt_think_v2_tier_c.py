"""
Test suite for feature_022: Think Anywhere V2 — Tier C.

Covers design_003_tier_c.md §3 tests 1–22 (each test cites its item):

  C1  omt_think_verify (structural placement-integrity verify: anchor
      re-resolution → verified/stale; append-only verify records), the
      session-start digest stale count, and think-gate message weighting
      (risk-first + ⚠️ STALE suffix, fail-open without an index).
  C2  per-file consult granularity: think_consult records gain files[];
      hasConsultedThoughts(session, rel, {risk, root}) checks per-file
      coverage with legacy grandfathering; the cross-session window is
      dropped for risk:-carrying files; before-hook integration.

Strategy mirrors Tiers A/B1+D1: invoke the REAL plugin tools via
_think_runner.mjs (omt_think_verify + session-start modes) and the REAL
enforcer helpers/hooks via _think_gate_runner.mjs (consulted root-injected
mode + before-hook batch mode) — no opencode server, no reimplementation.
"""

import json
import os
import re
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
TEST_DIR = Path(__file__).parent
THINK_RUNNER = TEST_DIR / "_think_runner.mjs"
GATE_RUNNER = TEST_DIR / "_think_gate_runner.mjs"
THOUGHTS_INDEX = REPO_ROOT / ".meta" / ".omt" / "thoughts.jsonl"
LEDGER = REPO_ROOT / ".meta" / ".omt" / "ledger.jsonl"

NODE = shutil.which("node")
needs_node = pytest.mark.skipif(not NODE, reason="node not available")


def _run_tool(tool_name: str, args: dict | None = None, cwd: Path = REPO_ROOT):
    """Invoke a real omt_think plugin tool via node; return its string result or None."""
    if not NODE:
        return None
    proc = subprocess.run(
        [NODE, "--experimental-strip-types", str(THINK_RUNNER), tool_name, json.dumps(args or {})],
        capture_output=True, text=True, cwd=cwd, timeout=30,
    )
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def _session_start(cwd: Path = REPO_ROOT):
    """Drive the real session.start hook (thinkDigest); return the digest string or None."""
    if not NODE:
        return None
    proc = subprocess.run(
        [NODE, "--experimental-strip-types", str(THINK_RUNNER), "session-start"],
        capture_output=True, text=True, cwd=cwd, timeout=60,
    )
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def _consulted(session=None, rel=None, risk=None, root=None):
    """Call the REAL hasConsultedThoughts via the root-injected runner mode."""
    if not NODE:
        return None
    payload = {"session": session, "rel": rel, "risk": risk, "root": str(root) if root else None}
    proc = subprocess.run(
        [NODE, "--experimental-strip-types", str(GATE_RUNNER), "consulted", json.dumps(payload)],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=30,
    )
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout).get("consulted")
    except json.JSONDecodeError:
        return None


def _before_hook_batch(directory: Path, calls: list[dict]):
    """Drive the REAL OmtEnforcer tool.execute.before through a batch of calls on
    ONE plugin instance; return [{blocked:bool, message?}] or None."""
    if not NODE:
        return None
    proc = subprocess.run(
        [NODE, "--experimental-strip-types", str(GATE_RUNNER), "before-hook",
         str(directory), json.dumps(calls)],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=30,
    )
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def _edit_call(path: Path, session: str, tool: str = "edit") -> dict:
    """One fake before-hook invocation for `tool` on `path` in `session`.

    REAL SDK shape (tool.execute.before — feature_023 T1.2): input carries
    {tool,sessionID,callID}; args on OUTPUT (the before-hook's only payload).
    Pinned by tests/scripts/omt/test_opencode_sdk_contract.py."""
    return {
        "input": {"tool": tool, "sessionID": session, "callID": "c1"},
        "output": {"args": {"filePath": str(path)}},
    }


def _marker() -> str:
    return "TAUTOMARK_" + uuid.uuid4().hex[:8]


def _write_tmp(tmp_path: Path, name: str, content: str = "") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def _rel(p: Path) -> str:
    return os.path.relpath(str(p), str(REPO_ROOT))


def _index_records(root: Path, path_filter: str, kind: str | None = None) -> list[dict]:
    """thoughts.jsonl records for a given rel path (optionally by kind), oldest first."""
    index = root / ".meta" / ".omt" / "thoughts.jsonl"
    recs = []
    if index.exists():
        for line in index.read_text().splitlines():
            s = line.strip()
            if not s:
                continue
            try:
                r = json.loads(s)
            except json.JSONDecodeError:
                continue
            if isinstance(r, dict) and r.get("path") == path_filter:
                if kind is None or r.get("kind") == kind:
                    recs.append(r)
    return recs


def _ledger_size(root: Path) -> int:
    ledger = root / ".meta" / ".omt" / "ledger.jsonl"
    return ledger.stat().st_size if ledger.exists() else 0


def _ledger_records_after(root: Path, offset: int) -> list[dict]:
    ledger = root / ".meta" / ".omt" / "ledger.jsonl"
    if not ledger.exists():
        return []
    data = ledger.read_bytes()[offset:]
    recs = []
    for line in data.decode("utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            recs.append(json.loads(s))
        except json.JSONDecodeError:
            continue
    return recs


def _seed_ledger(root: Path, records: list[dict]) -> None:
    ledger = root / ".meta" / ".omt" / "ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


def _seed_index(root: Path, records: list[dict]) -> None:
    index = root / ".meta" / ".omt" / "thoughts.jsonl"
    index.parent.mkdir(parents=True, exist_ok=True)
    with index.open("a", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# C1 — omt_think_verify (runner; tmp files; index records filtered by tmp path)
# ---------------------------------------------------------------------------
@needs_node
class TestC1Verify:
    def test_anchor_intact_verified(self, tmp_path):
        """design §3.1 — anchor intact → verified + basis anchor; index gains a
        kind:verify record {status:verified, basis:anchor} for (path,line)."""
        f = _write_tmp(tmp_path, "v1.py", "alpha = 1\nbeta = 2\ngamma = 3\n")
        m = _marker()
        ins = _run_tool("omt_think", {"path": str(f), "thought": m, "after": "beta = 2"}, cwd=tmp_path)
        assert ins is not None and "✅" in ins, f"insert failed: {ins}"
        out = _run_tool("omt_think_verify", {"path": str(f), "line": 3}, cwd=tmp_path)
        assert out is not None, "omt_think_verify tool missing or runner failed"
        assert "verified" in out, f"must verify: {out!r}"
        assert "basis: anchor" in out, f"basis must be anchor: {out!r}"
        ver = [r for r in _index_records(tmp_path, f.name, kind="verify") if r.get("thought") == m]
        assert ver, f"no verify record for the thought: {_index_records(tmp_path, f.name)}"
        assert ver[-1].get("status") == "verified" and ver[-1].get("basis") == "anchor", (
            f"verify record wrong: {ver[-1]}")
        assert ver[-1].get("line") == 3, f"verify record line wrong: {ver[-1]}"

    def test_anchor_deleted_stale(self, tmp_path):
        """design §3.2 — anchor line deleted after insert → STALE; verify
        record {status:stale}."""
        f = _write_tmp(tmp_path, "v2.py", "alpha = 1\nbeta = 2\n")
        m = _marker()
        ins = _run_tool("omt_think", {"path": str(f), "thought": m, "after": "alpha = 1"}, cwd=tmp_path)
        assert ins is not None and "✅" in ins, f"insert failed: {ins}"
        # Delete the anchor line; the thought shifts up to line 1.
        lines = f.read_text().splitlines()
        f.write_text("\n".join(lines[1:]) + "\n", encoding="utf-8")
        out = _run_tool("omt_think_verify", {"path": str(f), "line": 1}, cwd=tmp_path)
        assert out is not None, "omt_think_verify tool missing or runner failed"
        assert "STALE" in out, f"must be stale: {out!r}"
        ver = [r for r in _index_records(tmp_path, f.name, kind="verify") if r.get("thought") == m]
        assert ver and ver[-1].get("status") == "stale", f"verify record wrong: {ver[-1] if ver else None}"

    def test_anchor_duplicated_stale(self, tmp_path):
        """design §3.3 — anchor text duplicated after insert (2 matches) →
        STALE (ambiguous)."""
        f = _write_tmp(tmp_path, "v3.py", "alpha = 1\nbeta = 2\n")
        m = _marker()
        ins = _run_tool("omt_think", {"path": str(f), "thought": m, "after": "alpha = 1"}, cwd=tmp_path)
        assert ins is not None and "✅" in ins, f"insert failed: {ins}"
        # Duplicate the anchor text on a later line; thought stays at line 2.
        f.write_text(f.read_text() + "alpha = 1\n", encoding="utf-8")
        out = _run_tool("omt_think_verify", {"path": str(f), "line": 2}, cwd=tmp_path)
        assert out is not None, "omt_think_verify tool missing or runner failed"
        assert "STALE" in out, f"ambiguous anchor must be stale: {out!r}"
        ver = [r for r in _index_records(tmp_path, f.name, kind="verify") if r.get("thought") == m]
        assert ver and ver[-1].get("status") == "stale", f"verify record wrong: {ver[-1] if ver else None}"

    def test_thought_drifted_stale_anchor_moved(self, tmp_path):
        """design §3.4 — line inserted between anchor and thought → STALE
        ('anchor moved'); exercises the (path,text) index fallback (the
        thought's current line no longer matches the add-record line)."""
        f = _write_tmp(tmp_path, "v4.py", "alpha = 1\nbeta = 2\n")
        m = _marker()
        ins = _run_tool("omt_think", {"path": str(f), "thought": m, "after": "alpha = 1"}, cwd=tmp_path)
        assert ins is not None and "✅" in ins, f"insert failed: {ins}"
        # Insert a line between anchor (line 1) and thought (line 2 → 3).
        lines = f.read_text().splitlines()
        f.write_text("\n".join([lines[0], "gamma = 3"] + lines[1:]) + "\n", encoding="utf-8")
        out = _run_tool("omt_think_verify", {"path": str(f), "line": 3}, cwd=tmp_path)
        assert out is not None, "omt_think_verify tool missing or runner failed"
        assert "STALE" in out, f"drifted thought must be stale: {out!r}"
        assert "anchor moved" in out, f"reason must name the move: {out!r}"

    def test_line_mode_verified_basis_exists(self, tmp_path):
        """design §3.5 — line-mode thought (anchor:null record) → verified,
        basis exists (weaker: existence only)."""
        f = _write_tmp(tmp_path, "v5.py", "alpha = 1\nbeta = 2\n")
        m = _marker()
        ins = _run_tool("omt_think", {"path": str(f), "thought": m, "line": 1}, cwd=tmp_path)
        assert ins is not None and "✅" in ins, f"insert failed: {ins}"
        out = _run_tool("omt_think_verify", {"path": str(f), "line": 2}, cwd=tmp_path)
        assert out is not None, "omt_think_verify tool missing or runner failed"
        assert "verified" in out, f"must verify: {out!r}"
        assert "basis: exists" in out, f"basis must be exists: {out!r}"

    def test_handwritten_no_index_verified_basis_exists(self, tmp_path):
        """design §3.6 — hand-written TA: line, no index record at all →
        verified, basis exists."""
        m = _marker()
        f = _write_tmp(tmp_path, "v6.py", f"x = 1\n# TA: gotcha: {m}\n")
        out = _run_tool("omt_think_verify", {"path": str(f), "line": 2}, cwd=tmp_path)
        assert out is not None, "omt_think_verify tool missing or runner failed"
        assert "verified" in out, f"must verify: {out!r}"
        assert "basis: exists" in out, f"basis must be exists: {out!r}"

    def test_non_thought_line_refused(self, tmp_path):
        """design §3.7 — verify at a non-thought line → 'not a TA: comment'
        refusal."""
        f = _write_tmp(tmp_path, "v7.py", "x = 1\n# an ordinary comment\n")
        out = _run_tool("omt_think_verify", {"path": str(f), "line": 1}, cwd=tmp_path)
        assert out is not None, "omt_think_verify tool missing or runner failed"
        assert "not a TA: comment" in out, f"refusal: {out!r}"

    def test_line_out_of_range_refused(self, tmp_path):
        """design §3.8 — line out of range → refusal naming the file length."""
        f = _write_tmp(tmp_path, "v8.py", "x = 1\ny = 2\n")
        out = _run_tool("omt_think_verify", {"path": str(f), "line": 99}, cwd=tmp_path)
        assert out is not None, "omt_think_verify tool missing or runner failed"
        assert "out of range" in out, f"refusal: {out!r}"
        assert "file has" in out, f"must name the file length: {out!r}"

    def test_missing_file_refused(self, tmp_path):
        """design §3.9 — missing file → refusal."""
        out = _run_tool("omt_think_verify",
                        {"path": str(tmp_path / "no_such_file_xyz.py"), "line": 1}, cwd=tmp_path)
        assert out is not None, "omt_think_verify tool missing or runner failed"
        assert "does not exist" in out, f"refusal: {out!r}"

    def test_protected_path_refused(self, tmp_path):
        """design §3.10 — protected path (.env) → refusal (never reads the file)."""
        out = _run_tool("omt_think_verify", {"path": ".env", "line": 1}, cwd=tmp_path)
        assert out is not None, "omt_think_verify tool missing or runner failed"
        assert "protected" in out, f"refusal: {out!r}"


# ---------------------------------------------------------------------------
# C1 — digest stale count (session-start; unique temp file INSIDE repo root)
# ---------------------------------------------------------------------------
@needs_node
class TestC1Digest:
    def test_digest_reports_stale(self, tmp_path):
        """design §3.11 — one current thought marked stale → digest contains
        'stale' + the omt_think_verify pointer. Temp file lives inside the tmp
        cwd (digest greps the cwd with F17 isolation); finally: remove thought + unlink."""
        name = f"ta_digest_{uuid.uuid4().hex[:8]}.py"
        f = tmp_path / name
        m = _marker()
        try:
            f.write_text("alpha = 1\nbeta = 2\n", encoding="utf-8")
            ins = _run_tool("omt_think", {"path": name, "thought": m, "after": "alpha = 1"}, cwd=tmp_path)
            assert ins is not None and "✅" in ins, f"insert failed: {ins}"
            # Break the anchor; the thought shifts up to line 1 → verify → stale.
            lines = f.read_text().splitlines()
            f.write_text("\n".join(lines[1:]) + "\n", encoding="utf-8")
            ver = _run_tool("omt_think_verify", {"path": name, "line": 1}, cwd=tmp_path)
            assert ver is not None and "STALE" in ver, f"verify must go stale: {ver}"
            digest = _session_start(tmp_path)
            assert digest is not None, "session-start mode missing or runner failed"
            assert "stale" in digest, f"digest must report stale thoughts: {digest!r}"
            assert "omt_think_verify" in digest, f"digest must point at verify: {digest!r}"
        finally:
            if f.exists():
                _run_tool("omt_think_remove", {"path": name, "line": 1}, cwd=tmp_path)
                f.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# C1 — gate weighting (before-hook; tmpdir directory; no consult → blocked)
# ---------------------------------------------------------------------------
@needs_node
class TestC1GateWeighting:
    def test_risk_renders_before_other_categories(self, tmp_path):
        """design §3.12 — gotcha: (line 1) + risk: (line 2) → block message
        renders the risk: thought before the gotcha: one."""
        ggg, rrr = "GGGMARK_" + uuid.uuid4().hex[:6], "RRRMARK_" + uuid.uuid4().hex[:6]
        f = _write_tmp(tmp_path, "carry.py", f"# TA: gotcha: {ggg}\n# TA: risk: {rrr}\nx = 1\n")
        results = _before_hook_batch(tmp_path, [_edit_call(f, "s1")])
        assert results is not None, "before-hook runner failed"
        assert results[0]["blocked"], f"must block (no consult): {results[0]}"
        msg = results[0]["message"]
        assert rrr in msg and ggg in msg, f"both thoughts must render: {msg!r}"
        assert msg.index(rrr) < msg.index(ggg), (
            f"risk: thought must render before gotcha:: {msg!r}")

    def test_stale_suffix_from_tmpdir_index(self, tmp_path):
        """design §3.13 — tmpdir index seeded stale for the line-2 thought →
        its block-message line carries '⚠️ STALE'; a verified-record line does
        not."""
        ggg, rrr = "GGGMARK_" + uuid.uuid4().hex[:6], "RRRMARK_" + uuid.uuid4().hex[:6]
        f = _write_tmp(tmp_path, "carry.py", f"# TA: gotcha: {ggg}\n# TA: risk: {rrr}\nx = 1\n")
        _seed_index(tmp_path, [
            {"ts": _now_iso(), "kind": "verify", "path": "carry.py", "line": 1,
             "status": "verified", "basis": "anchor"},
            {"ts": _now_iso(), "kind": "verify", "path": "carry.py", "line": 2,
             "status": "stale", "basis": "anchor"},
        ])
        results = _before_hook_batch(tmp_path, [_edit_call(f, "s1")])
        assert results is not None, "before-hook runner failed"
        assert results[0]["blocked"], f"must block (no consult): {results[0]}"
        msg = results[0]["message"]
        stale_line = next((l for l in msg.splitlines() if rrr in l), None)
        verified_line = next((l for l in msg.splitlines() if ggg in l), None)
        assert stale_line is not None and verified_line is not None, (
            f"both thoughts must render: {msg!r}")
        assert "STALE" in stale_line, f"stale line must carry the marker: {stale_line!r}"
        assert "STALE" not in verified_line, (
            f"verified line must not carry the marker: {verified_line!r}")

    def test_no_index_fail_open_no_stale(self, tmp_path):
        """design §3.14 — no index file at all → block message renders
        normally, no STALE (fail-open control)."""
        m = _marker()
        f = _write_tmp(tmp_path, "carry.py", f"# TA: {m}\nx = 1\n")
        results = _before_hook_batch(tmp_path, [_edit_call(f, "s1")])
        assert results is not None, "before-hook runner failed"
        assert results[0]["blocked"], f"must block (no consult): {results[0]}"
        msg = results[0]["message"]
        assert m in msg, f"thought must render: {msg!r}"
        assert "STALE" not in msg, f"no index → no STALE markers: {msg!r}"


# ---------------------------------------------------------------------------
# C2 — consult record gains files[] (real ledger; assert only new records)
# ---------------------------------------------------------------------------
@needs_node
class TestC2ConsultRecord:
    def test_list_records_consulted_files(self, tmp_path):
        """design §3.15 — omt_think_list on a tmp file with a thought → new
        think_consult record has files containing the tmp file's rel path."""
        m = _marker()
        f = _write_tmp(tmp_path, "cons.py", f"x = 1\n# TA: {m}\n")
        offset = _ledger_size(tmp_path)
        out = _run_tool("omt_think_list", {"path": str(f)}, cwd=tmp_path)
        assert out is not None and m in out, f"list must find the thought: {out!r}"
        new = [r for r in _ledger_records_after(tmp_path, offset) if r.get("kind") == "think_consult"]
        assert new, "omt_think_list must append a think_consult record"
        files = new[-1].get("files")
        assert isinstance(files, list), f"consult record must carry files[]: {new[-1]}"
        assert f.name in files, f"consulted files must include the tmp file: {files}"

    def test_list_empty_result_records_empty_files(self, tmp_path):
        """design §3.16 — omt_think_list with 0 hits → new record has
        files: [] (covers nothing; no clearance granted)."""
        f = _write_tmp(tmp_path, "empty.py", "x = 1\n")
        offset = _ledger_size(tmp_path)
        out = _run_tool("omt_think_list",
                        {"path": str(f), "query": "NOMATCH_" + uuid.uuid4().hex[:8]}, cwd=tmp_path)
        assert out is not None and "0 thoughts" in out, f"must be empty: {out!r}"
        new = [r for r in _ledger_records_after(tmp_path, offset) if r.get("kind") == "think_consult"]
        assert new, "omt_think_list must still record the consult"
        assert new[-1].get("files") == [], (
            f"empty result → files must be []: {new[-1]}")


# ---------------------------------------------------------------------------
# C2 — hasConsultedThoughts (consulted runner mode; tmpdir ledger root)
# ---------------------------------------------------------------------------
@needs_node
class TestC2HasConsulted:
    def test_exact_session_per_file_coverage(self, tmp_path):
        """design §3.17 — exact-session record files:[a.py] →
        consulted(a.py)=true, consulted(b.py)=false."""
        _seed_ledger(tmp_path, [
            {"ts": _now_iso(), "kind": "think_consult", "session": "s1", "files": ["a.py"]},
        ])
        assert _consulted(session="s1", rel="a.py", root=tmp_path) is True, (
            "covered file must be consulted")
        assert _consulted(session="s1", rel="b.py", root=tmp_path) is False, (
            "uncovered file must not be consulted")

    def test_legacy_record_grandfathered(self, tmp_path):
        """design §3.18 — legacy record (no files) same session →
        consulted(any rel)=true (grandfather; ages out with the window)."""
        _seed_ledger(tmp_path, [
            {"ts": _now_iso(), "kind": "think_consult", "session": "s1"},
        ])
        assert _consulted(session="s1", rel="anything.py", root=tmp_path) is True, (
            "legacy no-files record must grandfather any rel")

    def test_cross_session_window_without_risk(self, tmp_path):
        """design §3.19 — cross-session within-window record files:[a.py],
        no risk → consulted=true."""
        _seed_ledger(tmp_path, [
            {"ts": _now_iso(), "kind": "think_consult", "session": "other", "files": ["a.py"]},
        ])
        assert _consulted(session="s1", rel="a.py", risk=False, root=tmp_path) is True, (
            "within-window cross-session consult must clear non-risk files")

    def test_cross_session_window_dropped_for_risk(self, tmp_path):
        """design §3.20 — same as §3.19 with risk:true → consulted=false
        (window dropped for risk:)."""
        _seed_ledger(tmp_path, [
            {"ts": _now_iso(), "kind": "think_consult", "session": "other", "files": ["a.py"]},
        ])
        assert _consulted(session="s1", rel="a.py", risk=True, root=tmp_path) is False, (
            "risk:-carrying file demands an exact-session consult")


# ---------------------------------------------------------------------------
# C2 — before-hook integration (tmpdir; files carry thoughts)
# ---------------------------------------------------------------------------
@needs_node
class TestC2BeforeHook:
    def test_per_file_consult_allows_only_covered_file(self, tmp_path):
        """design §3.21 — ledger exact-session consult files:[A] → edit A
        allowed, edit B blocked (one plugin instance, batch of 2)."""
        ma, mb = _marker(), _marker()
        fa = _write_tmp(tmp_path, "a.py", f"x = 1\n# TA: {ma}\n")
        fb = _write_tmp(tmp_path, "b.py", f"y = 2\n# TA: {mb}\n")
        _seed_ledger(tmp_path, [
            {"ts": _now_iso(), "kind": "think_consult", "session": "s1", "files": ["a.py"]},
        ])
        results = _before_hook_batch(tmp_path, [_edit_call(fa, "s1"), _edit_call(fb, "s1")])
        assert results is not None, "before-hook runner failed"
        assert results[0]["blocked"] is False, (
            f"consulted file must be editable: {results[0]}")
        assert results[1]["blocked"] is True, (
            f"unconsulted thought-carrying file must block: {results[1]}")

    def test_risk_file_requires_exact_session_consult(self, tmp_path):
        """design §3.22 — R carries a risk: thought; ledger has only a
        cross-session within-window consult covering R → edit R blocked;
        after adding an exact-session consult for R → allowed."""
        m = _marker()
        fr = _write_tmp(tmp_path, "r.py", f"x = 1\n# TA: risk: {m}\n")
        _seed_ledger(tmp_path, [
            {"ts": _now_iso(), "kind": "think_consult", "session": "other", "files": ["r.py"]},
        ])
        first = _before_hook_batch(tmp_path, [_edit_call(fr, "s1")])
        assert first is not None, "before-hook runner failed"
        assert first[0]["blocked"] is True, (
            f"risk: file must block without an exact-session consult: {first[0]}")
        _seed_ledger(tmp_path, [
            {"ts": _now_iso(), "kind": "think_consult", "session": "s1", "files": ["r.py"]},
        ])
        second = _before_hook_batch(tmp_path, [_edit_call(fr, "s1")])
        assert second is not None, "before-hook runner failed"
        assert second[0]["blocked"] is False, (
            f"exact-session consult must clear the risk: file: {second[0]}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
