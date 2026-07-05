"""Models TUI Screen — select the current AI model provider.

Reached from the Main screen (``m`` key or "🎛️ Models" button).  Lists the
available providers in an :class:`OptionList`, marks the current selection, and
lets the user pick one with ``Enter``.

Design: ``design_001_model_selector.md`` (dialog diagram + flow 1).

MVC++: pure View — no ``agentx.model.*`` import.  The controller is duck-typed
``Any`` and reached only through the :class:`IModelsViewPartner` methods
(``list_providers`` / ``get_current_id`` / ``select_provider`` /
``get_status_text``).  Provider objects returned by the controller are also
duck-typed (``.id`` / ``.name`` / ``.kind`` / ``.description``).
"""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Footer, Header, Label, OptionList
from textual.widgets.option_list import Option

from agentx.ui.tui.framework import BaseAgentXScreen


class ModelsTUIScreen(BaseAgentXScreen):
    """Screen for selecting the current AI model provider."""

    BINDINGS = [
        Binding("enter", "select", "Select", show=True),
        Binding("escape", "back", "Back", show=True),
        Binding("b", "back", "Back", show=True),
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh", "Refresh", show=False),
    ]

    DEFAULT_CSS = """
    ModelsTUIScreen {
        layout: vertical;
    }

    ModelsTUIScreen #models-container {
        height: 1fr;
        padding: 1 2;
    }

    ModelsTUIScreen #models-title {
        text-style: bold;
        color: $primary;
        text-align: center;
        margin-bottom: 0;
    }

    ModelsTUIScreen #models-status {
        color: $text-muted;
        margin-bottom: 1;
    }

    ModelsTUIScreen #models-list {
        height: 1fr;
        border: solid $primary;
    }
    """

    # __init__, action_quit, action_back are inherited from BaseAgentXScreen.

    def compose(self) -> ComposeResult:
        """Compose the Models screen layout."""
        yield Header(show_clock=True)
        with Vertical(id="models-container"):
            yield Label("🎛️  Select AI Model Provider", id="models-title")
            yield Label("", id="models-status")
            yield OptionList(id="models-list")
        yield Footer()

    def on_mount(self) -> None:
        """Populate the list on mount."""
        self._refresh()

    # ----------------------------------------------------------- rendering

    def _refresh(self) -> None:
        """Reload the provider list + status from the controller."""
        if not self._controller:
            self.safe_update("models-status", "No controller connected.")
            return
        try:
            providers: Any = self._controller.list_providers()
            current_id: str = self._controller.get_current_id()
            status: str = self._controller.get_status_text()
        except Exception as exc:  # noqa: BLE001 — never crash the TUI
            self.safe_error(f"Error loading providers: {exc}")
            return

        self.safe_update("models-status", status)

        try:
            ol = self.query_one("#models-list", OptionList)
            ol.clear_options()
            highlight_idx = 0
            for idx, p in enumerate(providers):
                marker = "●" if p.id == current_id else "○"
                prompt = f"{marker}  {p.name}  [{p.kind}] — {p.description}"
                ol.add_option(Option(prompt, id=p.id))
                if p.id == current_id:
                    highlight_idx = idx
            ol.highlighted = highlight_idx
        except Exception as exc:  # noqa: BLE001
            self.safe_error(f"Error rendering list: {exc}")

    # ----------------------------------------------------------- selection

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:  # type: ignore[override]
        """Handle Enter / click on an option — select it."""
        self._select_option_id(event.option.id)

    def action_select(self) -> None:
        """Handle the screen-level ``Enter`` binding — select the highlighted option."""
        try:
            ol = self.query_one("#models-list", OptionList)
            idx = ol.highlighted if ol.highlighted is not None else 0
            option = ol.get_option_at_index(idx)
        except Exception:
            return
        self._select_option_id(option.id)

    def action_refresh(self) -> None:
        """Reload the list (``r`` key)."""
        self._refresh()

    def _select_option_id(self, provider_id: str | None) -> None:
        """Delegate the selection to the controller and refresh."""
        if not provider_id or not self._controller:
            return
        try:
            ok: bool = self._controller.select_provider(provider_id)
        except Exception as exc:  # noqa: BLE001
            self.safe_error(f"Error selecting provider: {exc}")
            return
        if ok:
            self.safe_notify(f"Provider set: {provider_id}", timeout=2)
            self._refresh()
        else:
            self.safe_error(f"Unknown provider: {provider_id}")
