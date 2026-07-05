# Implementation Notes — feature_013.ai_model_provider_selector

> **Phase:** Programming | **Feature:** feature_013.ai_model_provider_selector

## What was built

A user-selectable, persistent AI model provider, surfaced as a "Models" module on
the Main screen.  Replaces the hardcoded `openrouter_llm_provider()` calls with a
central `ModelRegistry` whose current selection every feature consults.

## Files created

| File | Layer | Purpose |
|---|---|---|
| `src/agentx/model/ai/model_registry.py` | Model | `ProviderInfo` + `ModelRegistry` (catalog, selection, JSON persistence, factory) + `default_registry` |
| `src/agentx/ui/screens/models/models_controller.py` | Controller | `IModelsViewPartner(ABC)` + `ModelsController` |
| `src/agentx/ui/screens/models/__init__.py` | — | package |
| `src/agentx/ui/tui/screens/models_screen.py` | View | `ModelsTUIScreen(BaseAgentXScreen)` — OptionList of providers |

## Files modified

| File | Change |
|---|---|
| `src/agentx/model/ai/providers.py` | Added `OllamaProvider`, `GeminiProvider` (unify ad-hoc code under `LLMProvider`). |
| `src/agentx/model/ai/service.py` | Added `get_current_llm()` / `get_current_provider_info()` / `get_registry()` delegating to the registry; `AIService.__init__(registry=None)`; legacy methods kept. |
| `src/agentx/agent/model/ai_adapter.py` | `_ensure_llm()` now tries the user-selected provider first, then the legacy OpenRouter→OpenAI fallback chain (preserves graceful degradation). |
| `src/agentx/ui/screens/chat/chat_controller.py` | `openrouter_llm_provider().create_llm()` → `get_current_llm()`. |
| `src/agentx/ui/screens/rag/rag_chat_controller.py` | Same refactor. |
| `src/agentx/model/rag/rag.py` | Same refactor. |
| `src/agentx/ui/screens/main/main_controller.py` | Added `show_models()` (idempotent, C5 pattern) + `get_models_controller()`. |
| `src/agentx/ui/tui/screens/main_screen.py` | Added `m` binding, `action_open_models()` (navigate_to_child), button handler, help text. |
| `src/agentx/ui/tui/framework/widgets.py` | `MenuGrid` gains 6th button "🎛️ Models" (`btn-models`). |

## Key design decisions (realised)

1. **JSON persistence, not sqlite.** Selection is one scalar (`{"selected": "<id>"}`);
   the project's sqlite DP pattern is for entities (Session/RAG). JSON at
   `~/.agentx/model_selection.json`, best-effort I/O (missing/corrupt/unwritable →
   default `openrouter`, never crashes). `config_path` is injectable for tests.
2. **Unified providers.** `Ollama` (plain class) and `get_remote_llm_google_gemini()`
   (ad-hoc fn) are now `LLMProvider` subclasses (`OllamaProvider`, `GeminiProvider`)
   so the catalog is homogeneous. Lazy imports inside `create_llm()` keep module
   load light.
3. **Backward compatibility.** `AIService` legacy methods (`openrouter_llm_provider`
   etc.) are unchanged, so nothing still calling them breaks. The 4 hardcoded call
   sites migrated to `get_current_llm()`.
4. **Agent adapter robustness.** The selected provider is tried first; on failure
   the legacy OpenRouter→OpenAI fallback runs, so a bad selection can't brick the
   reflection engine (it degrades gracefully, as before).
5. **Pure View.** `ModelsTUIScreen` imports no `agentx.model.*`; it duck-types the
   controller (`list_providers`/`get_current_id`/`select_provider`/`get_status_text`)
   and the provider objects it returns (`.id`/`.name`/`.kind`/`.description`).
6. **Persistence scope = tests.** Test edits were gated by AGENTS.md Stop Point #4
   and unlocked via a logged `omt_skip{scope:"tests"}` (audited in the ledger), the
   same mechanism feature_012 used.

## Provider catalog

| id | name | kind | factory |
|---|---|---|---|
| `openrouter` | OpenRouter | cloud | `OpenRouterProvider()` (default) |
| `openai` | OpenAI GPT | cloud | `OpenAIProvider()` |
| `gemini` | Google Gemini | cloud | `GeminiProvider()` |
| `ollama` | Ollama | local | `OllamaProvider()` |
| `llamacpp` | LlamaCpp | local | `LlamaCppProvider(default_model, 4096)` |

## Verification (at end of Programming)

- feature_013 suite: **56 passed**.
- Full suite: **635 passed, 1 failed** (the 1 = pre-existing
  `test_llm_initialization_attempted`, documented in WORK.md; unrelated to this
  feature — it asserts `hasattr(ChatTUIScreen(), 'llm')` on a Textual Screen that
  never had `.llm`, and `chat_screen.py` was not touched).
- MVC++ `mvc_check.py` on full `src/`: **0 errors, 6 warnings** (all pre-existing
  baseline; 0 from new code).
- 5 existing tests updated for the new Models button/binding (refactor-driven, per
  the feature_012 precedent): `test_menu_grid_has_*_buttons`,
  `test_compose_yields_*_buttons`, `test_button_ids`, `test_button_variants`,
  `test_bindings_count`; plus a new `test_binding_m_models`.
