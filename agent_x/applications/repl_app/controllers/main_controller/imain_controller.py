from abc import ABC, abstractmethod
from typing import Protocol


class IMainController(Protocol):
    @abstractmethod
    def close(self) -> None: ...
