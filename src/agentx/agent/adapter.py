"""AgentAdapter — factory wiring AgentController ↔ AgentTUIScreen (feature_004 integration, design §10).

Provides a single entry point that the main TUI app calls to build the agent
triad.  Keeps the wiring self-contained in the agent module so the existing UI
code is not modified.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, cast

from agentx.agent.controller.agent_controller import AgentController
from agentx.agent.interfaces import IAIServicePartner, IAgentViewPartner
from agentx.agent.model.agent import Agent
from agentx.agent.types import AgentConfig
from agentx.agent.view.tui.agent_screen import AgentTUIScreen

if TYPE_CHECKING:
    from agentx.agent.view.tui.fast_agent_screen import FastAgentTUIScreen

_log = logging.getLogger(__name__)


class AgentAdapter:
    """Creates and wires the Agent + AgentController (+ optional TUI screen)."""

    @staticmethod
    def create_agent(
        config: AgentConfig,
        ai_service: IAIServicePartner | None = None,
        resume: bool = True,
    ) -> tuple[Agent, AgentController]:
        """Build a wired ``(Agent, AgentController)`` pair (I4: AI wiring lives here).

        * ``ai_service`` — if ``None`` a default :class:`AIServiceAdapter` is
          created (degrades gracefully if no API keys are configured).
        * ``resume`` — when true, the latest persisted snapshot for this agent
          id is restored (C5/I1), and the AI service is re-injected afterwards
          (C3).
        """
        agent = Agent(config)

        # I4: the adapter owns AI-service wiring so controllers don't import it.
        if ai_service is None:
            from agentx.agent.model.ai_adapter import AIServiceAdapter

            ai_service = AIServiceAdapter()
        agent.set_ai_service(ai_service)

        # C5/I1: resume the latest snapshot so state survives reopen.
        if resume:
            latest = agent.load_latest_snapshot()
            if latest is not None:
                try:
                    agent.resume_session(latest.snapshot_id)
                    # C3: re-inject the AI service after resume (it is not
                    # serialisable; resume preserves it on the same instance
                    # but be explicit for the fresh-agent path).
                    agent.set_ai_service(ai_service)
                    _log.info("agent %s resumed from snapshot %s", agent.id, latest.snapshot_id[:8])
                except Exception as exc:  # noqa: BLE001 — resume is non-fatal
                    _log.warning("session resume failed for agent %s: %s", agent.id, exc)

        controller = AgentController(agent)
        return agent, controller

    @staticmethod
    def create(
        config: AgentConfig,
        ai_service: IAIServicePartner | None = None,
        resume: bool = True,
    ) -> tuple[Agent, AgentController, AgentTUIScreen]:
        """Build a fully wired agent triad.

        Returns ``(agent, controller, screen)``.  The caller pushes *screen*
        onto the Textual app stack.
        """
        agent, controller = AgentAdapter.create_agent(config, ai_service, resume)
        screen = AgentTUIScreen(controller)
        _wire_view(controller, screen)
        return agent, controller, screen

    @staticmethod
    def create_screen(controller: AgentController) -> AgentTUIScreen:
        """Create a TUI screen for an existing controller."""
        screen = AgentTUIScreen(controller)
        _wire_view(controller, screen)
        return screen

    @staticmethod
    def create_fast(
        config: AgentConfig,
        ai_service: IAIServicePartner | None = None,
        resume: bool = True,
    ) -> tuple[Agent, AgentController, "FastAgentTUIScreen"]:
        """Build a wired Fast Agent triad (feature_011).

        Mirrors :meth:`create` but uses :class:`FastAgentTUIScreen` (modal-flow
        host) + :class:`FastAgentTUIView` (no-op partner) instead of
        :class:`AgentTUIScreen`.  The no-op view swallows the controller's
        push-style UI callbacks during ``run_cycle()`` — the modal flow queries
        the controller explicitly via ``get_cycle_summary()``.
        """
        # Lazy imports to avoid top-level circular dependency and keep the
        # Fast Agent UI optional (only loaded when the user opens it).
        from agentx.agent.view.tui.fast_agent_screen import FastAgentTUIScreen
        from agentx.agent.view.tui.fast_agent_view import FastAgentTUIView

        agent, controller = AgentAdapter.create_agent(config, ai_service, resume)
        # The no-op FastAgentTUIView is the controller's partner (NOT the screen).
        view = FastAgentTUIView()
        if not isinstance(view, IAgentViewPartner):  # m9-style runtime check
            raise TypeError("FastAgentTUIView does not implement IAgentViewPartner")
        controller.set_view(view)
        screen = FastAgentTUIScreen(controller)
        return agent, controller, screen


def _wire_view(controller: AgentController, screen: AgentTUIScreen) -> None:
    """Connect *screen* as the controller's view (m9: runtime isinstance check).

    ``AgentTUIScreen`` is registered as a virtual subclass of
    :class:`IAgentViewPartner` (avoids the Textual/abc metaclass conflict), so
    the ``isinstance`` check passes at runtime and validates the cast.
    """
    if not isinstance(screen, IAgentViewPartner):  # m9
        raise TypeError(
            f"screen {type(screen).__name__} does not implement IAgentViewPartner"
        )
    controller.set_view(cast(IAgentViewPartner, screen))
