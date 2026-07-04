"""CritiqueParser — parse AIService JSON into typed Critique + Proposal[] (design §8.3).

Resilient to malformed output: a failed parse degrades to a low-confidence
:class:`Critique` with zero proposals, so reflection is always non-fatal.
"""

from __future__ import annotations

import json
import re
import uuid
from typing import Any

from agentx.agent.types import (
    Critique,
    DecisionTrace,
    Proposal,
    ProposalStatus,
    ProposalType,
    ReflectionEntry,
)


class CritiqueParser:
    """Parse AI-generated JSON reflection into typed objects."""

    def parse(self, raw: str, trace: DecisionTrace) -> ReflectionEntry:
        payload = self._extract_json(raw)
        if payload is None:
            return ReflectionEntry(
                id=str(uuid.uuid4()),
                trace=trace,
                critique=Critique(
                    summary="(unparseable reflection)",
                    weaknesses=["AI returned non-JSON"],
                    confidence=0.0,
                ),
                proposals=[],
            )
        critique = self._parse_critique(payload.get("critique", {}))
        proposals = self._parse_proposals(payload.get("proposals", []))
        return ReflectionEntry(
            id=str(uuid.uuid4()),
            trace=trace,
            critique=critique,
            proposals=proposals,
        )

    # ----------------------------------------------------------- JSON extraction

    @staticmethod
    def _extract_json(raw: str) -> dict[str, Any] | None:
        """Strip ```json fences and parse; return None on failure.

        m5: the fenced regex uses a *greedy* capture so nested objects
        (``{"a": {"b": 1}}``) are not truncated at the first ``}``.
        """
        if not raw or not raw.strip():
            return None
        # strip markdown code fences
        fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, re.DOTALL)
        if fenced:
            raw = fenced.group(1)
        # try direct parse first
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
        # fall back to the outermost {...} block (greedy)
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
        return None

    @staticmethod
    def _parse_critique(data: dict[str, Any]) -> Critique:
        confidence_raw = data.get("confidence", 0.0)
        # accept "High"/"Medium"/"Low" or numeric
        if isinstance(confidence_raw, str):
            confidence_map = {"high": 0.9, "medium": 0.6, "low": 0.3}
            confidence = confidence_map.get(confidence_raw.lower(), 0.5)
        else:
            confidence = float(confidence_raw)
        return Critique(
            summary=data.get("summary", ""),
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            confidence=confidence,
        )

    @staticmethod
    def _parse_proposals(data: list[Any]) -> list[Proposal]:
        proposals: list[Proposal] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            try:
                ptype = ProposalType(item.get("type", ""))
            except ValueError:
                continue  # skip unknown proposal types
            proposals.append(
                Proposal(
                    type=ptype,
                    content=item.get("content", {}),
                    rationale=item.get("rationale", ""),
                    status=ProposalStatus.PROPOSED,
                )
            )
        return proposals
