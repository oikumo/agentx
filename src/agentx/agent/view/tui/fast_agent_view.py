"""FastAgentTUIView — no-op :class:`IAgentViewPartner` for the Fast Agent flow.

The Fast Agent's modal UI (feature_011) queries the controller *explicitly* for
display data via ``get_cycle_summary()`` / ``list_pending_proposals()`` etc.
However, :meth:`AgentController.run_cycle` still fires View-side callbacks
(``show_status``, ``show_reflection_log`` …) on every cycle.  This no-op
partner swallows those callbacks so the cycle can run without a full
:class:`AgentTUIScreen` being wired.

Registered as a *virtual subclass* of :class:`IAgentViewPartner` (matches the
``AgentTUIScreen`` / ``AgentDemoScreen`` pattern) so the controller's
``isinstance`` check (m9) passes.

Design: ``design_001_fast_agent.md`` §3–§4, §8.
Operation spec: ``operation_spec_001_fast_agent.md`` (FastAgentTUIView).
"""

from __future__ import annotations

from typing import Any

from agentx.agent.interfaces import IAgentViewPartner


class FastAgentTUIView:
    """No-op :class:`IAgentViewPartner` — swallows controller UI callbacks.

    The Fast Agent modal flow does not use these push-style callbacks; it pulls
    data from the controller on demand.  This partner exists so
    :meth:`AgentController.set_view` has a valid target and the cycle does not
    raise ``AttributeError`` when the Agent emits status/reflection events.
    """

    def show_status(self, status: Any) -> None:  # noqa: D401 — no-op
        """No-op — RunningModal queries ``get_cycle_summary()`` instead."""

    def show_reflection_log(self, entries: list[Any]) -> None:
        """No-op — ReflectionModal queries ``list_pending_proposals()`` instead."""

    def show_memory_view(self, query: Any) -> None:
        """No-op — Fast Agent does not surface memory in v1."""

    def show_policy_editor(self, rules: list[Any]) -> None:
        """No-op — Fast Agent hides policy authoring (Advanced toggle only)."""

    def refresh_goal_tree(self) -> None:
        """No-op — Fast Agent shows one goal at a time, no tree sidebar."""

    def show_message(self, message: str) -> None:
        """No-op — Fast Agent surfaces messages via modals, not push callbacks."""


# Register as a virtual subclass of IAgentViewPartner (avoids the
# Textual/abc metaclass conflict — this is a plain class, not a Screen, but
# we follow the same registration convention for consistency and so the
# controller's isinstance check passes).
IAgentViewPartner.register(FastAgentTUIView)
