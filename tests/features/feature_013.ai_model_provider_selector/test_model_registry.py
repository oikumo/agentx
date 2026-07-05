"""Unit tests for the Model layer (feature_013.ai_model_provider_selector).

Covers ``ModelRegistry`` (catalog, selection, JSON persistence, factory) and
``AIService`` delegation.  Each test uses an isolated ``tmp_path`` config so the
shared ``default_registry`` (``~/.agentx/model_selection.json``) is never touched.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentx.model.ai.model_registry import (
    DEFAULT_PROVIDER_ID,
    ModelRegistry,
    ProviderInfo,
    default_registry,
)
from agentx.model.ai.providers import (
    GeminiProvider,
    LlamaCppProvider,
    LLMProvider,
    NvidiaProvider,
    OpenAIProvider,
    OpenRouterProvider,
    OllamaProvider,
)
from agentx.model.ai.service import AIService


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def registry(tmp_path: Path) -> ModelRegistry:
    """A registry backed by an isolated temp config file."""
    return ModelRegistry(config_path=tmp_path / "model_selection.json")


# ===========================================================================
# Provider catalog
# ===========================================================================


class TestProviderCatalog:
    def test_catalog_has_six_providers(self, registry: ModelRegistry) -> None:
        ids = [p.id for p in registry.list_providers()]
        assert ids == ["openrouter", "openai", "gemini", "nvidia", "ollama", "llamacpp"]

    def test_catalog_entries_are_provider_info(self, registry: ModelRegistry) -> None:
        for p in registry.list_providers():
            assert isinstance(p, ProviderInfo)
            assert p.kind in ("cloud", "local")
            assert p.name and p.description
            assert callable(p.factory)

    def test_cloud_vs_local_kinds(self, registry: ModelRegistry) -> None:
        kinds = {p.id: p.kind for p in registry.list_providers()}
        assert kinds["openrouter"] == "cloud"
        assert kinds["openai"] == "cloud"
        assert kinds["gemini"] == "cloud"
        assert kinds["nvidia"] == "cloud"
        assert kinds["ollama"] == "local"
        assert kinds["llamacpp"] == "local"

    def test_factories_return_llm_providers(self, registry: ModelRegistry) -> None:
        for p in registry.list_providers():
            provider = p.factory()
            assert isinstance(provider, LLMProvider)

    def test_default_current_is_openrouter(self, registry: ModelRegistry) -> None:
        assert registry.get_current_id() == DEFAULT_PROVIDER_ID == "openrouter"

    def test_get_provider_known_and_unknown(self, registry: ModelRegistry) -> None:
        assert registry.get_provider("openai") is not None
        assert registry.get_provider("does-not-exist") is None


# ===========================================================================
# New provider subclasses (unification)
# ===========================================================================


class TestUnifiedProviders:
    def test_ollama_provider_is_llm_provider(self) -> None:
        assert isinstance(OllamaProvider(), LLMProvider)

    def test_gemini_provider_is_llm_provider(self) -> None:
        assert isinstance(GeminiProvider(), LLMProvider)

    def test_nvidia_provider_is_llm_provider(self) -> None:
        assert isinstance(NvidiaProvider(), LLMProvider)

    def test_all_existing_providers_still_llm_providers(self) -> None:
        assert isinstance(OpenRouterProvider(), LLMProvider)
        assert isinstance(OpenAIProvider(), LLMProvider)
        assert isinstance(LlamaCppProvider("m.gguf", 2048), LLMProvider)


# ===========================================================================
# NVIDIA provider (ChatNVIDIA wiring)
# ===========================================================================


class TestNvidiaProvider:
    def test_default_model_is_nemotron(self) -> None:
        from agentx.model.ai.model_registry import DEFAULT_NVIDIA_MODEL

        provider = NvidiaProvider()
        assert provider._model_name == DEFAULT_NVIDIA_MODEL
        assert provider._model_name == "nvidia/nemotron-3-ultra-550b-a55b"

    def test_custom_model_passthrough(self) -> None:
        provider = NvidiaProvider(model_name="meta/llama-3.3-70b-instruct")
        assert provider._model_name == "meta/llama-3.3-70b-instruct"

    def test_create_llm_calls_chatnvidia_with_model(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """create_llm constructs a ChatNVIDIA with the configured model.

        Patches the (installed) ``langchain_nvidia_ai_endpoints.ChatNVIDIA``
        attribute so the lazy ``from … import ChatNVIDIA`` inside ``create_llm``
        resolves to the stub — no ``NVIDIA_API_KEY`` needed.
        """
        import langchain_nvidia_ai_endpoints as nv

        calls: dict[str, object] = {}

        class _FakeChatNVIDIA:
            def __init__(self, **kwargs: object) -> None:
                calls.update(kwargs)

        monkeypatch.setattr(nv, "ChatNVIDIA", _FakeChatNVIDIA)

        provider = NvidiaProvider(model_name="nvidia/nemotron-3-ultra-550b-a55b")
        llm = provider.create_llm()
        assert isinstance(llm, _FakeChatNVIDIA)
        assert calls["model"] == "nvidia/nemotron-3-ultra-550b-a55b"


# ===========================================================================
# Selection
# ===========================================================================


class TestSelection:
    def test_select_valid_provider(self, registry: ModelRegistry) -> None:
        assert registry.select("openai") is True
        assert registry.get_current_id() == "openai"

    def test_select_invalid_provider_returns_false(self, registry: ModelRegistry) -> None:
        assert registry.select("nope") is False
        # selection unchanged
        assert registry.get_current_id() == "openrouter"

    def test_select_each_provider(self, registry: ModelRegistry) -> None:
        for pid in ("openrouter", "openai", "gemini", "nvidia", "ollama", "llamacpp"):
            assert registry.select(pid) is True
            assert registry.get_current_id() == pid

    def test_get_current_returns_provider_info(self, registry: ModelRegistry) -> None:
        registry.select("gemini")
        info = registry.get_current()
        assert isinstance(info, ProviderInfo)
        assert info.id == "gemini"
        assert info.name == "Google Gemini"

    def test_invalid_stored_selection_resets_to_default(self, tmp_path: Path) -> None:
        cfg = tmp_path / "model_selection.json"
        cfg.write_text(json.dumps({"selected": "removed-provider"}))
        r = ModelRegistry(config_path=cfg)
        # invalid stored id → silently reset to default
        assert r.get_current_id() == DEFAULT_PROVIDER_ID


# ===========================================================================
# Persistence
# ===========================================================================


class TestPersistence:
    def test_select_writes_json(self, registry: ModelRegistry, tmp_path: Path) -> None:
        registry.select("ollama")
        data = json.loads((tmp_path / "model_selection.json").read_text())
        assert data == {"selected": "ollama"}

    def test_reload_restores_selection(self, tmp_path: Path) -> None:
        cfg = tmp_path / "model_selection.json"
        r1 = ModelRegistry(config_path=cfg)
        r1.select("gemini")
        # fresh registry reading the same file
        r2 = ModelRegistry(config_path=cfg)
        assert r2.get_current_id() == "gemini"

    def test_missing_config_uses_default(self, tmp_path: Path) -> None:
        r = ModelRegistry(config_path=tmp_path / "absent.json")
        assert r.get_current_id() == DEFAULT_PROVIDER_ID

    def test_corrupt_config_uses_default(self, tmp_path: Path) -> None:
        cfg = tmp_path / "model_selection.json"
        cfg.write_text("{not valid json")
        r = ModelRegistry(config_path=cfg)
        assert r.get_current_id() == DEFAULT_PROVIDER_ID

    def test_save_failure_is_non_fatal(self, tmp_path: Path) -> None:
        # config path inside a file (not a dir) → parent.mkdir / write fails
        cfg = tmp_path / "blocker"  # we'll make 'blocker' a file so mkdir fails
        cfg.write_text("x")
        bad_path = cfg / "sub" / "model_selection.json"
        r = ModelRegistry(config_path=bad_path)
        # select still succeeds in-memory despite the unwritable path
        assert r.select("openai") is True
        assert r.get_current_id() == "openai"


# ===========================================================================
# Factory
# ===========================================================================


class TestFactory:
    def test_create_current_llm_uses_selected_provider(
        self, registry: ModelRegistry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """create_current_llm should call the selected provider's create_llm."""
        calls: list[str] = []

        class _StubProvider(LLMProvider):
            def create_llm(self):  # type: ignore[override]
                calls.append("called")
                return "stub-llm"

        # inject a stub provider into the catalog
        registry._providers["stub"] = ProviderInfo(
            id="stub", name="Stub", kind="cloud", description="d",
            factory=lambda: _StubProvider(),
        )
        registry.select("stub")
        llm = registry.create_current_llm()
        assert llm == "stub-llm"
        assert calls == ["called"]


# ===========================================================================
# AIService facade
# ===========================================================================


class TestAIServiceFacade:
    def test_get_current_provider_info(self, registry: ModelRegistry) -> None:
        registry.select("openai")
        ai = AIService(registry=registry)
        info = ai.get_current_provider_info()
        assert info.id == "openai"

    def test_get_current_llm_delegates_to_registry(
        self, registry: ModelRegistry, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class _StubProvider(LLMProvider):
            def create_llm(self):  # type: ignore[override]
                return "stub-via-service"

        registry._providers["stub"] = ProviderInfo(
            id="stub", name="Stub", kind="cloud", description="d",
            factory=lambda: _StubProvider(),
        )
        registry.select("stub")
        ai = AIService(registry=registry)
        assert ai.get_current_llm() == "stub-via-service"

    def test_get_registry_returns_backing_registry(
        self, registry: ModelRegistry
    ) -> None:
        ai = AIService(registry=registry)
        assert ai.get_registry() is registry

    def test_legacy_methods_still_work(self) -> None:
        ai = AIService()
        assert isinstance(ai.openrouter_llm_provider(), OpenRouterProvider)
        assert isinstance(ai.cloud_llm_provider(), OpenAIProvider)
        assert isinstance(
            ai.local_llm_provider("m.gguf", 2048), LlamaCppProvider
        )

    def test_default_service_uses_default_registry(self) -> None:
        ai = AIService()
        assert ai.get_registry() is default_registry
