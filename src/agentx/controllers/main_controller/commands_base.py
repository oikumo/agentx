from abc import ABC, abstractmethod


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



