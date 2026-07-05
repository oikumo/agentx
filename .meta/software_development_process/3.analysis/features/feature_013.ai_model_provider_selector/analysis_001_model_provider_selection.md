# Analysis 001: AI Model Provider Selection

> **Phase:** Analysis — `omt_agent_guide.md §2` | **Feature:** feature_013.ai_model_provider_selector

## Problem / domain concepts

Today the AI model provider is **hardcoded**. Every feature builds its LLM with
`AIService().openrouter_llm_provider().create_llm()`:

| Call site | File:line | Hardcoded provider |
|---|---|---|
| Chat | `ui/screens/chat/chat_controller.py:11` | OpenRouter |
| RAG chat | `ui/screens/rag/rag_chat_controller.py:13` | OpenRouter |
| RAG orchestrator | `model/rag/rag.py:33` | OpenRouter |
| Agent reflection | `agent/model/ai_adapter.py:51-53` | OpenRouter → OpenAI (fallback chain) |

There is no user-facing way to pick a different provider. The available
providers are also modelled inconsistently:

- `LLMProvider(ABC)` (`model/ai/providers.py`) — the strategy interface, with
  `OpenRouterProvider`, `OpenAIProvider`, `LlamaCppProvider`.
- `Ollama` (`model/ai/local/ollama/ollama.py`) — a plain class, **not** an
  `LLMProvider`; reached via `local_ollama_models`.
- `get_remote_llm_google_gemini()` (`model/ai/cloud/google/google_gemini.py`) —
  an ad-hoc factory function, **not** an `LLMProvider`.

**Key domain concepts (candidate classes):**

- **Provider** — a strategy that builds a `BaseChatModel` (already modelled by
  `LLMProvider`). Needs: unify `Ollama` and Gemini under it.
- **Provider catalog** — the static list of *available* providers with display
  metadata (id, display name, kind = cloud|local, description). Read-only.
- **Selection** — the mutable, persistent *currently chosen* provider id.
  Survives app restarts. Single value, not entity CRUD → JSON file, not sqlite.
- **Registry** — combines catalog + selection + factory; the single source of
  truth the `AIService` consults.
- **Models screen** — a TUI screen (View + Controller) that lists the catalog
  and lets the user change the selection.
- **Main screen** — gains a `m` binding + button to open the Models screen.

## Analysis class sketch (static path)

```
LLMProvider (ABC, exists)                       [model/ai/providers.py]
  + create_llm() -> BaseChatModel
  -- subclasses: OpenRouterProvider, OpenAIProvider, LlamaCppProvider
  -- NEW subclasses: OllamaProvider, GeminiProvider (wrap existing ad-hoc code)

ProviderInfo (dataclass)                        [model/ai/model_registry.py]  NEW
  - id: str
  - name: str
  - kind: Literal["cloud","local"]
  - description: str
  - factory: Callable[[], LLMProvider]

ModelRegistry                                    [model/ai/model_registry.py]  NEW
  - providers: dict[str, ProviderInfo]          (static catalog)
  - _selected_id: str                           (mutable; default "openrouter")
  - _config_path: Path                          (JSON persistence, best-effort)
  + list_providers() -> list[ProviderInfo]
  + get_current() -> ProviderInfo
  + select(provider_id) -> bool                 (validates id, persists)
  + create_current_llm() -> BaseChatModel       (factory → LLMProvider.create_llm)

AIService (exists, refactored)                  [model/ai/service.py]
  + get_current_llm() -> BaseChatModel          NEW: delegates to ModelRegistry
  + get_current_provider_info() -> ProviderInfo NEW
  - openrouter_llm_provider() / cloud_llm_provider() / local_llm_provider()  (kept for backward-compat)

ModelsController (IModelsViewPartner)           [ui/screens/models/models_controller.py]  NEW
  + list_providers() -> list[ProviderInfo]
  + get_current_id() -> str
  + select_provider(provider_id) -> bool
  + get_status_text() -> str

ModelsTUIScreen (BaseAgentXScreen)              [ui/tui/screens/models_screen.py]  NEW
  + compose() / on_select / action_select / action_back
  -- delegates to ModelsController via Abstract Partner

MainController (exists, extended)               [ui/screens/main/main_controller.py]
  + show_models() -> None                       NEW
  + get_models_controller() -> ModelsController NEW

MainTUIScreen (exists, extended)                [ui/tui/screens/main_screen.py]
  + action_open_models()                        NEW (navigate_to_child)
  -- BINDINGS += Binding("m", "open_models", "Models")
```

Associations: `MainController` → `ModelsController` (creates/owns, like
`_chat_controller`). `ModelsController` → `ModelRegistry` (consults). The
`AIService` → `ModelRegistry` (delegates `get_current_llm`). No OID foreign keys
needed — selection is a single scalar, not an entity graph.

## UI behaviour (if UI changes)

**Dialog structure (Models screen):**

```
┌─────────────────────────────────────────────┐
│  Header                                      │
├─────────────────────────────────────────────┤
│  "Select AI Model Provider"  (title)         │
│  Current: OpenRouter (cloud)                 │
├─────────────────────────────────────────────┤
│  ▸ [●] OpenRouter      cloud  — auto-routing │
│    [ ] OpenAI GPT      cloud  — gpt-3.5      │
│    [ ] Google Gemini   cloud  — gemini-flash │
│    [ ] Ollama          local  — qwen3.5      │
│    [ ] LlamaCpp        local  — local GGUF   │
├─────────────────────────────────────────────┤
│  Enter=select  Esc/b=back  q=quit            │
│  Footer                                      │
└─────────────────────────────────────────────┘
```

- Reached from Main screen via `m` key or "🎛️ Models" button.
- Uses a Textual `SelectionList` (or `OptionList`) showing each provider; the
  current selection is highlighted/marked.
- `Enter` selects the focused option → delegates to controller → confirms.
- `Esc` / `b` pops back to Main (no change if nothing selected).
- Pure View: no `agentx.model.*` import; calls only `ModelsController` methods.

**Main screen changes:** add a 6th button "🎛️ Models" to `MenuGrid` (grid
becomes 3×2 → already 3×2; add as 6th cell) and a `m` binding.

## Open questions

- **Where to persist the selection?** Decision: a small JSON file
  (`~/.agentx/model_selection.json`), best-effort write. Rationale: selection is
  a single key/value, not entity CRUD, so sqlite (the project's DP pattern for
  entities) is overkill. The `ModelRegistry` accepts an injectable
  `config_path` so tests use `tmp_path`.
- **LlamaCpp needs config (model filename + context size).** Decision: ship a
  sensible default in the catalog entry's factory; the user picks "LlamaCpp"
  and gets the default model. Configurable model params are out of scope for
  this feature (the selector chooses the *provider*, not per-call params).
- **Does selecting persist across sessions?** Yes (that is the point). The
  registry reads the JSON on first access and writes on every successful
  `select()`.
- **Backward compatibility of `AIService` legacy methods?** Kept unchanged so
  nothing that still calls `openrouter_llm_provider()` breaks during the
  transition; the 4 hardcoded call sites are migrated to `get_current_llm()`.
