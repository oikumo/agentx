# TUI End-to-End Tests (Pilot)

System-level tests for **feature_004.modern_ui**. Unlike the mock-based unit
tests in `tests/`, these drive the **real** `TUIApplication` through Textual's
[`Pilot`](https://textual.textualize.io/guide/testing/) harness — simulating
actual key presses, button clicks and input submission, then asserting on real
widget/screen state.

## Why a separate module

`AGENTS.md` forbids modifying `tests/`. This automated end-to-end suite lives in
`tests_automated/tui/` as required by `WORK.md`.

## Async style

`pytest-asyncio` is **not** a project dependency. Following the convention
already used in `tests/tui/test_main_screen.py`, each test is a plain `def` that
builds an inner `async def scenario()` and runs it with `asyncio.run(...)` (via
the `drive()` helper in `conftest.py`).

## Running

```bash
uv run pytest tests_automated/tui/ -v
```

## Coverage (Use-Case → Test mapping)

| Use case / workflow                              | Test |
|--------------------------------------------------|------|
| App boots and shows the Main screen + widgets    | `test_main_navigation_e2e.py::test_app_boots_to_main_screen` |
| Key `c` opens Chat                               | `test_main_navigation_e2e.py::test_key_c_opens_chat` |
| Key `r` opens RAG                                | `test_main_navigation_e2e.py::test_key_r_opens_rag` |
| `escape` returns from Chat to Main               | `test_main_navigation_e2e.py::test_escape_returns_from_chat` |
| Button `Chat` navigates to Chat                  | `test_main_navigation_e2e.py::test_chat_button_opens_chat` |
| Key `q` quits the app                            | `test_main_navigation_e2e.py::test_key_q_quits` |
| Submitting a command delegates to the controller | `test_command_input_e2e.py::test_command_submit_delegates_to_controller` |
| Input is cleared after submission                | `test_command_input_e2e.py::test_input_cleared_after_submit` |
| Empty input is a no-op                           | `test_command_input_e2e.py::test_empty_input_is_noop` |
</invoke>
