"""SafetyEvaluator — proposal safety gate (design §8.4).

Every proposal passes through an :class:`ISafetyEvaluator` before routing.  The
evaluator encodes the agent's :class:`AutonomyLevel` and a small deny-list.
"""

from __future__ import annotations

from typing import Any

from agentx.agent.interfaces import ISafetyEvaluator
from agentx.agent.types import (
    AutonomyLevel,
    PolicyContext,
    Proposal,
    ProposalStatus,
    ProposalVerdict,
)


class DefaultSafetyEvaluator(ISafetyEvaluator):
    """SUPERVISED autonomy → most proposals need confirmation; AUTONOMOUS → auto-apply safe ones.

    Standard ``op`` values per ProposalType (M7):

    * ``POLICY_CHANGE``      — ``add`` | ``update`` | ``delete`` | ``disable``
    * ``MEMORY_UPDATE``      — ``add`` | ``update`` | ``delete`` | ``delete_all``
    * ``GOAL_ADJUSTMENT``    — ``add`` | ``update`` | ``delete`` | ``demote`` | ``abandon_root``
    * ``TOOL_CONFIGURATION`` — ``enable`` | ``disable`` | ``delete`` | ``uninstall``
    """

    #: (proposal_type, op) pairs that are always rejected regardless of autonomy.
    DANGEROUS = {
        "POLICY_CHANGE:delete",
        "POLICY_CHANGE:disable",
        "MEMORY_UPDATE:delete_all",
        "GOAL_ADJUSTMENT:abandon_root",
        "GOAL_ADJUSTMENT:delete",
        "GOAL_ADJUSTMENT:demote",
        "TOOL_CONFIGURATION:delete",
        "TOOL_CONFIGURATION:uninstall",
    }

    def evaluate(self, proposal: Proposal, ctx: PolicyContext) -> ProposalVerdict:
        op = proposal.content.get("op", "")
        key = f"{proposal.type.value}:{op}"
        if key in self.DANGEROUS:
            return ProposalVerdict(ProposalStatus.REJECTED, "deny-listed operation")
        autonomy = ctx.autonomy_level
        if autonomy in (AutonomyLevel.SUPERVISED, AutonomyLevel.CONFIRMATION_REQUIRED):
            return ProposalVerdict(ProposalStatus.NEEDS_CONFIRMATION, "supervised mode")
        if autonomy == AutonomyLevel.MANUAL_ONLY:
            return ProposalVerdict(ProposalStatus.NEEDS_CONFIRMATION, "manual-only mode")
        # FULLY_AUTONOMOUS
        return ProposalVerdict(ProposalStatus.APPROVED, "autonomous mode, safe")
