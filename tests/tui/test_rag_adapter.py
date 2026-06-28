"""TUIRagAdapter (rag_adapter.py) — full mock-based unit tests.

Covers:
  - Construction and initial state
  - ``show()`` — currently a placeholder (no-op)
  - ``print_message`` — delegates to screen.notify()
  - ``print_message_error`` — delegates to screen.notify()
  - ``show_repository_state`` — delegates to screen._update_repository_ui()
  - ``show_menu`` — delegates to screen._show_menu()
  - IRagView ABC compliance
  - Edge cases: None screen, None controller
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agentx.ui.interfaces import IRagView
from agentx.ui.tui.adapters.rag_adapter import TUIRagAdapter


# ---------------------------------------------------------------------------
# IRagView ABC compliance
# ---------------------------------------------------------------------------

class TestIRagViewABC:
    """Verify IRagView cannot be instantiated."""

    def test_interface_is_abstract(self):
        with pytest.raises(TypeError, match="show"):
            IRagView()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestTUIRagAdapterConstruction:
    """Verify clean initial state."""

    def test_construction_stores_controller_and_none_screen(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        assert adapter._controller is mock_rag_controller
        assert adapter._screen is None

    def test_implements_iragview(self, mock_rag_controller):
        """Concrete check: every abstract method from IRagView is present."""
        for method in ("show", "print_message", "print_message_error",
                       "show_repository_state", "show_menu"):
            assert hasattr(TUIRagAdapter, method), f"Missing {method}"
            assert callable(getattr(TUIRagAdapter, method)), f"{method} not callable"

    def test_accepts_none_controller(self):
        """Should accept None (duck typing)."""
        adapter = TUIRagAdapter(None)  # type: ignore[arg-type]
        assert adapter._controller is None
        assert adapter._screen is None

    def test_set_screen_stores_screen(self, mock_rag_controller):
        """set_screen should store the screen reference."""
        adapter = TUIRagAdapter(mock_rag_controller)
        mock_screen = MagicMock()
        adapter.set_screen(mock_screen)
        assert adapter._screen is mock_screen


# ---------------------------------------------------------------------------
# show() — placeholder
# ---------------------------------------------------------------------------

class TestTUIRagAdapterShow:
    """show() is currently a no-op placeholder."""

    def test_show_is_noop(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        result = adapter.show()
        assert result is None

    def test_show_with_none_controller(self):
        adapter = TUIRagAdapter(None)  # type: ignore[arg-type]
        result = adapter.show()
        assert result is None


# ---------------------------------------------------------------------------
# print_message — delegates to screen.notify()
# ---------------------------------------------------------------------------

class TestTUIRagAdapterPrintMessage:
    """print_message delegates to screen.notify() with info severity."""

    def test_print_message_delegates_to_screen(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        mock_screen = MagicMock()
        adapter.set_screen(mock_screen)
        
        adapter.print_message("info text")
        
        mock_screen.notify.assert_called_once_with("info text", severity="information", timeout=3)

    def test_print_message_no_screen_does_not_raise(self, mock_rag_controller):
        """Should not raise when no screen is set."""
        adapter = TUIRagAdapter(mock_rag_controller)
        # No screen set
        adapter.print_message("info text")  # Should not raise

    def test_print_message_with_none_controller(self):
        adapter = TUIRagAdapter(None)  # type: ignore[arg-type]
        mock_screen = MagicMock()
        adapter.set_screen(mock_screen)
        
        adapter.print_message("test")
        
        mock_screen.notify.assert_called_once_with("test", severity="information", timeout=3)

    def test_print_message_multiple_calls(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        mock_screen = MagicMock()
        adapter.set_screen(mock_screen)
        
        adapter.print_message("first")
        adapter.print_message("second")
        
        assert mock_screen.notify.call_count == 2


# ---------------------------------------------------------------------------
# print_message_error — delegates to screen.notify() with error severity
# ---------------------------------------------------------------------------

class TestTUIRagAdapterPrintError:
    """print_message_error delegates to screen.notify() with error severity."""

    def test_print_error_delegates_to_screen(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        mock_screen = MagicMock()
        adapter.set_screen(mock_screen)
        
        adapter.print_message_error("error text")
        
        mock_screen.notify.assert_called_once_with("error text", severity="error", timeout=None)

    def test_print_error_no_screen_does_not_raise(self, mock_rag_controller):
        """Should not raise when no screen is set."""
        adapter = TUIRagAdapter(mock_rag_controller)
        adapter.print_message_error("error text")  # Should not raise

    def test_print_error_vs_print_message_different_severity(self, mock_rag_controller):
        """Info and error use different severities."""
        adapter = TUIRagAdapter(mock_rag_controller)
        mock_screen = MagicMock()
        adapter.set_screen(mock_screen)
        
        adapter.print_message("info")
        adapter.print_message_error("error")
        
        calls = mock_screen.notify.call_args_list
        assert calls[0][1]["severity"] == "information"
        assert calls[1][1]["severity"] == "error"


# ---------------------------------------------------------------------------
# show_repository_state — delegates to screen._update_repository_ui()
# ---------------------------------------------------------------------------

class TestTUIRagAdapterShowRepositoryState:
    """show_repository_state delegates to screen._update_repository_ui()."""

    def test_show_repository_state_delegates_to_screen(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        mock_screen = MagicMock()
        adapter.set_screen(mock_screen)
        
        adapter.show_repository_state({"repo": "test", "status": "ready"})
        
        mock_screen._update_repository_ui.assert_called_once_with({"repo": "test", "status": "ready"})

    def test_show_repository_state_with_none(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        mock_screen = MagicMock()
        adapter.set_screen(mock_screen)
        
        adapter.show_repository_state(None)  # should not raise
        
        mock_screen._update_repository_ui.assert_called_once_with(None)

    def test_show_repository_state_no_screen_does_not_raise(self, mock_rag_controller):
        """Should not raise when no screen is set."""
        adapter = TUIRagAdapter(mock_rag_controller)
        adapter.show_repository_state("test")  # Should not raise

    def test_show_repository_state_with_various_types(self, mock_rag_controller):
        """Should handle various state types."""
        adapter = TUIRagAdapter(mock_rag_controller)
        mock_screen = MagicMock()
        adapter.set_screen(mock_screen)
        
        # Test with dict
        adapter.show_repository_state({"key": "value"})
        mock_screen._update_repository_ui.assert_called_with({"key": "value"})
        
        # Test with string
        adapter.show_repository_state("state_string")
        mock_screen._update_repository_ui.assert_called_with("state_string")
        
        # Test with integer
        adapter.show_repository_state(42)
        mock_screen._update_repository_ui.assert_called_with(42)
        
        # Test with custom object
        class CustomState:
            def __str__(self) -> str:
                return "CustomState[sync=True]"
        adapter.show_repository_state(CustomState())
        args = mock_screen._update_repository_ui.call_args[0][0]
        assert isinstance(args, CustomState)


# ---------------------------------------------------------------------------
# show_menu — delegates to screen._show_menu()
# ---------------------------------------------------------------------------

class TestTUIRagAdapterShowMenu:
    """show_menu delegates to screen._show_menu()."""

    def test_show_menu_delegates_to_screen(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        mock_screen = MagicMock()
        adapter.set_screen(mock_screen)
        
        adapter.show_menu()
        
        mock_screen._show_menu.assert_called_once()

    def test_show_menu_no_screen_does_not_raise(self, mock_rag_controller):
        """Should not raise when no screen is set."""
        adapter = TUIRagAdapter(mock_rag_controller)
        adapter.show_menu()  # Should not raise

    def test_show_menu_takes_no_args(self, mock_rag_controller):
        """show_menu() takes no arguments beyond self."""
        adapter = TUIRagAdapter(mock_rag_controller)
        mock_screen = MagicMock()
        adapter.set_screen(mock_screen)
        
        adapter.show_menu()  # should not raise TypeError
        mock_screen._show_menu.assert_called_once_with()


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestTUIRagAdapterEdgeCases:
    """All methods called in sequence without errors."""

    def test_full_workflow(self, mock_rag_controller):
        """Simulate a typical RAG session: info, menu, state updates, error."""
        adapter = TUIRagAdapter(mock_rag_controller)
        mock_screen = MagicMock()
        adapter.set_screen(mock_screen)
        
        adapter.show()
        adapter.print_message("Repository loaded")
        adapter.show_menu()
        adapter.show_repository_state({"status": "ready", "files": 3})
        adapter.print_message_error("No results found")
        
        # Verify all delegations happened
        assert mock_screen.notify.call_count == 2  # info + error
        mock_screen._show_menu.assert_called_once()
        mock_screen._update_repository_ui.assert_called_once_with({"status": "ready", "files": 3})

    def test_very_long_state_message(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        mock_screen = MagicMock()
        adapter.set_screen(mock_screen)
        
        long_state = "x" * 10000
        adapter.show_repository_state(long_state)
        
        mock_screen._update_repository_ui.assert_called_once_with(long_state)