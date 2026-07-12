"""Unit tests for the TUI framework base classes (feature_012.tui_framework).

Covers BaseAgentXScreen, BaseAgentXModalScreen, BaseAgentXApp,
BaseScreenAdapter, register_partner, and the reusable widgets.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from textual.app import App, ComposeResult
from textual.screen import ModalScreen, Screen
from textual.widgets import Footer, Header, Input, Static

from agentx.ui.tui.framework import (
    BaseAgentXApp,
    BaseAgentXModalScreen,
    BaseAgentXScreen,
    BaseScreenAdapter,
    ChatMessage,
    CommandInput,
    MenuGrid,
    NavigationMixin,
    SessionStatusBar,
    WelcomePanel,
    register_partner,
)


# ---------------------------------------------------------------------------
# Helpers — concrete subclasses for testing
# ---------------------------------------------------------------------------


class _DemoScreen(BaseAgentXScreen):
    """Concrete screen exercising the base hooks."""

    DEFAULT_CSS = ""  # keep minimal

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield from self.compose_chrome()


class _DemoModal(BaseAgentXModalScreen[str]):
    DEFAULT_CSS = ""

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield Static("modal")


# ===========================================================================
# BaseAgentXScreen
# ===========================================================================


class TestBaseAgentXScreen:
    def test_init_stores_controller(self):
        ctrl = object()
        s = _DemoScreen(ctrl)
        assert s._controller is ctrl

    def test_init_default_controller_none(self):
        s = _DemoScreen()
        assert s._controller is None

    def test_set_controller(self):
        s = _DemoScreen()
        ctrl = object()
        s.set_controller(ctrl)
        assert s._controller is ctrl

    def test_is_textual_screen(self):
        assert issubclass(BaseAgentXScreen, Screen)

    def test_has_navigation_mixin(self):
        """BaseAgentXScreen includes NavigationMixin (navigate_to_child)."""
        assert issubclass(BaseAgentXScreen, NavigationMixin)
        assert hasattr(BaseAgentXScreen, "navigate_to_child")

    @patch("textual.widget.Widget.app", new_callable=PropertyMock)
    def test_action_quit_calls_app_exit(self, mock_app):
        s = _DemoScreen.__new__(_DemoScreen)
        mock_app.return_value = MagicMock()
        s.action_quit()
        mock_app.return_value.exit.assert_called_once()

    @patch("textual.widget.Widget.app", new_callable=PropertyMock)
    def test_action_back_calls_pop_screen(self, mock_app):
        s = _DemoScreen.__new__(_DemoScreen)
        mock_app.return_value = MagicMock()
        s.action_back()
        mock_app.return_value.pop_screen.assert_called_once()

    def test_action_back_swallows_error(self):
        """action_back must not raise if pop_screen fails (empty stack)."""
        s = _DemoScreen.__new__(_DemoScreen)
        with patch.object(type(s), "app", new_callable=PropertyMock) as mock_app:
            mock_app.return_value = MagicMock()
            mock_app.return_value.pop_screen.side_effect = RuntimeError("empty")
            s.action_back()  # must not raise

    def test_compose_chrome_yields_header_and_footer(self):
        s = _DemoScreen.__new__(_DemoScreen)
        items = list(s.compose_chrome())
        assert any(isinstance(i, Header) for i in items)
        assert any(isinstance(i, Footer) for i in items)

    def test_compose_chrome_without_footer(self):
        s = _DemoScreen.__new__(_DemoScreen)
        items = list(s.compose_chrome(footer=False))
        assert any(isinstance(i, Header) for i in items)
        assert not any(isinstance(i, Footer) for i in items)

    def test_safe_notify_no_crash_without_app(self):
        """safe_notify must swallow NoActiveAppError (no app context)."""
        s = _DemoScreen.__new__(_DemoScreen)
        # No notify mock — Textual would raise; the wrapper swallows it.
        s.safe_notify("hello")  # must not raise

    def test_safe_notify_calls_notify_when_mocked(self):
        s = _DemoScreen.__new__(_DemoScreen)
        s.notify = MagicMock()
        s.safe_notify("hi", severity="warning", timeout=9)
        s.notify.assert_called_once_with("hi", severity="warning", timeout=9)

    def test_safe_error_uses_error_severity_none_timeout(self):
        s = _DemoScreen.__new__(_DemoScreen)
        s.notify = MagicMock()
        s.safe_error("boom")
        s.notify.assert_called_once()
        kwargs = s.notify.call_args[1]
        assert kwargs["severity"] == "error"
        assert kwargs["timeout"] is None

    def test_safe_update_returns_false_when_widget_missing(self):
        s = _DemoScreen.__new__(_DemoScreen)
        s.query_one = MagicMock(side_effect=Exception("no match"))
        assert s.safe_update("missing", "text") is False

    def test_safe_update_returns_true_and_updates(self):
        s = _DemoScreen.__new__(_DemoScreen)
        widget = MagicMock()
        s.query_one = MagicMock(return_value=widget)
        assert s.safe_update("status", "hello") is True
        widget.update.assert_called_once_with("hello")

    def test_safe_log_no_crash_when_missing(self):
        s = _DemoScreen.__new__(_DemoScreen)
        s.query_one = MagicMock(side_effect=Exception("no match"))
        s.safe_log("log", "line")  # must not raise

    def test_handle_input_submitted_empty_returns_false(self):
        s = _DemoScreen.__new__(_DemoScreen)
        inp = MagicMock()
        assert s.handle_input_submitted("   ", inp) is False
        inp.value = ""  # not cleared on empty
        assert inp.value == ""

    def test_handle_input_submitted_nonempty_clears_and_returns_true(self):
        s = _DemoScreen.__new__(_DemoScreen)
        inp = MagicMock()
        assert s.handle_input_submitted("hello", inp) is True
        assert inp.value == ""


# ===========================================================================
# BaseAgentXModalScreen
# ===========================================================================


class TestBaseAgentXModalScreen:
    def test_is_modal_screen_subclass(self):
        assert issubclass(BaseAgentXModalScreen, ModalScreen)

    def test_is_base_screen_subclass(self):
        assert issubclass(BaseAgentXModalScreen, BaseAgentXScreen)

    def test_init_sets_dismissed_false(self):
        m = _DemoModal()
        assert m._dismissed is False

    def test_init_stores_controller(self):
        ctrl = object()
        m = _DemoModal(ctrl)
        assert m._controller is ctrl

    def test_mro_modal_before_screen(self):
        """ModalScreen must appear in the MRO so dismiss() is available."""
        names = [c.__name__ for c in BaseAgentXModalScreen.__mro__]
        assert "ModalScreen" in names
        assert "BaseAgentXScreen" in names
        assert names.index("ModalScreen") < names.index("Screen")

    def test_safe_dismiss_guards_double_dismiss(self):
        """safe_dismiss must call dismiss exactly once."""

        class _App(App):
            def on_mount(self) -> None:
                self.push_screen(_DemoModal())

        async def run() -> int:
            app = _App()
            async with app.run_test() as pilot:
                modal = app.screen
                assert isinstance(modal, _DemoModal)
                modal.safe_dismiss("first")
                modal.safe_dismiss("second")  # should be a no-op
                await pilot.pause()
                return modal._dismissed

        dismissed = asyncio.run(run())
        assert dismissed is True


# ===========================================================================
# register_partner
# ===========================================================================


class _IDemoPartner(ABC):
    @abstractmethod
    def do_thing(self) -> None: ...


class TestRegisterPartner:
    def test_makes_screen_virtual_subclass(self):
        register_partner(_IDemoPartner, _DemoScreen)
        assert issubclass(_DemoScreen, _IDemoPartner)
        assert isinstance(_DemoScreen(), _IDemoPartner)

    def test_idempotent(self):
        register_partner(_IDemoPartner, _DemoScreen)
        register_partner(_IDemoPartner, _DemoScreen)  # second call no-op
        assert issubclass(_DemoScreen, _IDemoPartner)


# ===========================================================================
# BaseAgentXApp
# ===========================================================================


class TestBaseAgentXApp:
    def test_is_textual_app(self):
        from textual.app import App as _App

        assert issubclass(BaseAgentXApp, _App)

    def test_init_stores_controller(self):
        ctrl = object()

        class _A(BaseAgentXApp):
            def make_initial_screen(self):  # type: ignore[override]
                return _DemoScreen()

        a = _A(ctrl)
        assert a._controller is ctrl

    def test_make_initial_screen_not_implemented_by_default(self):
        a = BaseAgentXApp()
        with pytest.raises(NotImplementedError):
            a.make_initial_screen()

    def test_css_contains_base_styles(self):
        assert "Screen" in BaseAgentXApp.CSS
        assert "Header" in BaseAgentXApp.CSS
        assert "Footer" in BaseAgentXApp.CSS


# ===========================================================================
# BaseScreenAdapter
# ===========================================================================


class TestBaseScreenAdapter:
    def test_init_stores_controller_and_none_screen(self):
        ctrl = object()
        a = BaseScreenAdapter(ctrl)
        assert a._controller is ctrl
        assert a._screen is None

    def test_set_screen(self):
        a = BaseScreenAdapter(object())
        scr = MagicMock()
        a.set_screen(scr)
        assert a._screen is scr

    def test_show_is_noop(self):
        a = BaseScreenAdapter(object())
        assert a.show() is None  # no-op


# ===========================================================================
# Reusable widgets
# ===========================================================================


class TestWidgets:
    def test_session_status_bar_defaults(self):
        bar = SessionStatusBar()
        assert bar.session_name == "default"
        assert bar.current_screen == "Main"

    def test_welcome_panel_compose(self):
        items = list(WelcomePanel().compose())
        assert len(items) == 2
        assert all(isinstance(i, Static) for i in items)

    def test_menu_grid_has_seven_buttons(self):
        from textual.widgets import Button

        items = list(MenuGrid().compose())
        assert len(items) == 8
        assert all(isinstance(i, Button) for i in items)
        ids = [b.id for b in items]
        assert "btn-chat" in ids and "btn-rag" in ids and "btn-models" in ids and "btn-react" in ids and "btn-coding" in ids

    def test_command_input_compose(self):
        items = list(CommandInput().compose())
        assert len(items) == 2  # Label + Input

    def test_chat_message_role_class(self):
        m = ChatMessage("hi", "user")
        assert m.role == "user"
        assert "user" in m.classes

    def test_chat_message_no_timestamp(self):
        """ChatMessage no longer accepts timestamp (feature_018 simplification).

        Feature_018 removes timestamps for cleaner UI. ChatMessage now only
        accepts (message, role) - 2 positional arguments.
        """
        m = ChatMessage("hello", "assistant")
        assert m.role == "assistant"
        assert "assistant" in m.classes
        assert not hasattr(m, 'timestamp')  # No timestamp attribute

    def test_chat_message_user_has_you_prefix(self):
        """User messages display with 'You:' prefix."""
        m = ChatMessage("hello", "user")
        # The display text should include "You:" prefix
        assert "You:" in str(m.content)

    def test_chat_message_assistant_has_assistant_prefix(self):
        """Assistant messages display with 'Assistant:' prefix."""
        m = ChatMessage("hello", "assistant")
        # The display text should include "Assistant:" prefix
        assert "Assistant:" in str(m.content)
