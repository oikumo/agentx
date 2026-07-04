"""Shared fixtures for feature_011 Fast Agent tests."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from agentx.agent.controller.agent_controller import AgentController
from agentx.agent.model.agent import Agent
from agentx.agent.types import AgentConfig, AutonomyLevel, MemoryConfig


@pytest.fixture()
def tmp_agent_dir():
    """Temp directory for agent persistence (db + sandbox)."""
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture()
def agent_config(tmp_agent_dir):
    """Minimal AgentConfig pointing at a temp sandbox."""
    sandbox = Path(tmp_agent_dir) / "sandbox"
    sandbox.mkdir()
    return AgentConfig(
        id="fast-test-agent",
        name="Fast Test Agent",
        memory_config=MemoryConfig(persistent_path=tmp_agent_dir),
        autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
        sandbox_root=str(sandbox),
    )


@pytest.fixture()
def wired_controller(agent_config):
    """A wired (Agent, AgentController) pair with FastAgentTUIView partner."""
    from agentx.agent.view.tui.fast_agent_view import FastAgentTUIView

    agent = Agent(agent_config)
    controller = AgentController(agent)
    controller.set_view(FastAgentTUIView())  # type: ignore[arg-type]
    return agent, controller
