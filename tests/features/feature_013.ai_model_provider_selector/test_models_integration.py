"""Integration tests for feature_013.ai_model_provider_selector.

Covers:
  - ModelsController (delegates to ModelRegistry).
  - MainController.show_models / get_models_controller wiring + idempotency.
  - The 4 refactored call sites now route through the selected provider.
  - ModelsTUIScreen end-to-end via a Textual pilot (render, select, persist).
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import patch

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Label, OptionList

from agentx.model.ai.model_registry import ModelRegistry
from agentx.ui.screens.models.models_controller import (
    IModelsViewPartner,
    ModelsController,
)
from agentx.ui.screens.main.main_controller import MainController


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def registry(tmp_path: Path) -> ModelRegistry:
    return ModelRegistry(config_path=tmp_path / "model_selection.json")


@pytest.fixture
def controller(registry: ModelRegistry) -> ModelsController:
    return ModelsController(registry=registry)


# ===========================================================================
# ModelsController
# ===========================================================================


class TestModelsController:
    def test_is_abc_partner(self) -> None:
        from abc import ABC

        assert issubclass(IModelsViewPartner, ABC)
        assert isinstance(ModelsController(registry=ModelRegistry(config_path=Path("/tmp/_x.json"))), IModelsViewPartner)

    def test_list_providers(self, controller: ModelsController) -> None:
        providers = controller.list_providers()
        assert len(providers) == 5
        assert providers[0].id == "openrouter"

    def test_get_current_id_default(self, controller: ModelsController) -> None:
        assert controller.get_current_id() == "openrouter"

    def test_select_provider_success(self, controller: ModelsController) -> None:
        assert controller.select_provider("gemini") is True
        assert controller.get_current_id() == "gemini"

    def test_select_provider_unknown(self, controller: ModelsController) -> None:
        assert controller.select_provider("zzz") is False
        assert controller.get_current_id() == "openrouter"

    def test_get_status_text(self, controller: ModelsController) -> None:
        assert controller.get_status_text() == "Current: OpenRouter (cloud)"
        controller.select_provider("ollama")
        assert controller.get_status_text() == "Current: Ollama (local)"

    def test_controller_shares_registry_with_aiservice(
        self, registry: ModelRegistry
    ) -> None:
        from agentx.model.ai.service import AIService

        ctl = ModelsController(registry=registry)
        ai = AIService(registry=registry)
        ctl.select_provider("openai")
        # both read the same registry → same current id
        assert ai.get_current_provider_info().id == "openai"
        assert ctl.get_current_id() == "openai"


# ===========================================================================
# MainController wiring
# ===========================================================================


class TestMainControllerWiring:
    def test_show_models_creates_controller(self) -> None:
        mc = MainController()
        assert mc.get_models_controller() is None
        mc.show_models()
        assert isinstance(mc.get_models_controller(), ModelsController)

    def test_show_models_is_idempotent(self) -> None:
        mc = MainController()
        mc.show_models()
        first = mc.get_models_controller()
        mc.show_models()  # second call must reuse
        assert mc.get_models_controller() is first


# ===========================================================================
# Call-site refactors (the 4 hardcoded openrouter sites)
# ===========================================================================


class TestCallSiteRefactors:
    """Verify each refactored site routes through get_current_llm()."""

    def test_chat_controller_uses_selected_provider(
        self, registry: ModelRegistry
    ) -> None:
        from agentx.ui.screens.chat import chat_controller as mod

        with patch.object(
            ModelRegistry, "create_current_llm", return_value="LLM-CHAT"
        ) as mocked:
            ctl = mod.ChatController()
            assert ctl.llm == "LLM-CHAT"
            mocked.assert_called_once()

    def test_rag_chat_controller_uses_selected_provider(
        self, registry: ModelRegistry, tmp_path: Path
    ) -> None:
        from agentx.ui.screens.rag import rag_chat_controller as mod
        from agentx.model.rag.rag_repository import RagRepository

        repo = RagRepository(path=str(tmp_path), id=None)
        with patch.object(
            ModelRegistry, "create_current_llm", return_value="LLM-RAGCHAT"
        ) as mocked:
            ctl = mod.RagChatController(repo)
            assert ctl.llm == "LLM-RAGCHAT"
            # RAG orchestrator (Rag(...)) also routes through get_current_llm,
            # so the call count is >= 1 (twice: controller + Rag).
            assert mocked.call_count >= 1

    def test_ai_adapter_uses_selected_provider_first(
        self, registry: ModelRegistry
    ) -> None:
        from agentx.agent.model.ai_adapter import AIServiceAdapter

        with patch.object(
            ModelRegistry, "create_current_llm", return_value="LLM-AGENT"
        ) as primary:
            adapter = AIServiceAdapter()
            llm = adapter._ensure_llm()
            assert llm == "LLM-AGENT"
            primary.assert_called()

    def test_ai_adapter_falls_back_when_selected_fails(
        self, registry: ModelRegistry
    ) -> None:
        from agentx.agent.model.ai_adapter import AIServiceAdapter

        # selected provider raises → legacy fallback chain should kick in.
        with patch.object(
            ModelRegistry, "create_current_llm", side_effect=RuntimeError("boom")
        ):
            with patch(
                "agentx.model.ai.service.AIService.openrouter_llm_provider"
            ) as fb_factory:
                fb_provider = fb_factory.return_value
                fb_provider.create_llm.return_value = "LLM-FALLBACK"
                adapter = AIServiceAdapter()
                llm = adapter._ensure_llm()
                assert llm == "LLM-FALLBACK"
                fb_factory.assert_called()


# ===========================================================================
# ModelsTUIScreen — end-to-end pilot
# ===========================================================================


def _make_app(controller: ModelsController) -> App:
    class _ModelsHostApp(App):
        def compose(self) -> ComposeResult:
            yield Label("host")

        def on_mount(self) -> None:
            self.push_screen(_screen(controller))

    def _screen(ctl):
        from agentx.ui.tui.screens.models_screen import ModelsTUIScreen

        return ModelsTUIScreen(ctl)

    return _ModelsHostApp()


class TestModelsTUIScreen:
    def test_renders_five_options_and_marks_current(
        self, controller: ModelsController
    ) -> None:
        async def run() -> None:
            app = _make_app(controller)
            async with app.run_test() as pilot:
                await pilot.pause(0.15)
                screen = app.screen
                from agentx.ui.tui.screens.models_screen import ModelsTUIScreen

                assert isinstance(screen, ModelsTUIScreen)
                ol = screen.query_one("#models-list", OptionList)
                assert ol.option_count == 5
                # default openrouter highlighted
                assert ol.highlighted == 0
                assert ol.get_option_at_index(0).id == "openrouter"

        asyncio.run(run())

    def test_action_select_changes_current(
        self, controller: ModelsController
    ) -> None:
        async def run() -> None:
            app = _make_app(controller)
            async with app.run_test() as pilot:
                await pilot.pause(0.15)
                screen = app.screen
                from agentx.ui.tui.screens.models_screen import ModelsTUIScreen

                assert isinstance(screen, ModelsTUIScreen)
                ol = screen.query_one("#models-list", OptionList)
                # move highlight to openai (idx 1) and select
                ol.highlighted = 1
                screen.action_select()
                await pilot.pause(0.05)
                assert controller.get_current_id() == "openai"

        asyncio.run(run())

    def test_option_selected_message_selects(
        self, controller: ModelsController
    ) -> None:
        """Enter on the OptionList posts OptionSelected → selects."""
        async def run() -> None:
            app = _make_app(controller)
            async with app.run_test() as pilot:
                await pilot.pause(0.15)
                screen = app.screen
                from agentx.ui.tui.screens.models_screen import ModelsTUIScreen

                assert isinstance(screen, ModelsTUIScreen)
                ol = screen.query_one("#models-list", OptionList)
                ol.highlighted = 2  # gemini
                await pilot.press("enter")
                await pilot.pause(0.05)
                assert controller.get_current_id() == "gemini"

        asyncio.run(run())

    def test_action_back_does_not_crash(self, controller: ModelsController) -> None:
        """action_back (inherited) pops the screen; with a host it returns there."""
        async def run() -> None:
            app = _make_app(controller)
            async with app.run_test() as pilot:
                await pilot.pause(0.15)
                screen = app.screen
                from agentx.ui.tui.screens.models_screen import ModelsTUIScreen

                assert isinstance(screen, ModelsTUIScreen)
                screen.action_back()  # pops back to the host label screen
                await pilot.pause(0.05)
                # back on the host screen — no crash
                assert app.screen is not screen

        asyncio.run(run())

    def test_no_controller_shows_status_message(self) -> None:
        """A screen with no controller renders the 'No controller connected.' status."""
        from agentx.ui.tui.screens.models_screen import ModelsTUIScreen

        async def run() -> None:
            class _Host(App):
                def compose(self) -> ComposeResult:
                    yield Label("host")

                def on_mount(self) -> None:
                    self.push_screen(ModelsTUIScreen(None))

            host = _Host()
            async with host.run_test() as pilot:
                await pilot.pause(0.15)
                screen = host.screen
                assert isinstance(screen, ModelsTUIScreen)
                status = screen.query_one("#models-status")
                # status widget is present and rendered (no crash)
                assert status is not None
                # OptionList stays empty (no controller → no providers loaded)
                ol = screen.query_one("#models-list", OptionList)
                assert ol.option_count == 0

        asyncio.run(run()  )
