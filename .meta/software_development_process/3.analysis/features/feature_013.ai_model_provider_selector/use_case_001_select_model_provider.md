# Use Case: Select AI Model Provider

> **Phase:** Analysis (functional path) — `omt_agent_guide.md §3`
> **Feature:** feature_013.ai_model_provider_selector

## Actor

The AgentX user (developer running the TUI application).

## Goal

The user wants to choose which AI model provider (OpenRouter, OpenAI, Google
Gemini, Ollama, or LlamaCpp) powers the application's AI features (Chat, RAG,
Agent) so that every feature uses the same, user-selected provider instead of a
hardcoded one.

## Preconditions

- The AgentX TUI application is running and the Main screen is visible.
- At least one provider is available in the catalog (always true: OpenRouter is
  the default entry).

## Main flow

1. From the Main screen, the user presses `m` (or clicks the "🎛️ Models"
   button).
2. The Main screen pushes the Models screen.
3. The Models screen displays the list of available providers with their kind
   (cloud/local), a short description, and marks the currently selected one.
4. The user navigates the list (↑/↓ or click) and presses `Enter` on the
   desired provider.
5. The Models screen delegates the selection to the ModelsController.
6. The ModelsController asks the ModelRegistry (Model layer) to select the
   provider by id and persist the choice.
7. The Models screen confirms the new selection and refreshes the highlight.
8. The user presses `Esc` (or `b`) to return to the Main screen.
9. Subsequent Chat / RAG / Agent operations use the newly selected provider.

## Alternate / exception flows

- **[provider unavailable at use time]** → The selection is still stored, but
  when a feature tries to create the LLM the provider raises (missing API key,
  model not found). The calling feature already handles LLM errors (chat pops
  the failed message; the agent reflection engine degrades gracefully), so the
  selection screen only reports success of *storing* the choice, not of
  instantiating the model.
- **[persistence write fails]** → The selection is applied in-memory for the
  current session; a non-fatal warning is shown ("selection saved for this
  session only"). The app continues.
- **[no provider selected yet / corrupted config]** → The registry falls back
  to the default provider (`openrouter`) so the app always has a working
  provider; the Models screen shows the default as the current selection.
- **[user cancels without selecting]** → Pressing `Esc` without choosing pops
  back with no change to the current selection.

## Postconditions

- The chosen provider id is the registry's current selection and (on success)
  persisted to the config file.
- Every feature that asks `AIService` for an LLM receives one built from the
  selected provider.
- The Models screen reflects the new current selection on next open.

## Operations extracted

<!-- Each step that changes state becomes a Controller method with an operation spec (§10). -->

- `list_providers()` → returns catalog of available providers + current selection
- `select_provider(provider_id)` → sets + persists the current selection
- `get_current_provider()` → returns the currently selected provider info
- `get_current_llm()` → (Model-layer convenience) builds the LLM from the selection
