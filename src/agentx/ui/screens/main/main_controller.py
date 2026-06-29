from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from agentx.ui.screens.chat.chat_controller import ChatController
from agentx.ui.screens.main.commands.commands import SumCommand, QuitCommand, ClearCommand, HelpCommand, \
    AIChat, HistoryCommand, NewSessionCommand, LSCommand, RagShowCommand, VersionCommand
from agentx.ui.screens.main.commands.commands_base import Command
from agentx.ui.screens.main.commands.commands_parser import CommandParser
from agentx.model.session.session_manager import SessionManager
from agentx.ui.screens.main.main_view import MainView
from agentx.ui.interfaces import IMainViewPartner, IChatView, IRagView, IMainView
from agentx.ui.screens.rag.rag_controller import RagController

if TYPE_CHECKING:
    from agentx.ui.interfaces import IUIProvider
    from agentx.agent.controller.agent_controller import AgentController


class MainController(IMainViewPartner):
    def __init__(self, view: IMainView | None = None, provider: "IUIProvider | None" = None):
        self.commands: dict[str, Command] = {}
        self.parser = CommandParser()
        self.view: IMainView = view if view else MainView(self)
        self._provider = provider
        self.session_controller = SessionManager()
        # Store sub-controllers and views for screen connection
        self._chat_controller: ChatController | None = None
        self._chat_controller: ChatController | None = None
        self._chat_view: IChatView | None = None
        self._rag_controller: RagController | None = None
        self._rag_view: IRagView | None = None
        self._agent_controller: AgentController | None = None
        self.load_commands()

    def load_commands(self):
        self.add_command(SumCommand("sum", self))
        self.add_command(QuitCommand("quit", self))
        self.add_command(ClearCommand("clear", self))
        self.add_command(HelpCommand("help", self))
        self.add_command(HistoryCommand("history", self))
        self.add_command(AIChat("chat", self))
        self.add_command(NewSessionCommand("new", self))
        self.add_command(LSCommand("ls", self))
        self.add_command(RagShowCommand("rag", self))
        self.add_command(VersionCommand("version", self))

    def get_session_manager(self):
        return self.session_controller

    def show_chat(self):
        # Use provider to create appropriate chat view if available
        if self._provider:
            chat_controller = ChatController()
            chat_view = self._provider.create_chat_view(chat_controller)
            chat_controller.view = chat_view
            # Store for screen connection
            self._chat_controller = chat_controller
            self._chat_view = chat_view
            # Don't call show() - screen will be pushed by MainTUIScreen
        else:
            # Fallback: create controller without view (will use console default)
            chat_controller = ChatController()
            chat_controller.show()

    def show_rag(self):
        # Use provider to create appropriate RAG view if available
        if self._provider:
            rag_controller = RagController()
            rag_view = self._provider.create_rag_view(rag_controller)
            rag_controller.view = rag_view
            # Store for screen connection
            self._rag_controller = rag_controller
            self._rag_view = rag_view
            # Don't call show() - screen will be pushed by MainTUIScreen
        else:
            # Fallback: create controller without view (will use console default)
            rag_controller = RagController()
            rag_controller.show()

    def get_chat_controller(self) -> tuple[ChatController | None, IChatView | None]:
        """Get the chat controller and view for screen connection."""
        return self._chat_controller, self._chat_view

    def get_rag_controller(self) -> tuple[RagController | None, IRagView | None]:
        """Get the RAG controller and view for screen connection."""
        return self._rag_controller, self._rag_view

    def show_agent(self) -> None:
        """Create and wire an Agent + AgentController for the TUI agent screen."""
        from agentx.agent.model.agent import Agent
        from agentx.agent.model.ai_adapter import AIServiceAdapter
        from agentx.agent.controller.agent_controller import AgentController
        from agentx.agent.types import AgentConfig, AutonomyLevel, MemoryConfig

        # Use the session working directory for persistence + sandbox
        session_dir = "."
        try:
            session = self.session_controller.get_current_session()
            if session and session.directory:
                session_dir = session.directory
        except Exception:
            pass

        import os
        agent_id = f"agent_{os.getpid()}"
        config = AgentConfig(
            id=agent_id,
            name="AgentX Agent",
            autonomy_level=AutonomyLevel.SUPERVISED,
            memory_config=MemoryConfig(persistent_path=session_dir),
            sandbox_root=session_dir,
        )
        agent = Agent(config)
        # Wire the AI service so reflection works (degrades gracefully if
        # no API keys are configured)
        agent.set_ai_service(AIServiceAdapter())
        controller = AgentController(agent)
        self._agent_controller = controller

    def get_agent_controller(self) -> AgentController | None:
        """Get the agent controller for screen connection."""
        return self._agent_controller

    def show_react(self):
        from agentx.ui.screens.react.react_controller import ReActController
        react_controller = ReActController()
        react_controller.show()

    def print_message(self, message: str):
        self.view.print_message(message)

    def print_warring_message(self, message: str):
        self.view.print_warring_message(message)

    def print_error_message(self, message: str):
        self.view.print_error_message(message)

    def run(self):
        self.view.show()

    def get_commands(self) -> list[Command]:
        return copy.deepcopy(list(self.commands.values()))

    def add_command(self, command: Command):
        self.commands[command.key] = command

    def commands_history(self) -> list[str]:
        history: list[str] = []

        entries = self.session_controller.select_history_entry()
        if entries:
            for entry in entries:
                history.append(entry.command)
        return history


    def close(self):
        exit(0)

    def error(self):
        pass

    def print(self):
        pass

    def run_command(self, user_input: str):
        command_data = self.parser.parse(user_input)
        if not command_data:
            return

        command = self.commands.get(command_data.key)
        if not command:
            self.view.print_response_error(f"Unknown command: {command_data.key}")
            return

        self.session_controller.insert_history_entry(command_data.key)

        try:
            command.run(command_data.arguments)

        except Exception as e:
            self.view.print_response_error(f"Command execution failed")
            print(e)