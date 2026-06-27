"""TUIAdapter (main_adapter.py) — full mock-based unit tests.

Covers:
  - Construction with controller
  - ``show()`` — creates TUIApplication and calls ``app.run()``
  - ``print_message`` / ``print_error_message`` / ``print_warring_message``
    — delegates to ``app.notify()``
  - ``print_response`` / ``print_response_error`` — alias methods
  - Graceful handling when ``_app`` is ``None`` (no-op)
  - IMainView ABC compliance
"""

from __future__ import annotations

from unittest.mock import MagicMock, create_autospec, patch

import pytest

from agentx.ui.interfaces import IMainView
from agentx.ui.tui.adapters.main_adapter import TUIAdapter


# ---------------------------------------------------------------------------
# IMainView ABC compliance
# ---------------------------------------------------------------------------

class TestIMainViewABC:
    """Verify IMainView cannot be instantiated."""

    def test_interface_is_abstract(self):
        with pytest.raises(TypeError, match="show"):
            IMainView()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestTUIAdapterConstruction:
    """Verify the adapter is initialised correctly."""

    def test_construction_stores_controller_and_none_app(self, mock_main_controller):
        adapter = TUIAdapter(mock_main_controller)
        assert adapter._controller is mock_main_controller
        assert adapter._app is None

    def test_implements_imainview(self, mock_main_controller):
        """Concrete check: every abstract method from IMainView is present."""
        adapter = TUIAdapter.__new__(TUIAdapter)
        for method in ("show", "print_message", "print_error_message",
                       "print_warring_message", "print_response",
                       "print_response_error"):
            assert hasattr(adapter, method), f"Missing {method}"
            assert callable(getattr(adapter, method)), f"{method} not callable"

    def test_imainview_has_correct_abstract_methods(self):
        """All 6 abstract methods declared in IMainView are indeed abstract."""
        import inspect
        from agentx.ui.interfaces import IMainView

        abstract_methods = {
            name
            for name, method in inspect.getmembers(
                IMainView, predicate=inspect.isfunction
            )
            if getattr(method, "__isabstractmethod__", False)
        }
        assert abstract_methods == {
            "show", "print_message", "print_error_message",
            "print_warring_message", "print_response",
            "print_response_error",
        }, f"Unexpected abstract methods: {abstract_methods}"


# ---------------------------------------------------------------------------
# show()
# ---------------------------------------------------------------------------

class TestTUIAdapterShow:
    """``show()`` creates a TUIApplication and calls ``app.run()``."""

    def test_show_creates_tui_application_and_runs(self, mock_main_controller):
        adapter = TUIAdapter(mock_main_controller)

        with patch("agentx.ui.tui.app.TUIApplication") as mock_app_cls:
            mock_app_instance = MagicMock()
            mock_app_cls.return_value = mock_app_instance

            adapter.show()

            # Verify TUIApplication was constructed with the controller
            mock_app_cls.assert_called_once_with(mock_main_controller)

            # Verify app.run() was called
            mock_app_instance.run.assert_called_once()

            # Verify the adapter stores the app reference
            assert adapter._app is mock_app_instance

    def test_show_stores_app_reference(self, mock_main_controller):
        adapter = TUIAdapter(mock_main_controller)
        with patch("agentx.ui.tui.app.TUIApplication") as mock_app_cls:
            mock_app = MagicMock()
            mock_app_cls.return_value = mock_app
            adapter.show()
            assert adapter._app is mock_app

    def test_show_passes_controller_to_app(self, mock_main_controller):
        adapter = TUIAdapter(mock_main_controller)
        with patch("agentx.ui.tui.app.TUIApplication") as mock_app_cls:
            mock_app = MagicMock()
            mock_app_cls.return_value = mock_app
            adapter.show()
            # Check that TUIApplication received the controller
            call_kwargs = mock_app_cls.call_args
            assert call_kwargs[0][0] is mock_main_controller, \
                "Controller was not passed to TUIApplication"


# ---------------------------------------------------------------------------
# print_message / print_error_message / print_warring_message
# ---------------------------------------------------------------------------

class TestTUIAdapterNotifications:
    """Message printing delegates to ``app.notify()`` with correct severity."""

    def test_print_message_calls_notify_with_info(self, mock_main_controller, mock_textual_app):
        adapter = TUIAdapter(mock_main_controller)
        adapter._app = mock_textual_app

        adapter.print_message("hello")
        mock_textual_app.notify.assert_called_once_with(
            "hello", severity="information", timeout=3
        )

    def test_print_error_message_calls_notify_with_error(self, mock_main_controller, mock_textual_app):
        adapter = TUIAdapter(mock_main_controller)
        adapter._app = mock_textual_app

        adapter.print_error_message("error!")
        mock_textual_app.notify.assert_called_once_with(
            "error!", severity="error", timeout=None
        )

    def test_print_warring_message_calls_notify_with_warning(self, mock_main_controller, mock_textual_app):
        adapter = TUIAdapter(mock_main_controller)
        adapter._app = mock_textual_app

        adapter.print_warring_message("warning!")
        mock_textual_app.notify.assert_called_once_with(
            "warning!", severity="warning", timeout=5
        )

    def test_print_message_multiple_calls(self, mock_main_controller, mock_textual_app):
        """Multiple print_message calls each invoke notify."""
        adapter = TUIAdapter(mock_main_controller)
        adapter._app = mock_textual_app

        adapter.print_message("first")
        adapter.print_message("second")
        assert mock_textual_app.notify.call_count == 2

    def test_print_error_message_timeout_none(self, mock_main_controller, mock_textual_app):
        """Error messages should stay until dismissed (timeout=None)."""
        adapter = TUIAdapter(mock_main_controller)
        adapter._app = mock_textual_app
        adapter.print_error_message("critical!")
        _call = mock_textual_app.notify.call_args
        assert _call[1]["timeout"] is None


# ---------------------------------------------------------------------------
# print_response / print_response_error  (alias methods)
# ---------------------------------------------------------------------------

class TestTUIAdapterResponseAliases:
    """``print_response`` / ``print_response_error`` are aliases."""

    def test_print_response_delegates_to_print_message(self, mock_main_controller, mock_textual_app):
        adapter = TUIAdapter(mock_main_controller)
        adapter._app = mock_textual_app

        with patch.object(adapter, "print_message") as mock_print:
            adapter.print_response("response text")
            mock_print.assert_called_once_with("response text")

    def test_print_response_error_delegates_to_print_error_message(self, mock_main_controller, mock_textual_app):
        adapter = TUIAdapter(mock_main_controller)
        adapter._app = mock_textual_app

        with patch.object(adapter, "print_error_message") as mock_err:
            adapter.print_response_error("error text")
            mock_err.assert_called_once_with("error text")


# ---------------------------------------------------------------------------
# Graceful no-op when _app is None
# ---------------------------------------------------------------------------

class TestTUIAdapterNoApp:
    """When ``_app`` is ``None`` (before ``show()`` is called), methods are no-ops."""

    def test_print_message_app_none_no_error(self, mock_main_controller):
        """print_message with _app=None should not crash."""
        adapter = TUIAdapter(mock_main_controller)
        assert adapter._app is None
        adapter.print_message("test")  # should not raise

    def test_print_error_message_app_none_no_error(self, mock_main_controller):
        adapter = TUIAdapter(mock_main_controller)
        adapter.print_error_message("test")

    def test_print_warring_message_app_none_no_error(self, mock_main_controller):
        adapter = TUIAdapter(mock_main_controller)
        adapter.print_warring_message("test")

    def test_print_response_app_none_no_error(self, mock_main_controller):
        adapter = TUIAdapter(mock_main_controller)
        adapter.print_response("test")

    def test_print_response_error_app_none_no_error(self, mock_main_controller):
        adapter = TUIAdapter(mock_main_controller)
        adapter.print_response_error("test")


# ---------------------------------------------------------------------------
# Edge cases — empty / special messages
# ---------------------------------------------------------------------------

class TestTUIAdapterEdgeCases:
    """Boundary conditions for message content."""

    def test_empty_message(self, mock_main_controller, mock_textual_app):
        adapter = TUIAdapter(mock_main_controller)
        adapter._app = mock_textual_app
        adapter.print_message("")
        mock_textual_app.notify.assert_called_once_with(
            "", severity="information", timeout=3
        )

    def test_message_with_unicode(self, mock_main_controller, mock_textual_app):
        adapter = TUIAdapter(mock_main_controller)
        adapter._app = mock_textual_app
        adapter.print_message("🎨 Unicode ✓")
        mock_textual_app.notify.assert_called_once_with(
            "🎨 Unicode ✓", severity="information", timeout=3
        )

    def test_message_with_newlines(self, mock_main_controller, mock_textual_app):
        adapter = TUIAdapter(mock_main_controller)
        adapter._app = mock_textual_app
        adapter.print_message("line1\nline2")
        mock_textual_app.notify.assert_called_once_with(
            "line1\nline2", severity="information", timeout=3
        )


# ---------------------------------------------------------------------------
# Integration: adapter <-> controller bridge
# ---------------------------------------------------------------------------

class TestTUIAdapterControllerBridge:
    """Verify the controller reference is properly wired through the adapter."""

    def test_controller_is_stored(self, mock_main_controller):
        adapter = TUIAdapter(mock_main_controller)
        assert adapter._controller is mock_main_controller

    def test_controller_accessible_after_show(self, mock_main_controller):
        adapter = TUIAdapter(mock_main_controller)
        with patch("agentx.ui.tui.app.TUIApplication") as mock_app_cls:
            mock_app_cls.return_value = MagicMock()
            adapter.show()
            # The controller should still be available
            assert adapter._controller is mock_main_controller

    def test_controller_passed_to_app(self, mock_main_controller):
        adapter = TUIAdapter(mock_main_controller)
        with patch("agentx.ui.tui.app.TUIApplication") as mock_app_cls:
            mock_app_cls.return_value = MagicMock()
            adapter.show()
            # Verify TUIApplication received the controller
            mock_app_cls.assert_called_with(mock_main_controller)


# ---------------------------------------------------------------------------
# Constructor error handling
# ---------------------------------------------------------------------------

class TestTUIAdapterConstructorErrors:
    """Verify the adapter handles edge cases in construction."""

    def test_none_controller(self):
        """Constructor should accept None controller."""
        adapter = TUIAdapter(None)  # type: ignore[arg-type]
        assert adapter._controller is None
        assert adapter._app is None

    def test_invalid_controller_type(self):
        """Constructor should accept any object (duck typing)."""
        controller = object()
        adapter = TUIAdapter(controller)  # type: ignore[arg-type]
        assert adapter._controller is controller
