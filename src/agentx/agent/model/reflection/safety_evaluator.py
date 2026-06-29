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
    """SUPERVISED autonomy → most proposals need confirmation; AUTONOMOUS → auto-apply safe ones."""

    #: (proposal_type, op) pairs that are always rejected.
    DANGEROUS = {
        "TOOL_CONFIGURATION:delete",
        "GOAL_ADJUSTMENT:abandon_root",
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
