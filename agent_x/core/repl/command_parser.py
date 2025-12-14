from typing import List
from dataclasses import dataclass

from agent_x.core.repl.command import Command


@dataclass
class CommandData:
    key: str
    arguments: list[str]

class CommandParser:
    def __init__(self):
        self.commands_list: list[Command] = []

    def add(self, command: Command):
        self.commands_list.append(command)

    def parse(self, text) -> CommandData | None:
        print(f"command process input: {text}")

        raw_command : CommandData = self._parse_text_command(text)
        if raw_command is None:
            print("command process INVALID COMMAND")
            return None

        return raw_command

    def _parse_text_command(self, text_command: str) -> CommandData | None:
        command_arguments = text_command.split()
        if len(command_arguments) <= 0: return None

        command = command_arguments[0]
        raw_arguments = command_arguments[1:]

        return CommandData(key=command, arguments=raw_arguments)

    def _tokenize_arguments(self, arguments: List[str]):
        raw_arguments = [(a, type(a).__name__) for a in arguments]
        print(*raw_arguments, sep='\n')
