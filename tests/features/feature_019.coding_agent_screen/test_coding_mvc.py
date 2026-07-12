"""MVC++ compliance tests for Coding Agent Screen."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest


class TestMVCCompliance:
    """Verify MVC++ architecture compliance for Coding Agent Screen."""

    def test_view_imports_no_model(self):
        """CodingTUIScreen must not import from agentx.model."""
        view_path = Path("src/agentx/ui/tui/screens/coding/coding_screen.py")
        content = view_path.read_text()

        # Check for model imports
        assert "from agentx.model" not in content
        assert "import agentx.model" not in content
        # Allow import of coding_agent_service if used as type hint only (TYPE_CHECKING)
        # But the actual implementation should not import model

    def test_controller_imports_no_view(self):
        """CodingController must not import from agentx.ui.tui.screens.coding."""
        controller_path = Path("src/agentx/ui/tui/screens/coding/coding_controller.py")
        content = controller_path.read_text()

        # Controller should not import view
        assert "from agentx.ui.tui.screens.coding.coding_screen" not in content
        assert "import agentx.ui.tui.screens.coding.coding_screen" not in content

    def test_controller_uses_interface(self):
        """CodingController must implement ICodingViewPartner."""
        controller_path = Path("src/agentx/ui/tui/screens/coding/coding_controller.py")
        content = controller_path.read_text()

        # Check it implements ICodingViewPartner
        assert "ICodingViewPartner" in content
        assert "class CodingController(ICodingViewPartner)" in content

    def test_view_uses_interface(self):
        """CodingTUIScreen must type-hint controller as ICodingViewPartner."""
        view_path = Path("src/agentx/ui/tui/screens/coding/coding_screen.py")
        content = view_path.read_text()

        assert "ICodingViewPartner" in content
        assert "register_partner(ICodingViewPartner, CodingTUIScreen)" in content

    def test_no_sql_in_view(self):
        """View must not contain SQL execution."""
        view_path = Path("src/agentx/ui/tui/screens/coding/coding_screen.py")
        content = view_path.read_text()

        # Check for SQL patterns
        assert ".execute(" not in content
        assert ".executemany(" not in content
        assert "cursor" not in content.lower()
        assert "sqlite" not in content.lower()

    def test_no_sql_in_controller(self):
        """Controller must not contain SQL execution."""
        controller_path = Path("src/agentx/ui/tui/screen/coding/coding_controller.py")
        if controller_path.exists():
            content = controller_path.read_text()
            assert ".execute(" not in content
            assert ".executemany(" not in content

    def test_model_has_no_ui_imports(self):
        """Model layer must not import UI frameworks."""
        model_dir = Path("src/agentx/model/coding")
        for py_file in model_dir.glob("*.py"):
            content = py_file.read_text()
            assert "textual" not in content
            assert "Textual" not in content
            assert "rich.console" not in content

    def test_coding_tools_only_stdlib_and_langchain(self):
        """coding_tools.py should only use stdlib and langchain.tools."""
        tools_path = Path("src/agentx/model/coding/coding_tools.py")
        content = tools_path.read_text()

        # Should use langchain.tools for @tool decorator
        assert "from langchain.tools import tool" in content
        # Should not use external deps beyond stdlib
        assert "import requests" not in content
        assert "import httpx" not in content

    def test_coding_agent_service_model_layer(self):
        """coding_agent_service should be pure model (no UI)."""
        service_path = Path("src/agentx/model/coding/coding_agent_service.py")
        content = service_path.read_text()

        # Should import model dependencies
        assert "from langchain.agents import create_agent" in content
        assert "from langgraph.checkpoint.memory import InMemorySaver" in content
        # Should not import UI
        assert "textual" not in content

    def test_interface_is_abstract(self):
        """ICodingViewPartner must be an ABC with abstract methods."""
        interface_path = Path("src/agentx/ui/interfaces.py")
        content = interface_path.read_text()

        # Find ICodingViewPartner class
        assert "class ICodingViewPartner(ABC):" in content
        # Check for required abstract methods
        required_methods = [
            "send_message", "cancel", "is_running", "get_history",
            "close", "start_new_conversation"
        ]
        for method in required_methods:
            assert f"def {method}" in content
            assert "@abstractmethod" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])