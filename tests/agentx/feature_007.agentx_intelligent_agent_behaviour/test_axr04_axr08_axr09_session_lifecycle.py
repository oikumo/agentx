"""AXR-04/08/09 durable regression: one session-ownership contract (package 4).

Acceptance (sandbox/consistency_enforcement/round_005_package_04_session_lifecycle.md
§Result, user picked A): ``session.py`` backs up ``current`` then creates the
replacement AT ``current`` (startup contract), refuses the transition on backup
failure, and rolls back if replacement creation fails; ``NewSessionCommand``
invalidates ``MainController``'s cached agent controllers; per-session per-mode
stable ids ``agent``/``fast_agent`` (PID is execution metadata only);
``load_latest_snapshot`` adopts the latest per-mode legacy ``agent_<pid>`` id via
``_adopt_identity`` (``SELECT_LATEST_AGENT_ID_BY_PREFIX`` with ESCAPE'd prefixes
so mode families never overlap); ``start_session`` rebuilds db/repositories/
subsystems/tools and swaps atomically (carry-over = AI service only), raising
pre-swap on B-init failure.

Replaces sandbox/consistency_enforcement/round_001_review_probes.py::
test_axr04_new_session_undefined_helper,
test_axr04_helper_only_patch_does_not_restore_restart,
test_axr08_pid_change_loses_snapshot_selection (x2 modes),
test_axr09_start_session_retains_database_and_goals (observation probes retired
per D4 — never gated in CI). All fixtures hermetic (temp dirs, real SQLite,
fake AI services, no network, no live terminal input).

NOTE: ``GoalTree.nodes`` is a dict keyed by id — tests iterate ``.values()``.
"""

from __future__ import annotations

import os
import socket
import sqlite3
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock

import pytest

os.environ["PYTHON_DOTENV_DISABLED"] = "1"
os.environ["LLAMA_CPP_MODELS_CACHE_PATH"] = tempfile.gettempdir()
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def refused(*args, **kwargs):
        raise AssertionError("regression tests must not open network connections")

    monkeypatch.setattr(socket.socket, "connect", refused)
    monkeypatch.setattr(socket, "create_connection", refused)


def _agent_config(path, agent_id="agent"):
    from agentx.agent.types import AgentConfig, MemoryConfig

    return AgentConfig(
        id=agent_id,
        memory_config=MemoryConfig(persistent_path=str(path)),
        sandbox_root=str(path),
    )


def _mock_ai_service(monkeypatch):
    """Mirror the axr08 probe: stub AIServiceAdapter so no real LLM is built."""
    from agentx.agent.model import ai_adapter

    monkeypatch.setattr(ai_adapter, "AIServiceAdapter", Mock())


def _goal_descriptions(agent) -> set[str]:
    # GoalTree.nodes is a dict keyed by id — iterate .values().
    return {goal.description for goal in agent.list_goals().nodes.values()}


def _seed_legacy_goal(path, legacy_id, description):
    """Persist one goal under a legacy PID-derived id; returns the agent."""
    from agentx.agent.model.agent import Agent

    agent = Agent(_agent_config(path, legacy_id))
    agent.submit_goal(agent.goal_manager.create_goal(description))
    assert agent.persist()
    return agent


def test_legacy_adoption_resumes_goals(tmp_path, monkeypatch):
    """A saved legacy ``agent_<pid>`` snapshot is adopted as the stable
    identity and its goals recover on resume."""
    from agentx.agent.adapter import AgentAdapter

    _mock_ai_service(monkeypatch)
    _seed_legacy_goal(tmp_path, "agent_101", "legacy-goal")

    agent, _controller = AgentAdapter.create_agent(
        _agent_config(tmp_path, "agent"), ai_service=Mock(), resume=True
    )
    assert agent.id == "agent_101"
    assert agent.config.id == "agent_101"
    assert "legacy-goal" in _goal_descriptions(agent)


def test_unrelated_legacy_candidates_resolve_to_latest(tmp_path, monkeypatch):
    """Several legacy candidates -> the latest ``agent_202``-style id wins
    deterministically (ORDER BY timestamp DESC)."""
    from agentx.agent.model.agent import Agent

    _mock_ai_service(monkeypatch)
    _seed_legacy_goal(tmp_path, "agent_201", "goal-201")
    time.sleep(0.02)  # keep snapshot timestamps distinct for deterministic order
    _seed_legacy_goal(tmp_path, "agent_202", "goal-202")

    fresh = Agent(_agent_config(tmp_path, "agent"))
    snapshot = fresh.load_latest_snapshot()
    assert snapshot is not None
    assert snapshot.agent_id == "agent_202"
    assert fresh.id == "agent_202"
    fresh.resume_session(snapshot.snapshot_id)
    descriptions = _goal_descriptions(fresh)
    assert "goal-202" in descriptions
    assert "goal-201" not in descriptions


def test_per_mode_isolation_never_cross_adopts(tmp_path, monkeypatch):
    """``fast_agent`` never adopts ``agent_*`` rows (and vice versa) — the
    ESCAPE'd ``agent\\_%`` / ``fast_agent\\_%`` families never overlap."""
    from agentx.agent.model.agent import Agent

    _mock_ai_service(monkeypatch)
    _seed_legacy_goal(tmp_path, "agent_101", "agent-goal")
    time.sleep(0.02)
    _seed_legacy_goal(tmp_path, "fast_agent_101", "fast-goal")

    stable_agent = Agent(_agent_config(tmp_path, "agent"))
    snapshot = stable_agent.load_latest_snapshot()
    assert snapshot is not None
    assert snapshot.agent_id == "agent_101"
    stable_agent.resume_session(snapshot.snapshot_id)
    assert _goal_descriptions(stable_agent) == {"agent-goal"}

    stable_fast = Agent(_agent_config(tmp_path, "fast_agent"))
    snapshot = stable_fast.load_latest_snapshot()
    assert snapshot is not None
    assert snapshot.agent_id == "fast_agent_101"
    stable_fast.resume_session(snapshot.snapshot_id)
    assert _goal_descriptions(stable_fast) == {"fast-goal"}


def test_restart_recovers_agent_mode_goals(tmp_path, monkeypatch):
    """A PID change across restarts still recovers agent-mode goals — the id
    is the stable ``agent``, never ``agent_<pid>``."""
    from agentx.agent.model import ai_adapter
    from agentx.model.session import session
    from agentx.ui.screens.main.main_controller import MainController

    monkeypatch.setattr(session, "SESSION_DEFAULT_BASE_DIRECTORY", str(tmp_path))
    monkeypatch.setattr(ai_adapter, "AIServiceAdapter", Mock())
    monkeypatch.setattr(os, "getpid", lambda: 101)
    first = MainController(view=Mock())
    first.show_agent()
    controller = first.get_agent_controller()
    controller.submit_goal("saved-goal")
    assert controller._agent.persist()  # noqa: SLF001

    monkeypatch.setattr(os, "getpid", lambda: 102)
    second = MainController(view=Mock())
    second.show_agent()
    resumed = second.get_agent_controller()._agent  # noqa: SLF001
    assert resumed.id == "agent"
    assert "saved-goal" in _goal_descriptions(resumed)


def test_restart_recovers_fast_agent_mode_goals(tmp_path, monkeypatch):
    """Same restart contract for fast_agent mode."""
    from agentx.agent.model import ai_adapter
    from agentx.model.session import session
    from agentx.ui.screens.main.main_controller import MainController

    monkeypatch.setattr(session, "SESSION_DEFAULT_BASE_DIRECTORY", str(tmp_path))
    monkeypatch.setattr(ai_adapter, "AIServiceAdapter", Mock())
    monkeypatch.setattr(os, "getpid", lambda: 101)
    first = MainController(view=Mock())
    first.show_fast_agent()
    controller = first.get_fast_agent_controller()
    controller.submit_goal("saved-fast-goal")
    assert controller._agent.persist()  # noqa: SLF001

    monkeypatch.setattr(os, "getpid", lambda: 102)
    second = MainController(view=Mock())
    second.show_fast_agent()
    resumed = second.get_fast_agent_controller()._agent  # noqa: SLF001
    assert resumed.id == "fast_agent"
    assert "saved-fast-goal" in _goal_descriptions(resumed)


def test_start_session_fresh_switch_and_a_reopenable(tmp_path, monkeypatch):
    """A->B is a fresh switch (B db, empty goals, B sandbox, AI service
    carried over) while A stays reopenable with its original data."""
    from agentx.agent.adapter import AgentAdapter
    from agentx.agent.model.agent import Agent

    _mock_ai_service(monkeypatch)
    first, second = tmp_path / "a", tmp_path / "b"
    agent = Agent(_agent_config(first, "old-agent"))
    agent.submit_goal(agent.goal_manager.create_goal("old-goal"))
    assert agent.persist()
    sentinel = Mock()
    agent.set_ai_service(sentinel)

    new_id = agent.start_session(_agent_config(second, "new-agent"))
    assert new_id == "new-agent"
    assert agent._ai_service is sentinel  # noqa: SLF001 — carry-over = AI service only
    assert Path(agent._db.path).parent == Path(str(second))  # noqa: SLF001 — storage in B
    assert agent._db.path.endswith("agent_session.db")  # noqa: SLF001
    assert not agent.list_goals().nodes  # fresh state, old goals do not ride along
    filesystem = agent.tool_registry.get_actuator("filesystem")
    assert Path(filesystem._root).resolve() == second.resolve()  # noqa: SLF001

    # Writes land only in B.
    agent.submit_goal(agent.goal_manager.create_goal("new-goal"))
    assert agent.persist()
    assert (second / "agent_session.db").exists()

    # A reopens with its original data and none of B's.
    reopened, _controller = AgentAdapter.create_agent(
        _agent_config(first, "old-agent"), ai_service=Mock(), resume=True
    )
    descriptions = _goal_descriptions(reopened)
    assert "old-goal" in descriptions
    assert "new-goal" not in descriptions


def test_failed_switch_leaves_agent_intact(tmp_path, monkeypatch):
    """B-init failure raises pre-swap — the old session stays fully usable
    (identity, goals, storage unchanged)."""
    from agentx.agent.model.agent import Agent

    _mock_ai_service(monkeypatch)
    first, second = tmp_path / "a", tmp_path / "b"
    agent = Agent(_agent_config(first, "live-agent"))
    agent.submit_goal(agent.goal_manager.create_goal("live-goal"))
    assert agent.persist()
    registry_before = agent.tool_registry

    monkeypatch.setattr(
        Agent,
        "_register_builtin_tools",
        Mock(side_effect=RuntimeError("synthetic B-init failure")),
    )
    with pytest.raises(RuntimeError, match="synthetic B-init failure"):
        agent.start_session(_agent_config(second, "new-agent"))

    assert agent.id == "live-agent"
    assert agent.config.id == "live-agent"
    assert Path(agent._db.path).parent == first  # noqa: SLF001 — storage still A
    assert agent.tool_registry is registry_before
    assert "live-goal" in _goal_descriptions(agent)
    assert agent.persist()  # still persists to the live session
    assert (first / "agent_session.db").exists()


def test_new_command_end_to_end(tmp_path, monkeypatch):
    """``new`` end-to-end — backup keeps old history, replacement is created
    AT ``current`` (not ``current_<ts>``), accepts + reopens new history,
    cached agent controllers are invalidated, and the rebuild lands on the
    replacement storage + sandbox."""
    from agentx.agent.model import ai_adapter
    from agentx.model.session import session
    from agentx.ui.screens.main.commands.commands import NewSessionCommand
    from agentx.ui.screens.main.main_controller import MainController

    monkeypatch.setattr(session, "SESSION_DEFAULT_BASE_DIRECTORY", str(tmp_path))
    monkeypatch.setattr(ai_adapter, "AIServiceAdapter", Mock())
    controller = MainController(view=Mock(), provider=None)
    manager = controller.get_session_manager()
    assert manager.get_current_session().insert_history_entry("old-history")

    # Warm the session-scoped caches against the old session.
    controller.show_agent()
    controller.show_fast_agent()
    old_agent_controller = controller.get_agent_controller()
    old_fast_controller = controller.get_fast_agent_controller()
    assert old_agent_controller is not None
    assert old_fast_controller is not None
    old_agent_controller.submit_goal("old-agent-goal")
    assert old_agent_controller._agent.persist()  # noqa: SLF001
    old_session_dir = manager.get_current_session().directory

    NewSessionCommand("new", controller).run([])

    current = manager.get_current_session()
    assert Path(current.directory).name == "current"
    assert current.directory == old_session_dir  # replacement AT current

    backups = [d for d in tmp_path.iterdir() if d.name.startswith("current_backup_")]
    assert len(backups) == 1
    with sqlite3.connect(backups[0] / "session.db") as conn:
        backup_commands = [row[0] for row in conn.execute("SELECT command FROM history")]
    assert "old-history" in backup_commands

    # Cached agent controllers invalidated.
    assert controller.get_agent_controller() is None
    assert controller.get_fast_agent_controller() is None

    # Replacement accepts new history and a reopen sees it.
    assert current.insert_history_entry("new-history")
    reopened = session.Session()
    assert [entry.command for entry in reopened.select_history_entry()] == ["new-history"]

    # Rebuilt agent lands on the replacement storage + sandbox, starting fresh.
    controller.show_agent()
    rebuilt = controller.get_agent_controller()._agent  # noqa: SLF001
    assert Path(rebuilt._db.path).parent == Path(current.directory)  # noqa: SLF001
    filesystem = rebuilt.tool_registry.get_actuator("filesystem")
    assert Path(filesystem._root).resolve() == Path(current.directory).resolve()  # noqa: SLF001
    assert not rebuilt.list_goals().nodes


def test_backup_failure_refuses_transition(tmp_path, monkeypatch):
    """Backup failure raises/refuses — the old session stays fully usable
    (directory, history, writability intact; no backup taken)."""
    from agentx.model.session import session

    monkeypatch.setattr(session, "SESSION_DEFAULT_BASE_DIRECTORY", str(tmp_path))
    original = session.Session()
    assert original.insert_history_entry("old-history")
    old_directory = original.directory

    monkeypatch.setattr(session.Session, "backup_current_session", lambda self: None)
    with pytest.raises(RuntimeError, match="back up"):
        original.create_new_session()

    assert original.is_created()
    assert original.directory == old_directory
    assert Path(old_directory).is_dir()
    assert [entry.command for entry in original.select_history_entry()] == ["old-history"]
    assert original.insert_history_entry("still-usable")
    assert [entry.command for entry in original.select_history_entry()] == [
        "old-history",
        "still-usable",
    ]
    assert not [d for d in tmp_path.iterdir() if d.name.startswith("current_backup_")]
