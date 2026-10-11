"""Shared fixtures for feature_007 agent tests."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from agentx.agent.types import (
    AgentConfig,
    AutonomyLevel,
    MemoryConfig,
)


@pytest.fixture()
def tmp_agent_dir():
    """Temp directory for agent persistence (db + sandbox)."""
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture()
def agent_config(tmp_agent_dir):
    """Minimal AgentConfig pointing at a temp directory."""
    sandbox = Path(tmp_agent_dir) / "sandbox"
    sandbox.mkdir()
    return AgentConfig(
        id="test-agent",
        name="Test Agent",
        memory_config=MemoryConfig(persistent_path=tmp_agent_dir),
        autonomy_level=AutonomyLevel.FULLY_AUTONOMOUS,
        sandbox_root=str(sandbox),
    )


@pytest.fixture()
def sandbox_dir(tmp_agent_dir):
    """Sandbox directory for FileSystemTool tests."""
    sandbox = Path(tmp_agent_dir) / "sandbox"
    sandbox.mkdir(exist_ok=True)
    return sandbox
