from abc import ABC, abstractmethod

from app.repl.command import Command


class IMainController:
    def get_commands(self) -> list[Command]:
        pass
    def close(self):
        pass

class CommandResult(ABC):
    @abstractmethod
    def apply(self):
        pass

class Command(ABC):
    def __init__(self, key: str, controller: IMainController, description: str = ""):
        self.key = key
        self.description = description
        self.controller = controller
    @abstractmethod
    def run(self, arguments: list[str]) -> CommandResult | None:
        pass
