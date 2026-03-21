from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.repl.base.IMainController import IMainController

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
