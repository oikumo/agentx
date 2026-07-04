"""MVC++ compliance tests for Fast Agent (feature_011).

Verifies:
  - mvc_check.py reports 0 errors on touched files
  - View files import no Model modules
  - FastAgentTUIView is a virtual subclass of IAgentViewPartner
  - MainTUIScreen has the new f binding + Advanced Agent relabel
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SRC = _REPO_ROOT / "src" / "agentx"


class TestMvcFastAgent:
    def test_touched_files_zero_errors(self):
        """mvc_check.py must report 0 errors on all feature_011 touched files."""
        touched = [
            _SRC / "agent" / "view" / "tui" / "fast_agent_screen.py",
            _SRC / "agent" / "view" / "tui" / "fast_agent_modals.py",
            _SRC / "agent" / "view" / "tui" / "fast_agent_view.py",
            _SRC / "agent" / "controller" / "agent_controller.py",
            _SRC / "agent" / "adapter.py",
            _SRC / "ui" / "screens" / "main" / "main_controller.py",
            _SRC / "ui" / "tui" / "screens" / "main_screen.py",
        ]
        result = subprocess.run(
            ["uv", "run", "scripts/omt/mvc_check.py", "--json"] + [str(p) for p in touched],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
        )
        assert result.returncode == 0, f"mvc_check failed: {result.stderr}"
        data = json.loads(result.stdout)
        errors = [f for f in data["findings"] if f["severity"] == "error"]
        assert len(errors) == 0, (
            f"MVC++ errors on touched files: {json.dumps(errors, indent=2)}"
        )

    def test_view_files_import_no_model(self):
        """Fast Agent View files must not import from agentx.agent.model or types."""
        view_files = [
            _SRC / "agent" / "view" / "tui" / "fast_agent_screen.py",
            _SRC / "agent" / "view" / "tui" / "fast_agent_modals.py",
            _SRC / "agent" / "view" / "tui" / "fast_agent_view.py",
        ]
        for vf in view_files:
            source = vf.read_text()
            assert "from agentx.agent.model" not in source, (
                f"View file {vf.name} imports Model layer — MVC++ violation"
            )
            assert "from agentx.agent.types" not in source, (
                f"View file {vf.name} imports agentx.agent.types — MVC++ violation"
            )

    def test_fast_agent_view_is_partner(self):
        """FastAgentTUIView must be registered as IAgentViewPartner virtual subclass."""
        from agentx.agent.interfaces import IAgentViewPartner
        from agentx.agent.view.tui.fast_agent_view import FastAgentTUIView

        assert issubclass(FastAgentTUIView, IAgentViewPartner)
        assert isinstance(FastAgentTUIView(), IAgentViewPartner)

    def test_main_screen_has_fast_agent_binding(self):
        """MainTUIScreen must have the 'f' → open_fast_agent binding."""
        from agentx.ui.tui.screens.main_screen import MainTUIScreen

        actions = [b.action for b in MainTUIScreen.BINDINGS]
        assert "open_fast_agent" in actions

    def test_main_screen_has_advanced_agent_label(self):
        """MainTUIScreen's 'a' binding must be labeled 'Advanced Agent'."""
        from agentx.ui.tui.screens.main_screen import MainTUIScreen

        for b in MainTUIScreen.BINDINGS:
            if b.action == "open_agent":
                assert "Advanced" in b.description, (
                    f"Expected 'Advanced Agent' label, got '{b.description}'"
                )
                return
        raise AssertionError("open_agent binding not found")

    def test_main_screen_has_fast_agent_button(self):
        """MenuGrid must contain a btn-fast-agent button."""
        from agentx.ui.tui.screens.main_screen import MenuGrid

        source = Path(
            _SRC / "ui" / "tui" / "screens" / "main_screen.py"
        ).read_text()
        assert 'id="btn-fast-agent"' in source, "Missing btn-fast-agent button"

    def test_grid_is_3x2(self):
        """MenuGrid CSS must use grid-size: 3 2 (to fit 5 buttons)."""
        source = Path(
            _SRC / "ui" / "tui" / "screens" / "main_screen.py"
        ).read_text()
        assert "grid-size: 3 2" in source, "MenuGrid should use grid-size: 3 2"

    def test_controller_has_get_cycle_summary(self):
        """AgentController must have the get_cycle_summary method."""
        from agentx.agent.controller.agent_controller import AgentController

        assert hasattr(AgentController, "get_cycle_summary")

    def test_adapter_has_create_fast(self):
        """AgentAdapter must have the create_fast method."""
        from agentx.agent.adapter import AgentAdapter

        assert hasattr(AgentAdapter, "create_fast")

    def test_main_controller_has_show_fast_agent(self):
        """MainController must have show_fast_agent + get_fast_agent_controller."""
        from agentx.ui.screens.main.main_controller import MainController

        assert hasattr(MainController, "show_fast_agent")
        assert hasattr(MainController, "get_fast_agent_controller")
