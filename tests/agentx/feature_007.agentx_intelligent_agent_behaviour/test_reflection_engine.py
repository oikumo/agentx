from __future__ import annotations

import uuid

from agentx.agent.model.reflection.critique_parser import CritiqueParser
from agentx.agent.model.reflection.safety_evaluator import DefaultSafetyEvaluator
from agentx.agent.model.reflection.proposal_router import ProposalRouter
from agentx.agent.model.reflection.engine import ReflectionEngine
from agentx.agent.model.policy.evaluator import PolicyEngine
from agentx.agent.model.memory.manager import MemoryManager
from agentx.agent.model.goal.manager import GoalManager
from agentx.agent.model.tools.registry import ToolRegistry
from agentx.agent.types import (
    AutonomyLevel,
    Critique,
    DecisionTrace,
    Proposal,
    ProposalStatus,
    ProposalType,
    PolicyContext,
    AgentState,
    EnvironmentModel,
    Goal,
    GoalStatus,
)


class TestCritiqueParser:
    def test_parse_valid_json(self):
        raw = """```json
        {
            "critique": {
                "summary": "good",
                "strengths": ["fast"],
                "weaknesses": ["risky"],
                "confidence": "High"
            },
            "proposals": [
                {"type": "POLICY_CHANGE", "content": {}, "rationale": "try this"}
            ]
        }
        ```"""
        parser = CritiqueParser()
        entry = parser.parse(raw, DecisionTrace(agent_id="a1"))
        assert entry.critique.summary == "good"
        assert entry.critique.strengths == ["fast"]
        assert entry.critique.confidence == 0.9
        assert len(entry.proposals) == 1
        assert entry.proposals[0].type == ProposalType.POLICY_CHANGE

    def test_parse_garbage_degrades_gracefully(self):
        parser = CritiqueParser()
        entry = parser.parse("not json at all", DecisionTrace(agent_id="a1"))
        assert entry.critique.confidence == 0.0
        assert "unparseable" in entry.critique.summary
        assert len(entry.proposals) == 0

    def test_parse_unknown_proposal_type_skipped(self):
        raw = '{"critique": {"summary": "ok"}, "proposals": [{"type": "BOGUS", "content": {}, "rationale": "x"}]}'
        parser = CritiqueParser()
        entry = parser.parse(raw, DecisionTrace(agent_id="a1"))
        assert len(entry.proposals) == 0

    def test_parse_numeric_confidence(self):
        raw = '{"critique": {"summary": "ok", "confidence": 0.75}, "proposals": []}'
        parser = CritiqueParser()
        entry = parser.parse(raw, DecisionTrace(agent_id="a1"))
        assert entry.critique.confidence == 0.75

    def test_parse_empty_string(self):
        parser = CritiqueParser()
        entry = parser.parse("", DecisionTrace(agent_id="a1"))
        assert entry.critique.confidence == 0.0


class TestSafetyEvaluator:
    def test_supervised_needs_confirmation(self):
        evaluator = DefaultSafetyEvaluator()
        proposal = Proposal(type=ProposalType.POLICY_CHANGE, content={})
        ctx = PolicyContext(autonomy_level=AutonomyLevel.SUPERVISED)
        verdict = evaluator.evaluate(proposal, ctx)
        assert verdict.status == ProposalStatus.NEEDS_CONFIRMATION

    def test_autonomous_approved(self):
        evaluator = DefaultSafetyEvaluator()
        proposal = Proposal(type=ProposalType.POLICY_CHANGE, content={})
        ctx = PolicyContext(autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS)
        verdict = evaluator.evaluate(proposal, ctx)
        assert verdict.status == ProposalStatus.APPROVED

    def test_dangerous_rejected(self):
        evaluator = DefaultSafetyEvaluator()
        proposal = Proposal(
            type=ProposalType.TOOL_CONFIGURATION,
            content={"op": "delete"},
        )
        ctx = PolicyContext(autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS)
        verdict = evaluator.evaluate(proposal, ctx)
        assert verdict.status == ProposalStatus.REJECTED

    def test_abandon_root_rejected(self):
        evaluator = DefaultSafetyEvaluator()
        proposal = Proposal(
            type=ProposalType.GOAL_ADJUSTMENT,
            content={"op": "abandon_root"},
        )
        ctx = PolicyContext(autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS)
        verdict = evaluator.evaluate(proposal, ctx)
        assert verdict.status == ProposalStatus.REJECTED


class TestProposalRouter:
    def _setup(self):
        policy = PolicyEngine()
        memory = MemoryManager()
        goals = GoalManager()
        tools = ToolRegistry()
        return ProposalRouter(policy=policy, memory=memory, goals=goals, tools=tools)

    def test_route_memory_update(self):
        router = self._setup()
        proposal = Proposal(
            type=ProposalType.MEMORY_UPDATE,
            content={"note": "learned", "importance": 0.7},
        )
        outcome = router.route(proposal)
        assert outcome.status == ProposalStatus.APPLIED
        assert outcome.token is not None

    def test_route_policy_change(self):
        router = self._setup()
        proposal = Proposal(
            type=ProposalType.POLICY_CHANGE,
            content={"id": "p1", "condition": "true", "priority": 500},
        )
        outcome = router.route(proposal)
        assert outcome.status == ProposalStatus.APPLIED

    def test_route_revert_memory(self):
        router = self._setup()
        proposal = Proposal(
            type=ProposalType.MEMORY_UPDATE,
            content={"note": "temp"},
        )
        outcome = router.route(proposal)
        assert outcome.token is not None
        router.revert(ProposalType.MEMORY_UPDATE, outcome.token)
        # After revert, memory should be empty
        from agentx.agent.types import MemoryQuery

        assert len(router._memory.retrieve(MemoryQuery(limit=100))) == 0  # noqa: SLF001


class TestReflectionEngine:
    def test_reflect_without_ai_service(self):
        engine = ReflectionEngine()
        entry = engine.reflect(DecisionTrace(agent_id="a1"), PolicyContext())
        assert "disabled" in entry.critique.summary
        assert len(engine.get_log()) == 1

    def test_reflect_with_ai_service(self):
        class FakeAI:
            def complete(self, prompt: str) -> str:
                return '{"critique": {"summary": "ok", "confidence": 0.8}, "proposals": []}'

        from agentx.agent.interfaces import IAIServicePartner

        IAIServicePartner.register(FakeAI)
        engine = ReflectionEngine(ai_service=FakeAI())  # type: ignore[arg-type]
        entry = engine.reflect(DecisionTrace(agent_id="a1"), PolicyContext())
        assert entry.critique.summary == "ok"
        assert entry.critique.confidence == 0.8


class TestReflectionEngineAI:
    """Test reflection with real AI service (or failures)."""

    def test_reflect_ai_service_fails_shows_clear_message(self) -> None:
        """Reflection engine shows "AI service unavailable: ..." when LLM call fails."""
        from unittest.mock import Mock
        from agentx.agent.types import DecisionTrace, PolicyContext

        mock_ai = Mock()
        mock_ai.complete.side_effect = RuntimeError("API key not set")
        
        engine = ReflectionEngine(ai_service=mock_ai)
        trace = DecisionTrace(agent_id="test_agent")
        entry = engine.reflect(trace=trace, ctx=PolicyContext())
        assert entry.critique.summary.startswith("(AI service unavailable: ")
        assert "API key not set" in entry.critique.summary
        assert len(entry.critique.weaknesses) == 1
        assert "AI service not configured or unreachable" in entry.critique.weaknesses[0]
        assert entry.critique.confidence == 0.0
        assert not entry.proposals
