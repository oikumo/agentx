"""MVC++ compliance tests for ReAct screen feature.

These tests verify the architectural separation of layers:
- View must not import Model
- Controller must import Model + View interface
- Abstract Partners must be ABCs
- mvc_check.py must pass with 0 errors
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


# ─── View layer tests ─────────────────────────────────────────────────────────


class TestReactViewLayerIsolation:
    """Ensure ReactTUIScreen (View) has no Model imports."""

    VIEW_FILE = Path("src/agentx/ui/tui/screens/react_screen.py")

    def test_view_file_exists(self) -> None:
        assert self.VIEW_FILE.exists(), f"View file not found: {self.VIEW_FILE}"

    def test_view_does_not_import_model(self) -> None:
        """View must not import agentx.model.*"""
        text = self.VIEW_FILE.read_text()
        assert "from agentx.model" not in text, (
            f"View imports Model: 'from agentx.model' found in {self.VIEW_FILE}"
        )
        assert "import agentx.model" not in text, (
            f"View imports Model: 'import agentx.model' found in {self.VIEW_FILE}"
        )

    def test_view_does_not_import_react_model(self) -> None:
        """View must not import react-specific model modules."""
        text = self.VIEW_FILE.read_text()
        assert "agentx.model.react" not in text
        assert "ReactAgentService" not in text

    def test_view_only_imports_framework_and_textual(self) -> None:
        """View should only import from framework, textual, and ui.interfaces."""
        text = self.VIEW_FILE.read_text()
        # Check it imports from allowed modules
        assert "from agentx.ui.tui.framework" in text
        assert "from agentx.ui.interfaces import IReactViewPartner" in text


# ─── Controller layer tests ───────────────────────────────────────────────────


class TestReactControllerLayer:
    """Ensure ReactController (Controller) imports correctly."""

    CONTROLLER_FILE = Path("src/agentx/ui/screens/react/react_controller.py")
    INTERFACES_FILE = Path("src/agentx/ui/interfaces.py")

    def test_controller_imports_model(self) -> None:
        """Controller MUST import Model (ReactAgentService)."""
        text = self.CONTROLLER_FILE.read_text()
        assert "from agentx.model.react.react_agent_service import ReactAgentService" in text

    def test_controller_imports_view_interface(self) -> None:
        """Controller must import the View's Abstract Partner interface."""
        text = self.CONTROLLER_FILE.read_text()
        assert "from agentx.ui.interfaces import IReactViewPartner" in text

    def test_controller_implements_abc(self) -> None:
        """Controller must implement IReactViewPartner ABC."""
        text = self.CONTROLLER_FILE.read_text()
        assert "class ReactController(IReactViewPartner)" in text

    def test_ireact_view_partner_is_abc(self) -> None:
        """IReactViewPartner must be an ABC with abstractmethods."""
        text = self.INTERFACES_FILE.read_text()
        assert "class IReactViewPartner(ABC)" in text
        assert "@abstractmethod" in text
        assert "def send_message" in text
        assert "def cancel" in text
        assert "def is_running" in text
        assert "def get_history" in text
        assert "def close" in text
        assert "def start_new_conversation" in text


# ─── Abstract Partner virtual registration ────────────────────────────────────


class TestReactPartnerRegistration:
    """Verify register_partner is called for React screen."""

    VIEW_FILE = Path("src/agentx/ui/tui/screens/react_screen.py")

    def test_register_partner_called(self) -> None:
        """View must call register_partner(IReactViewPartner, ReactTUIScreen)."""
        text = self.VIEW_FILE.read_text()
        assert "register_partner(IReactViewPartner, ReactTUIScreen)" in text


# ─── mvc_check tool ───────────────────────────────────────────────────────────


class TestMvcCheckTool:
    """Run mvc_check.py on all React-related files."""

    @pytest.mark.parametrize(
        "file_path",
        [
            "src/agentx/model/react/__init__.py",
            "src/agentx/model/react/react_tools.py",
            "src/agentx/model/react/react_agent_service.py",
            "src/agentx/ui/screens/react/__init__.py",
            "src/agentx/ui/screens/react/react_controller.py",
            "src/agentx/ui/tui/screens/react_screen.py",
        ],
    )
    def test_mvc_check_zero_errors(self, file_path: str) -> None:
        """mvc_check.py should report 0 errors for each file."""
        path = Path(file_path)
        if not path.exists():
            pytest.skip(f"File not found: {file_path}")

        result = subprocess.run(
            [sys.executable, "-m", "scripts.omt.mvc_check", str(path)],
            cwd=Path(__file__).parent.parent.parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, (
            f"mvc_check failed for {file_path}:\n{result.stdout}\n{result.stderr}"
        )
        assert "no violations" in result.stdout.lower() or " 0 error" in result.stdout, (
            f"mvc_check found errors in {file_path}:\n{result.stdout}"
        )

    def test_mvc_check_all_react_files(self) -> None:
        """mvc_check.py should pass on all React files combined."""
        paths = [
            "src/agentx/model/react",
            "src/agentx/ui/screens/react",
            "src/agentx/ui/tui/screens/react_screen.py",
        ]
        for p in paths:
            if not Path(p).exists():
                pytest.skip(f"Path not found: {p}")

        result = subprocess.run(
            [sys.executable, "-m", "scripts.omt.mvc_check", *paths],
            cwd=Path(__file__).parent.parent.parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, (
            f"mvc_check failed:\n{result.stdout}\n{result.stderr}"
        )
        assert "no violations" in result.stdout.lower() or " 0 error" in result.stdout, (
            f"mvc_check found errors:\n{result.stdout}"
        )