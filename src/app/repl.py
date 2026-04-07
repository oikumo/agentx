from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    pass


class CommandResult(ABC):
    @abstractmethod
    def apply(self):
        pass


class Command(ABC):
    def __init__(self, key: str, description: str = ""):
        self.key = key
        self.description = description

    @abstractmethod
    def run(self, arguments: list[str]) -> CommandResult | None:
        pass


class MainController:
    def __init__(self):
        self.commands: dict[str, Command] = {}

    def get_commands(self) -> list[Command]:
        return list(self.commands.values())

    def find_command(self, key) -> Command | None:
        return self.commands.get(key)

    def add_command(self, command: Command):
        self.commands[command.key] = command

    def close(self):
        exit(0)


@dataclass
class CommandData:
    key: str
    arguments: list[str]


class CommandParser:
    def __init__(self):
        self.commands_list: list[Command] = []

    def add(self, command: Command):
        self.commands_list.append(command)

    def parse(self, text: str) -> CommandData | None:
        raw_command = self._parse_text_command(text)
        if raw_command is None:
            from views.common.console import Console

            Console.log_error("command process INVALID COMMAND")
            return None
        return raw_command

    def _parse_text_command(self, text_command: str) -> CommandData | None:
        command_arguments = text_command.split()
        if len(command_arguments) <= 0:
            return None
        command = command_arguments[0]
        raw_arguments = command_arguments[1:]
        return CommandData(key=command, arguments=raw_arguments)

    def _tokenize_arguments(self, arguments: List[str]):
        raw_arguments = [(a, type(a).__name__) for a in arguments]


class ReplApp:
    def __init__(self, controller: MainController):
        self.controller = controller
        self.parser = CommandParser()

    def run(self):
        from views.common.console import Console
        from model.session.session import Session
        from model.session.session import SessionDatabase

        Console.log_success("Agent-X")
        Console.log_info("Type 'help' for commands, Ctrl+C to exit")
        session = Session("test_2")
        if not session.create() or not session.is_created():
            raise Exception()
        database = SessionDatabase(session)

        while True:
            try:
                user_input = input("(agent-x) > ").strip()
                if not user_input:
                    continue

                command_data = self.parser.parse(user_input)
                if not command_data:
                    continue

                command = self.controller.find_command(command_data.key)
                if not command:
                    Console.log_error(f"Unknown command: {command_data.key}")
                    continue

                database.insert_history_entry(command_data.key)

                try:
                    result = command.run(command_data.arguments)
                    if result:
                        result.apply()

                except Exception as e:
                    Console.log_error(f"Command execution failed: {e}")

                Console.log_header("History")
                entries = database.select_history_entry()
                if entries:
                    for entry in entries:
                        Console.log_info(entry.command)

            except KeyboardInterrupt:
                Console.log_info("\nReceived interrupt, exiting...")
                break
            except EOFError:
                Console.log_info("\nEOF received, exiting...")
                break
