# Plan — Remove the TUI module and functionality from AgentX

> **Scope note (NOT a feature):** this is a refactor/removal plan, not an OMT feature. No
> `.meta/software_development_process/2.requirements/features/` dir is created. This plan lives
> in the sandbox (`sandbox/meta/remove_tui/`). Execution still flows through the OMT gates
> (`omt_phase` for `src/` edits, `omt_kb_nav` KB consult, think-gate for `TA:`-tagged files)
> because it touches `src/` and `tests/`.
>
> **Intent:** delete the Textual-based TUI front-end (`src/agentx/ui/tui/`,
> `src/agentx/agent/view/tui/`) and every runtime entry point, test, dev script, dependency, and
> doc reference that exists solely to serve it. The console REPL (`agentx.ui.screens.*` →
> `MainView`/`ProviderRegistry("console")`) becomes the **only** UI and the new default/sole entry
> path.

---

## 1. Architecture summary (relevant slice)

AgentX is an MVC + **provider** architecture:

```
main.py (entry: agentx.main:start)
  └─ ProviderRegistry (IUIProvider factory)  [agentx/ui/providers.py]
        ├─ ConsoleProvider  (registered "console")            ← KEEP  (the target)
        └─ TUIProvider      (registered "tui", set_default)    ← DELETE
  └─ MainController (agentx/ui/screens/main/main_controller.py) ← KEEP (adjust)
        ├─ controllers+views under agentx/ui/screens/* (console MVC)   ← KEEP
        └─ Textual screens under agentx/ui/tui/*                        ← DELETE
```

The model layer (`agentx/model/**`, `agentx/agent/**`) is **UI-agnostic** — grep confirms **zero**
`textual` imports under `src/agentx/model/` or `src/agentx/agent/model/`. Only stale docstrings say
"for the TUI". So the deletion is largely contained to the two TUI packages plus a small, known
coupling surface.

### Coupling surface (the only 3 non-TUI source files that import TUI)

| File | TUI import | Action |
|---|---|---|
| `src/agentx/ui/providers.py` (L245–250) | `from agentx.ui.tui import provider` (guarded `try/except`) | remove block |
| `src/agentx/ui/screens/main/main_controller.py` (L29, L308) | `from agentx.ui.tui.screens.coding.coding_controller import CodingController` | **relocate** `CodingController` into `ui/screens/coding/`, fix import |
| `src/agentx/agent/adapter.py` (L17–20, L107–116) | `agentx.agent.view.tui.*` (AgentTUIScreen / FastAgent*) | remove TUI-only methods `create`, `create_screen`, `create_fast`, `_wire_view`; keep `create_agent` |

### Key findings discovered during analysis

1. **`TUIProvider` is already half-broken.** Its `create_react_view` / `create_coding_view` /
   `create_models_view` / `create_agent_view` / `create_fast_agent_view` import adapters
   (`react_adapter`, `coding_adapter`, `models_adapter`, `agent_adapter`, `fast_agent_adapter`) that
   **do not exist** — only `chat_adapter`, `main_adapter`, `rag_adapter` are present. So those TUI
   entry paths would `ImportError` today. Removal is therefore low-risk (no green behavior lost).

2. **`CodingController` is a console MVC controller misplaced inside the TUI package.** It contains
   no Textual import; the console `coding` command (`CodingCommand` → `MainController.show_coding`,
   L308) uses it. Relocate to `src/agentx/ui/screens/coding/coding_controller.py` (sibling to the
   console `coding_view.py`). Only the TUI *screen* (`ui/tui/screens/coding/coding_screen.py`) is
   deleted.

3. **`AgentAdapter.create_agent` is console-used and TUI-free**; the TUI-coupled symbols
   (`create`, `create_screen`, `create_fast`, `_wire_view` + the modules they import) are
   TUI-only. Keep `create_agent`, delete the rest.

4. **`DemoController` is core, not TUI.** `agent/controller/demo_controller.py` is imported by
   `AgentController` and imports `agent/demo/scenarios.py` — both survive. Only the TUI *view* of
   the demo feature (`agent/view/tui/demo_screen.py`) is deleted.

5. **v1 RAG becomes dead code once TUI is gone.** In `main_controller.load_commands`, `rag` routes
   to v1 `RagShowCommand` *only* when the provider is **not** `ConsoleProvider` (i.e. the TUI
   path); the console branch already routes to v2 `RagV2ShowCommand`. After step (a) forces
   `ConsoleProvider`, `show_rag` / `RagController` / `RagView` / `rag_chat_*` /
   `rag_create_repository_*` / `rag_(web_ingestion|repository_selection)_*` and the
   `IRagView`/`IRagViewPartner` ABCs are unreachable. **Phase 2 (optional)** — see §6.

6. **`ui/common/**` is console-shared and stays.** It is imported by console views
   (`main_view`, `chat_view`, `react_view`, `coding_view`, `agent_view`, `models_view`,
   `fast_agent_view`, all `rag_v2` views).

---

## 2. Delete — source

### 2a. TUI app package (delete `src/agentx/ui/tui/` except one move)
```
src/agentx/ui/tui/__init__.py
src/agentx/ui/tui/app.py
src/agentx/ui/tui/provider.py
src/agentx/ui/tui/adapters/__init__.py
src/agentx/ui/tui/adapters/chat_adapter.py
src/agentx/ui/tui/adapters/main_adapter.py
src/agentx/ui/tui/adapters/rag_adapter.py
src/agentx/ui/tui/framework/__init__.py
src/agentx/ui/tui/framework/async_runner.py
src/agentx/ui/tui/framework/base_adapter.py
src/agentx/ui/tui/framework/base_app.py
src/agentx/ui/tui/framework/base_modal.py
src/agentx/ui/tui/framework/base_screen.py
src/agentx/ui/tui/framework/partner.py
src/agentx/ui/tui/framework/widgets.py
src/agentx/ui/tui/screens/__init__.py
src/agentx/ui/tui/screens/chat_screen.py
src/agentx/ui/tui/screens/main_screen.py
src/agentx/ui/tui/screens/models_screen.py
src/agentx/ui/tui/screens/rag_screen.py
src/agentx/ui/tui/screens/rag_screens.py
src/agentx/ui/tui/screens/react_screen.py
src/agentx/ui/tui/screens/coding/coding_screen.py      ← TUI screen only
```
(23 files deleted; `screens/coding/coding_controller.py` is **moved**, §3.)

### 2b. Agent TUI views (delete whole `src/agentx/agent/view/tui/`)
```
src/agentx/agent/view/tui/__init__.py
src/agentx/agent/view/tui/agent_screen.py
src/agentx/agent/view/tui/demo_screen.py
src/agentx/agent/view/tui/fast_agent_modals.py
src/agentx/agent/view/tui/fast_agent_screen.py
src/agentx/agent/view/tui/fast_agent_view.py
```
(6 files. Console equivalents already exist: `agent/view/agent_view.py`,
`ui/screens/fast_agent/fast_agent_view.py`, `ui/screens/agent/agent_view.py`.)

---

## 3. Move — `CodingController`

```
FROM  src/agentx/ui/tui/screens/coding/coding_controller.py
TO    src/agentx/ui/screens/coding/coding_controller.py
```
- Content unchanged logically; edit the module/class docstrings that say "sits between the **TUI
  View** (`CodingTUIScreen`)" → "sits between the console view and the Model".
- Update the two importers: `main_controller.py` (L29 type + L308 runtime) and
  `tests/features/feature_024.../test_console_provider_and_views.py:618`.

---

## 4. Modify — source

| File | Change |
|---|---|
| `src/agentx/main.py` | Remove `--tui`/`--no-tui` handling, the TTY probe, and the `use_tui` branch + console fallback. Always `ui_provider = ProviderRegistry.get("console")`. Remove the `ProviderRegistry.get_default()` call. |
| `src/agentx/ui/providers.py` | Delete the TUI import block (L245–250) + stale comment (L242). Optionally remove `ProviderRegistry.get_default()`/`list_providers` + `_default` field (now unused). |
| `src/agentx/ui/screens/main/main_controller.py` | Fix `CodingController` import path (§3). Simplify `load_commands` rag routing: always `RagV2ShowCommand` (drop `isinstance(..., ConsoleProvider)` branch). Optionally drop `show_rag`/`get_rag_controller` + `_rag_controller`/`_rag_view` (+ `IRagView` fields) per §6. Fix `FastAgentTUIView`/`MainTUIScreen` docstring references (L215–216). |
| `src/agentx/agent/adapter.py` | Remove `from agentx.agent.view.tui.agent_screen import AgentTUIScreen` (L17), the `TYPE_CHECKING` fast-agent import (L20), and methods `create`, `create_screen`, `create_fast` + helper `_wire_view` (L68–131). Drop now-unused `IAgentViewPartner`/`cast` imports. Reword module docstring (no more "AgentTUIScreen"). **Precondition:** before deleting, grep-confirm zero console callers of `create`/`create_screen`/`create_fast` — specifically that `ConsoleProvider.create_fast_agent_view` (and `create_view`/`create_agent_view`) do NOT route through these methods (see §7 step 0). |
| `src/agentx/ui/interfaces.py` | Cosmetic only, unless §6: reword docstrings that say "the TUI View calls" / "metaclass conflict with Textual" (L361, L411, etc.). **Keep** all ABCs used by console (`I*View`, `I*ViewPartner`, `IRagV2*`). |
| `pyproject.toml` | Remove `"textual>=8.2.8"` from `dependencies`; drop "modern Textual TUI and" from `description`. |
| `src/agentx/agent/__init__.py`, `agent/view/__init__.py`, `agent/demo/__init__.py`, `model/react/react_agent_service.py`, `model/coding/coding_agent_service.py`, `model/rag_v2/__init__.py`, `model/tools/registry.py` | Docstring-only cleanup where they say "TUI …". No logic change. |
| `src/agentx/agent/controller/agent_controller.py` (L263) | Comment references TUI `demo_screen` — reword (the demo controller survives; only its TUI view is deleted). |
| `src/agentx/agent/view/agent_view.py` (L3–4) | Docstring points at `view/tui/agent_screen.py` as the "rich Textual experience" — rewrite: this **is** the view now. |
| `src/agentx/ui/screens/models/models_view.py` (L22) | Docstring mentions the TUI `models_screen` `q` binding — drop that clause. |

---

## 5. Delete / modify — tests, scripts, docs, e2e

### 5a. Delete test files (pure TUI)
```
tests/tui/                              (conftest.py, __init__.py, test_app.py, test_chat_adapter.py,
                                         test_chat_rag_screens.py, test_main_adapter.py, test_main_screen.py,
                                         test_provider.py, test_rag_adapter.py, test_tui_bug_reproduction.py)
tests/features/feature_012.tui_framework/                     (whole dir)
tests/features/feature_014.tui_nonblocking_runner/            (whole dir)
tests/features/feature_007.agentx_intelligent_agent_behaviour/test_tui_agent_screen.py
tests/features/feature_010.agent_demo_screen/test_demo_screen.py
tests/features/feature_011.fast_agent/                        (conftest.py + 4 test files — all TUI fast-agent)
tests/features/feature_018.react_screen/                      (test_react_freeze/integration/mvc/screen — TUI react screen)
tests/features/feature_013.ai_model_provider_selector/test_models_integration.py   (TUI models screen)
tests/features/feature_019.coding_agent_screen/test_coding_mvc.py                 (TUI MVC architectural gate)
tests_automated/tui/                                          (whole dir incl. README)
```
Note: feature_013's `test_mvc_model_selector.py` (console MVC) and feature_018 console coverage
(`tests/views/test_react_view.py`) **survive**. feature_019's `test_coding_integration.py` is
**split (decided):** keep the controller/service assertions (with the §5b import fix), delete the
`CodingTUIScreen` assertions. This is the single canonical instruction — §5b only carries the
import line for the kept half. The split is a **modification** (not a deletion) and is executed
as its own ordered step (§7 step 6b) with the `tests/` canary approval called out.

Note re semantic drift: the dir named `feature_024.no_tui_full_features` will keep its name, but
after removal its premise ("console works without TUI") becomes the only reality rather than a
mode. No action beyond the §5b import fix — just confirm the suite still asserts something
meaningful (it does: console provider + views work).

### 5b. Modify test files (import path update only)
```
tests/features/feature_024.no_tui_full_features/test_console_provider_and_views.py:618
    from agentx.ui.tui.screens.coding.coding_controller import CodingController
    →  from agentx.ui.screens.coding.coding_controller import CodingController
    (The rest of feature_024 asserts console-only behavior — the suite survives unchanged;
     only this one import line moves.)
tests/features/feature_019.coding_agent_screen/test_coding_integration.py:25
    Same import move — but see §5a: this file is SPLIT (controller/service assertions kept,
    CodingTUIScreen assertions deleted); the kept half uses the new import path.
```

### 5c. Delete dev scripts (all import TUI/Textual)
```
scripts/debug_tui.py
scripts/demo_tui.py
scripts/test_full_tui.py
scripts/test_keyboard_events.py
scripts/test_pilot_full.py
scripts/test_tui_basic.py
scripts/test_tui_interactive.py
scripts/test_tui_run.py
scripts/test_tui_simple.py
```

### 5d. Docs
- `README.md` — remove/rewrite the TUI sections (title blurb, the ASCII `AgentX TUI` banner, the
  "Modern TUI (Textual Interface)" section, TUI navigation, ReactTUIScreen/CodingTUIScreen view
  notes, the `ui/tui/screens/` + `agent/view/` tree snippet, provider-pattern "TUI vs Console"
  text, TUI test/pilot mentions, feature_004/012/014 bullets, the Textual attribution footnote).
  **Preferred:** drop the duplicated source-tree snippet from README entirely rather than updating
  it — one less drift source for `harnessc check` to flag.
- `GETTING_STARTED.md` — no TUI references found; verify `README.md` on-disk tree/quick-start text.
- `shared/META.md`, `.meta/doc/omt++/*.md|*.omt`, `.meta/META_HARNESS.omt` — grep for
  `tui`/`textual` and reconcile only the **architecture/code-kb** docs (these are harness-internal;
  do not edit harness `.omt` unless a doc literally documents the app's UI layer).

---

## 6. Phase 2 (optional, needs user decision) — v1 RAG + provider ABC dead code

Removing TUI makes these unreachable. Confirm before deleting:

- **v1 RAG** (`src/agentx/ui/screens/rag/**`, `MainController.show_rag`/`get_rag_controller`,
  `ConsoleProvider.create_rag_view`, and `IRagView`/`IRagViewPartner` in `interfaces.py`).
  → console `rag` already uses **v2** (`rag_v2`) exclusively.
- **`ProviderRegistry.get_default`/`_default`/`list_providers`** in `providers.py` (only used by the
  removed TUI branch).

Default plan: **do Phase 1 only** (targeted, low-risk), file Phase 2 as a follow-up decision.

---

## 7. Ordered execution (Phase 1)

1. `git status` + confirm baseline; record current `WORK.md` state.
2. Delete `src/agentx/ui/tui/**` (except `coding_controller.py`) and `src/agentx/agent/view/tui/**`.
3. Move `coding_controller.py` to `ui/screens/coding/`; fix its docstring; fix the 2 importers
   (source + tests).
4. Edit `main.py` (console-only), `providers.py` (drop TUI import), `main_controller.py`
   (`CodingController` path + `rag` routing), `agent/adapter.py` (drop TUI methods).
5. Edit `pyproject.toml` (drop `textual`), remove `uv.lock` textual entry via `uv sync`/`uv lock`.
6. Delete TUI test files/suites + dev scripts (§5a/§5c). Split feature_019 integration test (§5a).
7. Doc cleanup (README.md §5d).
8. Verify:
   - `uv run python -c "import agentx; from agentx.main import main"` imports clean (no textual import anywhere).
   - `grep -rEni "ui\.tui|view\.tui|textual|\btui\b" src/ tests/ scripts/` → only allowed
     docstring/inert-string hits (§5d remainder). Note: bare `no_tui` (e.g. the
     `feature_024.no_tui_full_features` dir name) is an **expected, allowed hit** — do not chase it.
   - `uv run pytest` — full suite green; expect the count to drop by the deleted TUI tests
     (~90–110 tests) with **zero** regressions in console tests.
9. `omt_complete` and log the removal in `WORK.md` / rotate post-done notes.

### Risk / gotchas
- **README.md is protected:** it sits on the NEVER-edit list — step 7 needs
  `omt_skip{scope:"all", purpose:"override"}` before touching it, or the §5d step is blocked.
- **Gate discipline:** `src/` edits need `omt_phase`; `tests/` edits need canary approval;
  `TA:`-tagged files (`main_controller.py`, `app.py`, `react_view.py`, …) need `omt_think{op:list}`
  consult first. The per-file second-edit guard applies to harness-surface — batch one edit per file
  per round.
- **`uv.lock`:** removing `textual` requires regenerating the lock (`uv lock`/`uv sync`); do this with
  the uv toolchain, not by hand.
- **feature_019 split:** `test_coding_integration.py` mixes shared-controller and TUI-screen
  assertions — separate them; the controller/service halves must stay green.
- **README tree block** duplicates the on-disk layout; if the plan deletes `ui/tui/`, the tree
  snippet must be updated in the same commit or `harnessc check` may flag drift.

## 8. Verification signals (done = true when)
- No `textual`/`agentx.ui.tui`/`agentx.agent.view.tui` import anywhere in `src/` (except relocated
  `CodingController` docstring).
- `uv run agentx` launches straight into the console REPL (no TUI flag banner).
- `uv run pytest` green (reduced test count, no console regressions).
- `uv run pip check` / import smoke test clean; `textual` absent from the lock.