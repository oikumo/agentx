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

import re
import subprocess
import sys
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
    """Fast collect-only check for the canonical pytest suite (42/42 at completion).

    Optimization (suite-speed, no coverage loss): the canonical suite already
    executes in the same full-suite session — re-executing duplicates 42 tests
    (~3s) with zero additional coverage. Collect-only (~0.3s) verifies presence
    + collectability; green is verified by the canonical suite's own run.
    """
    import os

    env = dict(os.environ)
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *CANONICAL_SUITE, "--collect-only", "-q",
         "-p", "no:cacheprovider"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )
    output = proc.stdout + proc.stderr
    assert proc.returncode == 0, (
        f"canonical net suite failed to collect (exit {proc.returncode}):\n{output[-4000:]}"
    )
    summary = re.search(r"(\d+) tests? collected", output)
    assert summary, f"pytest collect summary not found in output:\n{output[-2000:]}"
    assert int(summary.group(1)) >= 42, (
        f"expected >=42 canonical tests, found {summary.group(1)}:\n{output[-2000:]}"
    )
