from typing import Optional, List, Any
from dataclasses import dataclass

class Command:
    def __init__(self):
        pass

@dataclass
class CommandData:
    key: str
    arguments: List[Any]

class Commands:
    def __init__(self):
        self.commands_list: list[Command] = []

    def add(self, command: Command):
        self.commands_list.append(command)

    def call(self, text):
        print(f"command process input: {text}")
        raw_command = self._parse_text_command(text)
        if raw_command is None:
            print("command process INVALID COMMAND")
            return

        if raw_command.key not in self.commands_list:
            print("command not found")
            return

        print("command process OK")

        self._tokenize_arguments(raw_command.arguments)

    def _parse_text_command(self, text_command: str) -> Optional[CommandData]:
        command_arguments = list(map(str, text_command.split()))
        if len(command_arguments) <= 0: return None

        command = command_arguments[0]
        raw_arguments = command_arguments[1:]

        return CommandData(key=command, arguments=raw_arguments)

    def _tokenize_arguments(self, arguments: List[str]):
        raw_arguments = [(a, type(a).__name__) for a in arguments]
        print(*raw_arguments, sep='\n')
