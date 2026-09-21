"""AXR-11 durable regression: safe execution boundary + cycle recovery (package 6).

Acceptance (round_007, from round_001 §AXR-11 Regression check): a wrong
path type and a custom validator that raises must each return an
unsuccessful result and release the busy state; correcting/removing the
malformed rule lets the next valid action actually execute; an exception
elsewhere in the cycle (not just tool execution) releases the busy state;
intentional PAUSED/TERMINATED transitions are preserved by recovery.

Replaces sandbox/consistency_enforcement/round_001_review_probes.py::
test_axr11_validation_exception_leaves_agent_busy (observation probe retired
per D4 — never gated in CI). All fixtures hermetic (temp dirs, no network).
"""

from __future__ import annotations

import os
import tempfile

import pytest

os.environ["PYTHON_DOTENV_DISABLED"] = "1"
os.environ["LLAMA_CPP_MODELS_CACHE_PATH"] = tempfile.gettempdir()
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def refused(*args, **kwargs):
        raise AssertionError("regression tests must not open network connections")

    monkeypatch.setattr("socket.socket.connect", refused)
    monkeypatch.setattr("socket.create_connection", refused)


def _rule(condition="true", action_type=None, **parameters):
    from agentx.agent.types import ActionType, PolicyAction, PolicyRule

    return PolicyRule(
        id="review-rule",
        condition_expr=condition,
        action=PolicyAction(action_type or ActionType.EXECUTE_TOOL, parameters),
    )


def _agent_config(path, agent_id="review-agent"):
    from agentx.agent.types import AgentConfig, MemoryConfig

    return AgentConfig(
        id=agent_id,
        memory_config=MemoryConfig(persistent_path=str(path)),
        sandbox_root=str(path),
    )


class TestAxr11SafeExecutionAndRecovery:
    def test_raising_validator_returns_unsuccessful_result(self):
        from agentx.agent.model.tools.registry import ToolRegistry
        from agentx.agent.model.tools.spec import (
            ActuatorSchema,
            IActuator,
            JsonSchema,
        )
        from agentx.agent.types import ActuatorCommand

        class BoomValidator(IActuator):
            id = "boom"

            def get_actuator_schema(self):
                return ActuatorSchema(
                    actuator_id="boom",
                    description="validator that raises",
                    input_schema=JsonSchema(type="object"),
                    output_schema=JsonSchema(type="object"),
                )

            def validate(self, command):
                raise RuntimeError("kaboom")

            def act(self, command):
                raise AssertionError("must not reach act()")

        registry = ToolRegistry()
        registry.register_actuator(BoomValidator())
        result = registry.execute_safely(
            ActuatorCommand(
                actuator_id="boom", action="read", parameters={"path": "x"}
            )
        )
        assert result.success is False
        assert "boom" in result.error and "kaboom" in result.error

    def test_wrong_path_type_is_an_actionable_validation_error(self, tmp_path):
        from agentx.agent.model.tools.filesystem_tool import FileSystemTool
        from agentx.agent.model.tools.registry import ToolRegistry
        from agentx.agent.types import ActuatorCommand

        registry = ToolRegistry()
        registry.register_actuator(FileSystemTool(sandbox_root=tmp_path))
        result = registry.execute_safely(
            ActuatorCommand(
                actuator_id="filesystem", action="read", parameters={"path": 123}
            )
        )
        assert result.success is False
        assert "'path' must be a string or Path, got int" in result.error

    def test_malformed_policy_no_longer_strands_agent(self, tmp_path):
        from agentx.agent.controller.agent_controller import AgentController
        from agentx.agent.model.agent import Agent
        from agentx.agent.types import AgentState

        agent = Agent(_agent_config(tmp_path))
        assert agent.update_policy(
            _rule(tool_id="filesystem", action="read", path=123)
        )
        controller = AgentController(agent)
        assert controller.send_message("read a file") is True  # no raise
        assert agent.state == AgentState.PERCEIVING  # busy released
        assert not controller.is_running
        assert controller.send_message("try again") is True  # not blocked

    def test_next_valid_action_executes_after_correcting_rule(self, tmp_path):
        from agentx.agent.controller.agent_controller import AgentController
        from agentx.agent.model.agent import Agent

        (tmp_path / "note.txt").write_text("payload")
        agent = Agent(_agent_config(tmp_path))
        assert agent.update_policy(
            _rule(tool_id="filesystem", action="read", path=123)
        )
        controller = AgentController(agent)
        assert controller.send_message("read a file") is True  # failed result
        # correct the malformed rule
        assert agent.update_policy(
            _rule(tool_id="filesystem", action="read", path="note.txt")
        )
        fs = agent.tool_registry.get_actuator("filesystem")
        executed = []
        original_act = fs.act
        fs.act = lambda command: (executed.append(1), original_act(command))[1]
        assert controller.send_message("read it now") is True
        assert executed == [1]  # the valid action actually executed

    def test_exception_elsewhere_in_cycle_releases_busy(self, tmp_path):
        from agentx.agent.controller.agent_controller import AgentController
        from agentx.agent.model.agent import Agent
        from agentx.agent.types import AgentState

        agent = Agent(_agent_config(tmp_path))
        controller = AgentController(agent)
        original_decide = agent.decide
        calls = []

        def one_shot_decide():
            calls.append(1)
            if len(calls) == 1:
                raise RuntimeError("decide exploded")
            return original_decide()

        agent.decide = one_shot_decide
        with pytest.raises(RuntimeError):  # error stays visible (re-raised)
            controller.send_message("hello")
        assert agent.state == AgentState.PERCEIVING  # released
        assert not controller.is_running
        assert controller.send_message("again") is True  # later turn not blocked
        assert len(calls) == 2

    def test_intentional_pause_is_preserved_by_recovery(self, tmp_path):
        from agentx.agent.model.agent import Agent
        from agentx.agent.types import AgentState

        agent = Agent(_agent_config(tmp_path))

        def pausing_decide():
            agent.state = AgentState.PAUSED
            raise RuntimeError("died mid-pause")

        agent.decide = pausing_decide
        with pytest.raises(RuntimeError):
            agent.run_cycle()
        assert agent.state == AgentState.PAUSED  # NOT overwritten by recovery

    def test_intentional_termination_is_preserved_by_recovery(self, tmp_path):
        from agentx.agent.model.agent import Agent
        from agentx.agent.types import AgentState

        agent = Agent(_agent_config(tmp_path))

        def terminating_decide():
            agent.state = AgentState.TERMINATED
            raise RuntimeError("died mid-termination")

        agent.decide = terminating_decide
        with pytest.raises(RuntimeError):
            agent.run_cycle()
        assert agent.state == AgentState.TERMINATED  # NOT overwritten
