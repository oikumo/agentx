"""
Test suite for feature_022: Think Anywhere V2 — Tier B1 + D1.

Covers design_002_tier_b1_d1.md §3 tests 1–17 (each test cites its item):

  B1  anchor-based omt_think insertion (after: literal substring, symbol:
      definition-regex; ambiguity/zero-match refusal; index anchor field)
  D1  read-time thought injection in the enforcer's tool.execute.after hook
      (once per file per session, capped, no consult record, fail-open)

Strategy mirrors Tier A: invoke the REAL plugin tools via _think_runner.mjs
(node --experimental-strip-types) against temp files — args pass through, so
after/symbol reach the real omt_think. D1 drives the REAL OmtEnforcer's
tool.execute.after via _think_gate_runner.mjs after-hook mode: one plugin
instance per batch (injectedThisSession is process-lifetime state), isolated
tmpdir ledger, no opencode server.
"""

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
GATE_RUNNER = TEST_DIR / "_think_gate_runner.mjs"
THOUGHTS_INDEX = REPO_ROOT / ".meta" / ".omt" / "thoughts.jsonl"

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


def _after_hook_batch(directory: Path, calls: list[dict]):
    """Drive the REAL OmtEnforcer tool.execute.after through a batch of calls on
    ONE plugin instance; return the list of mutated output dicts or None."""
    if not NODE:
        return None
    proc = subprocess.run(
        [NODE, "--experimental-strip-types", str(GATE_RUNNER), "after-hook",
         str(directory), json.dumps(calls)],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=30,
    )
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def _read_call(path: Path, session: str, tool: str = "read") -> dict:
    """One fake after-hook invocation for `tool` on `path` in `session`.

    REAL SDK shape (tool.execute.after — feature_023 T1.2/F14): args on INPUT,
    output={title,output,metadata} exactly. Pinned by
    tests/scripts/omt/test_opencode_sdk_contract.py."""
    return {
        "input": {"tool": tool, "sessionID": session, "callID": "c1",
                  "args": {"filePath": str(path)}},
        "output": {
            "title": tool,
            "output": "ORIG",
            "metadata": {},
        },
    }


def _marker() -> str:
    return "TAUTOMARK_" + uuid.uuid4().hex[:8]


def _write_tmp(tmp_path: Path, name: str, content: str = "") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# B1 — anchor-based insertion (omt_think after:/symbol:)
# ---------------------------------------------------------------------------
@needs_node
class TestB1AnchorInsertion:
    def test_after_unique_match(self, tmp_path):
        """design §3.1 — after: unique match → thought on the line immediately
        after the anchor line; success message names the new line."""
        f = _write_tmp(tmp_path, "anc.py", "alpha = 1\nbeta = 2\ngamma = 3\n")
        out = _run_tool("omt_think", {"path": str(f), "thought": f"m {_marker()}",
                                      "after": "beta = 2"}, cwd=tmp_path)
        assert out is not None and "✅" in out, f"insert failed: {out}"
        m = re.search(r":(\d+)$", out)
        assert m and m.group(1) == "3", f"thought must land at line 3: {out!r}"
        lines = f.read_text().splitlines()
        assert lines[1] == "beta = 2", "anchor line must stay put"
        assert lines[2].startswith("# TA:"), f"line 3 must be the thought: {lines!r}"

    def test_after_no_match_denied(self, tmp_path):
        """design §3.2 — after: 0 matches → 'anchor not found' denial; file
        byte-unchanged."""
        f = _write_tmp(tmp_path, "none.py", "alpha = 1\n")
        before = f.read_bytes()
        out = _run_tool("omt_think", {"path": str(f), "thought": "m",
                                      "after": "no such text anywhere"}, cwd=tmp_path)
        assert out is not None and "refused" in out.lower(), f"must refuse: {out!r}"
        assert "anchor not found" in out, f"message: {out!r}"
        assert f.read_bytes() == before, "file must be unchanged after refusal"

    def test_after_ambiguous_denied(self, tmp_path):
        """design §3.3 — after: 2+ matches → denial naming the count and the
        candidate line numbers; file unchanged."""
        f = _write_tmp(tmp_path, "amb.py", "return x\nfoo()\nreturn y\nbar()\nreturn z\n")
        before = f.read_bytes()
        out = _run_tool("omt_think", {"path": str(f), "thought": "m", "after": "return"}, cwd=tmp_path)
        assert out is not None and "refused" in out.lower(), f"must refuse: {out!r}"
        assert "matches 3 lines" in out, f"count missing: {out!r}"
        assert "1, 3, 5" in out, f"candidate lines missing: {out!r}"
        assert f.read_bytes() == before, "file must be unchanged after refusal"

    def test_conflicting_modes_denied(self, tmp_path):
        """design §3.4 — two or more addressing modes → 'at most one of' denial
        naming the combination; file unchanged."""
        f = _write_tmp(tmp_path, "c.py", "x = 1\n")
        before = f.read_bytes()
        out1 = _run_tool("omt_think", {"path": str(f), "thought": "m",
                                       "line": 1, "after": "x"}, cwd=tmp_path)
        assert out1 is not None and "at most one of" in out1, f"line+after: {out1!r}"
        assert "line+after" in out1, f"combination must be named: {out1!r}"
        out2 = _run_tool("omt_think", {"path": str(f), "thought": "m",
                                       "after": "x", "symbol": "y"}, cwd=tmp_path)
        assert out2 is not None and "at most one of" in out2, f"after+symbol: {out2!r}"
        assert "after+symbol" in out2, f"combination must be named: {out2!r}"
        assert f.read_bytes() == before, "file must be unchanged after refusal"

    def test_symbol_py_def(self, tmp_path):
        """design §3.5 — symbol: py def → inserted after the 'def target(' line."""
        f = _write_tmp(tmp_path, "sym.py", "def target():\n    pass\n\ny = 2\n")
        out = _run_tool("omt_think", {"path": str(f), "thought": f"m {_marker()}",
                                      "symbol": "target"}, cwd=tmp_path)
        assert out is not None and "✅" in out, f"insert failed: {out}"
        lines = f.read_text().splitlines()
        assert lines[0] == "def target():"
        assert lines[1].startswith("# TA:"), f"line 2 must be the thought: {lines!r}"

    @pytest.mark.parametrize("src,name", [
        ("class MyClass:\n    pass\n", "MyClass"),
        ("async def afunc():\n    pass\n", "afunc"),
    ])
    def test_symbol_py_class_and_async_def(self, tmp_path, src, name):
        """design §3.6 — symbol: py class and async def forms both resolve."""
        f = _write_tmp(tmp_path, "sym2.py", src)
        out = _run_tool("omt_think", {"path": str(f), "thought": f"m {_marker()}",
                                      "symbol": name}, cwd=tmp_path)
        assert out is not None and "✅" in out, f"{name}: insert failed: {out}"
        lines = f.read_text().splitlines()
        assert lines[0].strip().startswith(("class", "async def"))
        assert lines[1].startswith("# TA:"), f"{name}: line 2 must be the thought: {lines!r}"

    @pytest.mark.parametrize("src,name,opener", [
        ("export function helperFn() {\n  return 1\n}\n", "helperFn", "export function"),
        ("const otherThing = 1\nconst second = 2\n", "otherThing", "const"),
    ])
    def test_symbol_ts_forms(self, tmp_path, src, name, opener):
        """design §3.7 — symbol: ts export function / const forms resolve."""
        f = _write_tmp(tmp_path, "sym.ts", src)
        out = _run_tool("omt_think", {"path": str(f), "thought": f"m {_marker()}",
                                      "symbol": name}, cwd=tmp_path)
        assert out is not None and "✅" in out, f"{name}: insert failed: {out}"
        lines = f.read_text().splitlines()
        assert lines[0].startswith(opener)
        assert lines[1].startswith("// TA:"), f"{name}: line 2 must be the thought: {lines!r}"

    def test_symbol_unsupported_extension_denied(self, tmp_path):
        """design §3.8 — symbol: on .sql → 'not supported' denial pointing at
        after:; file unchanged."""
        f = _write_tmp(tmp_path, "q.sql", "SELECT 1\n")
        before = f.read_bytes()
        out = _run_tool("omt_think", {"path": str(f), "thought": "m", "symbol": "whatever"}, cwd=tmp_path)
        assert out is not None and "refused" in out.lower(), f"must refuse: {out!r}"
        assert "not supported" in out, f"message: {out!r}"
        assert "after" in out, f"must point at after:: {out!r}"
        assert f.read_bytes() == before, "file must be unchanged after refusal"

    def test_symbol_regex_metachars_literal(self, tmp_path):
        """design §3.9 — symbol name 'foo.bar' is regex-escaped: matches only a
        literal 'foo.bar' definition, never 'fooXbar' (0-match denial)."""
        f1 = _write_tmp(tmp_path, "m1.py", "def fooXbar():\n    pass\n")
        before = f1.read_bytes()
        out1 = _run_tool("omt_think", {"path": str(f1), "thought": "m",
                                       "symbol": "foo.bar"}, cwd=tmp_path)
        assert out1 is not None and "anchor not found" in out1, (
            f"foo.bar must not match fooXbar (metachars literal): {out1!r}")
        assert f1.read_bytes() == before, "decoy file must be unchanged"
        f2 = _write_tmp(tmp_path, "m2.py", "def foo.bar():\n    pass\n")
        out2 = _run_tool("omt_think", {"path": str(f2), "thought": f"m {_marker()}",
                                       "symbol": "foo.bar"}, cwd=tmp_path)
        assert out2 is not None and "✅" in out2, (
            f"literal foo.bar definition must match: {out2!r}")
        lines = f2.read_text().splitlines()
        assert lines[1].startswith("# TA:"), f"line 2 must be the thought: {lines!r}"

    def test_after_anchor_inside_string_refused(self, tmp_path):
        """design §3.10 — after: anchor whose next line lies inside a
        triple-quoted string → the A3 guard composes with anchor mode
        (same refusal as line-mode); file unchanged."""
        src = 'CSS = """\n.foo { color: red; }\n"""\nx = 1\n'
        f = _write_tmp(tmp_path, "s.py", src)
        before = f.read_bytes()
        out = _run_tool("omt_think", {"path": str(f), "thought": "inside css",
                                      "after": ".foo { color: red; }"}, cwd=tmp_path)
        assert out is not None and "refused" in out.lower(), f"must refuse: {out!r}"
        assert "string" in out.lower() or "fence" in out.lower(), f"message: {out!r}"
        assert f.read_bytes() == before, "file must be unchanged after refusal"

    def test_index_anchor_field(self, tmp_path):
        """design §3.11 — thoughts.jsonl: after-mode record carries
        anchor:{kind:'after',value}; line-mode record carries anchor:null
        (records filtered to this test's tmp file)."""
        f = _write_tmp(tmp_path, "idx.py", "alpha = 1\nbeta = 2\n")
        m1, m2 = _marker(), _marker()
        r1 = _run_tool("omt_think", {"path": str(f), "thought": m1, "after": "alpha = 1"}, cwd=tmp_path)
        assert r1 is not None and "✅" in r1, f"after insert: {r1}"
        r2 = _run_tool("omt_think", {"path": str(f), "thought": m2, "line": 1}, cwd=tmp_path)
        assert r2 is not None and "✅" in r2, f"line insert: {r2}"
        # Read from tmp_path's index (F17 cwd isolation)
        index_file = tmp_path / ".meta" / ".omt" / "thoughts.jsonl"
        recs = []
        if index_file.exists():
            for line in index_file.read_text().splitlines():
                s = line.strip()
                if not s:
                    continue
                try:
                    r = json.loads(s)
                except json.JSONDecodeError:
                    continue
                if isinstance(r, dict) and r.get("path") == f.name:
                    recs.append(r)
        by_thought = {r.get("thought"): r for r in recs}
        a = by_thought.get(m1)
        assert a is not None, f"no index record for the after-mode thought: {recs}"
        assert a.get("anchor") == {"kind": "after", "value": "alpha = 1"}, (
            f"after-mode anchor field wrong: {a}")
        b = by_thought.get(m2)
        assert b is not None, f"no index record for the line-mode thought: {recs}"
        assert b.get("anchor") is None, f"line-mode anchor must be null: {b}"

    def test_back_compat_eof_append(self, tmp_path):
        """design §3.12 — no addressing args → EOF append exactly as Tier A
        (regression guard; passes on v1 and must keep passing)."""
        f = _write_tmp(tmp_path, "eof.py", "one = 1\n")
        out = _run_tool("omt_think", {"path": str(f), "thought": f"m {_marker()}"}, cwd=tmp_path)
        assert out is not None and "✅" in out, f"insert failed: {out}"
        lines = f.read_text().splitlines()
        assert lines[0] == "one = 1"
        assert len(lines) == 2 and lines[1].startswith("# TA:"), (
            f"thought must append at EOF: {lines!r}")


# ---------------------------------------------------------------------------
# D1 — read-time thought injection (enforcer tool.execute.after)
# ---------------------------------------------------------------------------
@needs_node
class TestD1ReadTimeInjection:
    def test_first_read_injects_thoughts(self, tmp_path):
        """design §3.13 — first read of a thought-carrying file appends the 💡
        block (thought content + 'think-gate applies'); hook does not throw."""
        m = _marker()
        f = _write_tmp(tmp_path, "carry.py", f"x = 1\n# TA: gotcha: {m}\n")
        results = _after_hook_batch(tmp_path, [_read_call(f, "s1")])
        assert results is not None, "after-hook runner failed (threw?)"
        out = results[0]["output"]
        assert out.startswith("ORIG"), f"original output must be preserved: {out!r}"
        assert "💡 TA: thoughts in" in out, f"injection block missing: {out!r}"
        assert m in out, f"thought content missing: {out!r}"
        assert "think-gate applies" in out, f"gate note missing: {out!r}"

    def test_read_injection_once_per_session(self, tmp_path):
        """design §3.14 — second read same session+file → NOT re-appended;
        a different sessionID → re-injected (one plugin instance, batch of 3)."""
        m = _marker()
        f = _write_tmp(tmp_path, "carry.py", f"x = 1\n# TA: {m}\n")
        calls = [_read_call(f, "s1"), _read_call(f, "s1"), _read_call(f, "s2")]
        results = _after_hook_batch(tmp_path, calls)
        assert results is not None, "after-hook runner failed (threw?)"
        assert m in results[0]["output"], "first read must inject"
        assert m not in results[1]["output"], (
            f"same session must not re-inject: {results[1]['output']!r}")
        assert m in results[2]["output"], "new session must re-inject"

    def test_thought_free_and_edit_untouched(self, tmp_path):
        """design §3.15 — thought-free file → output unchanged (except F14c nav
        reminder on first call per session); tool:'edit' on a thought file →
        output unchanged (D1 does not alter the edit path; no nav reminder on
        subsequent calls in same session)."""
        m = _marker()
        clean = _write_tmp(tmp_path, "clean.py", "y = 2\n")
        carry = _write_tmp(tmp_path, "carry.py", f"x = 1\n# TA: {m}\n")
        calls = [_read_call(clean, "s1"), _read_call(carry, "s1", tool="edit")]
        results = _after_hook_batch(tmp_path, calls)
        assert results is not None, "after-hook runner failed (threw?)"
        # First call in session s1 gets F14c nav reminder but NOT thought injection
        # (clean.py has no thoughts). Nav reminder is prepended to ORIG.
        assert results[0]["output"].startswith("ORIG"), (
            f"output must start with ORIG: {results[0]['output']!r}")
        assert "NAVIGATION TIP" in results[0]["output"], (
            f"first call per session must carry nav reminder: {results[0]['output']!r}")
        # Second call same session s1: no nav reminder, D1 doesn't inject on edit
        assert results[1]["output"] == "ORIG", (
            f"edit path must be untouched (no nav reminder, no thought injection): {results[1]['output']!r}")

    def test_injection_writes_no_consult_record(self, tmp_path):
        """design §3.16 — injection writes NO think_consult record (awareness ≠
        consult; the edit-time think-gate still applies)."""
        m = _marker()
        f = _write_tmp(tmp_path, "carry.py", f"x = 1\n# TA: {m}\n")
        results = _after_hook_batch(tmp_path, [_read_call(f, "s9")])
        assert results is not None and m in results[0]["output"], "injection must fire"
        ledger = tmp_path / ".meta" / ".omt" / "ledger.jsonl"
        if ledger.exists():
            for line in ledger.read_text().splitlines():
                s = line.strip()
                if not s:
                    continue
                try:
                    rec = json.loads(s)
                except json.JSONDecodeError:
                    continue
                assert rec.get("kind") != "think_consult", (
                    f"D1 must not record consults: {rec}")

    def test_injection_capped_at_ten(self, tmp_path):
        """design §3.17 — file with 12 thoughts → block shows 10 lines plus a
        '+2 more' pointer."""
        lines = ["x = 1"] + [f"# TA: note {i:02d} {_marker()}" for i in range(12)]
        f = _write_tmp(tmp_path, "many.py", "\n".join(lines) + "\n")
        results = _after_hook_batch(tmp_path, [_read_call(f, "s1")])
        assert results is not None, "after-hook runner failed (threw?)"
        out = results[0]["output"]
        assert "💡 TA: thoughts in" in out, f"injection block missing: {out!r}"
        shown = [l for l in out.splitlines() if l.strip().startswith("many.py:")]
        assert len(shown) == 10, f"expected 10 shown thoughts, got {len(shown)}: {out!r}"
        assert "+2 more" in out, f"remainder pointer missing: {out!r}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
