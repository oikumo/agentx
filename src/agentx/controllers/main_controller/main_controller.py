from __future__ import annotations

import copy

from agentx.controllers.main_controller.commands import (
    QuitCommand,
    ClearCommand,
    HelpCommand,
    AIChat,
    SumCommand, HistoryCommand,
    NewSessionCommand, LSCommand, RagShowCommand,
)

from agentx.controllers.chat_controller.chat_controller import ChatController
from agentx.controllers.main_controller.commands_base import Command
from agentx.controllers.main_controller.commands_parser import CommandParser
from agentx.controllers.rag_controller.rag_controller import RagController
from agentx.controllers.session_controller.session_controller import SessionController
from agentx.views.main_view.main_view import MainView, IMainViewPartner
from agentx.ui.ui_console import UIConsole, UIPrompt


class MainController(IMainViewPartner):
    def __init__(self):
        self.commands: dict[str, Command] = {}
        self.parser = CommandParser()
        self.console = UIConsole(UIPrompt("agentx"))

        self.view = MainView(self, self.console)
        self.session_controller = SessionController()
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

    def get_session_manager(self):
        return self.session_controller

    def show_chat(self):
        chat_controller = ChatController(self.console)
        chat_controller.show()
        self.console.reset_prompt()

    def show_rag(self):
        rag_controller = RagController(self.console)
        rag_controller.show()
        self.console.reset_prompt()

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
