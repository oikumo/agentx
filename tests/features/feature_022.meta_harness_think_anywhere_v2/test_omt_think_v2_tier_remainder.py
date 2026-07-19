"""
Test suite for feature_022: Think Anywhere V2 — Tier Remainder (B2 + E1 + E2).

Covers design_004_tier_b2_e1_e2.md §4 tests 1–16 (each test cites its item):

  B2  omt_think_suggest{path, top?} — read-only AST-ranked insertion-site
      advisor (paper's table Assign>Return>Expr>If>AugAssign, source-order
      tie-break, coverage exclusion ±1 line, end_lineno splice-safety,
      clean refusals, no side effects).
  E1  omt_think_reindex{path?} — JSONL index reconciliation (keep / repair
      with repaired_from / drop dead-vanished-ambiguous, verify-record prune,
      path filter, idempotence).
  E2  theory-doc guard — every ```python fence in think_anywhere_langchain.md
      ast.parses; F10–F13 fix markers present, defect markers absent.

Strategy mirrors Tiers A–C: invoke the REAL plugin tools via _think_runner.mjs
(node, cwd=REPO_ROOT, tmp_path fixtures) — no opencode server, no reimplementation.
"""

import ast
import json
import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
TEST_DIR = Path(__file__).parent
THINK_RUNNER = TEST_DIR / "_think_runner.mjs"
THOUGHTS_INDEX = REPO_ROOT / ".meta" / ".omt" / "thoughts.jsonl"
THEORY_DOC = REPO_ROOT / ".meta" / "doc" / "harness" / "think_anywhere_langchain.md"

NODE = shutil.which("node")
needs_node = pytest.mark.skipif(not NODE, reason="node not available")


def _run_tool(tool_name: str, args: dict | None = None, timeout: int = 60):
    """Invoke a real omt_think plugin tool via node; return its string result or None."""
    if not NODE:
        return None
    proc = subprocess.run(
        [NODE, "--experimental-strip-types", str(THINK_RUNNER), tool_name, json.dumps(args or {})],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=timeout,
    )
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def _marker() -> str:
    return "TAUTOMARK_" + uuid.uuid4().hex[:8]


def _write_tmp(tmp_path: Path, name: str, content: str = "") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def _rel(p: Path) -> str:
    return os.path.relpath(str(p), str(REPO_ROOT))


def _index_records(path_filter: str, kind: str | None = "__none__") -> list[dict]:
    """thoughts.jsonl records for a rel path. kind: '__none__' = add-records only
    (no kind field); 'verify' = verify records; None = all kinds."""
    recs = []
    if THOUGHTS_INDEX.exists():
        for line in THOUGHTS_INDEX.read_text().splitlines():
            s = line.strip()
            if not s:
                continue
            try:
                r = json.loads(s)
            except json.JSONDecodeError:
                continue
            if isinstance(r, dict) and r.get("path") == path_filter:
                if kind == "__none__" and "kind" not in r:
                    recs.append(r)
                elif kind is not None and kind != "__none__" and r.get("kind") == kind:
                    recs.append(r)
                elif kind is None:
                    recs.append(r)
    return recs


def _seed_index(records: list[dict]) -> None:
    THOUGHTS_INDEX.parent.mkdir(parents=True, exist_ok=True)
    with THOUGHTS_INDEX.open("a", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


# Fixture: one ranked statement of each paper-table kind, scrambled line order.
RANKED_FIXTURE = (
    "x = 1\n"               # L1 Assign
    "def f():\n"
    "    if x:\n"           # L3 If
    "        pass\n"
    "    y = []\n"          # L5 Assign
    "    y.append(1)\n"     # L6 Expr
    "    x += 1\n"          # L7 AugAssign
    "    return y\n"        # L8 Return
)


# ---------------------------------------------------------------------------
# B2 — omt_think_suggest
# ---------------------------------------------------------------------------
@needs_node
class TestB2Suggest:
    def test_suggest_ranking_order(self, tmp_path):
        """design §4.1 — output order = paper rank (Assign>Return>Expr>If>AugAssign),
        source-order tie-break inside one rank."""
        f = _write_tmp(tmp_path, "ranked.py", RANKED_FIXTURE)
        out = _run_tool("omt_think_suggest", {"path": str(f), "top": 6})
        assert out is not None, "runner failed (tool missing?)"
        kinds = re.findall(r"L\d+ (\w+) →", out)
        assert kinds == ["Assign", "Assign", "Return", "Expr", "If", "AugAssign"]

    def test_suggest_top_clamp(self, tmp_path):
        """design §4.2 — top=2 → exactly 2 sites; top=0 clamps to 1."""
        f = _write_tmp(tmp_path, "clamp.py", RANKED_FIXTURE)
        out = _run_tool("omt_think_suggest", {"path": str(f), "top": 2})
        assert out is not None
        assert len(re.findall(r"^\s*\d+\. L\d+", out, re.M)) == 2
        out1 = _run_tool("omt_think_suggest", {"path": str(f), "top": 0})
        assert out1 is not None
        assert len(re.findall(r"^\s*\d+\. L\d+", out1, re.M)) == 1

    def test_suggest_excludes_covered(self, tmp_path):
        """design §4.3 — a thought adjacent (±1) to a site excludes it; the
        covered count is reported."""
        f = _write_tmp(tmp_path, "covered.py",
                       "# TA: gotcha: header note\nx = 1\ny = 2\nz = 3\n")
        out = _run_tool("omt_think_suggest", {"path": str(f)})
        assert out is not None
        assert "1 already covered" in out
        assert "L3 Assign" in out          # y = 2 uncovered → suggested
        assert "L2 Assign" not in out      # x = 1 covered (thought at L1) → excluded

    def test_suggest_refuses_non_py(self, tmp_path):
        """design §4.4 — non-.py extension → refusal naming the extension."""
        f = _write_tmp(tmp_path, "s.ts", "const x = 1\n")
        out = _run_tool("omt_think_suggest", {"path": str(f)})
        assert out is not None
        assert "refused" in out and ".ts" in out

    def test_suggest_refuses_protected_and_missing(self, tmp_path):
        """design §4.5 — protected rel and nonexistent file → refusal strings."""
        out_p = _run_tool("omt_think_suggest", {"path": "README.md"})
        assert out_p is not None and "protected" in out_p
        out_m = _run_tool("omt_think_suggest",
                          {"path": f"no_such_dir_{uuid.uuid4().hex[:6]}/ghost.py"})
        assert out_m is not None and "does not exist" in out_m

    def test_suggest_unparseable(self, tmp_path):
        """design §4.6 — syntax-error .py → clean refusal string (exit 0, no crash)."""
        f = _write_tmp(tmp_path, "broken.py", "def broken(:\n")
        out = _run_tool("omt_think_suggest", {"path": str(f)})
        assert out is not None, "runner crashed instead of returning a refusal"
        assert "refused" in out

    def test_suggest_multiline_end(self, tmp_path):
        """design §4.7 — multi-line statement suggests insertAfter = end_lineno
        (splice-safe), not the statement's first line."""
        f = _write_tmp(tmp_path, "multi.py",
                       "result = compute(\n    a, b,\n)\n")
        out = _run_tool("omt_think_suggest", {"path": str(f)})
        assert out is not None
        assert "L1 Assign → insert after L3" in out

    def test_suggest_read_only(self, tmp_path):
        """design §4.8 — no target writes, no index writes."""
        f = _write_tmp(tmp_path, "ro.py", RANKED_FIXTURE)
        before_bytes = f.read_bytes()
        idx_before = THOUGHTS_INDEX.read_bytes() if THOUGHTS_INDEX.exists() else None
        out = _run_tool("omt_think_suggest", {"path": str(f)})
        assert out is not None
        assert f.read_bytes() == before_bytes
        idx_after = THOUGHTS_INDEX.read_bytes() if THOUGHTS_INDEX.exists() else None
        assert idx_after == idx_before

    def test_suggest_zero_candidates(self, tmp_path):
        """design §4.9 — no ranked statements → 0-candidates message."""
        f = _write_tmp(tmp_path, "empty.py", "# nothing ranked here\n")
        out = _run_tool("omt_think_suggest", {"path": str(f)})
        assert out is not None
        assert "0 candidate sites" in out


# ---------------------------------------------------------------------------
# E1 — omt_think_reindex
# ---------------------------------------------------------------------------
@needs_node
class TestE1Reindex:
    def test_reindex_keep_idempotent(self, tmp_path):
        """design §4.10 — live at-line record kept; second run all-keep."""
        text = _marker()
        f = _write_tmp(tmp_path, "keep.py", f"a = 1\n# TA: {text}\n")
        rel = _rel(f)
        _seed_index([{"path": rel, "line": 2, "category": None, "thought": text, "anchor": None}])
        out1 = _run_tool("omt_think_reindex", {"path": rel})
        assert out1 is not None
        assert "kept 1" in out1 and "repaired 0" in out1 and "dropped 0" in out1
        out2 = _run_tool("omt_think_reindex", {"path": rel})
        assert out2 is not None
        assert "kept 1" in out2 and "repaired 0" in out2 and "dropped 0" in out2

    def test_reindex_repairs_drift(self, tmp_path):
        """design §4.11 — record line drifts (thought actually at L3, record says
        L1) → repaired 1→3 with repaired_from; old-slot verify record pruned."""
        text = _marker()
        f = _write_tmp(tmp_path, "drift.py", f"a = 1\nb = 2\n# TA: {text}\n")
        rel = _rel(f)
        _seed_index([
            {"path": rel, "line": 1, "category": None, "thought": text, "anchor": None},
            {"kind": "verify", "path": rel, "line": 1, "status": "verified", "basis": "exists"},
        ])
        out = _run_tool("omt_think_reindex", {"path": rel})
        assert out is not None
        assert "repaired 1" in out and f"{rel}: 1→3" in out
        adds = _index_records(rel)
        assert len(adds) == 1 and adds[0]["line"] == 3 and adds[0]["repaired_from"] == 1
        assert _index_records(rel, "verify") == [], "old-slot verify must be pruned"

    def test_reindex_drops_dead_files(self, tmp_path):
        """design §4.12 — record for a nonexistent path (+ its verify) dropped."""
        rel = f"zz_dead_{uuid.uuid4().hex[:8]}/ghost.py"
        _seed_index([
            {"path": rel, "line": 1, "category": None, "thought": _marker(), "anchor": None},
            {"kind": "verify", "path": rel, "line": 1, "status": "stale", "basis": "exists"},
        ])
        out = _run_tool("omt_think_reindex", {"path": rel})
        assert out is not None
        assert "dropped 1" in out and "verify-pruned 1" in out
        assert _index_records(rel, None) == []

    def test_reindex_drops_vanished(self, tmp_path):
        """design §4.13 — thought text no longer in the file → record dropped."""
        f = _write_tmp(tmp_path, "vanish.py", "a = 1\nb = 2\n")
        rel = _rel(f)
        _seed_index([{"path": rel, "line": 1, "category": None,
                      "thought": _marker(), "anchor": None}])
        out = _run_tool("omt_think_reindex", {"path": rel})
        assert out is not None
        assert "dropped 1" in out
        assert _index_records(rel, None) == []

    def test_reindex_path_filter(self, tmp_path):
        """design §4.14 — only the given path's records are processed."""
        text_a, text_b = _marker(), _marker()
        fa = _write_tmp(tmp_path, "fa.py", f"a = 1\n# TA: {text_a}\n")
        fb = _write_tmp(tmp_path, "fb.py", f"b = 1\n# TA: {text_b}\n")
        rel_a, rel_b = _rel(fa), _rel(fb)
        _seed_index([
            {"path": rel_a, "line": 1, "category": None, "thought": text_a, "anchor": None},
            {"path": rel_b, "line": 1, "category": None, "thought": text_b, "anchor": None},
        ])
        out = _run_tool("omt_think_reindex", {"path": rel_a})
        assert out is not None and "repaired 1" in out
        b_recs = _index_records(rel_b)
        assert len(b_recs) == 1 and b_recs[0]["line"] == 1, "unfiltered path must stay untouched"

    def test_reindex_ambiguous_drops(self, tmp_path):
        """design §4.15 — thought text present at >1 line → drop (never silently
        retarget, B1 ambiguity philosophy)."""
        text = _marker()
        f = _write_tmp(tmp_path, "amb.py",
                       f"a = 1\n# TA: {text}\nb = 2\n# TA: {text}\n")
        rel = _rel(f)
        _seed_index([{"path": rel, "line": 1, "category": None, "thought": text, "anchor": None}])
        out = _run_tool("omt_think_reindex", {"path": rel})
        assert out is not None
        assert "dropped 1" in out
        assert _index_records(rel, None) == []


# ---------------------------------------------------------------------------
# E2 — theory-doc guard (F10–F13)
# ---------------------------------------------------------------------------
class TestE2TheoryDoc:
    def test_doc_python_blocks_parse_and_fixed(self):
        """design §4.16 — every ```python fence ast.parses; fix markers present,
        defect markers absent."""
        doc = THEORY_DOC.read_text(encoding="utf-8")
        blocks = re.findall(r"```python\n(.*?)```", doc, re.DOTALL)
        assert blocks, "no python fences found — doc structure changed?"
        for i, block in enumerate(blocks):
            ast.parse(block, filename=f"think_anywhere_langchain.md python-block #{i + 1}")
        # F10: closed paren in the core formula
        assert "P(c | x, s)" in doc
        # F11: unbiased pass@k estimator; wrong metric gone
        assert "math.comb" in doc
        assert "passed / k" not in doc
        # F13: sandbox warning for executing model-generated code; dead stub gone
        assert "sandbox" in doc.lower()
        assert "stream_think_anywhere" not in doc
