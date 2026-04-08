from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    pass

class IMainViewPartner:
    def run_command(self, user_input: str):
        pass
    def error(self):
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


