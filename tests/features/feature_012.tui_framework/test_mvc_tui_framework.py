"""MVC++ compliance + regression invariants for feature_012.tui_framework.

Verifies:
  - mvc_check.py reports 0 errors on the new framework package.
  - Framework files import no Model layer.
  - The refactored screens/adapters inherit the new base classes.
  - Regression: AgentTUIScreen / AgentDemoScreen are still IAgentViewPartner.
  - Regression: the existing public symbols still exist with the right bases.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SRC = _REPO_ROOT / "src" / "agentx"
_FRAMEWORK = _SRC / "ui" / "tui" / "framework"


class TestMvcTuiFramework:
    def test_framework_zero_errors(self):
        """mvc_check.py must report 0 errors on the framework package."""
        result = subprocess.run(
            ["uv", "run", "scripts/omt/mvc_check.py", "--json", str(_FRAMEWORK)],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
        )
        assert result.returncode == 0, f"mvc_check failed: {result.stderr}"
        data = json.loads(result.stdout)
        errors = [f for f in data["findings"] if f["severity"] == "error"]
        assert errors == [], f"MVC++ errors in framework: {json.dumps(errors, indent=2)}"

    def test_framework_imports_no_model(self):
        """Framework files must not import from agentx.model."""
        for py in sorted(_FRAMEWORK.rglob("*.py")):
            source = py.read_text()
            assert "from agentx.model" not in source, (
                f"Framework file {py.name} imports Model layer — MVC++ violation"
            )
            assert "import agentx.model" not in source, (
                f"Framework file {py.name} imports Model layer — MVC++ violation"
            )


class TestRefactoredInheritance:
    """The 9 refactored screens/adapters inherit the new base classes."""

    def test_main_screen_inherits_base(self):
        from agentx.ui.tui.screens.main_screen import MainTUIScreen
        from agentx.ui.tui.framework import BaseAgentXScreen

        assert issubclass(MainTUIScreen, BaseAgentXScreen)

    def test_chat_screen_inherits_base(self):
        from agentx.ui.tui.screens.chat_screen import ChatTUIScreen
        from agentx.ui.tui.framework import BaseAgentXScreen

        assert issubclass(ChatTUIScreen, BaseAgentXScreen)

    def test_rag_screen_inherits_base(self):
        from agentx.ui.tui.screens.rag_screen import RagTUIScreen
        from agentx.ui.tui.framework import BaseAgentXScreen

        assert issubclass(RagTUIScreen, BaseAgentXScreen)

    def test_app_inherits_base_app(self):
        from agentx.ui.tui.app import TUIApplication
        from agentx.ui.tui.framework import BaseAgentXApp

        assert issubclass(TUIApplication, BaseAgentXApp)

    def test_agent_screen_inherits_base(self):
        from agentx.agent.view.tui.agent_screen import AgentTUIScreen
        from agentx.ui.tui.framework import BaseAgentXScreen

        assert issubclass(AgentTUIScreen, BaseAgentXScreen)

    def test_demo_screen_inherits_base(self):
        from agentx.agent.view.tui.demo_screen import AgentDemoScreen
        from agentx.ui.tui.framework import BaseAgentXScreen

        assert issubclass(AgentDemoScreen, BaseAgentXScreen)

    def test_fast_agent_screen_inherits_base(self):
        from agentx.agent.view.tui.fast_agent_screen import FastAgentTUIScreen
        from agentx.ui.tui.framework import BaseAgentXScreen

        assert issubclass(FastAgentTUIScreen, BaseAgentXScreen)

    def test_modals_inherit_base_modal(self):
        from agentx.agent.view.tui.fast_agent_modals import (
            GoalModal,
            ReflectionModal,
            ResultModal,
            RunningModal,
        )
        from agentx.ui.tui.framework import BaseAgentXModalScreen

        for modal in (GoalModal, RunningModal, ReflectionModal, ResultModal):
            assert issubclass(modal, BaseAgentXModalScreen), (
                f"{modal.__name__} must inherit BaseAgentXModalScreen"
            )

    def test_adapters_inherit_base_adapter(self):
        from agentx.ui.tui.adapters.chat_adapter import TUIChatAdapter
        from agentx.ui.tui.adapters.main_adapter import TUIAdapter
        from agentx.ui.tui.adapters.rag_adapter import TUIRagAdapter
        from agentx.ui.tui.framework import BaseScreenAdapter

        for adapter in (TUIAdapter, TUIChatAdapter, TUIRagAdapter):
            assert issubclass(adapter, BaseScreenAdapter), (
                f"{adapter.__name__} must inherit BaseScreenAdapter"
            )

    def test_adapters_still_implement_view_interfaces(self):
        from agentx.ui.interfaces import IChatView, IMainView, IRagView
        from agentx.ui.tui.adapters.chat_adapter import TUIChatAdapter
        from agentx.ui.tui.adapters.main_adapter import TUIAdapter
        from agentx.ui.tui.adapters.rag_adapter import TUIRagAdapter

        assert issubclass(TUIAdapter, IMainView)
        assert issubclass(TUIChatAdapter, IChatView)
        assert issubclass(TUIRagAdapter, IRagView)


class TestRegressionPartnerRegistration:
    """The agent screens remain registered as IAgentViewPartner virtual subclasses."""

    def test_agent_screen_is_view_partner(self):
        from agentx.agent.interfaces import IAgentViewPartner
        from agentx.agent.view.tui.agent_screen import AgentTUIScreen

        assert issubclass(AgentTUIScreen, IAgentViewPartner)
        assert isinstance(AgentTUIScreen(), IAgentViewPartner)

    def test_demo_screen_is_view_partner(self):
        from agentx.agent.interfaces import IAgentViewPartner
        from agentx.agent.view.tui.demo_screen import AgentDemoScreen

        assert issubclass(AgentDemoScreen, IAgentViewPartner)
        assert isinstance(AgentDemoScreen(), IAgentViewPartner)


class TestPublicApi:
    """The framework package exposes the documented public API."""

    def test_public_symbols(self):
        from agentx.ui.tui import framework

        for name in (
            "BaseAgentXScreen",
            "BaseAgentXModalScreen",
            "BaseAgentXApp",
            "BaseScreenAdapter",
            "NavigationMixin",
            "register_partner",
            "SessionStatusBar",
            "WelcomePanel",
            "MenuGrid",
            "CommandInput",
            "ChatMessage",
        ):
            assert hasattr(framework, name), f"framework missing public symbol: {name}"
            assert name in framework.__all__
