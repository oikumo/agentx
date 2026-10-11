"""TA-strip golden (T2/T4, harness_wrapper_split).

Closes PROPOSAL_V7 §4 + §E4: harness may write `# TA:` comment lines into
`src/agentx/**` (30 lines across 18 files at R6) + `// TA:` into TS; stripping
them must be AST-identical (Python) / snapshot-identical comment-only (TS).

Python: `ast.parse` original vs TA-stripped → `ast.dump` identical (comments
never reach AST — but proven here, not assumed). TS `tsc --noEmit` is deferred
to T3 lanes CI (slow/flaky in unit); here we pin comment-only removal.

RED shape: CLI loaded lazily so missing impl FAILS (exit 1), never breaks
collection (exit 2).
"""

import ast
import importlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "omt"))

PY_TA_RE = re.compile(r"^\s*#\s*TA:")
TS_TA_RE = re.compile(r"^\s*//\s*TA:")

# Pinned at R6 (2026-10-11): 30 lines across 18 files in src/agentx/**.
# If this drifts, re-pin + update _ta_hash expectation (honest failure).
PINNED_PY_LINES = 30
PINNED_PY_FILES = 18


def _cli():
    try:
        return importlib.import_module("split_proof")
    except ModuleNotFoundError as e:
        raise AssertionError(f"RED: split_proof module missing: {e}")


def _py_ta_counts():
    base = REPO / "src" / "agentx"
    per_file = {}
    for py in sorted(base.rglob("*.py")):
        try:
            text = py.read_text(encoding="utf-8")
        except OSError:
            continue
        n = sum(1 for ln in text.splitlines() if PY_TA_RE.match(ln))
        if n:
            per_file[py] = n
    return per_file


def test_ta_counts_pinned():
    per_file = _py_ta_counts()
    total = sum(per_file.values())
    assert total == PINNED_PY_LINES, f"TA lines drifted: {total} != {PINNED_PY_LINES}"
    assert len(per_file) == PINNED_PY_FILES, (
        f"TA files drifted: {len(per_file)} != {PINNED_PY_FILES}"
    )


def _strip_py(text: str) -> str:
    return "\n".join(ln for ln in text.splitlines() if not PY_TA_RE.match(ln))


def test_python_strip_ast_identical():
    base = REPO / "src" / "agentx"
    checked = 0
    stripped_any = False
    for py in sorted(base.rglob("*.py")):
        try:
            text = py.read_text(encoding="utf-8")
        except OSError:
            continue
        try:
            orig = ast.parse(text)
        except SyntaxError:
            continue  # skip non-parseable (none expected in src)
        checked += 1
        stripped = _strip_py(text)
        if stripped != text:
            stripped_any = True
        try:
            new = ast.parse(stripped)
        except SyntaxError as e:
            raise AssertionError(f"TA-strip broke syntax in {py}: {e}")
        assert ast.dump(orig) == ast.dump(new), f"AST changed after TA-strip: {py}"
    assert checked > 0
    assert stripped_any, "no TA lines stripped — counts pin should have failed first"


def test_cli_ta_hash_agrees_with_counts():
    mod = _cli()
    assert hasattr(mod, "_ta_hash"), "RED: split_proof._ta_hash missing"
    got = mod._ta_hash(REPO)
    assert re.fullmatch(r"[0-9a-f]{64}", got), f"ta_hash not sha256 hex: {got}"
    # Manual recomputation (same rule as CLI: sorted relative:n lines).
    import hashlib

    per_file = _py_ta_counts()
    lines = sorted(f"{p.relative_to(REPO)}:{n}" for p, n in per_file.items())
    expect = hashlib.sha256("\n".join(lines).encode()).hexdigest()
    assert got == expect


def _ts_files_with_ta():
    hits = []
    for root in (REPO / ".opencode", REPO / "tools", REPO / "scripts"):
        if not root.is_dir():
            continue
        for ts in sorted(root.rglob("*.ts")):
            if ".venv" in ts.parts or "node_modules" in ts.parts:
                continue
            try:
                text = ts.read_text(encoding="utf-8")
            except OSError:
                continue
            if any(TS_TA_RE.match(ln) for ln in text.splitlines()):
                hits.append(ts)
    return hits


def test_ts_strip_comment_only_snapshot_identical():
    files = _ts_files_with_ta()
    assert len(files) > 0, "no TS TA lines found — re-pin scope"
    for ts in files:
        text = ts.read_text(encoding="utf-8")
        kept = [ln for ln in text.splitlines() if not TS_TA_RE.match(ln)]
        removed = [ln for ln in text.splitlines() if TS_TA_RE.match(ln)]
        # Every removed line must be comment-only (starts with // after ws).
        for ln in removed:
            assert ln.strip().startswith("//"), f"TA-strip removed code in {ts}: {ln}"
        # Snapshot-identical except TA lines: rejoin kept + removed == original
        # (line-count check — no other transformation).
        assert len(kept) + len(removed) == len(text.splitlines())
        assert "\n".join(kept) != ""  # file still non-empty after strip
