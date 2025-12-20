from typing import Protocol

from agent_x.core.repl.command import Command


class ICommandsController(Protocol):
    def get_commands(self) -> list[Command]:
        ...

