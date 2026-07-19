"""
Test suite for feature_022: Think Anywhere V2 — Tier A correctness hotfixes.

Covers design_001_tier_a_hotfixes.md §5 tests 1–14 (item 15, the feature_021
regression suite, is run separately). Each test cites its design item.

  A1  anchored THOUGHT_PATTERN (+ A1b .venv/__pycache__ excludes)
  A2  explicit extension map, unknown → deny
  A3  string-context insertion guard (.py triple-quote, .md code fence)
  A4  filter escaping, category case, dedup, CRLF preservation

Strategy mirrors feature_021: invoke the REAL plugin tools via
_think_runner.mjs (node --experimental-strip-types) against temp files, and
the REAL fileThoughtsIn gate helper via _think_gate_runner.mjs file-thoughts
mode — no reimplementation of plugin logic in Python.
"""

import json
import re
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
TEST_DIR = Path(__file__).parent
THINK_RUNNER = TEST_DIR / "_think_runner.mjs"
GATE_RUNNER = TEST_DIR / "_think_gate_runner.mjs"
PLUGIN = REPO_ROOT / ".opencode" / "plugins" / "omt_think.ts"
ENFORCER = REPO_ROOT / ".opencode" / "plugins" / "omt_enforcer.ts"

NODE = shutil.which("node")
needs_node = pytest.mark.skipif(not NODE, reason="node not available")

# Byte-exact THOUGHT_PATTERN string literal both plugins must carry (A1 §1,
# extended with the sql `--` opener so the gate is never blind to what
# omt_think emits for .sql — see design §5 test 3 round-trip).
EXPECTED_PATTERN_LITERAL = r"^\\s*(#|//|/\\*|<!--|--)\\s*TA:"


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


def _file_thoughts(abs_path: Path, cwd: Path = REPO_ROOT):
    """Invoke the REAL fileThoughtsIn (enforcer think-gate helper); return hits or None."""
    if not NODE:
        return None
    proc = subprocess.run(
        [NODE, "--experimental-strip-types", str(GATE_RUNNER), "file-thoughts", str(abs_path)],
        capture_output=True, text=True, cwd=cwd, timeout=30,
    )
    if proc.returncode != 0:
        return None
    return json.loads(proc.stdout)


def _marker() -> str:
    return "TAUTOMARK_" + uuid.uuid4().hex[:8]


def _write_tmp(tmp_path: Path, name: str, content: str = "") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# A1 — anchored thought pattern
# ---------------------------------------------------------------------------
@needs_node
class TestA1AnchoredPattern:
    def test_prose_lines_rejected(self, tmp_path):
        """design §5.1 — F3 false-positive class: prose, META:/DATA: substrings
        and string literals mentioning TA: are NOT thoughts (list AND gate)."""
        f = _write_tmp(
            tmp_path, "prose.py",
            "# a comment mentioning the TA: marker in prose\n"
            "META: some harness metadata line\n"
            "DATA: some other line\n"
            'x = "a string with TA: inside"\n',
        )
        out = _run_tool("omt_think_list", {"path": str(f)}, cwd=tmp_path)
        assert out is not None
        assert out.startswith("0 thoughts"), f"prose must not be listed: {out!r}"
        hits = _file_thoughts(f)
        assert hits == [], f"gate must be blind to prose TA: mentions: {hits}"

    def test_real_tag_forms_detected(self, tmp_path):
        """design §5.2 — every comment form buildThoughtLine emits is detected
        by both list and the gate (incl. the sql `--` form)."""
        forms = {
            "t_hash.py": "# TA: hash form",
            "t_slash.ts": "// TA: slash form",
            "t_css.css": "/* TA: block form */",
            "t_md.md": "<!-- TA: html form -->",
            "t_sql.sql": "-- TA: sql form",
        }
        for name, line in forms.items():
            f = _write_tmp(tmp_path, name, line + "\n")
            hits = _file_thoughts(f)
            assert hits is not None and len(hits) == 1, (
                f"gate blind to {line.split('TA:')[0]!r} form in {name}: {hits}")
        out = _run_tool("omt_think_list", {"path": str(tmp_path)}, cwd=tmp_path)
        assert out is not None
        for form in ["hash form", "slash form", "block form", "html form", "sql form"]:
            assert form in out, f"list missed {form}: {out!r}"

    def test_round_trip_every_family(self, tmp_path):
        """design §5.3 — for every commentSyntaxFor family: omt_think insert →
        fileThoughtsIn finds it (the gate can never be blind to think's line)."""
        for name in ["rt.py", "rt.ts", "rt.md", "rt.css", "rt.sql"]:
            f = _write_tmp(tmp_path, name, "base\n")
            m = _marker()
            out = _run_tool("omt_think", {"path": str(f), "thought": f"roundtrip {m}"}, cwd=tmp_path)
            assert out is not None and "✅" in out, f"{name}: insert failed: {out}"
            hits = _file_thoughts(f)
            assert hits is not None and len(hits) == 1, (
                f"{name}: gate blind to think's own line: {f.read_text()!r}")
            assert m in hits[0]["content"]

    def test_venv_and_pycache_excluded(self, tmp_path):
        """design §5.4 (A1b) — hits under .venv/ and __pycache__/ are excluded."""
        (tmp_path / "pkg").mkdir()
        _write_tmp(tmp_path / "pkg", "mod.py", f"# TA: real thought {_marker()}\n")
        (tmp_path / ".venv").mkdir()
        _write_tmp(tmp_path / ".venv", "noise.py", "# TA: venv noise\n")
        (tmp_path / "__pycache__").mkdir()
        _write_tmp(tmp_path / "__pycache__", "c.py", "# TA: cache noise\n")
        out = _run_tool("omt_think_list", {"path": str(tmp_path)}, cwd=tmp_path)
        assert out is not None
        assert "real thought" in out
        assert "venv noise" not in out, f".venv not excluded: {out!r}"
        assert "cache noise" not in out, f"__pycache__ not excluded: {out!r}"

    def test_remove_requires_anchored_line(self, tmp_path):
        """design §5.5 — remove refuses prose-mention lines, removes real ones."""
        f = _write_tmp(
            tmp_path, "rm.py",
            "# a comment mentioning the TA: marker\n"
            "# TA: real thought\n",
        )
        bad = _run_tool("omt_think_remove", {"path": str(f), "line": 1}, cwd=tmp_path)
        assert bad is not None and "refused" in bad.lower(), (
            f"prose line must be refused: {bad!r}")
        assert "TA: marker" in f.read_text(), "prose line must be untouched"
        ok = _run_tool("omt_think_remove", {"path": str(f), "line": 2}, cwd=tmp_path)
        assert ok is not None and "removed" in ok.lower(), f"real line: {ok!r}"
        assert "real thought" not in f.read_text()

    def test_thought_pattern_identical_in_both_plugins(self):
        """design §5.6 — the two THOUGHT_PATTERN copies (standalone plugins,
        no cross-imports) must be byte-identical so list/gate never drift."""
        rx = re.compile(r'THOUGHT_PATTERN\s*=\s*"([^"]+)"')
        think_src = PLUGIN.read_text()
        enf_src = ENFORCER.read_text()
        mt, me = rx.search(think_src), rx.search(enf_src)
        assert mt, "omt_think.ts must define a THOUGHT_PATTERN string const"
        assert me, "omt_enforcer.ts must define a THOUGHT_PATTERN string const"
        assert mt.group(1) == me.group(1), (
            f"pattern copies drifted:\n  think: {mt.group(1)}\n  enforcer: {me.group(1)}")
        assert mt.group(1) == EXPECTED_PATTERN_LITERAL, (
            f"unexpected pattern: {mt.group(1)!r} (must cover every opener "
            f"buildThoughtLine emits, incl. sql `--`)")


# ---------------------------------------------------------------------------
# A2 — explicit extension map (unknown → deny)
# ---------------------------------------------------------------------------
@needs_node
class TestA2ExtensionMap:
    def test_new_language_mappings(self, tmp_path):
        """design §5.7 — .go/.rs/.java/.c → //, .sql → --, .html → <!-- -->."""
        cases = {
            "a.go": "// TA:",
            "a.rs": "// TA:",
            "a.java": "// TA:",
            "a.c": "// TA:",
            "a.sql": "-- TA:",
            "a.html": "<!-- TA:",
        }
        for name, prefix in cases.items():
            f = _write_tmp(tmp_path, name, "base\n")
            out = _run_tool("omt_think", {"path": str(f), "thought": f"m {_marker()}"}, cwd=tmp_path)
            assert out is not None and "✅" in out, f"{name}: insert failed: {out}"
            tag_line = [l for l in f.read_text().splitlines() if "TA:" in l][0]
            assert tag_line.startswith(prefix), (
                f"{name}: expected {prefix!r} opener, got {tag_line!r}")
        html = (tmp_path / "a.html").read_text()
        assert "-->" in html, ".html must close with -->"

    def test_unknown_extension_denied(self, tmp_path):
        """design §5.8 — unknown ext and extensionless: refuse; bytes unchanged
        (F2: the unsafe `#` default is gone)."""
        f = _write_tmp(tmp_path, "data.xyz", "original\n")
        out = _run_tool("omt_think", {"path": str(f), "thought": "nope"}, cwd=tmp_path)
        assert out is not None and "refused" in out.lower(), f".xyz: {out!r}"
        assert "unsupported file type" in out, f".xyz message: {out!r}"
        assert "commentSyntaxFor" in out, f".xyz should point at the mapping: {out!r}"
        assert f.read_text() == "original\n", ".xyz file must be unchanged"
        g = _write_tmp(tmp_path, "Makefile", "all:\n\techo hi\n")
        out2 = _run_tool("omt_think", {"path": str(g), "thought": "nope"}, cwd=tmp_path)
        assert out2 is not None and "refused" in out2.lower(), f"extensionless: {out2!r}"
        assert g.read_text() == "all:\n\techo hi\n", "extensionless file must be unchanged"


# ---------------------------------------------------------------------------
# A3 — string-context insertion guard
# ---------------------------------------------------------------------------
@needs_node
class TestA3StringGuard:
    PY_SRC = (
        "class Screen:\n"
        '    CSS = """\n'
        "    .foo { color: red; }\n"
        '    """\n'
        "    x = 1\n"
    )

    def test_py_insert_inside_triple_quoted_string_refused(self, tmp_path):
        """design §5.9 — F1 repro (main_screen.py:78-79 Textual CSS incident):
        inserting into a triple-quoted string is refused, file unchanged."""
        f = _write_tmp(tmp_path, "s.py", self.PY_SRC)
        before = f.read_text()
        out = _run_tool("omt_think", {"path": str(f), "thought": "inside css", "line": 3}, cwd=tmp_path)
        assert out is not None and "refused" in out.lower(), f"must refuse: {out!r}"
        assert "string" in out.lower() or "fence" in out.lower(), f"message: {out!r}"
        assert f.read_text() == before, "file must be unchanged after refusal"

    def test_py_insert_after_closed_docstring_allowed(self, tmp_path):
        """design §5.9 (pair) — balanced triple-quotes: insertion AFTER the
        closing delimiter is outside the string and allowed."""
        f = _write_tmp(tmp_path, "s2.py", self.PY_SRC)
        out = _run_tool("omt_think", {"path": str(f), "thought": "after css", "line": 4}, cwd=tmp_path)
        assert out is not None and "✅" in out, f"must allow: {out!r}"
        lines = f.read_text().split("\n")
        assert lines[4] == "# TA: after css", f"wrong insertion site: {lines!r}"

    def test_md_insert_inside_code_fence_refused(self, tmp_path):
        """design §5.10 — ``` fences in .md: inside refused, outside allowed."""
        src = "# Title\n\n```python\ncode here\n```\n\nafter fence\n"
        f = _write_tmp(tmp_path, "d.md", src)
        before = f.read_text()
        out = _run_tool("omt_think", {"path": str(f), "thought": "inside fence", "line": 4}, cwd=tmp_path)
        assert out is not None and "refused" in out.lower(), f"must refuse: {out!r}"
        assert f.read_text() == before, "file must be unchanged after refusal"
        ok = _run_tool("omt_think", {"path": str(f), "thought": "outside fence", "line": 5}, cwd=tmp_path)
        assert ok is not None and "✅" in ok, f"outside fence must be allowed: {ok!r}"


# ---------------------------------------------------------------------------
# A4 — filters, dedup, EOL
# ---------------------------------------------------------------------------
@needs_node
class TestA4FiltersDedupEol:
    def test_category_lowercased_insert_and_filter(self, tmp_path):
        """design §5.11 — category normalized to lowercase at insert AND at
        filter time (F7 case defect)."""
        m = _marker()
        f = _write_tmp(tmp_path, "c.py", "v = 0\n")
        _run_tool("omt_think", {"path": str(f), "thought": m, "category": "Gotcha"}, cwd=tmp_path)
        assert f"TA: gotcha: {m}" in f.read_text(), (
            f"category must be lowercased at insert: {f.read_text()!r}")
        out = _run_tool("omt_think_list", {"path": str(tmp_path), "category": "GOTCHA"}, cwd=tmp_path)
        assert out is not None and m in out, (
            f"uppercase filter must match lowercase tag: {out!r}")

    def test_query_is_regex_escaped(self, tmp_path):
        """design §5.12 — query 'a.b[' is literal: no grep error, matches only
        the literal text (F7 unescaped-query defect)."""
        m = _marker()
        f = _write_tmp(
            tmp_path, "q.py",
            f"# TA: config a.b[0] entry {m}\n"
            "# TA: config axb[0] decoy\n",
        )
        out = _run_tool("omt_think_list", {"path": str(f), "query": "a.b["}, cwd=tmp_path)
        assert out is not None, "tool call failed (grep error?)"
        assert m in out, f"literal query must match: {out!r}"
        assert "decoy" not in out, f"query metacharacters must be literal: {out!r}"

    def test_duplicate_thought_refused(self, tmp_path):
        """design §5.13 — identical (path, thought) refused with a pointer to
        the existing line; same text with a different category is allowed."""
        f = _write_tmp(tmp_path, "d.py", "x = 1\n")
        first = _run_tool("omt_think", {"path": str(f), "thought": "mutates history"}, cwd=tmp_path)
        assert first is not None and "✅" in first, f"first insert: {first!r}"
        m_first = re.search(r":(\d+)$", first)
        assert m_first, f"no line number in success message: {first!r}"
        first_line = int(m_first.group(1))
        dup = _run_tool("omt_think", {"path": str(f), "thought": "mutates history"}, cwd=tmp_path)
        assert dup is not None and "refused" in dup.lower(), f"dup must refuse: {dup!r}"
        assert "duplicate" in dup.lower(), f"dup message: {dup!r}"
        assert f":{first_line}" in dup, f"dup must point at existing line: {dup!r}"
        ok = _run_tool(
            "omt_think", {"path": str(f), "thought": "mutates history", "category": "gotcha"}, cwd=tmp_path)
        assert ok is not None and "✅" in ok, (
            f"same text, different category must be allowed: {ok!r}")

    def test_crlf_preserved(self, tmp_path):
        """design §5.14 — CRLF file: inserted line ends CRLF; no LF-only lines
        introduced (F9 mixed-endings defect)."""
        p = tmp_path / "win.py"
        p.write_bytes(b"x = 1\r\ny = 2\r\n")
        out = _run_tool("omt_think", {"path": str(p), "thought": "crlf note"}, cwd=tmp_path)
        assert out is not None and "✅" in out, f"insert: {out!r}"
        data = p.read_bytes()
        lines = data.split(b"\n")
        thought_lines = [l for l in lines if b"TA:" in l]
        assert len(thought_lines) == 1, f"expected one thought line: {data!r}"
        assert thought_lines[0].endswith(b"\r"), (
            f"thought line must end CRLF: {thought_lines[0]!r}")
        for l in lines:
            if l == b"":
                continue
            assert l.endswith(b"\r"), f"LF-only line introduced: {l!r}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
