# Operation Spec: Model Provider Selector

> Operation specs for feature_013 Controller/Model methods — `omt_agent_guide.md §10`.

## ModelsController.select_provider

```python
def select_provider(self, provider_id: str) -> bool:
    """
    Operation: Set and persist the current AI model provider.

    Preconditions:
      - provider_id is a non-empty string.
      - provider_id exists in the registry catalog.

    Exceptions:
      - Unknown provider_id: returns False (no change to current selection).
      - Persistence write failure: in-memory selection still applied; returns True
        (the selection succeeded for this session; persistence is best-effort).

    Postconditions:
      - On True: ModelRegistry.get_current().id == provider_id.
      - On False: current selection is unchanged.
    """
```

## ModelsController.list_providers

```python
def list_providers(self) -> list:
    """
    Operation: Return the catalog of available providers.

    Preconditions:
      - None (registry catalog is static; always non-empty).

    Exceptions:
      - None (catalog is code-defined; cannot fail).

    Postconditions:
      - Returns a list of ProviderInfo, each with id/name/kind/description.
      - The entry whose id == current selection is identifiable by get_current_id().
    """
```

## ModelsController.get_current_id

```python
def get_current_id(self) -> str:
    """
    Operation: Return the id of the currently selected provider.

    Preconditions:
      - None.

    Exceptions:
      - None (registry always has a default; falls back to "openrouter").

    Postconditions:
      - Returns a valid provider id present in the catalog.
    """
```

## ModelsController.get_status_text

```python
def get_status_text(self) -> str:
    """
    Operation: Return a one-line human-readable status of the current selection.

    Preconditions:
      - None.

    Exceptions:
      - None.

    Postconditions:
      - Returns e.g. "Current: OpenRouter (cloud)".
    """
```

## ModelRegistry.select

```python
def select(self, provider_id: str) -> bool:
    """
    Operation: Change the current provider and persist it.

    Preconditions:
      - provider_id is a key in self.providers.

    Exceptions:
      - Unknown id: returns False, _selected_id unchanged.
      - Config file not writable: _selected_id updated in-memory, _save() best-effort,
        returns True.

    Postconditions:
      - On True: _selected_id == provider_id and _save() attempted.
      - On False: _selected_id unchanged.
    """
```

## ModelRegistry.create_current_llm

```python
def create_current_llm(self) -> BaseChatModel:
    """
    Operation: Build a ready-to-use LLM from the current selection.

    Preconditions:
      - Current selection is a valid provider id.

    Exceptions:
      - Provider factory raises (missing API key, model not found): propagated
        to caller. The caller (chat/rag/agent) already handles LLM errors.

    Postconditions:
      - Returns a configured BaseChatModel instance.
    """
```

## MainController.show_models

```python
def show_models(self) -> None:
    """
    Operation: Create and wire a ModelsController for the Models screen.

    Preconditions:
      - MainController is initialised.

    Exceptions:
      - ModelsController construction failure: caught by navigate_to_child,
        a safe_error notification is shown; Main screen stays usable.

    Postconditions:
      - On success: self._models_controller is set and retrievable via
        get_models_controller(); the TUI screen is pushed by the caller.
      - Reuses an existing controller if already wired (C5 pattern).
    """
```
