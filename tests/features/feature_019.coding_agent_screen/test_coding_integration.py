"""Integration tests for Coding Agent Screen (without full LLM agent)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from agentx.model.coding.coding_tools import (
    CODING_TOOLS,
    set_sandbox_root,
    file_search,
    file_read,
    file_edit,
    file_list,
    file_create,
    _file_search_impl,
    _file_read_impl,
    _file_edit_impl,
    _file_list_impl,
    _file_create_impl,
)
from agentx.model.coding.coding_agent_service import CodingAgentService
from agentx.ui.tui.screens.coding.coding_controller import CodingController


class TestCodingToolsIntegration:
    """Integration tests for Coding tools with real file operations."""

    def setup_method(self):
        """Create a temporary sandbox with test files."""
        self.tmpdir = tempfile.mkdtemp()
        set_sandbox_root(self.tmpdir)

        # Create test structure
        Path(self.tmpdir, "src").mkdir()
        Path(self.tmpdir, "src", "main.py").write_text("def main():\n    print('hello')\n")
        Path(self.tmpdir, "src", "utils.py").write_text("def helper():\n    return 42\n")
        Path(self.tmpdir, "tests").mkdir()
        Path(self.tmpdir, "tests", "test_main.py").write_text("def test_main():\n    assert True\n")
        Path(self.tmpdir, "README.md").write_text("# Project\n")

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        set_sandbox_root(Path.cwd())

    def test_coding_tools_registry(self):
        """CODING_TOOLS registry contains all 5 file tools."""
        assert len(CODING_TOOLS) == 5
        tool_names = [t.name for t in CODING_TOOLS]
        assert "file_search" in tool_names
        assert "file_read" in tool_names
        assert "file_edit" in tool_names
        assert "file_list" in tool_names
        assert "file_create" in tool_names

    def test_file_tools_work_with_sandbox(self):
        """File tools work correctly within sandbox."""
        result = file_search.invoke({"pattern": "*.py"})
        assert result.total >= 3

        result = file_read.invoke({"path": "src/main.py"})
        assert "def main" in result.content

        result = file_edit.invoke({"path": "src/main.py", "old_str": "print('hello')", "new_str": "print('world')"})
        assert result.success is True

        content = Path(self.tmpdir, "src", "main.py").read_text()
        assert "print('world')" in content

    def test_file_list_and_create(self):
        """file_list and file_create work."""
        # Create a nested file
        Path(self.tmpdir, "parent").mkdir()
        Path(self.tmpdir, "parent", "nested.txt").write_text("nested")

        result = file_list.invoke({"path": ".", "recursive": True})
        assert len(result) >= 4
        nested = [e for e in result if "nested.txt" in e.path]
        assert len(nested) == 1

        result = file_create.invoke({"path": "new_file.py", "content": "x = 1"})
        assert result.success is True
        assert Path(self.tmpdir, "new_file.py").exists()

        result = file_create.invoke({"path": "new_file.py", "content": "x = 2"})
        assert result.success is False
        assert "already exists" in result.error.lower()

    def test_internal_implementations_directly(self):
        """Internal implementations can be called directly."""
        result = _file_search_impl("*.py")
        assert result.total >= 3

        result = _file_read_impl("src/main.py")
        assert "def main" in result.content

        # Create a fresh file for editing test
        Path(self.tmpdir, "edit_test.py").write_text("x = 1\n")
        result = _file_edit_impl("edit_test.py", "x = 1", "x = 2")
        assert result.success is True

        result = _file_list_impl(".", recursive=True)
        assert len(result) >= 4

        result = _file_create_impl("new.py", "x = 1")
        assert result.success is True


class TestCodingAgentServiceIntegration:
    """Integration tests for CodingAgentService (without full LLM)."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_service_initializes(self):
        """CodingAgentService initializes with default tools."""
        service = CodingAgentService()
        assert service._tools is not None
        assert len(service._tools) == 5

    def test_service_properties(self):
        """Service property getters work."""
        service = CodingAgentService()
        # Test is_running property
        assert isinstance(service.is_running, bool)
        # Test get_history
        history = service.get_history()
        assert isinstance(history, list)

    def test_stream_agent_requires_llm(self):
        """stream_agent needs LLM (we can't test fully without one)."""
        service = CodingAgentService()
        # Just verify the method exists and is callable
        assert callable(service.stream_agent)

    def test_reset_conversation(self):
        """reset_conversation generates new thread_id."""
        service = CodingAgentService()
        old_thread = service.thread_id
        service.reset_conversation()
        assert service.thread_id != old_thread


class TestCodingControllerIntegration:
    """Integration tests for CodingController (without full LLM)."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_controller_accepts_injected_service(self):
        """Controller accepts injected service."""
        service = CodingAgentService()
        controller = CodingController(service=service)
        assert controller._service is service

    def test_send_message_rejects_when_running(self):
        """send_message returns False if agent already running."""
        controller = CodingController()
        controller._service._is_running = True
        result = controller.send_message("test")
        assert result is False

    def test_cancel_calls_service_cancel(self):
        """cancel() calls service.cancel()."""
        controller = CodingController()
        controller.cancel()
        assert controller._service._cancel_event.is_set()

    def test_start_new_conversation(self):
        """start_new_conversation resets thread_id."""
        controller = CodingController()
        old_thread = controller._service.thread_id
        controller.start_new_conversation()
        assert controller._service.thread_id != old_thread

    def test_controller_properties(self):
        """Controller property getters work."""
        controller = CodingController()
        # Test is_running property
        assert isinstance(controller.is_running, bool)
        # Test get_history method
        history = controller.get_history()
        assert isinstance(history, list)

    def test_controller_set_app_and_view(self):
        """set_app and set_view store references."""
        controller = CodingController()
        mock_app = object()
        mock_view = object()
        controller.set_app(mock_app)
        controller.set_view(mock_view)
        assert controller._app is mock_app
        assert controller._view is mock_view

    def test_controller_close(self):
        """close() calls service.cancel()."""
        controller = CodingController()
        controller.close()
        assert controller._service._cancel_event.is_set()