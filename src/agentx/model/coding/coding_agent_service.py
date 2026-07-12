"""Coding agent service — wraps LangChain's create_agent for the TUI.

This is the **Model** layer for the Coding screen. It creates a LangChain
agent (via :func:`langchain.agents.create_agent`) with the user's
selected LLM, file tools, and an in-memory checkpointer for multi-turn
conversation history.

The agent is streamed via ``agent.stream_events(version="v3")`` which yields
typed projections (``messages``, ``tool_calls``) that this service routes to
caller-provided callbacks. This design keeps the Model layer UI-agnostic —
the Controller decides how to display each event.

Design: ``design_001_coding_agent_screen.md`` §3.1.
Operation spec: ``operation_spec_001_coding_operations.md`` OP-6/7/8/15.
"""

from __future__ import annotations

import threading
import uuid
from typing import Any, Callable, List, Optional

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.checkpoint.memory import InMemorySaver

from agentx.model.ai.service import AIService
from agentx.model.coding.coding_tools import CODING_TOOLS

DEFAULT_CODING_SYSTEM_PROMPT = (
    "You are a coding assistant that helps users explore, understand, and modify "
    "codebases. You have access to file system tools:\n\n"
    "• file_search(pattern, path?) — find files matching a glob pattern\n"
    "• file_read(path, start?, end?) — read a file (with optional line range)\n"
    "• file_edit(path, old_str, new_str) — make a precise edit (old_str must match exactly)\n"
    "• file_list(path?, recursive?) — list directory contents\n"
    "• file_create(path, content) — create a new file\n\n"
    "Workflow:\n"
    "1. Understand the user's request\n"
    "2. Use file_search/file_list to explore the codebase\n"
    "3. Use file_read to examine relevant files\n"
    "4. Use file_edit to make changes (or file_create for new files)\n"
    "5. Verify changes with file_read\n\n"
    "Always prefer reading files before editing. Show your reasoning (thinking) "
    "before each tool call. Make minimal, focused edits."
)

# Type aliases for callback signatures.
OnReasoning = Callable[[str], None]
OnToolCall = Callable[[str, str], None]
OnToolResult = Callable[[str, str], None]
OnAnswer = Callable[[str], None]
OnDone = Callable[[], None]
OnError = Callable[[str], None]


class CodingAgentService:
    """Manages a LangChain agent with streaming and cancellation.

    Attributes:
        _agent: The compiled LangGraph agent (CompiledStateGraph).
        _checkpointer: In-memory checkpointer for conversation history.
        _thread_id: UUID string for the current conversation thread.
        _cancel_event: Threading event for cancelling in-progress runs.
        _tools: List of tools available to the agent.
        _system_prompt: The agent's system prompt.
        _llm: The LLM instance used.
        _is_running: Whether a stream is currently in progress.
    """

    def __init__(
        self,
        llm: BaseChatModel | None = None,
        tools: List[BaseTool] | None = None,
        system_prompt: str | None = None,
    ) -> None:
        """Initialize the Coding agent service.

        Args:
            llm: The LLM to use. If None, uses AIService().get_current_llm().
            tools: Tools for the agent. If None, uses built-in file tools.
            system_prompt: System prompt. If None, uses DEFAULT_CODING_SYSTEM_PROMPT.
        """
        if llm is None:
            llm = AIService().get_current_llm()

        self._llm = llm
        self._tools: List[BaseTool] = list(tools) if tools is not None else list(CODING_TOOLS)
        self._system_prompt: str = system_prompt or DEFAULT_CODING_SYSTEM_PROMPT
        self._checkpointer = InMemorySaver()
        self._thread_id: str = str(uuid.uuid4())
        self._cancel_event = threading.Event()
        self._is_running: bool = False

        self._agent = create_agent(
            model=self._llm,
            tools=self._tools,
            system_prompt=self._system_prompt,
            checkpointer=self._checkpointer,
        )

    # ── Properties ──────────────────────────────────────────────────────────

    @property
    def thread_id(self) -> str:
        """The current conversation thread ID."""
        return self._thread_id

    @property
    def is_running(self) -> bool:
        """Whether a stream is currently in progress."""
        return self._is_running

    # ── Streaming ───────────────────────────────────────────────────────────

    def stream_agent(
        self,
        user_message: str,
        on_reasoning: OnReasoning,
        on_tool_call: OnToolCall,
        on_tool_result: OnToolResult,
        on_answer: OnAnswer,
        on_done: OnDone,
        on_error: OnError,
    ) -> None:
        """Run the agent and route streaming events to callbacks.

        This is a **blocking** call — it should be invoked on a background
        thread. The caller is responsible for marshalling UI updates back
        to the UI thread (e.g. via ``app.call_from_thread``).

        The cancel event is checked between every delta, so cancellation
        takes effect within one token.

        Args:
            user_message: The user's input text.
            on_reasoning: Called with each reasoning delta (thinking).
            on_tool_call: Called with (tool_name, args_str) when the model
                emits a tool call.
            on_tool_result: Called with (tool_name, result_str) when a tool
                finishes execution.
            on_answer: Called with each text delta (final answer streaming).
            on_done: Called when the agent finishes successfully.
            on_error: Called with an error message string if the run fails.
        """
        self._is_running = True

        try:
            agent_input: dict[str, Any] = {
                "messages": [{"role": "user", "content": user_message}]
            }
            config: dict[str, Any] = {
                "configurable": {"thread_id": self._thread_id}
            }

            stream = self._agent.stream_events(
                agent_input, config=config, version="v3"
            )

            # Consume the messages projection.
            for message in stream.messages:
                if self._cancel_event.is_set():
                    break

                # Reasoning deltas (thinking).
                for delta in message.reasoning:
                    if self._cancel_event.is_set():
                        break
                    on_reasoning(delta)

                # Text deltas (final answer).
                for delta in message.text:
                    if self._cancel_event.is_set():
                        break
                    on_answer(delta)

                # Tool calls emitted by the model.
                finalized = message.tool_calls.get()
                if finalized:
                    for tc in finalized:
                        if self._cancel_event.is_set():
                            break
                        name = tc.get("name", "unknown")
                        args = tc.get("args", {})
                        on_tool_call(name, str(args))

            # Consume the tool_calls projection (execution lifecycle).
            for call in stream.tool_calls:
                if self._cancel_event.is_set():
                    break
                name = getattr(call, "tool_name", "unknown")
                if getattr(call, "error", None):
                    on_tool_result(name, f"Error: {call.error}")
                else:
                    output = getattr(call, "output", "")
                    on_tool_result(name, str(output))

            if not self._cancel_event.is_set():
                on_done()

        except Exception as exc:
            on_error(str(exc))
        finally:
            self._is_running = False
            self._cancel_event.clear()

    # ── Control ─────────────────────────────────────────────────────────────

    def cancel(self) -> None:
        """Cancel an in-progress agent run."""
        self._cancel_event.set()

    def reset_conversation(self) -> None:
        """Start a new conversation (new thread_id)."""
        self._cancel_event.set()
        self._thread_id = str(uuid.uuid4())
        self._cancel_event.clear()

    def get_history(self) -> list:
        """Return the message history for the current thread.

        Returns:
            A list of BaseMessage objects from the checkpointer state.
        """
        try:
            config = {"configurable": {"thread_id": self._thread_id}}
            state = self._agent.get_state(config)
            if state and state.values:
                return state.values.get("messages", [])
        except Exception:
            pass
        return []