"""Observation probes for round_001_implementation_review.md; NOT fix acceptance tests.

Run separately from the normal suite, from the repository root:
    uv run pytest -q sandbox/consistency_enforcement/round_001_review_probes.py

Passing means the documented defect is still reproducible. All filesystem
writes use pytest temporary directories. Providers/retrieval are mocked,
dotenv is disabled before application imports, and network connections fail.
"""

import os
import socket
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

# Import-time configuration only; no real model or credential is needed.
os.environ["PYTHON_DOTENV_DISABLED"] = "1"
os.environ["LLAMA_CPP_MODELS_CACHE_PATH"] = tempfile.gettempdir()
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def refused(*args, **kwargs):
        raise AssertionError("Review probes must not open network connections")

    monkeypatch.setattr(socket.socket, "connect", refused)
    monkeypatch.setattr(socket, "create_connection", refused)


def rule(condition="true", action_type=None, **parameters):
    from agentx.agent.types import ActionType, PolicyAction, PolicyRule

    return PolicyRule(
        id="review-rule",
        condition_expr=condition,
        action=PolicyAction(action_type or ActionType.EXECUTE_TOOL, parameters),
    )


def agent_config(path, agent_id="review-agent"):
    from agentx.agent.types import AgentConfig, MemoryConfig

    return AgentConfig(
        id=agent_id,
        memory_config=MemoryConfig(persistent_path=str(path)),
        sandbox_root=str(path),
    )


def test_axr01_predictable_temp_symlink(tmp_path, monkeypatch):
    from agentx.model.coding import coding_tools as coding

    root = tmp_path / "sandbox"
    root.mkdir()
    monkeypatch.setattr(coding, "_sandbox_root", root)
    target = root / "file.txt"
    target.write_text("old")
    outside = tmp_path / "outside.txt"
    outside.write_text("outside-before")
    (root / "file.txt.tmp").symlink_to(outside)
    assert coding._file_edit_impl("file.txt", "old", "new").success
    assert outside.read_text() == "new"
    assert target.is_symlink()


def test_axr02_search_reads_outside_symlink(tmp_path, monkeypatch):
    from agentx.model.coding import coding_tools as coding

    root = tmp_path / "sandbox"
    root.mkdir()
    monkeypatch.setattr(coding, "_sandbox_root", root)
    outside = tmp_path / "outside.txt"
    outside.write_text("outside-sandbox-marker")
    (root / "link.txt").symlink_to(outside)
    assert "escapes sandbox" in coding._file_read_impl("link.txt").error
    result = coding._file_search_impl("*.txt")
    assert result.error is None
    assert result.matches[0].context == "outside-sandbox-marker"


def test_axr03_stale_and_invalid_replacements():
    from agentx.agent.model.policy.evaluator import PolicyEngine
    from agentx.agent.types import ActionType, PolicyContext

    engine = PolicyEngine()
    assert engine.add_rule_safely(rule())
    assert engine.add_rule_safely(rule("false"))
    assert engine.rules["review-rule"].condition_expr == "false"
    assert engine.evaluate(PolicyContext()).selected_action.type == ActionType.EXECUTE_TOOL
    assert engine.add_rule_safely(rule("@@invalid@@"))


def test_axr03_rejected_first_insertion_seeds_cache():
    from agentx.agent.model.policy.evaluator import PolicyEngine
    from agentx.agent.types import ActionType, PolicyContext

    engine = PolicyEngine()
    assert not engine.add_rule_safely(rule(**{str(i): i for i in range(11)}))
    assert not engine.rules
    assert engine.add_rule_safely(rule("false"))
    assert engine.evaluate(PolicyContext()).selected_action.type == ActionType.EXECUTE_TOOL


def test_axr03_replacement_conflicts_with_itself():
    from agentx.agent.model.policy.evaluator import PolicyEngine
    from agentx.agent.types import ActionType

    engine = PolicyEngine()
    assert engine.add_rule_safely(rule())
    assert not engine.add_rule_safely(rule(action_type=ActionType.PAUSE))


def test_axr03_failed_persistence_publishes_live_rule():
    from agentx.agent.model.policy.evaluator import PolicyEngine
    from agentx.agent.types import ActionType, PolicyContext

    repository = Mock()
    repository.save.side_effect = OSError("synthetic save failure")
    engine = PolicyEngine(repository=repository, agent_id="review-agent")
    with pytest.raises(OSError, match="synthetic save failure"):
        engine.add_rule_safely(rule())
    assert "review-rule" in engine.rules
    assert engine.evaluate(PolicyContext()).selected_action.type == ActionType.EXECUTE_TOOL


def test_axr04_new_session_undefined_helper(tmp_path, monkeypatch):
    from agentx.model.session import session

    monkeypatch.setattr(session, "SESSION_DEFAULT_BASE_DIRECTORY", str(tmp_path))
    with pytest.raises(NameError, match="is_directory_exists"):
        session.Session().create_new_session()


def test_axr04_helper_only_patch_does_not_restore_restart(tmp_path, monkeypatch):
    from agentx.model.session import session

    monkeypatch.setattr(session, "SESSION_DEFAULT_BASE_DIRECTORY", str(tmp_path))
    monkeypatch.setattr(
        session, "is_directory_exists", session.utils_directories.is_directory_exists,
        raising=False,
    )
    original = session.Session()
    assert original.insert_history_entry("old-history")
    replacement = original.create_new_session()
    assert replacement.insert_history_entry("new-history")
    assert Path(replacement.directory).name.startswith("current_")
    assert replacement.select_history_entry()[0].command == "new-history"
    reopened = session.Session()
    assert Path(reopened.directory).name == "current"
    assert not reopened.select_history_entry()


def test_axr05_service_tool_omits_backend(tmp_path, monkeypatch):
    from agentx.model.rag_v2 import rag_v2_agent_service as service
    from agentx.model.rag_v2.query import rag_v2_retriever as retrieval

    monkeypatch.setattr(service, "_DEEPAGENTS_AVAILABLE", True)
    monkeypatch.setattr(service, "create_deep_agent", Mock())
    monkeypatch.setattr(service, "create_summarization_tool_middleware", Mock())
    monkeypatch.setattr(retrieval, "build_retriever", lambda path: lambda q, k: [
        ("c0", "retrieved content", 0.9, "doc.md", None, 1),
    ])
    backend = Mock()
    instance = service.RagV2AgentService(str(tmp_path), llm=Mock(), backend=backend)
    search = next(tool for tool in instance._tools if tool.name == "search_documents")
    result = search.invoke({"query": "q"})
    assert len(result.hits) == 1 and result.chunks_uploaded == 0 and result.error is None
    backend.upload_files.assert_not_called()


def test_axr05_failed_upload_reported_successfully():
    from deepagents.backends.protocol import FileUploadResponse
    from agentx.model.rag_v2.rag_v2_tools import _search_documents_impl

    backend = Mock()
    backend.upload_files.return_value = [
        FileUploadResponse(path="chunk_0.txt", error="permission_denied"),
    ]
    result = _search_documents_impl(
        "q", "unused", backend=backend,
        _retriever=lambda q, k: [("c0", "content", 0.9)],
    )
    assert result.chunks_uploaded == 1 and result.error is None


@pytest.mark.parametrize("stage", ["factory", "upload"])
def test_axr05_setup_and_upload_exceptions_escape(stage, monkeypatch):
    from agentx.model.rag_v2 import rag_v2_tools as rag
    from agentx.model.rag_v2.query import rag_v2_retriever as retrieval

    failure = Mock(side_effect=RuntimeError("synthetic review failure"))
    with pytest.raises(RuntimeError, match="synthetic review failure"):
        if stage == "factory":
            monkeypatch.setattr(retrieval, "build_retriever", failure)
            rag.build_rag_v2_tools("unused")[0].invoke({"query": "q"})
        else:
            rag._search_documents_impl(
                "q", "unused", backend=SimpleNamespace(upload_files=failure),
                _retriever=lambda q, k: [("c0", "content", 0.9)],
            )


def test_axr05_real_graph_path_normalization_and_overwrite():
    from deepagents.backends import StateBackend
    from deepagents.middleware.filesystem import FilesystemState, validate_path
    from langgraph.graph import END, START, StateGraph
    from agentx.model.rag_v2.rag_v2_tools import _search_documents_impl

    backend = StateBackend()

    def probe(state):
        for content in ("first-search", "second-search"):
            result = _search_documents_impl(
                "q", "unused", backend=backend,
                _retriever=lambda q, k: [("c0", content, 0.9)],
            )
            assert result.chunks_uploaded == 1
            assert backend.read("chunk_0.txt").error is None
            assert backend.download_files(["chunk_0.txt"])[0].content == content.encode()
            assert validate_path("chunk_0.txt") == "/chunk_0.txt"
            assert backend.read(validate_path("chunk_0.txt")).error is not None
        return {}

    graph = StateGraph(FilesystemState)
    graph.add_node("probe", probe)
    graph.add_edge(START, "probe")
    graph.add_edge("probe", END)
    graph.compile().invoke({"messages": [], "files": {}})


def test_axr06_axr07_console_provider_and_persistence(tmp_path, monkeypatch):
    from agentx.model.ai.model_registry import ModelRegistry
    from agentx.model.ai.service import AIService
    from agentx.model.chat import ChatHistoryRepository
    from agentx.model.session import session
    from agentx.ui.screens.chat import chat_controller
    from agentx.ui.screens.main.main_controller import MainController
    from agentx.ui.screens.models.models_controller import ModelsController

    monkeypatch.setattr(session, "SESSION_DEFAULT_BASE_DIRECTORY", str(tmp_path / "sessions"))
    registry = ModelRegistry(config_path=tmp_path / "selection.json")
    calls = []

    def llm(name):
        def stream(history):
            calls.append(name)
            yield SimpleNamespace(content="answer")
        return SimpleNamespace(name=name, stream=stream)

    models = {name: llm(name) for name in ("openrouter", "ollama")}
    monkeypatch.setattr(registry, "create_current_llm", lambda: models[registry.get_current_id()])
    repository = ChatHistoryRepository(str(tmp_path / "chat.db"))
    monkeypatch.setattr(chat_controller, "AIService", lambda: AIService(registry))
    monkeypatch.setattr(chat_controller, "ChatHistoryRepository", lambda: repository)
    main = MainController(view=Mock(), provider=Mock())
    main.show_chat()
    chat, _ = main.get_chat_controller()
    assert ModelsController(registry).select_provider("ollama")
    main.show_chat()
    assert chat.process_user_message("review message")
    assert calls == ["openrouter"]
    assert "Ollama" in chat._format_chat_error(RuntimeError("synthetic error"))
    assert chat.current_conversation_id is None and len(chat.history) == 2
    assert not ChatHistoryRepository(str(tmp_path / "chat.db")).get_recent_conversations()


@pytest.mark.parametrize("mode", ["agent", "fast_agent"])
def test_axr08_pid_change_loses_snapshot_selection(mode, tmp_path, monkeypatch):
    from agentx.agent.model import ai_adapter
    from agentx.model.session import session
    from agentx.ui.screens.main.main_controller import MainController

    monkeypatch.setattr(session, "SESSION_DEFAULT_BASE_DIRECTORY", str(tmp_path))
    monkeypatch.setattr(ai_adapter, "AIServiceAdapter", Mock())
    monkeypatch.setattr(os, "getpid", lambda: 101)
    first = MainController(view=Mock())
    getattr(first, f"show_{mode}")()
    controller = getattr(first, f"get_{mode}_controller")()
    controller.submit_goal("saved-goal")
    assert controller._agent.persist()
    assert len(controller._agent.list_goals().nodes) == 1
    monkeypatch.setattr(os, "getpid", lambda: 102)
    second = MainController(view=Mock())
    getattr(second, f"show_{mode}")()
    resumed = getattr(second, f"get_{mode}_controller")()._agent
    assert resumed.id.endswith("102")
    assert not resumed.list_goals().nodes
    assert controller._agent.load_latest_snapshot() is not None


def test_axr09_start_session_retains_database_and_goals(tmp_path):
    from agentx.agent.model.agent import Agent

    first, second = tmp_path / "a", tmp_path / "b"
    agent = Agent(agent_config(first))
    agent.submit_goal(agent.goal_manager.create_goal("old-goal"))
    agent.start_session(agent_config(second, "second-agent"))
    assert agent.persist()
    assert Path(agent._db.path).parent == first
    assert agent.list_goals().nodes
    assert not (second / "agent_session.db").exists()
    assert agent.tool_registry.get_actuator("filesystem")._root == second


def test_axr10_pending_terminal_update_promotes_second_active():
    from agentx.agent.model.goal.manager import GoalManager
    from agentx.agent.types import GoalStatus

    manager = GoalManager()
    goals = [manager.create_goal(name) for name in ("A", "B", "C")]
    for goal in goals:
        manager.add_goal(goal)
    manager.update_status(goals[1].id, GoalStatus.ABANDONED)
    assert [g.description for g in manager.get_tree().nodes.values()
            if g.status == GoalStatus.ACTIVE] == ["A", "C"]


def test_axr11_validation_exception_leaves_agent_busy(tmp_path):
    from agentx.agent.controller.agent_controller import AgentController
    from agentx.agent.model.agent import Agent
    from agentx.agent.types import AgentState

    agent = Agent(agent_config(tmp_path))
    assert agent.update_policy(rule(tool_id="filesystem", action="read", path=123))
    controller = AgentController(agent)
    with pytest.raises(TypeError):
        controller.send_message("read a file")
    assert agent.state == AgentState.ACTING and controller.is_running
    assert controller.send_message("try again") is False


def test_axr12_guard_accepts_traversal_and_symlink(tmp_path, monkeypatch):
    from agentx.utils.utils import is_directory_allowed_to_deletion

    monkeypatch.chdir(tmp_path)
    allowed = tmp_path / "local_sessions"
    allowed.mkdir()
    outside = tmp_path / "unrelated"
    outside.mkdir()
    (allowed / "link").symlink_to(outside, target_is_directory=True)
    assert is_directory_allowed_to_deletion(str(allowed / ".." / "unrelated"))
    assert is_directory_allowed_to_deletion(str(allowed / "link"))
    with pytest.raises(PermissionError):
        is_directory_allowed_to_deletion(str(tmp_path / "local_sessions_suffix"))
