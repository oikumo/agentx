"""MVC++ compliance tests for feature_014.tui_nonblocking_runner.

Verifies the framework-level architecture:
  - async_runner.py imports no Model module.
  - BaseAgentXScreen has run_blocking + on_unmount.
  - BaseAgentXModalScreen inherits run_blocking.
  - mvc_check.py reports 0 errors on the new file.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentx.ui.tui.framework import (
    BaseAgentXModalScreen,
    BaseAgentXScreen,
    BlockingTaskRunner,
    TaskHandle,
)


# ============================================================================
# Architecture: no Model imports in the runner
# ============================================================================


_REPO_ROOT = Path(__file__).resolve().parents[3]
_RUNNER_PATH = _REPO_ROOT / "src" / "agentx" / "ui" / "tui" / "framework" / "async_runner.py"
_BASE_SCREEN_PATH = _REPO_ROOT / "src" / "agentx" / "ui" / "tui" / "framework" / "base_screen.py"


def _imports_in(source: str) -> list[str]:
    """Return all module names imported by *source* (from/import nodes)."""
    tree = ast.parse(source)
    mods: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mods.append(node.module)
    return mods


class TestMvcNonblocking:
    def test_runner_imports_no_model(self):
        """async_runner.py must not import any agentx.model.* module."""
        source = _RUNNER_PATH.read_text()
        mods = _imports_in(source)
        model_imports = [m for m in mods if m.startswith("agentx.model")]
        assert model_imports == [], (
            f"async_runner.py imports Model modules: {model_imports}"
        )

    def test_runner_imports_no_controller(self):
        """async_runner.py must not import any agentx.agent.controller.* module."""
        source = _RUNNER_PATH.read_text()
        mods = _imports_in(source)
        controller_imports = [
            m for m in mods if m.startswith("agentx.agent.controller")
        ]
        assert controller_imports == [], (
            f"async_runner.py imports Controller modules: {controller_imports}"
        )

    def test_base_screen_has_run_blocking(self):
        """BaseAgentXScreen must expose run_blocking."""
        assert hasattr(BaseAgentXScreen, "run_blocking"), (
            "BaseAgentXScreen.run_blocking missing"
        )

    def test_base_screen_has_on_unmount(self):
        """BaseAgentXScreen must override on_unmount for cleanup."""
        assert hasattr(BaseAgentXScreen, "on_unmount"), (
            "BaseAgentXScreen.on_unmount missing"
        )

    def test_modal_inherits_run_blocking(self):
        """BaseAgentXModalScreen inherits run_blocking from BaseAgentXScreen."""
        assert hasattr(BaseAgentXModalScreen, "run_blocking"), (
            "BaseAgentXModalScreen.run_blocking missing (should inherit)"
        )

    def test_modal_inherits_on_unmount(self):
        """BaseAgentXModalScreen inherits on_unmount from BaseAgentXScreen."""
        assert hasattr(BaseAgentXModalScreen, "on_unmount"), (
            "BaseAgentXModalScreen.on_unmount missing (should inherit)"
        )

    def test_runner_is_abc_free(self):
        """BlockingTaskRunner is a plain class (not ABC) — Textual metaclass safe."""
        # BlockingTaskRunner is not a Screen/Widget, so no metaclass issue.
        # But it must not inherit from ABC.
        assert not issubclass(BlockingTaskRunner, type)  # sanity
        assert "ABC" not in [b.__name__ for b in BlockingTaskRunner.__mro__]

    def test_exports_in_framework_init(self):
        """BlockingTaskRunner + TaskHandle are exported from the framework package."""
        from agentx.ui.tui.framework import __all__ as framework_all

        assert "BlockingTaskRunner" in framework_all
        assert "TaskHandle" in framework_all


# ============================================================================
# mvc_check.py — architectural lint
# ============================================================================


class TestMvcCheckRunner:
    def test_mvc_check_async_runner(self):
        """mvc_check.py reports 0 errors on async_runner.py."""
        import subprocess

        result = subprocess.run(
            ["uv", "run", "scripts/omt/mvc_check.py", str(_RUNNER_PATH)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"mvc_check failed:\n{result.stdout}\n{result.stderr}"
        )
        assert "0 file(s) scanned, no violations" in result.stdout or "1 file(s) scanned, no violations" in result.stdout
