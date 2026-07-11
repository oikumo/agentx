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
    ProposalType,
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
        # C2 (feature_015): derive op from the proposal's content shape, not
        # the untrusted 'op' field.  Previously the deny-list was dead code
        # because 'op' was never set by the proposal router for 3 of 4 types.
        op = self._infer_op(proposal)
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

    @staticmethod
    def _infer_op(proposal: Proposal) -> str:
        """Infer the operation from the proposal's content shape (C2).

        Derives the op from the content keys (primary signal) so a malicious
        or malformed proposal cannot bypass the deny-list by omitting or
        mislabelling ``op``.  Falls back to the ``op`` field for backward
        compatibility with callers that set it explicitly.
        """
        content = proposal.content
        ptype = proposal.type
        if ptype == ProposalType.POLICY_CHANGE:
            if content.get("enabled") is False:
                return "disable"
            return content.get("op", "update")
        if ptype == ProposalType.MEMORY_UPDATE:
            if content.get("delete_all") or content.get("clear"):
                return "delete_all"
            return content.get("op", "add")
        if ptype == ProposalType.GOAL_ADJUSTMENT:
            status = str(content.get("status", "")).upper()
            if status == "ABANDONED":
                return "abandon_root"
            if status == "DELETED":
                return "delete"
            if content.get("priority") is not None:
                try:
                    if int(content.get("priority", 0)) < 0:
                        return "demote"
                except (TypeError, ValueError):
                    pass
            # Fall back to op field for backward compat with explicit callers.
            op = content.get("op", "")
            if op in ("abandon_root", "delete", "demote"):
                return op
            return "update"
        if ptype == ProposalType.TOOL_CONFIGURATION:
            return content.get("op", "noop")
        return content.get("op", "")
