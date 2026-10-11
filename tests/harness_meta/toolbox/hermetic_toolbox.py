"""Hermetic toolbox helper — private per-module TOOLBOX_ROOT (xdist-safe).

Tier-2 suite-speed isolation: the toolbox CLI used to mutate REAL repo state
(``toolbox/index.sqlite3``, ``index.json``, generated ``*.md`` docs, promoted
tool dirs, ``.sandbox`` drafts, even ``tests/harness_meta/toolbox/test_*.py``
scaffolds). That blocked pytest-xdist parallelization (workers racing on the
same files) and polluted ``git status`` after every run.

``hermetic_cli`` is a module-scoped fixture building a private root per test
module (import it explicitly: ``from hermetic_toolbox import hermetic_cli``):
* ``toolbox/`` entries the CLI mutates (DB, index.json, generated docs) are
  COPIED — each module gets a private snapshot of real Seeds state.
* everything else (tool impl dirs, schema.sql) is SYMLINKED — tool ``main.py``
  files resolving ``repo_root()`` from ``__file__`` keep hitting the REAL repo,
  so ``harness.budget_check`` (shells to real ``harnessc check``) and the
  ledger slice behave exactly as in production (read-only paths).
* ``tests/harness_meta/toolbox/`` skeleton + ``TOOLBOX_ROOT`` env + fast subprocess
  env (no plugin autoload/bytecode/usersite) included.

NOTE: this is deliberately NOT named ``conftest.py`` — a second conftest
under ``tests/`` shadows the top-level ``conftest`` module that
``tests/harness_meta/session_inspect/test_*.py`` imports helpers from
(``from conftest import msg_row``), breaking those tests under xdist worker
import ordering. Explicit import keeps both working.

Same assertions, same seeds, zero repo writes. No coverage loss.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
TOOLBOX_CLI = [sys.executable, str(REPO_ROOT / "scripts" / "toolbox" / "toolbox.py")]

# Files the CLI writes -> private per-module copies. All other entries
# (tool impl dirs, schema.sql) are symlinked to the real tree.
_PRIVATE_FILES = {
    "index.sqlite3",
    "index.json",
    "categories.md",
    "tools.md",
    "STARTUP_SNIPPET.txt",
    "ONBOARDING.md",
}


def build_hermetic_root(base: Path) -> Path:
    """Create an isolated TOOLBOX_ROOT under ``base`` (module tmp dir)."""
    root = base / "toolbox_hermetic"
    tb = root / "toolbox"
    tb.mkdir(parents=True)
    real = REPO_ROOT / "toolbox"
    for entry in real.iterdir():
        dest = tb / entry.name
        if entry.name in _PRIVATE_FILES and entry.is_file():
            shutil.copy2(entry, dest)
        elif entry.is_dir():
            dest.symlink_to(entry)
        elif entry.is_file():
            dest.symlink_to(entry)
    (root / "tests" / "harness_meta" / "toolbox").mkdir(parents=True)
    return root


@pytest.fixture(scope="module")
def hermetic_cli(tmp_path_factory):
    """Module-scoped hermetic CLI runner (one private root per test module).

    Yields ``run_cli(*args, timeout=120, env_extra=None)`` with ``.root``
    pointing at the private root. Module scope = one 236K copy per file,
    shared safely by that file's sequential tests (same xdist worker via
    ``--dist loadfile``).
    """
    root = build_hermetic_root(tmp_path_factory.mktemp("toolbox"))
    env = dict(os.environ)
    env["TOOLBOX_ROOT"] = str(root)
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    env.setdefault("PYTHONNOUSERSITE", "1")

    def run_cli(*args, timeout=120, env_extra=None):
        e = dict(env)
        if env_extra:
            e.update(env_extra)
        return subprocess.run(
            [*TOOLBOX_CLI, *args],
            capture_output=True, text=True, timeout=timeout, env=e,
        )

    run_cli.root = root  # type: ignore[attr-defined]
    return run_cli
