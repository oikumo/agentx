from __future__ import annotations
from typing import TYPE_CHECKING
from agentx.controllers.main_controller.commands import (
    QuitCommand,
    ClearCommand,
    HelpCommand,
    AIChat,
    SumCommand, HistoryCommand,
    NewCommand, LSCommand, RagWebIngestion,
)

from agentx.controllers.chat_controller.chat_controller import ChatController
from agentx.controllers.main_controller.commands_base import Command
from agentx.controllers.main_controller.commands_parser import CommandParser
from agentx.controllers.session_controller.session_controller import SessionController
from agentx.views.main_view.main_view import MainView, IMainViewPartner

class MainController(IMainViewPartner):
    def __init__(self):
        self.commands: dict[str, Command] = {}
        self.parser = CommandParser()
        self.view = MainView(self)
        self.session_controller = SessionController()
        self.load_commands()

    def load_commands(self):
        self.add_command(SumCommand("sum", self))
        self.add_command(QuitCommand("quit", self))
        self.add_command(ClearCommand("clear", self))
        self.add_command(HelpCommand("help", self))
        self.add_command(HistoryCommand("history", self))
        self.add_command(AIChat("chat", self))
        self.add_command(NewCommand("new", self))
        self.add_command(LSCommand("ls", self))
        self.add_command(RagWebIngestion("ingest", self))

    def get_session_manager(self):
        return self.session_controller

    def showChat(self, query: str | None):
        chat_controller = ChatController()
        chat_controller.show(query)

    def run(self):
        self.view.show()

        while True:
            self.view.capture_input()

    def get_commands(self) -> list[Command]:
        return list(self.commands.values())

    def find_command(self, key) -> Command | None:
        return self.commands.get(key)

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

        command = self.find_command(command_data.key)
        if not command:
            self.view.print_response_error(f"Unknown command: {command_data.key}")
            return

        self.session_controller.insert_history_entry(command_data.key)

        try:
            result = command.run(command_data.arguments)
            if result:
                result.apply()

        except Exception as e:
            self.view.print_response_error(f"Command execution failed")
