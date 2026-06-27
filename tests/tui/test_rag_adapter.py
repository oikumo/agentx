"""TUIRagAdapter (rag_adapter.py) — full mock-based unit tests.

Covers:
  - Construction and initial state
  - ``show()`` — currently a placeholder (no-op)
  - ``print_message``
  - ``print_message_error``
  - ``show_repository_state`` — prints state object
  - ``show_menu``
  - IRagView ABC compliance
  - Edge cases: None state, non-string objects, empty messages
"""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

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
# print_message
# ---------------------------------------------------------------------------

class TestTUIRagAdapterPrintMessage:
    """print_message prints with [RAG INFO] prefix."""

    def test_print_message_prints_prefix_and_message(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.print_message("info text")
            output = mock_stdout.getvalue()
            assert "[RAG INFO]" in output
            assert "info text" in output

    def test_print_message_empty(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        with patch("sys.stdout", new_callable=StringIO):
            adapter.print_message("")  # should not raise

    def test_print_message_unicode(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.print_message("📚 RAG info")
            assert "📚 RAG info" in mock_stdout.getvalue()

    def test_print_message_multiple_calls(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.print_message("first")
            adapter.print_message("second")
            output = mock_stdout.getvalue()
            assert output.count("[RAG INFO]") == 2


# ---------------------------------------------------------------------------
# print_message_error
# ---------------------------------------------------------------------------

class TestTUIRagAdapterPrintError:
    """print_message_error prints with [RAG ERROR] prefix."""

    def test_print_error_prints_prefix_and_message(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.print_message_error("error text")
            output = mock_stdout.getvalue()
            assert "[RAG ERROR]" in output
            assert "error text" in output

    def test_print_error_empty(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        with patch("sys.stdout", new_callable=StringIO):
            adapter.print_message_error("")

    def test_print_error_vs_print_message_prefix_difference(self, mock_rag_controller):
        """Info and error use different prefixes."""
        adapter = TUIRagAdapter(mock_rag_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.print_message("info")
            adapter.print_message_error("error")
            output = mock_stdout.getvalue()
            assert "[RAG INFO]" in output
            assert "[RAG ERROR]" in output


# ---------------------------------------------------------------------------
# show_repository_state
# ---------------------------------------------------------------------------

class TestTUIRagAdapterShowRepositoryState:
    """show_repository_state prints the state object."""

    def test_show_repository_state_prints_state(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_repository_state("current_state")
            output = mock_stdout.getvalue()
            assert "[RAG STATE]" in output
            assert "current_state" in output

    def test_show_repository_state_with_dict(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        state_data = {"repo": "agentx", "branch": "main", "files": 42}
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_repository_state(state_data)
            output = mock_stdout.getvalue()
            assert "[RAG STATE]" in output
            assert "repo" in output
            assert "agentx" in output

    def test_show_repository_state_with_none(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_repository_state(None)  # should not raise
            output = mock_stdout.getvalue()
            assert "[RAG STATE]" in output

    def test_show_repository_state_with_integer(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_repository_state(42)
            output = mock_stdout.getvalue()
            assert "42" in output

    def test_show_repository_state_with_object(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        class CustomState:
            def __str__(self) -> str:
                return "CustomState[sync=True]"
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_repository_state(CustomState())
            output = mock_stdout.getvalue()
            assert "CustomState" in output

    def test_show_repository_state_casts_to_string(self, mock_rag_controller):
        """The state parameter is typed as `object`, so str() conversion is used."""
        adapter = TUIRagAdapter(mock_rag_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_repository_state(True)
            output = mock_stdout.getvalue()
            assert "True" in output


# ---------------------------------------------------------------------------
# show_menu
# ---------------------------------------------------------------------------

class TestTUIRagAdapterShowMenu:
    """show_menu prints a fixed [RAG MENU] marker."""

    def test_show_menu_prints_menu_marker(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_menu()
            output = mock_stdout.getvalue()
            assert "[RAG MENU]" in output

    def test_show_menu_takes_no_args(self, mock_rag_controller):
        """show_menu() takes no arguments beyond self."""
        adapter = TUIRagAdapter(mock_rag_controller)
        with patch("sys.stdout", new_callable=StringIO):
            adapter.show_menu()  # should not raise TypeError


# ---------------------------------------------------------------------------
# Edge cases — combined
# ---------------------------------------------------------------------------

class TestTUIRagAdapterEdgeCases:
    """All methods called in sequence without errors."""

    def test_full_workflow(self, mock_rag_controller):
        """Simulate a typical RAG session: info, menu, state updates, error."""
        adapter = TUIRagAdapter(mock_rag_controller)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show()
            adapter.print_message("Repository loaded")
            adapter.show_menu()
            adapter.show_repository_state({"status": "ready", "files": 3})
            adapter.print_message_error("No results found")
            output = mock_stdout.getvalue()
            assert "[RAG INFO]" in output
            assert "[RAG MENU]" in output
            assert "[RAG STATE]" in output
            assert "[RAG ERROR]" in output
            assert "ready" in output

    def test_very_long_state_message(self, mock_rag_controller):
        adapter = TUIRagAdapter(mock_rag_controller)
        long_state = "x" * 10000
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            adapter.show_repository_state(long_state)
            assert len(mock_stdout.getvalue()) > 10000
