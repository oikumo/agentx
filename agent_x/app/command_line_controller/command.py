
from abc import ABC, abstractmethod

from agent_x.app.controllers.main_controller.main_controller import Actions


class CommandResult(ABC):
    @abstractmethod
    def apply(self):
        pass

class Command(ABC):
    def __init__(self, key: str, description: str = ""):
        self.key = key
        self.description = description
        self.actions: Actions | None = None

    def set_actions_controller(self, actions: Actions):
        self.actions = actions

    @abstractmethod
    def run(self, arguments: list[str]) -> CommandResult | None:
        pass
