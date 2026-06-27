"""TUIApplication (app.py) — deep mock-based unit tests.

Covers both classes defined in app.py:

  - TUIApplication (the main Textual App subclass)
      - Construction with optional controller
      - ``on_mount()`` — TTY check, screen push, warning notification
      - CSS definitions

  - MainTUIScreen (the minimal fallback screen in app.py)
      - Construction
      - Compose (Header, Labels, Footer)
      - Bindings (q, c, r)
      - Actions (quit, open_chat, open_rag)
"""

from __future__ import annotations

from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from textual.binding import Binding

from agentx.ui.tui.app import TUIApplication


# ===================================================================
# TUIApplication — construction
# ===================================================================

class TestTUIApplicationConstruction:
    """Construction stores controller reference."""

    def test_default_controller_is_none(self):
        app = TUIApplication()
        assert app._controller is None

    def test_controller_stored(self, mock_main_controller):
        app = TUIApplication(mock_main_controller)
        assert app._controller is mock_main_controller

    def test_none_controller_accepted(self):
        app = TUIApplication(None)  # type: ignore[arg-type]
        assert app._controller is None

    def test_app_is_textual_app_instance(self):
        """TUIApplication is a subclass of textual.app.App."""
        from textual.app import App
        assert issubclass(TUIApplication, App), \
            "TUIApplication must extend textual App"


# ===================================================================
# TUIApplication — CSS
# ===================================================================

class TestTUIApplicationCSS:
    """Application-level CSS contains base styling."""

    def test_includes_screen_background(self):
        assert "$surface" in TUIApplication.CSS
        assert "Screen" in TUIApplication.CSS

    def test_includes_header_styling(self):
        assert "Header" in TUIApplication.CSS
        assert "$primary" in TUIApplication.CSS

    def test_includes_footer_dock(self):
        assert "Footer" in TUIApplication.CSS
        assert "dock: bottom" in TUIApplication.CSS


# ===================================================================
# TUIApplication — on_mount
# ===================================================================

class TestTUIApplicationOnMount:
    """on_mount checks TTY and pushes MainTUIScreen."""

    @patch("agentx.ui.tui.app.sys.stdin.isatty")
    def test_mount_pushes_main_screen(self, mock_isatty, mock_main_controller):
        """The primary responsibility: push MainTUIScreen with controller."""
        mock_isatty.return_value = True  # TTY available

        app = TUIApplication(mock_main_controller)
        app.push_screen = MagicMock()
        app.notify = MagicMock()

        app.on_mount()

        app.push_screen.assert_called_once()
        # The pushed screen should be a MainTUIScreen
        from agentx.ui.tui.screens.main_screen import MainTUIScreen as FullMainTUIScreen
        pushed_screen = app.push_screen.call_args[0][0]
        assert isinstance(pushed_screen, FullMainTUIScreen), \
            f"Expected MainTUIScreen from screens.main_screen, got {type(pushed_screen).__name__}"
        assert pushed_screen._controller is mock_main_controller

    @patch("agentx.ui.tui.app.sys.stdin.isatty")
    def test_mount_does_not_notify_in_tty(self, mock_isatty, mock_main_controller):
        """When TTY is available, no warning notification is shown."""
        mock_isatty.return_value = True

        app = TUIApplication(mock_main_controller)
        app.push_screen = MagicMock()
        app.notify = MagicMock()

        app.on_mount()

        app.notify.assert_not_called()

    @patch("agentx.ui.tui.app.sys.stdin.isatty")
    def test_mount_shows_warning_when_not_tty(self, mock_isatty, mock_main_controller):
        """When TTY is NOT available, a warning notification is shown."""
        mock_isatty.return_value = False

        app = TUIApplication(mock_main_controller)
        app.push_screen = MagicMock()
        app.notify = MagicMock()

        app.on_mount()

        app.notify.assert_called_once()
        call_str = str(app.notify.call_args)
        assert "Non-TTY" in call_str or "TTY" in call_str
        assert "warning" in str(app.notify.call_args[1].get("severity", ""))

    @patch("agentx.ui.tui.app.sys.stdin.isatty")
    def test_mount_with_none_controller(self, mock_isatty):
        """Mount works even without controller."""
        mock_isatty.return_value = True

        app = TUIApplication()
        app.push_screen = MagicMock()
        app.notify = MagicMock()

        app.on_mount()

        app.push_screen.assert_called_once()
        pushed_screen = app.push_screen.call_args[0][0]
        assert pushed_screen._controller is None

    @patch("agentx.ui.tui.app.sys.stdin.isatty")
    def test_mount_pushes_correct_screen_type(self, mock_isatty, mock_main_controller):
        """Verify exactly the right class is pushed."""
        mock_isatty.return_value = True
        app = TUIApplication(mock_main_controller)
        app.push_screen = MagicMock()
        app.notify = MagicMock()
        app.on_mount()

        from agentx.ui.tui.screens.main_screen import MainTUIScreen
        pushed = app.push_screen.call_args[0][0]
        assert type(pushed).__name__ == "MainTUIScreen"
        # The pushed screen class should be from screens.main_screen, not app.py
        assert type(pushed).__module__ == "agentx.ui.tui.screens.main_screen"


# ===================================================================
# app.py MainTUIScreen (minimal fallback)
# ===================================================================

class TestAppMainTUIScreen:
    """The minimal MainTUIScreen in app.py (not the full one from screens/)."""

    def test_has_bindings(self):
        from agentx.ui.tui.app import MainTUIScreen
        assert len(MainTUIScreen.BINDINGS) >= 1, \
            "Must define at least a quit binding"

    def test_bindings_include_quit(self):
        from agentx.ui.tui.app import MainTUIScreen
        keys = [b if isinstance(b, str) else b[0] if isinstance(b, tuple) else b.key
                for b in MainTUIScreen.BINDINGS]
        has_q = any(k == "q" for k in keys)
        # Check regardless of tuple vs Binding syntax
        binding_keys = set()
        for b in MainTUIScreen.BINDINGS:
            if isinstance(b, tuple):
                binding_keys.add(b[0])
            else:
                binding_keys.add(b.key)
        assert "q" in binding_keys, "Must have 'q' binding to quit"

    def test_compose_creates_header_labels_footer(self):
        from agentx.ui.tui.app import MainTUIScreen
        screen = MainTUIScreen.__new__(MainTUIScreen)
        items = list(screen.compose())
        from textual.widgets import Header, Footer, Label
        types = [type(i).__name__ for i in items]
        assert "Header" in types
        assert "Footer" in types
        assert "Label" in types, "compose should produce at least one Label"

    def test_action_quit_calls_app_exit(self):
        from agentx.ui.tui.app import MainTUIScreen
        screen = MainTUIScreen.__new__(MainTUIScreen)
        with patch.object(MainTUIScreen, "app", new_callable=PropertyMock) as mock_app:
            mock_app_instance = MagicMock()
            mock_app.return_value = mock_app_instance
            screen.action_quit()
            mock_app_instance.exit.assert_called_once()

    def test_action_open_chat_placeholder(self):
        from agentx.ui.tui.app import MainTUIScreen
        screen = MainTUIScreen.__new__(MainTUIScreen)
        screen.notify = MagicMock()
        screen.action_open_chat()
        screen.notify.assert_called_once()

    def test_action_open_rag_placeholder(self):
        from agentx.ui.tui.app import MainTUIScreen
        screen = MainTUIScreen.__new__(MainTUIScreen)
        screen.notify = MagicMock()
        screen.action_open_rag()
        screen.notify.assert_called_once()

    def test_construction_with_controller(self, mock_main_controller):
        from agentx.ui.tui.app import MainTUIScreen
        screen = MainTUIScreen(mock_main_controller)
        assert screen._controller is mock_main_controller

    def test_construction_without_controller(self):
        from agentx.ui.tui.app import MainTUIScreen
        screen = MainTUIScreen()
        assert screen._controller is None


# ===================================================================
# TUIApplication — controller access
# ===================================================================

class TestTUIApplicationControllerAccess:
    """Verify the controller can be accessed through the app."""

    def test_controller_accessible(self, mock_main_controller):
        app = TUIApplication(mock_main_controller)
        assert app._controller is mock_main_controller

    def test_controller_passed_to_screen_on_mount(self, mock_main_controller):
        """The controller stored in the app should reach the pushed screen."""
        app = TUIApplication(mock_main_controller)
        app.push_screen = MagicMock()
        app.notify = MagicMock()

        with patch("agentx.ui.tui.app.sys.stdin.isatty", return_value=True):
            app.on_mount()

        pushed = app.push_screen.call_args[0][0]
        assert pushed._controller is mock_main_controller, \
            "Controller from app was not passed to the screen"
