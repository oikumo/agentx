"""AXR-06 durable regression: provider dispatch follows selection (package 2).

Reconstructs the inline regression proof from
``sandbox/consistency_enforcement/round_003_package_02_provider_dispatch.md``
§Result (strategy A: per-request (llm, provider) binding + lazy refresh in
``chat_controller.py`` — ``_llm_provider_id`` snapshot + ``_ensure_llm_current``
+ per-request capture in ``process_user_message`` + ``_format_chat_error(exc,
provider_id, provider_name)`` — plus best-effort ``refresh_provider()`` on the
``show_chat`` reopen path, history + conversation ID untouched) as durable tests.

Acceptance (round_003 §1, from round_001 §AXR-06 Regression check): open chat
on A → select B → reopen existing chat → next request reaches **only B**;
repeat without reopen; B-construction failure → explicit failure naming B,
**no silent fallback** to A; errors name the provider used/attempted for that
request (never the registry's newer selection); refresh preserves conversation
ID + history (AXR-07 link — deeper persistence assertions stay in AXR-07's own
file; only identity/continuity is asserted here per D5).

Replaces the AXR-06 assertions of
``sandbox/consistency_enforcement/round_001_review_probes.py``::
``test_axr06_axr07_console_provider_and_persistence`` (observation probe retired
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


def _last_chat_error(chat):
    """Most recent error surfaced on the (mock) chat view."""
    shown = chat.view.show_message_chat_error.call_args_list
    assert shown, "expected an error to be surfaced on the chat view"
    return shown[-1][0][0]


class TestAxr06ProviderDispatch:
    def test_switch_and_reopen_next_request_reaches_only_new_provider(
        self, tmp_path, monkeypatch
    ):
        from langchain_core.messages import SystemMessage
        from agentx.model.chat import ChatHistoryRepository
        from agentx.ui.screens.models.models_controller import ModelsController

        main, repository, registry, calls = _wire(tmp_path, monkeypatch)
        main.show_chat()
        chat, _ = main.get_chat_controller()

        # Round 1 on the default provider (A = openrouter).
        assert chat.process_user_message("first message")
        assert calls == ["openrouter"]
        conv_id = chat.current_conversation_id
        assert conv_id is not None
        history_len_after_round_1 = len(chat.history)

        # Switch to B, then reopen: same controller, history kept (D5).
        assert ModelsController(registry).select_provider("ollama")
        main.show_chat()  # reopen → best-effort refresh_provider(), no reset
        assert main.get_chat_controller()[0] is chat
        assert chat.current_conversation_id == conv_id
        assert len(chat.history) == history_len_after_round_1

        # Next request reaches ONLY B.
        assert chat.process_user_message("second message")
        assert calls == ["openrouter", "ollama"]
        assert chat.current_conversation_id == conv_id  # still one conversation
        assert isinstance(chat.history[0], SystemMessage)
        assert len(chat.history) == history_len_after_round_1 + 2

        # Both rounds stored exactly once under the single conversation.
        _, messages = ChatHistoryRepository(
            str(tmp_path / "chat.db")
        ).get_conversation_with_messages(conv_id)
        assert [m.content for m in messages] == [
            "first message",
            "answer-1",
            "second message",
            "answer-2",
        ]

    def test_switch_without_reopen_next_request_reaches_only_new_provider(
        self, tmp_path, monkeypatch
    ):
        from agentx.ui.screens.models.models_controller import ModelsController

        main, repository, registry, calls = _wire(tmp_path, monkeypatch)
        main.show_chat()
        chat, _ = main.get_chat_controller()

        # Switch with NO reopen: the message-time lazy refresh still re-binds.
        assert ModelsController(registry).select_provider("ollama")
        assert main.get_chat_controller()[0] is chat
        assert chat.process_user_message("hello on ollama")
        assert calls == ["ollama"]  # only B — stale openrouter never served
        assert chat.current_conversation_id is not None
        assert len(chat.history) == 3  # system prompt + the single round

    def test_failed_construction_fails_explicitly_naming_attempted_provider(
        self, tmp_path, monkeypatch
    ):
        from agentx.ui.screens.models.models_controller import ModelsController

        main, repository, registry, calls = _wire(tmp_path, monkeypatch)
        main.show_chat()
        chat, _ = main.get_chat_controller()

        assert ModelsController(registry).select_provider("ollama")

        # B cannot be built: every construction attempt raises. A silent
        # fallback to A must blow up loudly instead.
        working_create = registry.create_current_llm

        def fail_on_ollama():
            if registry.get_current_id() == "ollama":
                raise RuntimeError("synthetic Ollama construction failure")
            raise AssertionError("must not fall back to another provider")

        monkeypatch.setattr(registry, "create_current_llm", fail_on_ollama)
        chat.view.show_message_chat_error.reset_mock()

        assert chat.process_user_message("hello") is True
        err = _last_chat_error(chat)
        assert "Ollama" in err  # names the ATTEMPTED provider ...
        assert "OpenRouter" not in err  # ... no silent fallback, no mislabel
        assert "OLLAMA base URL" in err  # actionable hint follows the attempt
        assert calls == []  # zero calls to A (or anyone)
        assert chat.current_conversation_id is None  # failed round stores nothing
        assert len(chat.history) == 1  # human message rolled back, prompt kept

        # Transient failure wedges nothing: once B builds, the retry serves B.
        monkeypatch.setattr(registry, "create_current_llm", working_create)
        assert chat.process_user_message("hello again")
        assert calls == ["ollama"]

    def test_streaming_error_names_captured_provider_not_current_selection(
        self, tmp_path, monkeypatch
    ):
        from agentx.ui.screens.models.models_controller import ModelsController

        main, repository, registry, calls = _wire(tmp_path, monkeypatch)
        main.show_chat()
        chat, _ = main.get_chat_controller()
        assert registry.get_current_id() == "openrouter"

        # Round 1 succeeds on A.
        assert chat.process_user_message("hello on A")
        assert calls == ["openrouter"]
        conv_id = chat.current_conversation_id

        # The NEXT request captures A, but the registry moves to B mid-stream
        # before the failure surfaces (in-flight requests keep their capture;
        # only the NEXT request re-binds — residual by design, round_003 §Result).
        def flaky(history):
            assert ModelsController(registry).select_provider("ollama")
            raise RuntimeError("synthetic streaming failure")
            yield  # pragma: no cover

        monkeypatch.setattr(chat.llm, "stream", flaky)
        chat.view.show_message_chat_error.reset_mock()

        assert chat.process_user_message("fails mid-flight") is True
        assert registry.get_current_id() == "ollama"  # registry HAS moved on
        err = _last_chat_error(chat)
        assert "OpenRouter" in err  # names the captured (used) provider ...
        assert "Ollama" not in err  # ... not the current selection
        assert "OPENROUTER_API_KEY" in err  # hint follows the capture, not B
        assert calls == ["openrouter"]  # failed round streamed nowhere new
        assert chat.current_conversation_id == conv_id  # failed round stores nothing
        assert len(chat.history) == 3  # system prompt + round 1 only

        # And the NEXT request after the move re-binds to B.
        assert chat.process_user_message("after the move")
        assert calls == ["openrouter", "ollama"]
        assert chat.current_conversation_id == conv_id
        assert len(chat.history) == 5
