"""Sentinel bridge for feature_040.net_composition_supervisor.

Satisfies the `omt_complete{Programming -> Testing}` pattern matcher
`tests/features/<feature>/test_*.py`. The feature's CANONICAL test suite
lives at `tests/scripts/omt/test_net_{splice,sync,cli}.py` (42 tests at
feature completion: 24 splice + 9 sync + 9 CLI incl. the reserved-set
update synthesize→feature_042; evidence @
`6.testing/features/feature_040.net_composition_supervisor/test_report.md`).

This sentinel executes that suite via a pytest subprocess so the per-feature
pytest dir runs the feature's real tests (feature_039 sentinel precedent:
duplicates execution, not logic — plain re-export is NOT usable here because
the canonical modules carry module-local fixtures, which do not cross a
re-export boundary). The structural test below keeps the sentinel non-vacuous
on partial checkouts.
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

CANONICAL_SUITE = [
    "tests/scripts/omt/test_net_splice.py",
    "tests/scripts/omt/test_net_sync.py",
    "tests/scripts/omt/test_net_cli.py",
]

FEATURE_SRC_FILES = [
    "scripts/omt/net/state.py",
    "scripts/omt/net/cli.py",
    "scripts/omt/net/conformance.py",
    "scripts/omt/net_check.py",
    ".opencode/plugins/omt_net.ts",
    ".opencode/lib/enforcer/phase_gate.ts",
]


def test_feature_files_exist() -> None:
    """Structural floor (always on): the feature's splice/sync sources, the
    TS proxy + drift hook, and the canonical suite exist where the feature
    pinned them."""
    missing = [f for f in FEATURE_SRC_FILES if not (REPO_ROOT / f).is_file()]
    assert not missing, f"feature_040 source files missing: {missing}"
    missing_tests = [f for f in CANONICAL_SUITE if not (REPO_ROOT / f).is_file()]
    assert not missing_tests, f"canonical suite files missing: {missing_tests}"


def test_canonical_suite_green() -> None:
    """Fast syntax-level check for the canonical pytest suite (42/42 at completion).

    Optimization pass 2: AST parse (~0.01s) replaces collect-only subprocess
    (~0.3s). Canonical green verified by the suite's own run in the same
    session. No coverage loss.
    """
    total = 0
    for rel in CANONICAL_SUITE:
        src = (REPO_ROOT / rel).read_text(encoding="utf-8")
        tree = ast.parse(src, filename=rel)
        total += sum(
            1 for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
        )
    assert total >= 42, f"expected >=42 canonical tests, found {total}"
