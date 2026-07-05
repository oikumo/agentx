"""Integration tests for NavigationMixin.navigate_to_child (feature_012.tui_framework)."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Static

from agentx.ui.tui.framework import (
    BaseAgentXScreen,
    BaseScreenAdapter,
    NavigationMixin,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _ChildScreen(BaseAgentXScreen):
    DEFAULT_CSS = ""

    def __init__(self, controller=None):
        super().__init__(controller)
        self.constructed_with = controller

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield Static("child")


class _HostScreen(BaseAgentXScreen):
    DEFAULT_CSS = ""

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield Static("host")


class _DemoAdapter(BaseScreenAdapter):
    """Trivial adapter to verify set_screen wiring."""


# ===========================================================================
# navigate_to_child — happy paths (real Textual app via pilot)
# ===========================================================================


class TestNavigateToChildPush:
    def test_pushes_child_screen(self):
        class _App(App):
            def on_mount(self) -> None:
                self.push_screen(_HostScreen())

        async def run() -> str:
            app = _App()
            async with app.run_test() as pilot:
                host = app.screen
                host.navigate_to_child(_ChildScreen)
                await pilot.pause()
                return type(app.screen).__name__

        assert asyncio.run(run()) == "_ChildScreen"

    def test_child_receives_controller_from_getter(self):
        ctrl = object()

        class _App(App):
            def on_mount(self) -> None:
                self.push_screen(_HostScreen())

        async def run() -> object:
            app = _App()
            async with app.run_test() as pilot:
                host = app.screen
                host.navigate_to_child(
                    _ChildScreen,
                    controller=ctrl,
                    getter=lambda c: c,  # return the controller itself
                )
                await pilot.pause()
                return app.screen.constructed_with

        assert asyncio.run(run()) is ctrl

    def test_setup_callback_invoked_with_controller(self):
        ctrl = MagicMock()
        setup_calls: list = []

        class _App(App):
            def on_mount(self) -> None:
                self.push_screen(_HostScreen())

        async def run() -> None:
            app = _App()
            async with app.run_test() as pilot:
                host = app.screen
                host.navigate_to_child(
                    _ChildScreen,
                    controller=ctrl,
                    setup=lambda c: setup_calls.append(c),
                )
                await pilot.pause()

        asyncio.run(run())
        assert setup_calls == [ctrl]

    def test_getter_tuple_wires_adapter(self):
        """When getter returns (controller, adapter), set_screen is called."""
        ctrl = MagicMock()
        adapter = _DemoAdapter(ctrl)
        assert adapter._screen is None

        class _App(App):
            def on_mount(self) -> None:
                self.push_screen(_HostScreen())

        async def run() -> bool:
            app = _App()
            async with app.run_test() as pilot:
                host = app.screen
                host.navigate_to_child(
                    _ChildScreen,
                    controller=ctrl,
                    getter=lambda c: (c, adapter),
                )
                await pilot.pause()
                return adapter._screen is not None

        assert asyncio.run(run()) is True

    def test_adapter_view_passed_directly_is_wired(self):
        ctrl = MagicMock()
        adapter = _DemoAdapter(ctrl)

        class _App(App):
            def on_mount(self) -> None:
                self.push_screen(_HostScreen())

        async def run() -> bool:
            app = _App()
            async with app.run_test() as pilot:
                host = app.screen
                host.navigate_to_child(
                    _ChildScreen,
                    controller=ctrl,
                    adapter_view=adapter,
                )
                await pilot.pause()
                return adapter._screen is not None

        assert asyncio.run(run()) is True

    def test_no_controller_still_pushes_with_none(self):
        class _App(App):
            def on_mount(self) -> None:
                self.push_screen(_HostScreen())

        async def run() -> object:
            app = _App()
            async with app.run_test() as pilot:
                host = app.screen
                host.navigate_to_child(_ChildScreen)  # no controller
                await pilot.pause()
                return app.screen.constructed_with

        assert asyncio.run(run()) is None


# ===========================================================================
# navigate_to_child — error handling
# ===========================================================================


class TestNavigateToChildErrors:
    def test_setup_error_does_not_push(self):
        """If setup raises, the child is NOT pushed and an error is notified."""
        pushed: list = []

        class _App(App):
            def on_mount(self) -> None:
                self.push_screen(_HostScreen())

        async def run() -> str:
            app = _App()
            async with app.run_test() as pilot:
                host = app.screen
                original_push = app.push_screen
                app.push_screen = lambda s: pushed.append(s)  # type: ignore
                host.navigate_to_child(
                    _ChildScreen,
                    controller=MagicMock(),
                    setup=lambda c: (_ for _ in ()).throw(RuntimeError("boom")),
                )
                app.push_screen = original_push  # restore
                await pilot.pause()
                return type(app.screen).__name__

        # Still on the host screen (child not pushed).
        assert asyncio.run(run()) == "_HostScreen"
        assert pushed == []

    def test_no_app_context_does_not_crash(self):
        """Without an app context, navigate_to_child notifies safely (no crash)."""
        host = _HostScreen.__new__(_HostScreen)
        host.notify = MagicMock()
        host.navigate_to_child(_ChildScreen)  # no app → safe notify path
        host.notify.assert_called()  # an "no app context" notification


# ===========================================================================
# NavigationMixin standalone
# ===========================================================================


class TestNavigationMixin:
    def test_mixin_provides_navigate_to_child(self):
        assert hasattr(NavigationMixin, "navigate_to_child")
        assert callable(NavigationMixin.navigate_to_child)
