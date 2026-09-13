"""T3-3 resume digest (feature_092.resume_digest).

Golden: simulated post-compaction resume = 1 digest read —
``omt_status{op:"resume"}`` returns a ≤2KB re-orientation (identity banner,
project Quick-Start Next, WORK.md next task, session trail, doc anchors)
instead of the ~58KB WORK.md+PROJECT.md+CURRENT_STATE.md re-read set
(mh3 measured: reads = 66% of tool bytes, same file re-read up to 29×/session;
root cause = compaction eviction, harness leverage indirect).

Design: 4.design/features/feature_092.resume_digest/design_001_resume_digest.md
"""
import json
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
OMT_STATUS_PLUGIN = REPO_ROOT / ".opencode" / "plugins" / "omt_status.ts"
SHARED_LIB = REPO_ROOT / ".opencode" / "lib" / "omt_shared"

BUN = shutil.which("bun")

F = "feature_092.resume_digest"
PROJECT = "mh8_probe"
DIGEST_CAP = 2048


def _copy_real_ir(tmp_path: Path) -> None:
    ir_dst = tmp_path / ".meta" / ".omt"
    ir_dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        REPO_ROOT / ".meta" / ".omt" / "harness.ir.json",
        ir_dst / "harness.ir.json",
    )


def _write_ledger(tmp_path: Path, records: list[dict]) -> Path:
    p = tmp_path / ".meta" / ".omt" / "ledger.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")
    return p


def _write_work_md(tmp_path: Path, task_line: str) -> None:
    (tmp_path / "WORK.md").write_text(
        "# WORK\n\n## Tasks\n\n" + task_line + "\n", encoding="utf-8")


def _write_project_home(tmp_path: Path, project: str, next_line: str) -> None:
    home = tmp_path / ".projects" / "meta" / project
    home.mkdir(parents=True, exist_ok=True)
    (home / "PROJECT.md").write_text(
        "# PROJECT\n\n## New Session Quick Start\n\n**Next:** " + next_line + "\n"
        "\n## The tracks\n\n(the rest of a 34KB PROJECT.md would live here)\n",
        encoding="utf-8")
    (home / "CURRENT_STATE.md").write_text(
        "# CURRENT_STATE\n\n> log\n\n---\n\n"
        "## 2026-09-13 (iter — resume digest work)\n\n- seeded entry\n",
        encoding="utf-8")


_probe_template = """
import { initOmtShared } from "%LIB%"
initOmtShared(process.argv[2])
const mod = await import("%PLUGIN%")
const { tool } = await mod.default({ directory: process.argv[2], worktree: process.argv[2] })
const result = await tool.omt_status.execute(%ARGS%, { sessionID: "%SESSION%" })
console.log(JSON.stringify(result))
"""


def _probe(args: dict, session: str, tmp_path: Path) -> dict:
# TA: gotcha: GOTCHA_PROBE_SERIALIZATION: omt_q execute returns JSON.stringify'd string (console.log(result) parses) but omt_status returns a plain object — bun console.log(obj) prints inspect format (unquoted keys, multi-line) so json.loads fails; object-returning tools MUST console.log(JSON.stringify(result)) (task_prep_slice.py:29 precedent). Root cause of 7 JSONDecodeError failures mid-feature_092; digest logic verified good via manual probe (432B).
    assert BUN is not None, "bun runtime required"
    probe = tmp_path / "probe_t33.ts"
    probe.write_text(
        _probe_template
        .replace("%LIB%", str(SHARED_LIB))
        .replace("%PLUGIN%", str(OMT_STATUS_PLUGIN))
        .replace("%ARGS%", json.dumps(args))
        .replace("%SESSION%", session),
        encoding="utf-8")
    out = subprocess.run([BUN, str(probe), str(tmp_path)],
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, f"bun probe failed:\n{out.stderr}\n---"
    return json.loads(out.stdout.strip().splitlines()[-1])


def _seeded_records(session: str, scope: str = "omt_status op:resume") -> list[dict]:
    base = datetime.now(timezone.utc) - timedelta(hours=1)
    ts = lambda m: (base + timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return [
        {"ts": ts(0), "kind": "think_consult", "session": session,
         "files": ["src/x.py"], "feature": F},
        {"ts": ts(2), "kind": "tdd_testlist", "session": session, "feature": F},
        {"ts": ts(4), "kind": "tdd", "session": session, "state": "red",
         "test_node": "tests/scripts/omt/test_resume_digest.py::test_one_read_resume",
         "feature": F},
        {"ts": ts(6), "kind": "phase", "session": session,
         "task_type": "minor_feature", "phase": "Programming",
         "scope": scope, "feature": F},
        {"ts": ts(7), "kind": "project_link", "feature": F, "project": PROJECT},
        {"ts": ts(8), "kind": "project", "project": PROJECT, "op": "create"},
    ]


class TestResumeDigest:
    """T3-3: op:resume — one ≤2KB read re-orients a post-compaction agent."""

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_one_read_resume(self, tmp_path):
        """The acceptance golden: seeded mid-feature session → 1 digest read
        carries identity, project Quick-Start Next, WORK.md next task, session
        trail (anti-duplicate signal), and doc anchors with sizes."""
        _copy_real_ir(tmp_path)
        _write_ledger(tmp_path, _seeded_records("ses_t33"))
        _write_work_md(tmp_path, "- [ ] T3-3 ship the resume digest")
        _write_project_home(tmp_path, PROJECT,
                            "T3-3 resume digest — design note first")

        out = _probe({"op": "resume"}, "ses_t33", tmp_path)
        text = out["output"]
        assert out["title"] == "OMT++ Resume Digest"
        nbytes = len(text.encode("utf-8"))
        assert nbytes <= DIGEST_CAP, f"digest {nbytes}B > {DIGEST_CAP}B:\n{text}"
        # identity banner
        assert "RESUME DIGEST" in text
        assert "minor_feature" in text and "Programming" in text
        assert F in text and "expires" in text
        # project + Quick-Start Next (the 34KB re-read, distilled)
        assert PROJECT in text
        assert "design note first" in text
        # WORK.md next task
        assert "T3-3 ship the resume digest" in text
        # session trail — what THIS session already did (anti-duplicate)
        assert "Trail (this session, 4)" in text, text
        for marker in ("think_consult", "tdd_testlist", "tdd red",
                       "phase Programming"):
            assert marker in text, f"trail missing '{marker}':\n{text}"
        # doc anchors: sizes + line anchors for bounded partial re-reads
        assert "WORK.md" in text
        assert "PROJECT.md" in text and "QuickStart@L" in text
        assert "CURRENT_STATE.md" in text and "newest@L" in text
        # metadata: small, honest byte count, not truncated
        assert out["metadata"]["op"] == "resume"
        assert out["metadata"]["cap"] == DIGEST_CAP
        assert out["metadata"]["truncated"] is False
        assert out["metadata"]["digest_bytes"] == nbytes

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_ledger_read_only(self, tmp_path):
        """A4 pin: op:resume never writes the ledger (byte-identical)."""
        _copy_real_ir(tmp_path)
        p = _write_ledger(tmp_path, _seeded_records("ses_t33"))
        _write_work_md(tmp_path, "- [ ] T3-3 ship the resume digest")
        _write_project_home(tmp_path, PROJECT, "T3-3 resume digest")
        before = p.read_bytes()
        _probe({"op": "resume"}, "ses_t33", tmp_path)
        assert p.read_bytes() == before, "op:resume must not write the ledger"

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_over_cap_drops_optional_then_marks(self, tmp_path):
        """Pathological seed (long scope + long task + fat trail) → optional
        lines (docs, trail) drop, marker lands, total stays ≤2048B."""
        _copy_real_ir(tmp_path)
        base = datetime.now(timezone.utc) - timedelta(hours=1)
        ts = lambda m: (base + timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%M:%SZ")
        records = _seeded_records("ses_t33", scope="s" * 400)
        node = "tests/scripts/omt/test_resume_digest.py::test_over_cap_drop_optional"
        for i in range(40):
            records.append({"ts": ts(10 + i), "kind": "tdd", "session": "ses_t33",
                            "state": "red", "test_node": node, "feature": F})
        _write_ledger(tmp_path, records)
        task = "t" * 500
        _write_work_md(tmp_path, "- [ ] " + task)
        _write_project_home(tmp_path, PROJECT, "n" * 200)

        out = _probe({"op": "resume"}, "ses_t33", tmp_path)
        text = out["output"]
        nbytes = len(text.encode("utf-8"))
        assert nbytes <= DIGEST_CAP, f"digest {nbytes}B > {DIGEST_CAP}B:\n{text}"
        assert "digest capped" in text, text
        assert out["metadata"]["truncated"] is True
        assert out["metadata"]["digest_bytes"] == nbytes
        # optional lines were the droppable ones
        assert "Trail (this session" not in text
        assert "Docs:" not in text
        # mandatory identity + next action survive
        assert "RESUME DIGEST" in text and task[:64] in text

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_hard_cut_when_mandatory_alone_over_cap(self, tmp_path):
        """Banner alone over cap (3KB scope) → hard-cut + marker, ≤2048B."""
        _copy_real_ir(tmp_path)
        _write_ledger(tmp_path, _seeded_records("ses_t33", scope="x" * 3000))
        _write_work_md(tmp_path, "- [ ] T3-3 ship the resume digest")
        _write_project_home(tmp_path, PROJECT, "T3-3 resume digest")

        out = _probe({"op": "resume"}, "ses_t33", tmp_path)
        text = out["output"]
        nbytes = len(text.encode("utf-8"))
        assert nbytes <= DIGEST_CAP, f"digest {nbytes}B > {DIGEST_CAP}B:\n{text}"
        assert "digest capped" in text
        assert out["metadata"]["truncated"] is True
        assert text.startswith("\U0001F9ED RESUME DIGEST"), text[:80]

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_no_unlock_cross_session_resume(self, tmp_path):
        """Fresh session, stale unlock (2d old): honest 'no unlock' banner +
        Last-activity fallback + project Quick-Start Next still orient."""
        _copy_real_ir(tmp_path)
        old = datetime.now(timezone.utc) - timedelta(days=2)
        F2 = "feature_091.budget_diet_bot"
        _write_ledger(tmp_path, [
            {"ts": old.strftime("%Y-%m-%dT%H:%M:%SZ"), "kind": "phase",
             "session": "ses_old", "task_type": "minor_feature",
             "phase": "Testing", "scope": "budget diet", "feature": F2},
            {"ts": old.strftime("%Y-%m-%dT%H:%M:%SZ"), "kind": "project_link",
             "feature": F2, "project": PROJECT},
            {"ts": old.strftime("%Y-%m-%dT%H:%M:%SZ"), "kind": "project",
             "project": PROJECT, "op": "create"},
        ])
        _write_work_md(tmp_path, "- [ ] T3-3 ship the resume digest")
        _write_project_home(tmp_path, PROJECT,
                            "T3-3 resume digest — design note first")

        out = _probe({"op": "resume"}, "ses_fresh", tmp_path)
        text = out["output"]
        assert len(text.encode("utf-8")) <= DIGEST_CAP
        assert "no unlock" in text
        assert "Last:" in text and F2 in text
        # cross-session: project context still orients via the stale link
        assert PROJECT in text and "design note first" in text
        assert "T3-3 ship the resume digest" in text

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_fast_path_no_lint_no_status_banner(self, tmp_path):
        """op:resume skips the lint subprocess (fast read) and is NOT the
        default status render (no OMT++ STATUS banner, no lint line)."""
        _copy_real_ir(tmp_path)
        _write_ledger(tmp_path, _seeded_records("ses_t33"))
        _write_work_md(tmp_path, "- [ ] T3-3 ship the resume digest")
        _write_project_home(tmp_path, PROJECT, "T3-3 resume digest")

        out = _probe({"op": "resume"}, "ses_t33", tmp_path)
        text = out["output"]
        assert "OMT++ STATUS" not in text
        assert "lint" not in text
        # TDD subprocess is fail-open in the hermetic tmp root (no uv project)
        assert "TDD Mode" not in text

    @pytest.mark.skipif(BUN is None, reason="bun runtime not available")
    def test_op_surface(self, tmp_path):
        """op enum: resume accepted; unknown op names all three ops."""
        _copy_real_ir(tmp_path)
        _write_ledger(tmp_path, _seeded_records("ses_t33"))
        _write_work_md(tmp_path, "- [ ] T3-3 ship the resume digest")
        _write_project_home(tmp_path, PROJECT, "T3-3 resume digest")

        bogus = _probe({"op": "bogus"}, "ses_t33", tmp_path)
        assert bogus["metadata"]["error"] == "unknown op"
        assert "status (default) | preflight | resume" in bogus["output"]
