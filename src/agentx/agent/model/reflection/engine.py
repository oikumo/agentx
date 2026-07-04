"""ReflectionEngine — turns completed decide→act cycles into self-improvement (design §8).

After each cycle it builds a :class:`DecisionTrace`, asks the AI (via
:class:`IAIServicePartner`) to critique it, parses the JSON response into
:class:`Critique` + ``Proposal[]``, runs a safety gate, and routes approved
proposals to the right subsystem.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from agentx.agent.interfaces import IAIServicePartner, ISafetyEvaluator
from agentx.agent.model.reflection.critique_parser import CritiqueParser
from agentx.agent.model.reflection.proposal_router import ProposalRouter
from agentx.agent.types import (
    AutonomyLevel,
    Critique,
    DecisionTrace,
    PolicyContext,
    Proposal,
    ProposalOutcome,
    ProposalStatus,
    ProposalVerdict,
    ReflectionEntry,
)

_log = logging.getLogger(__name__)

_CRITIQUE_PROMPT = """\
You are an AI critic reviewing an agent's decision trace.

Decision Trace:
- Perception: {perception}
- Decision: {decision}
- Action: {action}
- Outcome: {outcome}
- Goal: {goal}

Critique Requirements:
1. Strengths: Identify 1-3 positive aspects
2. Weaknesses: Identify 1-3 flaws/risks
3. Confidence: High/Medium/Low
4. Recommendations: 1-3 actionable improvements

Response Format (JSON):
```json
{{
    "critique": {{
        "summary": "str",
        "strengths": ["str"],
        "weaknesses": ["str"],
        "confidence": "High|Medium|Low"
    }},
    "proposals": [
        {{"type": "POLICY_CHANGE", "content": {{}}, "rationale": "str"}}
    ]
}}
```
"""


class ReflectionEngine:
    """Orchestrates critique → parse → safety → routing."""

    def __init__(
        self,
        ai_service: IAIServicePartner | None = None,
        safety_evaluator: ISafetyEvaluator | None = None,
        router: ProposalRouter | None = None,
    ) -> None:
        self._ai = ai_service
        self._safety = safety_evaluator
        self._router = router
        self._parser = CritiqueParser()
        self._entries: list[ReflectionEntry] = []

    def set_router(self, router: ProposalRouter) -> None:
        self._router = router

    def reflect(
        self, trace: DecisionTrace, ctx: PolicyContext
    ) -> ReflectionEntry:
        """Run a full reflection cycle on *trace*."""
        if self._ai is None:
            entry = ReflectionEntry(
                id=str(uuid.uuid4()),
                trace=trace,
                critique=Critique(
                    summary="(reflection disabled — no AI service)",
                    confidence=0.0,
                ),
                proposals=[],
            )
            self._entries.append(entry)
            return entry

        prompt = self._render_prompt(trace)
        try:
            raw = self._ai.complete(prompt)
        except Exception as exc:  # noqa: BLE001 — reflection is non-fatal
            _log.warning("AI reflection failed: %s", exc)
            entry = ReflectionEntry(
                id=str(uuid.uuid4()),
                trace=trace,
                critique=Critique(
                    summary=f"(AI service unavailable: {exc})",
                    weaknesses=["AI service not configured or unreachable"],
                    confidence=0.0,
                ),
                proposals=[],
            )
            self._entries.append(entry)
            return entry

        entry = self._parser.parse(raw, trace)
        self._route_proposals(entry, ctx)
        self._entries.append(entry)
        return entry

    def get_log(self) -> list[ReflectionEntry]:
        return list(self._entries)

    def restore_log(self, entries: list[ReflectionEntry]) -> None:
        """Replace the in-memory reflection log (used on session resume, M2)."""
        self._entries = list(entries)

    def has_ai_service(self) -> bool:
        """True if an AI service is wired (used to skip no-op reflection, N11)."""
        return self._ai is not None

    def set_ai_service(self, ai: IAIServicePartner) -> None:
        """Wire (or re-wire) the AI service (N13: public API, not _ai reach)."""
        self._ai = ai

    # ----------------------------------------------------------- approval flow (N4)

    def pending_proposals(self) -> list[tuple[str, int, Proposal]]:
        """Return ``(entry_id, proposal_index, proposal)`` for every proposal
        currently awaiting user confirmation."""
        result: list[tuple[str, int, Proposal]] = []
        for entry in self._entries:
            for idx, proposal in enumerate(entry.proposals):
                if proposal.status == ProposalStatus.NEEDS_CONFIRMATION:
                    result.append((entry.id, idx, proposal))
        return result

    def approve_proposal(self, entry_id: str, proposal_idx: int) -> ProposalOutcome:
        """Apply a pending proposal via the router (N4: closes the loop).

        In SUPERVISED mode the safety gate marks proposals
        ``NEEDS_CONFIRMATION``; this method is the user-approved path that
        routes them for real.
        """
        for entry in self._entries:
            if entry.id != entry_id:
                continue
            if not (0 <= proposal_idx < len(entry.proposals)):
                return ProposalOutcome(status=ProposalStatus.REJECTED, reason="bad index")
            proposal = entry.proposals[proposal_idx]
            if proposal.status != ProposalStatus.NEEDS_CONFIRMATION:
                return ProposalOutcome(
                    status=ProposalStatus.REJECTED, reason=f"not pending ({proposal.status.value})"
                )
            if self._router is None:
                return ProposalOutcome(status=ProposalStatus.REJECTED, reason="no router")
            return self._router.route(proposal)
        return ProposalOutcome(status=ProposalStatus.REJECTED, reason="entry not found")

    # ----------------------------------------------------------- internals

    @staticmethod
    def _render_prompt(trace: DecisionTrace) -> str:
        perception = ", ".join(trace.perception.sensor_readings.keys()) if trace.perception else "(none)"
        decision = trace.decision.reasoning if trace.decision else "none"
        action = str(trace.action.action) if trace.action else "none"
        outcome = "success" if (trace.result and trace.result.success) else "unknown"
        goal = trace.goal_context.description if trace.goal_context else "none"
        return _CRITIQUE_PROMPT.format(
            perception=perception,
            decision=decision,
            action=action,
            outcome=outcome,
            goal=goal,
        )

    def _route_proposals(self, entry: ReflectionEntry, ctx: PolicyContext) -> None:
        if self._safety is None or self._router is None:
            # M3: surface un-routed proposals instead of silently dropping them.
            _log.warning(
                "reflection safety/router missing — %d proposal(s) left for manual review",
                len(entry.proposals),
            )
            for proposal in entry.proposals:
                if proposal.status == ProposalStatus.PROPOSED:
                    proposal.status = ProposalStatus.NEEDS_CONFIRMATION
            return
        for proposal in entry.proposals:
            verdict: ProposalVerdict = self._safety.evaluate(proposal, ctx)
            if verdict.status == ProposalStatus.REJECTED:
                proposal.status = ProposalStatus.REJECTED
                continue
            if verdict.status == ProposalStatus.NEEDS_CONFIRMATION:
                proposal.status = ProposalStatus.NEEDS_CONFIRMATION
                continue
            # APPROVED → route
            self._router.route(proposal)
