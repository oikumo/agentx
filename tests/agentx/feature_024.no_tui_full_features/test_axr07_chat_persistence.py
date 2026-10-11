"""AXR-07 durable regression: console chats persist (agentx_1_0_0 package 6).

Acceptance (round_007, from round_001 §AXR-07 Regression check): drive the
actual console command entry with controlled input and a fake LLM. Complete a
message, exit and reopen chat in the same process, then complete another.
One retained conversation ID, preserved prior history, exactly one system
prompt in model context, exactly one stored copy of each completed
user/assistant message; reconstructed repository retrieves both rounds.
Reopen must never start a new conversation (the history-loss defect).

Replaces the AXR-07 assertions of
sandbox/consistency_enforcement/round_001_review_probes.py::
test_axr06_axr07_console_provider_and_persistence (observation probe retired
per D4 — never gated in CI). All fixtures hermetic (temp DBs, mocked
AIService/LLM, no network).
"""

from __future__ import annotations

import os
import tempfile
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

os.environ["PYTHON_DOTENV_DISABLED"] = "1"
os.environ["LLAMA_CPP_MODELS_CACHE_PATH"] = tempfile.gettempdir()
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def refused(*args, **kwargs):
        raise AssertionError("regression tests must not open network connections")

    monkeypatch.setattr("socket.socket.connect", refused)
    monkeypatch.setattr("socket.create_connection", refused)


def _wire(tmp_path, monkeypatch):
    """Console entry wiring with a fake streaming LLM and a temp chat DB."""
    from agentx.model.ai.model_registry import ModelRegistry
    from agentx.model.ai.service import AIService
    from agentx.model.chat import ChatHistoryRepository
    from agentx.model.session import session
    from agentx.ui.screens.chat import chat_controller
    from agentx.ui.screens.main.main_controller import MainController

    monkeypatch.setattr(
        session, "SESSION_DEFAULT_BASE_DIRECTORY", str(tmp_path / "sessions")
    )
    registry = ModelRegistry(config_path=tmp_path / "selection.json")
    calls = []

    def llm(name):
        def stream(history):
            calls.append(name)
            yield SimpleNamespace(content=f"answer-{len(calls)}")

        return SimpleNamespace(name=name, stream=stream)

    models = {name: llm(name) for name in ("openrouter", "ollama")}
    monkeypatch.setattr(
        registry, "create_current_llm", lambda: models[registry.get_current_id()]
    )
    repository = ChatHistoryRepository(str(tmp_path / "chat.db"))
    monkeypatch.setattr(chat_controller, "AIService", lambda: AIService(registry))
    monkeypatch.setattr(chat_controller, "ChatHistoryRepository", lambda: repository)
    main = MainController(view=Mock(), provider=Mock())
    return main, repository, registry, calls


class TestAxr07ConsoleChatPersists:
    def test_round_persists_and_reopen_retains(self, tmp_path, monkeypatch):
        from langchain_core.messages import SystemMessage
        from agentx.model.chat import ChatHistoryRepository
        from agentx.ui.screens.models.models_controller import ModelsController

        main, repository, registry, calls = _wire(tmp_path, monkeypatch)
        main.show_chat()
        chat, _ = main.get_chat_controller()
        assert ModelsController(registry).select_provider("ollama")
        main.show_chat()  # reopen after provider change (pkg-2 hook)

        # --- round 1 completes: conversation created, single prompt, stored once
        assert chat.process_user_message("first message")
        assert calls == ["ollama"]  # AXR-06 behavior still holds
        assert chat.current_conversation_id is not None  # AXR-07 fixed
        assert isinstance(chat.history[0], SystemMessage)
        assert len(chat.history) == 3  # exactly one system prompt + the round
        convs = ChatHistoryRepository(
            str(tmp_path / "chat.db")
        ).get_recent_conversations()
        assert len(convs) == 1
        conv_id = chat.current_conversation_id

        # --- exit and reopen chat in the same process, then round 2
        main.show_chat()  # reopen — must continue, not reset
        assert chat.process_user_message("second message")
        assert chat.current_conversation_id == conv_id  # same conversation
        assert len(chat.history) == 5  # prior history preserved, 1 system prompt
        assert isinstance(chat.history[0], SystemMessage)

        # --- reconstructed repository retrieves both rounds exactly once
        fresh = ChatHistoryRepository(str(tmp_path / "chat.db"))
        assert len(fresh.get_recent_conversations()) == 1
        result = fresh.get_conversation_with_messages(conv_id)
        assert result is not None
        _, messages = result
        assert [m.role for m in messages] == [
            "user", "assistant", "user", "assistant",
        ]
        assert [m.content for m in messages] == [
            "first message", "answer-1", "second message", "answer-2",
        ]

    def test_chat_and_quit_and_failed_rounds_store_nothing(
        self, tmp_path, monkeypatch
    ):
        from agentx.model.chat import ChatHistoryRepository

        main, repository, registry, calls = _wire(tmp_path, monkeypatch)
        main.show_chat()
        chat, _ = main.get_chat_controller()
        # empty input rejected, no conversation row
        assert chat.process_user_message("   ") is False
        assert chat.current_conversation_id is None
        assert not ChatHistoryRepository(
            str(tmp_path / "chat.db")
        ).get_recent_conversations()

        # failing LLM round → error surfaced, nothing persisted
        def boom(history):
            raise RuntimeError("LLM down")
            yield  # pragma: no cover

        chat.llm = SimpleNamespace(stream=boom)
        assert chat.process_user_message("will fail") is True
        assert chat.current_conversation_id is None
        assert not ChatHistoryRepository(
            str(tmp_path / "chat.db")
        ).get_recent_conversations()

        # next successful round creates the conversation and stores only itself
        def ok(history):
            yield SimpleNamespace(content="recovered")

        chat.llm = SimpleNamespace(stream=ok)
        assert chat.process_user_message("works now") is True
        conv_id = chat.current_conversation_id
        assert conv_id is not None
        _, messages = ChatHistoryRepository(
            str(tmp_path / "chat.db")
        ).get_conversation_with_messages(conv_id)
        assert [m.content for m in messages] == ["works now", "recovered"]
