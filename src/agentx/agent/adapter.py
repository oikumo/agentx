"""AgentAdapter — factory wiring Agent + AgentController (console UI).

Provides a single entry point that builds the agent pair. Keeps the wiring
self-contained in the agent module so the existing UI code is not modified.
"""

from __future__ import annotations

import logging

from agentx.agent.controller.agent_controller import AgentController
from agentx.agent.interfaces import IAIServicePartner
from agentx.agent.model.agent import Agent
from agentx.agent.types import AgentConfig

_log = logging.getLogger(__name__)


class AgentAdapter:
    """Creates and wires the Agent + AgentController."""

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
