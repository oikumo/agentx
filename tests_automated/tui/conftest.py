"""Shared fixtures/helpers for the TUI Pilot end-to-end tests.

These tests drive the *real* ``TUIApplication`` through Textual's ``Pilot``
harness. We deliberately avoid ``pytest-asyncio`` (not a project dependency)
and instead expose a small ``drive()`` helper that runs an async scenario with
``asyncio.run`` — matching the convention in ``tests/tui/test_main_screen.py``.
"""

from __future__ import annotations

import asyncio
import os

import pytest


def drive(scenario):
    """Run an async Pilot ``scenario`` coroutine to completion.

    Usage::

        async def scenario():
            app = TUIApplication(controller)
            async with app.run_test() as pilot:
                ...
                return True

        assert drive(scenario())
    """
    return asyncio.run(scenario())


class RecordingController:
    """Minimal honest stand-in for ``MainController`` (``IMainViewPartner``).

    The Main TUI screen only calls ``run_command`` on its controller; we record
    every command so tests can assert the View → Controller wiring end-to-end.
    The ``print_*`` no-ops exist so the object stays substitutable for the real
    partner if other code paths reach for them.
    """

    def __init__(self) -> None:
        self.commands: list[str] = []

    def run_command(self, user_input: str) -> None:
        self.commands.append(user_input)

    def print_message(self, message: str) -> None:  # pragma: no cover - no-op
        pass

    def print_error_message(self, message: str) -> None:  # pragma: no cover
        pass

    def print_warring_message(self, message: str) -> None:  # pragma: no cover
        pass

    def print_response(self, message: str) -> None:  # pragma: no cover
        pass

    def print_response_error(self, message: str) -> None:  # pragma: no cover
        pass


@pytest.fixture
def controller() -> RecordingController:
    """A fresh recording controller per test."""
    return RecordingController()


@pytest.fixture(autouse=True)
def _dummy_api_key():
    """Provide a deterministic dummy key.

    Navigating to the Chat screen constructs an LLM provider. Construction is
    lazy (no network), but a present key keeps it deterministic and avoids any
    interactive prompt. We restore the previous value afterwards.
    """
    previous = os.environ.get("OPENROUTER_API_KEY")
    os.environ["OPENROUTER_API_KEY"] = previous or "test-dummy-key"
    yield
    if previous is None:
        os.environ.pop("OPENROUTER_API_KEY", None)
    else:
        os.environ["OPENROUTER_API_KEY"] = previous
